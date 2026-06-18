# Research: subset-b-006977

Grouped research for Ceph RGW RADOS driver files. Each source file has a bounded section with the required split markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sal_rados.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sal_rados.h

## Purpose
This header declares the RADOS-backed implementation of RGW's storage abstraction layer. It adapts generic `rgw::sal` concepts such as `StoreDriver`, `StoreUser`, `StoreBucket`, `StoreObject`, `StoreWriter`, `Lifecycle`, `Restore`, notifications, Lua management, and roles onto the legacy `RGWRados` service stack and librados/neorados primitives.

## Important APIs, Types, and Functions
- `RadosStore` is the central `StoreDriver` implementation. It owns or exposes `RGWRados`, `RGWServices`, `RGWCtl`, the local `RadosZone`, `neorados::RADOS`, and user control pointers.
- `RadosZoneGroup`, `RadosZone`, and `RadosPlacementTier` wrap zonegroup, zone, placement, tiering, and sync-policy data from `RGWZoneGroup`, `RGWZone`, and `RGWZoneGroupPlacementTier`.
- `RadosUser`, `RadosBucket`, and `RadosObject` implement user, bucket, and object operations, including metadata, usage, ACLs, bucket index maintenance, quota checks, multipart, object copy/delete/read, cloud transition, restore, Swift versioning, omap helpers, and chown.
- `RadosObject::RadosReadOp` and `RadosObject::RadosDeleteOp` bridge SAL operations to `RGWRados::Object::Read` and `RGWRados::Object::Delete`.
- `RadosMultipartUpload` and `RadosMultipartPart` expose multipart state, part listing, abort, complete, part cleanup, and writer construction around `RGWMPObj`, manifests, and placement rules.
- `MPRadosSerializer`, `LCRadosSerializer`, and `RadosRestoreSerializer` provide cls lock based serialization for multipart, lifecycle, and restore operations, including renewal state for multipart locks.
- `RadosAtomicWriter`, `RadosAppendWriter`, and `RadosMultipartWriter` wrap `rgw::putobj::*ObjectProcessor` implementations behind the SAL `StoreWriter` interface.
- `RadosNotification` wraps `rgw::notify::reservation_t` for reserve/commit publication of object events.
- `RadosLuaManager` handles Lua scripts/packages stored in RADOS, with watch/notify callbacks for package reloads and script updates.
- `RadosRole` specializes `RGWRole` persistence through the RADOS store.

## Control Flow
Callers enter through generic SAL methods on `RadosStore`, `RadosBucket`, or `RadosObject`. The header shows that most work is delegated to the `RGWRados` object, service pointers from `svc()`, and metadata controllers from `ctl()`. Object writes flow through `get_atomic_writer()`, `get_append_writer()`, or multipart upload writers, then into put-object processors that prepare, process data chunks, and complete index/object metadata updates. Reads and deletes use nested op objects so the generic SAL operation can retain RADOS-specific operation state.

## State and Persistence Behavior
Persistent state is spread across RGW metadata objects, bucket indexes, object heads/tails, usage logs, lifecycle and restore queues, pubsub topic metadata, Lua package/script objects, role/account/group metadata, and multipart metadata. `RadosObject` owns an `RGWObjectCtx` in normal construction but shares it when copied, so cache invalidation and object state ownership matter. Serializers persist lock state in RADOS via cls lock. Writers persist object data, manifests, attrs, delete markers, version metadata, and index updates through `RGWRados` processors.

## Dependencies and Integration Points
The file depends on SAL base interfaces, `rgw_rados.h`, notification, roles, multipart, put-object processors, RADOS tiering services, cls lock, librados, and neorados. It is the main integration seam between portable RGW request logic and the RADOS backend. It also exposes admin integration through metadata list/remove functions, admin API registration, usage operations, sync wakeups, and sync-policy/data-sync managers.

## Risks
- The header is broad and exposes many raw pointers to services owned by `RGWRados`; lifetime ordering is critical.
- `RadosObject` copy construction shares `RGWObjectCtx` and manifest pointers while toggling ownership, so stale state or double-free bugs are possible if ownership assumptions drift.
- Lock renewal in `MPRadosSerializer` is asynchronous; cancellation and unlock paths need careful race handling.
- Many methods bridge generic SAL behavior to legacy RADOS-specific APIs, so behavioral changes can regress non-obvious areas such as versioning, notification, usage, or sync.
- The notification class notes that `reservation_t` is RADOS-specific even though notifications are a generic SAL concept.

## Test Signals
Useful signals include RGW object read/write/delete tests, multipart complete/abort/list tests, bucket lifecycle and restore tests, pubsub notification tests, Lua script reload/watch tests, role/account/group metadata tests, bucket index consistency tests, and multisite sync tests that exercise `wakeup_meta_sync_shards()` and `wakeup_data_sync_shards()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sal_rados.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_service.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_service.cc

## Purpose
This file constructs, initializes, starts, and shuts down the RGW RADOS service graph. It also initializes higher-level control objects and metadata handlers used by admin and metadata paths.

## Important APIs, Types, and Functions
- `RGWServices_Def::init()` allocates concrete service implementations such as bucket services, bucket index, bilog, cls, config-key, datalog, mdlog, notify, zone, quota, sync modules, sysobj, user, and async RADOS processor.
- `RGWServices_Def::shutdown()` tears down started services and stops the async processor.
- `RGWServices::do_init()` calls the definition initializer and exports raw service pointers through the public `RGWServices` facade.
- `RGWServiceInstance::start()` provides idempotent start-state handling for services and intentionally marks a service as starting before `do_start()` to tolerate circular service references.
- `RGWCtlDef::init()` builds metadata managers, metadata handlers, user/bucket controls, and topic cache.
- `RGWCtl::init()` attaches metadata handlers to the metadata manager and exposes control pointers.

## Control Flow
Initialization first allocates all service objects, starts the async RADOS processor, wires dependencies through each service's `init()`, then starts services in dependency-aware order. Notify starts first when cache support exists. In non-raw mode, zone, datalog, mdlog, sync modules, bucket, bucket-sync, and user services are started; raw mode skips several higher-level services. Core services such as cls, config key, zone utils, quota, sysobj core/cache/sysobj are started in both modes. Control initialization happens after services exist and attaches metadata handlers one by one, aborting on the first attach error.

## State and Persistence Behavior
The file manages in-memory ownership of service instances through `unique_ptr`s in `RGWServices_Def`, plus exposed non-owning pointers in `RGWServices`. It starts background stateful components including `RGWAsyncRadosProcessor`, datalog service, mdlog service, notify/cache integration, and sync modules. Metadata handlers created in `RGWCtlDef` persist and retrieve users, buckets, bucket instances, OTP, roles, OIDC providers, accounts, groups, and pubsub topics using the service graph.

## Dependencies and Integration Points
It depends on all RADOS service headers, metadata modules for accounts/groups/OIDC/roles/topics, `RGWRados`, `RGWBucketCtl`, `RGWUserCtl`, and the sync module service. Sync modules can override bucket and bucket-instance metadata handlers, which lets alternative sync modules alter metadata behavior without replacing the whole control graph.

## Risks
- Startup ordering is fragile because many services depend on previously initialized but not necessarily started services.
- `shutdown()` assumes many pointers are initialized once `can_shutdown` is set; partial init failures after that point require safe null/non-null behavior.
- `start_state` stays `StateStarting` if `do_start()` fails, so retries on the same instance return without re-running only if state is not reset elsewhere.
- Raw mode skips service starts; callers must not use skipped high-level services in raw contexts.
- Metadata handler attach errors are reported but already-attached handlers remain attached until teardown.

## Test Signals
Signals include RGW daemon startup/shutdown tests, raw store initialization tests, cache/no-cache configurations, sync module registration/configuration tests, metadata admin tests for every attached handler, and fault-injection tests where one service start or handler attach fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_service.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_service.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_service.h

## Purpose
This header defines the service container and control facade for the RGW RADOS driver. It separates owning service definitions from public non-owning service pointers and declares the metadata control structures used by RGW admin and metadata operations.

## Important APIs, Types, and Functions
- `RGWServiceInstance` is the base service class with `start()`, `do_start()`, `shutdown()`, and a start-state enum.
- `RGWServices_Def` owns concrete service objects using `std::unique_ptr` and declares `init()` and `shutdown()`.
- `RGWServices` exposes non-owning pointers to initialized services and has `init()` for normal mode and `init_raw()` for raw storage mode.
- `RGWCtlDef` owns metadata manager, metadata handlers, topic cache, user control, and bucket control.
- `RGWCtl` exposes non-owning pointers to initialized controls and attaches handlers to the metadata manager.

## Control Flow
Users of the header initialize `RGWServices`, which delegates to `RGWServices_Def` and then publishes service pointers. Control initialization uses `RGWCtlDef` to allocate handlers and then maps selected pointers into `RGWCtl`. `RGWServiceInstance::start()` acts as a common idempotent wrapper around each service's implementation-specific startup.

## State and Persistence Behavior
The header itself stores in-memory ownership and lifecycle state. Persistent behavior is delegated to service implementations and metadata handlers, but the type layout determines which persistent subsystems are available: bucket index, bilog, datalog, mdlog, config keys, sys objects, user records, quotas, sync modules, and topic metadata. `can_shutdown` and `has_shutdown` prevent premature or repeated shutdown.

## Dependencies and Integration Points
It forward-declares most concrete service classes to avoid including all service headers. It integrates with `CephContext`, `optional_yield`, `DoutPrefixProvider`, `rgw::SiteConfig`, `rgw::sal::RadosStore`, `rgw::sal::ConfigStore`, librados, metadata handlers, and chained caches.

## Risks
- Public raw pointers are valid only as long as the owning `_svc` or `_ctl` objects live.
- Callers can distinguish raw and normal initialization only by using different entry points; misuse can leave required pointers unset or services unstarted.
- The base `start()` method's circular-reference accommodation is useful but can hide reentrant startup errors.

## Test Signals
Compile-time coverage should catch service pointer type mismatches. Runtime tests should cover service lifecycle idempotency, raw initialization, normal initialization with and without cache, and metadata handler availability after `RGWCtl::init()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_service.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync.cc

## Purpose
This file implements RGW metadata sync for RADOS-backed multisite deployments. It fetches metadata log state from the master zone, initializes local sync status, builds full-sync maps, replays metadata changes into local metadata handlers, advances shard markers, coordinates leases and fairness bids, logs sync errors, and serializes sync status to RADOS.

## Important APIs, Types, and Functions
- Static status object names: `mdlog.sync-status`, `mdlog.sync-status.shard.<id>`, `meta.full-sync.index.<id>`, and fairness bid object `meta-sync-bids`.
- `RGWSyncErrorLogger` writes sharded timelog entries under `sync.error-log.<shard>`.
- `RGWSyncBackoff` and `RGWBackoffControlCR` implement exponential retry around failing coroutines.
- JSON decoders for `rgw_mdlog_info`, `rgw_mdlog_entry`, and `rgw_mdlog_shard_data` parse remote admin REST responses.
- `RGWShardCollectCR` is a bounded-concurrency fanout collector used for shard reads/lists.
- `RGWRemoteMetaLog` owns the remote master REST connection, HTTP manager, error logger, sync trace node, and top-level sync coroutine.
- `RGWMetaSyncStatusManager` opens the log pool, initializes `RGWRemoteMetaLog`, and exposes read/init/run/wakeup operations.
- `RGWInitSyncStatusCoroutine` writes initial `rgw_meta_sync_info`, reads remote shard positions, writes per-shard markers, then moves to `StateBuildingFullSyncMaps`.
- `RGWFetchAllMetaCR` performs full metadata listing by section, writes sharded omap full-sync indexes, and records total entries in shard markers.
- `RGWMetaSyncSingleEntryCR` fetches one remote metadata entry and stores or removes it locally.
- `RGWMetaSyncShardCR` performs full or incremental shard sync under a RADOS lease and fairness bid.
- `RGWMetaSyncCR` coordinates all shard controllers across period-history boundaries.
- `RGWCloneMetaLogCoroutine` copies remote mdlog entries into the local mdlog shard before local replay.

## Control Flow
`RGWRemoteMetaLog::run_sync()` is the top-level loop for non-master zones. It fetches remote mdlog info, reads local sync status, initializes status if absent or stale, verifies shard count, starts a RADOS-backed bid manager, then dispatches by sync state. In `StateBuildingFullSyncMaps`, `RGWFetchAllMetaCR` lists remote metadata sections through `/admin/metadata`, prioritizes user, bucket.instance, bucket, roles, and topic, and writes sharded full-sync indexes. After this it stores `StateSync`. In `StateSync`, `RGWMetaSyncCR` finds the local period cursor, spawns one `RGWMetaSyncShardControlCR` per shard, and advances to later periods when shard controllers finish.

Each shard controller wraps `RGWMetaSyncShardCR` in retry/backoff. Full sync reads keys from the full-sync omap index, spawns `RGWMetaSyncSingleEntryCR` workers, advances markers through `RGWMetaSyncShardMarkerTrack`, switches the marker to incremental state, and removes the full-sync index object. Incremental sync clones fresh remote mdlog entries into the local mdlog with `RGWCloneMetaLogCoroutine`, reads local mdlog entries, replays completed operations, skips pending operations while advancing markers, and waits at the tip based on `rgw_meta_sync_poll_interval`. Period markers stop replay at the boundary so the top-level coroutine can move to the next period.

## State and Persistence Behavior
Sync status is persisted in the zone log pool. The global info object stores state, shard count, period id, and realm epoch. Each shard marker object stores state, marker, next-step marker, total entries, current full-sync position, timestamp, and realm epoch. Full-sync indexes are temporary sharded omap objects. Metadata entries are written through `store->ctl()->meta.mgr->put(..., RGWMDLogSyncType::APPLY_ALWAYS, true)` and removed through `meta.mgr->remove()`. Remote mdlog entries are cloned into local mdlog shards with `store_entries_in_shard()`. RADOS cls locks protect status and shard marker objects. Fairness bids in the control pool prevent multiple workers from owning the same shard. Error details are persisted as cls timelog records.

## Dependencies and Integration Points
The implementation depends on `RGWRESTConn` and `/admin/log` plus `/admin/metadata` endpoints, `RGWHTTPManager`, coroutine infrastructure, async RADOS processor, metadata manager, mdlog service, cls service, sync trace manager, period history, RADOS lock/omap helpers, and `sync_fairness` bid manager. It is invoked through the RADOS services and surfaced by `RGWMetaSyncStatusManager`.

## Risks
- The sync state machine spans REST, local mdlog, metadata writes, RADOS locks, and fairness bids; partial failures rely on marker discipline for retry correctness.
- `RGWMetaSyncCR` contains an assertion that `next` exists after shard completion, so current-period behavior depends on shard controllers not returning as a terminal success at the live tip.
- Marker advancement is intentionally conservative; child failures set `can_adjust_marker=false`, which can cause duplicate replay but avoids skipping failed entries.
- Full-sync section ordering is hard-coded for metadata dependencies; new metadata sections with hidden dependencies may need ordering updates.
- REST retry behavior mainly special-cases endpoint internal errors; other transient HTTP failures can fail the coroutine and depend on outer backoff.
- Lease loss or bid loss returns busy-like errors; correctness depends on all writers respecting these guards.
- Error injection support can alter behavior under `rgw_sync_meta_inject_err_probability`, which should stay confined to testing.

## Test Signals
Strong signals include multisite metadata full sync tests, incremental mdlog replay tests, period transition tests, marker persistence/restart tests, lease-loss and competing-bid tests, remote REST failure retry tests, metadata deletion tests, pending mdlog operation handling, sync error log tests, and upgrade tests where local sync status lags the master's oldest mdlog period.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync.h

## Purpose
This header declares the metadata sync data structures and coroutine interfaces used by the RADOS driver. It defines remote mdlog response models, sync error logging, backoff helpers, sync environment wiring, remote metadata log management, status management, ordered marker tracking, and factory functions used by mdlog trimming.

## Important APIs, Types, and Functions
- `rgw_mdlog_info`, `rgw_mdlog_entry`, and `rgw_mdlog_shard_data` model remote metadata log info, entries, and list responses.
- `RGWSyncErrorLogger` creates sharded error log object names and returns coroutines for writing sync errors.
- `rgw_sync_error_info` is the encoded/dumped payload for sync error records.
- `RGWSyncBackoff` and `RGWBackoffControlCR` provide reusable retry behavior for sync coroutines.
- `RGWMetaSyncEnv` carries shared dependencies: store, REST connection, async RADOS processor, HTTP manager, error logger, sync tracer, and bid manager.
- `RGWRemoteMetaLog` owns remote mdlog access and top-level sync execution.
- `RGWMetaSyncStatusManager` exposes status initialization, status reads, master shard info reads, run, wakeup, stop, and logging-prefix behavior.
- `RGWOrderCallCR`, `RGWLastCallerWinsCR`, and `RGWSyncShardMarkerTrack<T,K>` coordinate ordered marker writes while multiple entries are processed concurrently.
- `RGWMetaSyncSingleEntryCR` replays one metadata entry.
- `RGWShardCollectCR` implements bounded concurrent shard fanout.
- Factory functions create remote mdlog shard info/list coroutines for users outside this implementation.

## Control Flow
The header reveals a layered sync design. `RGWMetaSyncStatusManager` delegates remote work to `RGWRemoteMetaLog`. `RGWRemoteMetaLog` initializes `RGWMetaSyncEnv`, reads remote log info, initializes local status, and runs the main sync loop. Shard workers process entries concurrently, while `RGWSyncShardMarkerTrack` only flushes high-water markers when earlier pending entries are complete. `RGWBackoffControlCR` repeatedly allocates child coroutines and optionally runs a finisher after success.

## State and Persistence Behavior
The declared objects track sync status, marker windows, retry sets, child coroutine pointers, shard object mappings, clone markers, and timestamp-to-shard state. Persistent state is represented by RADOS object names returned from `RGWMetaSyncEnv::status_oid()` and `shard_obj_name()`, error log shards, and marker writes implemented by subclasses. `RGWSyncShardMarkerTrack` maintains pending and finished marker maps to prevent marker persistence from skipping in-flight work.

## Dependencies and Integration Points
The header includes coroutine, HTTP client, metadata, meta sync status, SAL, RADOS SAL, sync trace, mdlog, and sync fairness headers. It forward-declares the REST connection, async RADOS processor, status manager, sync coroutine, and trace manager. It integrates with mdlog trimming through the remote mdlog factory functions.

## Risks
- Template marker tracking assumes markers are strictly orderable and that the lowest pending marker determines the safe high-water mark.
- `RGWBackoffControlCR` stores a raw child coroutine pointer protected by a mutex; allocation, cancellation, and destructor paths need careful ownership handling.
- `RGWMetaSyncEnv` is a raw-pointer dependency bag; all pointed services must outlive active coroutines.
- Wakeups target shard coroutines that may complete concurrently, so the implementation must synchronize map access correctly.

## Test Signals
Compile tests should cover factory function declarations and template use. Runtime signals include marker-order tests under concurrent entry replay, backoff reset behavior, sync error logging, status read/init APIs, and wakeup behavior for specific shards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_counters.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_counters.cc

## Purpose
This file builds and registers performance counters used by RGW sync and sync delta reporting.

## Important APIs, Types, and Functions
- `sync_counters::build()` creates a `PerfCountersBuilder`, marks counters useful for ceph-mgr, adds fetch, poll, and lock counters, registers them in the context collection, and returns a `PerfCountersRef`.
- `sync_deltas::add_rgw_sync_delta_counters()` adds the `sync_delta` time counter.
- `sync_deltas::SyncDeltaCountersManager` creates, registers, updates, and unregisters sync delta counters.

## Control Flow
Callers request a counter set by name. The builder defines counter ids and labels, creates the underlying `PerfCounters`, then registers it with `CephContext`'s perf counter collection. The delta manager validates the perf counter key name, constructs a counter set, and exposes `tset()` for updates.

## State and Persistence Behavior
Counters are process-local telemetry registered in memory with Ceph's perf counter collection. They are not persisted as RADOS objects, but ceph-mgr can scrape/report them. The delta manager removes its counter set on destruction.

## Dependencies and Integration Points
The file depends on `CephContext`, `PerfCountersBuilder`, `PerfCountersCollection`, perf counter key helpers, and the ids from `rgw_sync_counters.h`. It integrates with ceph-mgr through useful-priority perf counters.

## Risks
- Counter id ranges must remain unique and consistent with the header.
- `SyncDeltaCountersManager` asserts that the provided name has the expected key, so callers using a nonconforming name will abort.
- Lifetime matters: counters must be removed before the owning context/collection disappears.

## Test Signals
Signals include unit or daemon tests that instantiate the counter builders, verify counter names and types, update `sync_delta`, and confirm registration/removal behavior during service shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_counters.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_counters.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_counters.h

## Purpose
This header declares perf counter id ranges and the sync delta counter manager for RGW sync telemetry.

## Important APIs, Types, and Functions
- `sync_counters` enum reserves ids beginning at `805000` for fetch bytes, not-modified counts, fetch errors, poll latency/errors, and lock latency.
- `sync_counters::build()` returns a registered `PerfCountersRef`.
- `rgw_sync_delta_counters_key` names the delta counter set as `rgw_sync_delta`.
- `sync_deltas` enum reserves ids beginning at `806000` for datalog sync delta.
- `SyncDeltaCountersManager` owns a `PerfCounters` object and exposes `tset()`.

## Control Flow
The header is consumed by sync components that need to publish counters. Construction is delegated to the `.cc` implementation, while callers use enum ids when updating metrics.

## State and Persistence Behavior
State is in-memory perf counter state. The manager owns the counter object and removes it from the collection in its destructor.

## Dependencies and Integration Points
It depends on Ceph perf counter collection types and `CephContext` through declarations. It integrates with ceph-mgr-visible daemon telemetry.

## Risks
- Changing enum values can break metric continuity or collide with other counter ranges.
- Callers must use ids from the correct namespace with the correct counter object.

## Test Signals
Build coverage for enum use, perf dump checks for expected counter names, and lifecycle checks for manager construction/destruction are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_counters.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_error_repo.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_error_repo.cc

## Purpose
This file implements a RADOS omap-backed repository for bucket shard sync error timestamps. It provides binary key encoding/decoding, timestamp value decoding, compare-and-set writes, compare-and-remove deletes, and coroutine wrappers for asynchronous RADOS operations.

## Important APIs, Types, and Functions
- `binary_key_prefix` is `0x80`, chosen because it cannot start valid UTF-8 and can distinguish binary keys from legacy string keys.
- Internal `key_type` encodes `rgw_bucket_shard` plus optional generation.
- `encode_key()` serializes the prefix and `key_type` into a string.
- `decode_key()` validates the prefix, decodes the key, rejects trailing bytes, and returns `-EINVAL` or `-EIO` for invalid encodings.
- `decode_value()` decodes an omap value as a `uint64_t` duration from epoch into `ceph::real_time`, treating decode errors as zero.
- `write()` uses `cls::cmpomap::cmp_set_vals()` in U64 greater-than mode so newer timestamps overwrite older or missing values.
- `remove()` uses `cmp_rm_keys()` in U64 greater-than-or-equal mode so removal only succeeds when the caller's timestamp is at least as new as the stored one.
- `RGWErrorRepoWriteCR` and `RGWErrorRepoRemoveCR` wrap these operations as `RGWSimpleCoroutine`s.

## Control Flow
Synchronous helpers build an object write operation but do not submit it. Coroutine wrappers call the helper, resolve the `rgw_raw_obj` to a RADOS reference, submit `aio_operate()`, and complete with the librados return value. `write_cr()` and `remove_cr()` allocate the corresponding coroutine.

## State and Persistence Behavior
The repository stores one omap key per encoded bucket shard/generation and stores the timestamp as a U64 buffer. Compare operations make updates monotonic by timestamp: older writers cannot overwrite newer errors, and stale removers cannot erase newer error reports. This is important when sync workers race or retry out of order.

## Dependencies and Integration Points
It depends on buffer encoding, `rgw_bucket_shard`, `rgw_raw_obj`, SAL RADOS reference lookup, coroutine infrastructure, librados object operations, and `cls/cmpomap/client.h`. Consumers can compose the synchronous `write()`/`remove()` with other object operations or use the coroutine wrappers.

## Risks
- `decode_value()` converts decode errors to zero, which is tolerant for empty values but can hide corrupt omap values.
- Key compatibility depends on the binary prefix remaining distinct from old string keys.
- Timestamp comparisons use raw `time_since_epoch().count()`; all writers must use the same clock representation.
- The coroutine constructors cast `rados->cct()` to `CephContext*`, so valid librados context lifetime is required.

## Test Signals
Tests should cover encode/decode round trips, invalid prefix, truncated and trailing-byte decode failures, monotonic write behavior, stale remove rejection, newer remove success, and coroutine operation against a test RADOS object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_error_repo.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_error_repo.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_error_repo.h

## Purpose
This header declares the public API for the sync error repository. The repository stores timestamped error state for bucket shards in RADOS omap and exposes both object-operation helpers and coroutine helpers.

## Important APIs, Types, and Functions
- `encode_key(const rgw_bucket_shard&, optional<uint64_t>)` returns a binary string key for a bucket shard and optional generation.
- `decode_key()` reverses the key encoding and reports invalid binary format errors.
- `decode_value()` converts a stored buffer into `ceph::real_time`.
- `write(ObjectWriteOperation&, key, timestamp)` adds a conditional set to an existing write operation.
- `write_cr()` allocates a coroutine to submit a conditional write to a raw RADOS object.
- `remove(ObjectWriteOperation&, key, timestamp)` adds a conditional remove to an existing write operation.
- `remove_cr()` allocates a coroutine to submit a conditional remove.

## Control Flow
Callers either build a larger librados write operation using `write()`/`remove()` or ask for a standalone coroutine with `write_cr()`/`remove_cr()`. The compare semantics are implemented in the `.cc` file using cls cmpomap.

## State and Persistence Behavior
The header defines timestamp semantics: writes are intended to record a key only if the provided timestamp is newer, and removes are intended to erase only if no newer timestamp has appeared. The optional generation in the key lets state distinguish different incarnations of the same bucket shard.

## Dependencies and Integration Points
It depends on librados forward declarations, Ceph buffers/time, coroutine declarations, and RGW raw object/bucket shard types. It is suitable for sync code that needs durable, race-aware error bookkeeping.

## Risks
- Callers must use the same key encoding for write and remove; legacy string keys require separate compatibility handling by readers.
- The conditional semantics depend on cls cmpomap availability on the target cluster.
- The API does not list/read repository entries; callers need separate omap listing code.

## Test Signals
Header-level API use should be validated by unit tests around write/remove operation composition and integration tests that race write/remove timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_error_repo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module.cc

## Purpose
This file implements default sync module extension hooks, a coroutine for statting remote objects and invoking optional callbacks, and registration of built-in sync modules.

## Important APIs, Types, and Functions
- `RGWSyncModuleInstance::alloc_bucket_meta_handler()` returns the default bucket metadata handler.
- `RGWSyncModuleInstance::alloc_bucket_instance_meta_handler()` returns the default bucket-instance metadata handler.
- `RGWStatRemoteObjCBCR` captures stat results for callback subclasses.
- `RGWCallStatRemoteObjCR::operate()` stats a remote object through `RGWStatRemoteObjCR`, logs results, and optionally calls a callback allocated by `allocate_callback()`.
- `rgw_register_sync_modules()` registers built-in modules: `rgw` as default, `archive`, `log`, `elasticsearch`, and `cloud`.

## Control Flow
Sync module instances default to standard metadata handlers unless a module overrides them. Remote stat flow runs as a coroutine: call a lower-level remote stat coroutine, return on error, log successful metadata, allocate a callback, pass stat result state into it, and call it. Registration constructs shared module objects and registers each name with the manager.

## State and Persistence Behavior
The file does not persist state directly. Metadata handler allocation determines which handlers will persist bucket metadata. Remote object stat results are held in coroutine fields and optionally passed to callbacks. Module registration stores shared module instances in the manager map.

## Dependencies and Integration Points
It depends on RGW coroutine infrastructure, RADOS coroutine helpers, data sync context/environment, bucket metadata handlers, and built-in sync module headers for log, Elasticsearch, AWS/cloud, archive/default behavior. It integrates with `RGWSI_SyncModules` and service/control initialization.

## Risks
- Built-in module names are configuration-facing; changing them can break deployments.
- `RGWCallStatRemoteObjCR` silently skips callback behavior when `allocate_callback()` returns null, which is intended but easy to miss.
- Callback coroutines receive moved attrs/headers, so later code must not assume local copies remain populated.

## Test Signals
Signals include sync module registration tests, default module lookup by empty name and `rgw`, custom module metadata handler override tests, and remote stat callback tests for success and error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module.h

## Purpose
This header defines the extension interfaces for RGW sync modules. Modules can provide data-sync behavior, REST filters, metadata handler overrides, write support flags, data export support, and custom object stat callback flows.

## Important APIs, Types, and Functions
- `RGWDataSyncModule` is the data-plane interface with optional `init()`, `init_sync()`, `start_sync()`, and required `sync_object()`, `remove_object()`, and `create_delete_marker()`.
- `RGWSyncModuleInstance` represents a configured module instance. It exposes the data handler, REST filter, user-write support, metadata handler allocation, and `should_full_sync()`.
- `RGWSyncModule` is the module factory with write/export capability flags and `create_instance()`.
- `RGWSyncModulesManager` stores named module factories under a mutex, supports default module registration by empty name, lookup, data-export capability checks, instance creation, and listing names.
- `RGWStatRemoteObjCBCR` and `RGWCallStatRemoteObjCR` define a callback-capable remote object stat coroutine pattern.
- `rgw_register_sync_modules()` declares built-in module registration.

## Control Flow
Service initialization registers modules in a manager. Zone or sync configuration names a module, and the manager creates an instance from JSON configuration. Data sync calls the instance's data handler for object replication, deletion, and delete-marker creation. Metadata service/control initialization can ask the instance to allocate module-specific bucket metadata handlers. REST requests can be filtered by module-provided REST managers.

## State and Persistence Behavior
The manager keeps module factories in memory. Module instances may own configuration and persistent behavior indirectly through their data handlers and metadata handlers. `should_full_sync()` defaults to true, so modules opt out if incremental-only startup is safe for them.

## Dependencies and Integration Points
The header depends on librados forwards, RGW common types, coroutine support, bucket info, data sync context/environment, bucket sync pipes, REST managers, metadata handlers, bucket services, zone services, bucket index, bucket control, and datalog service. It is the contract used by default, archive, log, Elasticsearch, and cloud sync modules.

## Risks
- Required data-sync methods are pure virtual; incomplete module implementations fail at compile time but behavioral compatibility is module-specific.
- Manager methods lock around map access, but `get_registered_module_names()` is const and does not lock in the header, so concurrent registration/listing assumptions should be checked.
- Default module registration under empty string means empty config names have special behavior.
- Modules that return `supports_user_writes()` or `supports_writes()` incorrectly can expose unsupported write paths.

## Test Signals
Tests should cover registration/lookup, default module lookup, failed instance creation for missing names, module capability flags, metadata handler overrides, full-sync opt-out behavior, and data-sync coroutine behavior for object copy/delete/delete-marker flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sync_module.h -->
