# subset-b-006969 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_data_sync.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_data_sync.h

## Purpose
This header defines the RADOS-backed RGW multisite data-sync status, context, and administrative interfaces. It is mostly declarations plus inline serialization for data sync state, bucket sync state, remote data-log access, bucket-pipe sync status, sync modules, and permission helpers used by the data sync coroutines implemented elsewhere. It connects remote zone REST access, local RADOS status objects, bucket index log state, sync policy routing, fairness, tracing, error logging, and admin progress reporting.

## Important APIs, Types, and Functions
`rgw_data_sync_obligation` is the in-memory work descriptor for a bucket shard, optional bilog generation, marker, timestamp, and retry flag. `rgw_datalog_info`, `rgw_data_sync_info`, `rgw_data_sync_marker`, and `rgw_data_sync_status` model remote data-log shard count and per-shard full or incremental sync progress. They provide Ceph buffer encoding, JSON dump/decode, and test-instance hooks.

`RGWDataSyncEnv` is the service bundle passed into sync coroutines: dpp, cct, `RadosStore`, services, async rados processor, HTTP manager, error logger, trace manager, sync module, perf counters, fairness bid manager, and optional pretty-print stream. `RGWDataSyncCtx` adds a REST connection and source-zone id, with `LatencyConcurrencyControl` to reduce concurrency when sync lock latency approaches fractions of the lease period.

`RGWRemoteDataLog` is a coroutine manager facade over remote data-log operations: read log info, list shard info and next entries, read/init/run sync status, read recovering or lagging shard state, and wake up specific shards with data notifications. `RGWDataSyncStatusManager` wraps that remote log for zone-level sync status and implements `DoutPrefixProvider`.

The bucket-specific half declares `rgw_bucket_shard_full_sync_marker`, `rgw_bucket_shard_inc_sync_marker`, `rgw_bucket_shard_sync_info`, `rgw_bucket_full_sync_status`, `BucketSyncState`, `rgw_bucket_sync_status`, `bilog_status_v2`, `store_gen_shards`, and `rgw_bucket_index_marker_info`. `RGWBucketPipeSyncStatusManager` manages sync status for one destination bucket and one or more source pipes, including full status, incremental status, object-status oid naming, remote bilog info, and `run()`. `rgw_read_remote_bilog_info()`, `rgw_read_bucket_full_sync_status()`, and `rgw_read_bucket_inc_sync_status()` are the public read helpers.

`RGWDefaultSyncModule` and `RGWArchiveSyncModule` declare module capabilities. `RGWUserPermHandler` asynchronously loads user ACL/IAM state and exposes a nested `Bucket` helper that validates bucket/object permissions during sync.

## Control Flow
The declared flow starts with a status manager initializing a `RGWRemoteDataLog` against a source zone and REST connection. Admin or sync code can read remote data-log info, initialize the local status object, then run sync. Bucket-pipe sync construction discovers matching source pipes, builds per-source `RGWDataSyncCtx` values, reads remote bucket index marker info, initializes status objects, then runs a `RGWBucketSyncCR`.

Serialization flow is versioned. Zone sync info has states `init`, `building-full-sync-maps`, and `sync`; shard markers switch from `full-sync` to `incremental-sync`; bucket shard status moves from init to full to incremental or stopped. JSON decoding maps unknown or missing state strings conservatively toward init.

Concurrency flow is adjusted by `LatencyConcurrencyControl::adj_concurrency()`. It compares average lock latency to `rgw_sync_lease_period / 12`, halves proposed concurrency in throttled state, drops to one operation in overloaded state, and logs state transitions only when the state changes.

## State and Persistence Behavior
Most types are durable status records stored in RGW metadata or per-shard RADOS objects. `rgw_data_sync_status` encodes only `sync_info`; shard markers are intentionally encoded separately. Bucket shard status uses attrs for state and incremental markers, and retains backward decode support for the older full marker embedded in v1. `rgw_bucket_sync_status` version 2 persists full state, incremental generation, and per-shard generation completion bits.

The header defines important oid naming contracts: zone sync status object ids, source shard status prefixes, bucket full-status ids, incremental-status ids, and per-object status ids. These names are integration contracts with admin commands and sync coroutines.

## Dependencies and Integration Points
The file depends on RGW coroutine, HTTP client, SAL Rados store, data log, sync module, sync trace, sync policy, bucket sync, fairness, JSON, Ceph encoding, and formatter infrastructure. It integrates with remote REST APIs, local RADOS metadata/status objects, sync error logging, `radosgw-admin bucket sync run` pretty output, IAM/ACL policy evaluation, and perf counters.

## Risks and Test Signals
Compatibility risks are concentrated in versioned encoders and JSON state strings: old shard status attrs, missing `instance_id`, and unknown bucket sync states should decode safely. Runtime risks include stale object-id naming, lock latency feedback reducing too aggressively, and permission handler initialization racing sync work. Tests should cover encode/decode round trips for every status type, old-version decode paths, JSON admin output, remote datalog reads with truncated markers, bucket-pipe full-to-incremental transitions, pause/stopped status, and permission checks with ACL plus IAM policy combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_data_sync.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_datalog.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_datalog.cc

## Purpose
This file implements the RGW data changes log used by multisite data sync to record bucket shard changes. It supports two generation-aware backing formats, legacy cls log omap and newer cls fifo, plus background tasks that coalesce frequent changes, maintain semaphores for crash recovery, watch other RGWs, synthesize missed log entries, trim old generations, and expose admin semaphore tooling.

## Important APIs, Types, and Functions
`rgw_data_change`, `rgw_data_change_log_entry`, `rgw_data_notify_entry`, and `RGWDataChangesLogInfo` implement dump/decode helpers for log entries, notification entries, and per-shard marker info.

`RGWDataChangesOmap` and `RGWDataChangesFIFO` are concrete `RGWDataChangesBE` backends. Omap stores `cls::log::entry` values with `nlog::add/list/info/trim`; FIFO stores encoded bufferlists through `LazyFIFO`. Both convert backend records to `rgw_data_change_log_entry`, expose `max_marker()`, detect empty generations, and tolerate missing objects as empty where appropriate.

`DataLogBackends` owns generation metadata through `logback_generations` and a map of generation id to backend. Its `list()` walks generations using `cursorgen()` and `gencursor()`, `trim_entries()` trims all generations up to a target generation/cursor, and `trim_generations()` prunes empty non-head generations.

`RGWDataChangesLog` is the service class. Public APIs include `start()`, `add_entry()`, `list_entries()`, `get_info()`, `trim_entries()`, `trim_generations()`, `change_format()`, `mark_modified()`, `read_clear_modified()`, `recover()`, shutdown, and admin semaphore list/reset. Internal helpers include `choose_oid()`, `_get_change()`, `renew_entries()`, `watch_loop()`, `process_notification()`, `synthesize_entries()`, `gather_working_sets()`, and `decrement_sems()`.

## Control Flow
Startup initializes a RADOS ioctx for the zone log pool, initializes the generation metadata object with FIFO as the default backing, and optionally starts renew, watch, and recovery coroutines. If data logging is disabled, the ioctx and backends are still initialized but background logging returns early.

`add_entry()` filters buckets, notifies an observer, hashes the bucket shard to a datalog shard, and chooses between direct push and windowed coalescing. If the watch is unavailable, it pushes directly to the head backend and treats failure as fatal to that call. If the watch is healthy, it marks the shard modified, checks a per-bucket-generation `ChangeStatus`, writes at most once per `rgw_data_log_window`, and registers later changes in a current renewal cycle guarded by semaphores.

`renew_entries()` swaps the current cycle, adds each `BucketGen` key into an in-memory semaphore set, batches encoded `rgw_data_change` records per log shard, pushes them to the head backend, updates expiration timestamps, then decrements the semaphore set on RADOS only after successful backend pushes. This ordering is the core crash-recovery invariant.

Recovery lists semaphore objects, synthesizes data-log entries for outstanding keys, notifies other RGWs to subtract in-flight working sets, then decrements the remaining semaphore counts with a grace period. Watch notifications use `recovery_check` and `recovery_reply` payloads so live RGWs can report keys in `cur_cycle` or local semaphore sets. The watch loop handles overflow, cancellation, unwatch, and rewatch attempts.

Listing flow can list one shard with a string marker or scan all shards with `RGWDataChangesLogMarker`. Generation cursors are prepended to backend-native cursors so callers see one monotonic marker space across backends and log generations.

## State and Persistence Behavior
Persistent state includes generation metadata in `data_loggenerations_metadata`, data-log entries in `data_log.<shard>` or `data_log@G<gen>.<shard>`, and semaphore sets in `_sem_setdata_log.<shard>`. In-memory state includes LRU `changes`, `cur_cycle`, `semaphores`, modified shard notifications, watch cookie, background futures, and cancellation signals. The durable ordering is conservative: semaphores are incremented before deferred changes can be lost, and decremented only after a corresponding log entry is safely pushed or recovered.

## Dependencies and Integration Points
The file integrates with neorados, `cls/log`, `cls/fifo`, `cls/sem_set`, async spawn groups, blocked completion, RGW bucket layout, SAL Rados store, log backing generation helpers, bucket change observers, and admin output. Multisite sync readers depend on `list_entries()` and `get_info()`, while notification senders consume `read_clear_modified()` and v1/v2 notify encoders from the companion notify files.

## Risks and Test Signals
Key risks are duplicate or lost change entries around watch loss, renewal failure, semaphore decrement failure, and generation trimming. `read_sems()` has a subtle error condition that should be tested around ENOENT and end-of-buffer handling. Other risks include invalid `BucketGen` parsing, shard bounds, backend migration, async shutdown races, and FIFO/omap marker compatibility. Test signals should include direct-push fallback, coalesced updates inside and outside the window, crash recovery with outstanding semaphores, notification missed-response handling, generation cursor list/trim behavior, format changes, admin semaphore pagination/reset, and shutdown with background futures present or absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_datalog.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_datalog.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_datalog.h

## Purpose
This header declares the RGW data changes log model and service interface. It defines the durable entry formats, notification records, generation-aware backend manager, bucket-generation key type, and the `RGWDataChangesLog` class that producers, sync readers, admin commands, and tests use to add, list, trim, recover, and observe bucket change logs.

## Important APIs, Types, and Functions
`DataLogEntityType` currently distinguishes bucket entries from unknown entries. `rgw_data_change` is the encoded change payload and includes entity type, bucket shard key, timestamp, and bilog generation. Its encoder uses compat version 1 when `gen == 0` and requires version 2 when a generation is present. `rgw_data_change_log_entry` adds backend log id and log timestamp. `RGWDataChangesLogInfo` exposes a max marker and last update time, while `RGWDataChangesLogMarker` carries cross-shard listing position.

`rgw_data_notify_entry` is the per-bucket notification key plus generation, ordered by key then gen. `DataLogBackends` derives from `logback_generations` and a flat map of generation backends. It declares listing, trimming entries, trimming empty generations, and generation lifecycle callbacks.

`BucketGen` combines `rgw_bucket_shard` and generation into a lexicographically sortable key. Its parser decodes `tenant/name:instance:shard:gen` style keys, accepts buckets without tenants or bucket ids, and throws `boost::system_error` on malformed generations or shards. Equality, ordering, stream output, and `std::hash` are provided.

`RGWDataChangesLog` owns RADOS access, backend generations, async strands/futures for renew/watch/recovery, modified notification state, coalescing status, semaphore state, and public methods for lifecycle, entry production, entry listing, trimming, format changes, recovery, shutdown, and admin semaphore operations. `RGWDataChangesBE` is the abstract backend API implemented by omap and FIFO in the `.cc` file.

## Control Flow
The public interface supports blocking and coroutine start paths. Producers call one of the `add_entry()` overloads with bucket info, bucket log layout generation, and shard id. Sync readers call shard-specific or cross-shard `list_entries()`, then `trim_entries()` after replication. Background code calls `renew_run()`, `watch_loop()`, and `recover()` through start options. Administrators call `admin_sem_list()` and `admin_sem_reset()` to inspect or repair semaphore state.

The backend abstraction normalizes write preparation, batched push, yielding push, list, info, trim, max marker, and empty checks across cls log and FIFO. The generation manager ensures callers can list and trim through a single marker namespace even while backing generations change.

## State and Persistence Behavior
The header encodes persistence contracts for data changes and log entries. `rgw_data_change` versioning is important because older decoders do not understand nonzero generations. `RGWDataChangesLog` object names are declared as methods rather than constants because generation ids and shard ids are part of the durable namespace. In-memory coalescing state uses `ChangeStatus` entries with expiration, sent time, pending flag, condition variable, and sync policy reference.

## Dependencies and Integration Points
Dependencies include neorados, Ceph async conditions/yield contexts, spawn groups, LRU map, cls log types, sem_set, RGW basic types, sync policy, trim bilog helpers, zone config, and log backing generation support. Integration points are RGW bucket mutation paths, multisite data sync readers, metadata generation migration, admin commands, unit tests via `DataLogTestBase`, and optional bucket change observers.

## Risks and Test Signals
Header-level risks include marker compatibility, `BucketGen` parse ambiguity between bucket id and shard id, generation version compatibility, lock ordering around `modified_lock` and `lock`, and backend interface mismatches when adding a new log type. Tests should cover `BucketGen` round trips for tenant/no-tenant, bucket-id/no-bucket-id, shard, and malformed strings; encode/decode of v1 and v2 changes; marker truthiness and clearing; backend polymorphic list/trim contracts; and `max_marker()` ordering against real backend markers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_datalog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_datalog_notify.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_datalog_notify.cc

## Purpose
This file implements JSON compatibility adapters for the v1 RGW data-log notification API. The current notification entry type contains both bucket key and generation, but the v1 wire shape only exposed object keys as strings. These helpers encode and decode the old map-of-shards-to-set-of-strings form while preserving the current in-memory `rgw_data_notify_entry` container type.

## Important APIs, Types, and Functions
`EntryEncoderV1` wraps a single `rgw_data_notify_entry` and emits only `entry.key`. `SetEncoderV1` wraps a flat set of notification entries and emits an array of `"obj"` strings. The exported `encode_json(const char*, const rgw_data_notify_v1_encoder&, Formatter*)` emits an array of objects with `"key"` shard id and `"val"` encoded set.

`EntryDecoderV1` decodes one JSON string into `entry.key` and explicitly sets `entry.gen = 0`, because the v1 API had no generation field. `SetDecoderV1` iterates array children and inserts decoded entries into a `bc::flat_set`. The exported `decode_json_obj(rgw_data_notify_v1_decoder&, JSONObj*)` decodes the top-level array back into a flat map of shard id to entry set.

## Control Flow
Encoding walks shards in sorted flat-map order, opens an object for each shard, writes the shard id, then writes the v1 set of strings. Decoding mirrors that flow by iterating top-level array entries, reading `"key"` into `shard_id`, decoding `"val"` through `SetDecoderV1`, and replacing `d.shards[shard_id]` with the decoded set.

## State and Persistence Behavior
The file does not persist data directly. It defines a compatibility JSON representation used at API boundaries. Generation state is intentionally discarded when encoding v1 and defaults to zero when decoding v1, so v1 clients cannot distinguish bilog generations for the same key.

## Dependencies and Integration Points
It depends on `rgw_datalog_notify.h`, `rgw_datalog.h`, `Formatter`, `JSONObj`, `JSONObjIter`, and `JSONDecoder`. It integrates with data-log notification REST/admin paths that need legacy JSON while the internal notification set remains generation-aware.

## Risks and Test Signals
The main risk is lossy generation conversion. If a shard contains multiple entries with the same key but different generations, v1 encoding collapses them to duplicate strings in semantic terms, and v1 decoding reintroduces only `gen = 0`. Tests should verify exact v1 JSON shape, empty shard maps, multiple shards, deterministic ordering from flat containers, and mixed generation inputs documenting the lossy behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_datalog_notify.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_datalog_notify.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_datalog_notify.h

## Purpose
This header declares the v1 JSON encoder and decoder wrappers for RGW data-log notifications. It keeps old notification API formatting separate from the generation-aware `rgw_data_notify_entry` type declared in `rgw_datalog.h`.

## Important APIs, Types, and Functions
`rgw_data_notify_v1_encoder` holds a const reference to `bc::flat_map<int, bc::flat_set<rgw_data_notify_entry>>` and is passed to `encode_json()`. `rgw_data_notify_v1_decoder` holds a mutable reference to the same map shape and is passed to `decode_json_obj()`. The API is intentionally tiny and relies on custom overloads rather than changing the core notification entry's normal JSON shape.

## Control Flow
There is no runtime flow in the header beyond wrapper construction by callers. The implementation uses these wrappers to select v1 behavior: encode current entries as shard-to-key-string arrays, or decode those arrays back into entries with zero generation.

## State and Persistence Behavior
The wrappers do not own state; they borrow caller-provided maps. The v1 conversion contract is state-significant because it strips generation information from notifications crossing this compatibility path.

## Dependencies and Integration Points
The header depends on Boost flat containers and `rgw_datalog.h`, forward declares formatter and JSON types, and is consumed by the implementation file plus notification API callers. It is an integration shim between the current datalog notification model and legacy JSON clients.

## Risks and Test Signals
Risks are reference lifetime misuse, accidental use of v1 wrappers where generation-preserving JSON is required, and divergence between declarations and implementation overloads. Compile tests should include this header without the implementation's private wrappers, and API tests should verify v1 decode/encode compatibility with old clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_datalog_notify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup.cc

## Purpose
This file implements the RADOS-backed background deduplication scan for RGW. In the compiled configuration shown here, full dedup mutation support is behind `FULL_DEDUP_SUPPORT`, so the active production path performs estimate-oriented scanning: it creates or opens the dedup work pool, scans all bucket index shards into temporary slab objects partitioned by md5 shard, builds dedup tables to estimate duplicates, records cluster tokens/statistics, honors pause/abort/restart/throttle notifications, and cleans up temporary slabs and the work pool when all shards complete.

## Important APIs, Types, and Functions
`Background::DedupWatcher` receives cluster notifications and redirects valid watch cookies to `Background::handle_notify()`. `control_t` serialization records dedup request type, start/execution/shutdown/pause/abort/restart flags, and bucket-index/metadata throttles.

Pool and handle helpers include `create_pool()`, `init_dedup_pool_ioctx()`, `safe_pool_delete()`, and `init_rados_access_handles()`. `safe_pool_delete()` verifies the pool id still matches the expected id before deletion to avoid removing a recreated pool.

The active scan path includes `collect_all_buckets_stats()`, `calc_num_md5_shards()`, `setup()`, `objects_ingress_single_work_shard()`, `ingress_bucket_objects_single_shard()`, `process_bucket_shards()`, `ingress_bucket_idx_single_object()`, `process_all_slabs()`, `objects_dedup_single_md5_shard()`, `process_all_shards()`, `work_shards_barrier()`, `md5_shards_barrier()`, and `run()`. These functions enumerate buckets, list bucket index shards with cls rgw bucket list operations, filter buckets and storage classes, parse etags, skip too-small non-multipart objects, write `disk_record_t` records to slab objects, build dedup tables per md5 shard, count duplicates, remove slabs, and update heartbeats.

When `FULL_DEDUP_SUPPORT` is enabled, additional helpers read object attrs and manifests, calculate BLAKE3 hashes, split head objects into tail objects, compare strong hashes, manipulate refcount cls tags, adjust target manifests, write `RGW_ATTR_SHARE_MANIFEST` and `RGW_ATTR_BLAKE3`, free old tail refs, and execute actual dedup remapping. These paths are important for understanding intended design but are compiled out in the current non-full-dedup build.

## Control Flow
`Background::start()` launches `run()` once. The main loop waits for remote restart, pause, or shutdown. On a restart that `d_cluster.can_start_new_scan()` accepts, it sets `dedup_exec` and performs `setup()`: gather bucket stats, compute md5/work shard counts, initialize the dedup pool/ioctx, reset cluster epoch tokens, and validate request type. Without full support, setup asserts that the request type is estimate.

The scan allocates one raw memory buffer sized as `DISK_BLOCK_COUNT * sizeof(disk_block_t) * num_md5_shards`. It first claims work shard tokens and runs ingress. Each worker lists all bucket instances, filters configured buckets, opens each bucket index, processes only bucket-index shards assigned to that worker id, converts eligible entries into disk records, and flushes slab buffers into the dedup pool. After all work shards finish or time out, md5 shard workers load slabs from every work shard, build a dedup table, count duplicates, display statistics, remove input slabs, and mark md5 shard tokens completed. Once all md5 shards are complete, the dedup pool is deleted if the pool id is unchanged.

Notification flow decodes urgent messages. Abort and pause wait for the background thread to acknowledge, resume clears pause flags, restart optionally decodes a filter and requests a new scan, and throttle updates bucket-index or metadata throttle limits. Local pause closes watch and ioctx; resume refreshes handles and watch.

## State and Persistence Behavior
Persistent state is mostly temporary and coordination-oriented: the dedup pool stores slab objects, cluster epoch/token objects, shard heartbeats, and stats; pool deletion is the cleanup boundary. RGW bucket index entries and bucket stats are read but not modified in the active estimate build. Control state is encoded for cluster notifications/acks. In full-support builds, object attrs and manifests become persistent mutation targets, with compare-xattr guards intended to avoid deduping changed objects.

## Dependencies and Integration Points
The file integrates with RGW SAL, `RadosStore`, bucket metadata listing, bucket index cls operations, RGW placement/storage class helpers, dedup table/store/cluster/epoch utilities, cls refcount/version/rgw clients, librados aio throttles, Ceph crypto, and perf counters. It relies on companion dedup headers for disk record layout, filters, epoch tokens, and statistics.

## Risks and Test Signals
Active-path risks include races with bucket deletion, indexless buckets, malformed etags, changed storage class metadata, slab corruption, token heartbeat expiry, pool id reuse, and pause/shutdown condition-variable ordering. `collect_all_buckets_stats()` and `objects_ingress_single_work_shard()` complete the metadata-list handle inside the loop after each batch, which deserves focused regression coverage because premature completion could affect pagination semantics. In full-support builds, risks expand to manifest corruption, md5 collision without strong-hash validation, refcount rollback gaps, shared tail objects from server-side copy, split-head orphan tails, compare-xattr coverage, and compressed/encrypted object skips. Tests should cover estimate scans over sharded buckets, filters, small object and multipart thresholds, storage classes, corrupted bucket index records, pause/resume/abort/restart notifications, throttle changes, safe pool deletion after pool recreation, slab load failures, and full-support unit tests for hash/manifests/refcount rollback if that build flag is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup.cc -->
