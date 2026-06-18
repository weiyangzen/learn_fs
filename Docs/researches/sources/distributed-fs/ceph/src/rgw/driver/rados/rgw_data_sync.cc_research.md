# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_data_sync.cc

## Purpose

`rgw_data_sync.cc` implements Ceph RGW multisite data synchronization for the RADOS-backed driver. It pulls remote datalog and bucket-index log state over RGW admin REST endpoints, persists local sync status in the zone log pool, coordinates leases and fairness bids across workers, and drives object-level replication through sync module hooks.

The file contains two related sync layers. The outer data-log layer tracks remote datalog shards and translates each datalog entry into a bucket-shard sync obligation. The inner bucket-pipe layer synchronizes one source bucket shard into one destination bucket according to bucket sync policy, including bucket full sync, bucket-index incremental sync, stopped/resync state, generation changes, object fetch/delete/delete-marker operations, retry/error repositories, and admin/status read helpers.

## Important APIs, Types, and Functions

- `RGWRemoteDataLog` is the top-level source-zone data sync runner. It initializes `RGWDataSyncEnv`/`RGWDataSyncCtx`, starts an HTTP manager, reads remote datalog information, runs `RGWDataSyncControlCR`, exposes status reads, accepts wakeups for notified shards, and owns the data-sync fairness bid manager during `run_sync()`.
- `RGWDataSyncStatusManager` initializes source-zone sync support, validates zone/sync-module capability, creates `RGWSyncErrorLogger`, reads remote datalog shard count, constructs datalog status object names, and exposes `read_shard_status()` via `RGWRemoteDataLog`.
- `RGWDataSyncCR`, `RGWDataSyncShardControlCR`, and `RGWDataSyncShardCR` are the main data-log state machine. They read/init global sync status, build full-sync maps, start module hooks, spawn per-datalog-shard control coroutines, acquire per-shard leases, and dispatch full or incremental shard work based on `rgw_data_sync_marker::state`.
- `RGWInitDataSyncStatusCoroutine` and `RGWRDL::DataSyncInitCR` create/initialize global data sync status under a continuous `sync_lock`, seed shard markers from remote datalog shard info, and transition from `StateInit` to `StateBuildingFullSyncMaps`.
- `RGWListBucketIndexesCR` builds sharded omap full-sync indexes named by `data.full-sync.index.<source_zone>.<shard>`, using remote bucket instance metadata and the local datalog shard selection logic.
- `RGWDataFullSyncShardCR` consumes a full-sync index shard and launches `RGWDataFullSyncSingleEntryCR` for buckets/generations/shards, then transitions the datalog shard marker to `IncrementalSync`.
- `RGWDataIncSyncShardCR` loops forever while leased and highest bidder. It handles async wakeup notifications, retries from `<status_oid>.retry`, remote datalog entries from `/admin/log?type=data`, marker advancement, and backoff while idle.
- `RGWDataSyncSingleEntryCR` serializes and deduplicates bucket-shard obligations through `rgw::bucket_sync::Cache`, runs `RGWRunBucketSourcesSyncCR`, logs permanent failures, writes/removes retry omap entries, and finishes datalog markers.
- `RGWRunBucketSourcesSyncCR`, `RGWGetBucketPeersCR`, `RGWSyncBucketCR`, and `RGWSyncBucketShardCR` discover applicable bucket sync pipes and run bucket sync for each source/destination pair.
- `RGWBucketPipeSyncStatusManager` is the admin-oriented bucket sync manager. It constructs source pipes, initializes bucket status, reads per-shard status, runs manual bucket sync, and builds status object names.
- `RGWBucketFullSyncCR` lists remote bucket objects through the remote bucket API and applies prefix policy rules while advancing `rgw_bucket_sync_status.full`.
- `RGWBucketShardIncrementalSyncCR` reads remote bucket-index logs, squashes redundant operations, filters canceled/incomplete/redundant/unhandled entries, serializes object/OLH conflicts, advances shard incremental markers, and handles generation rollover through `RGWBucketShardIsDoneCR`.
- `RGWDefaultDataSyncModule` and `RGWArchiveDataSyncModule` implement the default object operation hooks. The default module fetches/removes/creates delete markers normally; the archive module gives replicated objects new instances and suppresses ordinary deletes.
- `RGWObjFetchCR`, `RGWFetchObjFilter_Sync`, and `RGWUserPermHandler` implement policy-aware remote object fetches: matching sync pipe rules, optional tag reads, ACL translation, storage-class override, and user-mode permission checks.
- Status and serialization helpers include `rgw_read_remote_bilog_info()`, `rgw_read_bucket_full_sync_status()`, `rgw_read_bucket_inc_sync_status()`, `decode_json()`/`dump()` methods for datalog and bucket sync structures, and `generate_test_instances()` for encode/decode coverage.

## Control Flow

The data sync daemon path starts with `RGWRemoteDataLog::run_sync()`. It creates a RADOS bid manager under `data-sync-bids.<source_zone>`, installs it into the sync environment, and runs `RGWDataSyncControlCR`. `RGWDataSyncCR` starts a periodic bid notification coroutine, reads `datalog.sync-status.<source_zone>`, obtains the global initialization lease when needed, initializes data sync state, builds full-sync maps, invokes sync module init/start hooks, then spawns one `RGWDataSyncShardControlCR` per datalog shard.

Each datalog shard runner first verifies it is the highest bidder, takes a continuous lease on `datalog.sync-status.shard.<source_zone>.<shard>`, rereads its marker with object version tracking, and enters either full-sync or incremental-sync mode. Full sync reads local full-sync omap index entries for that datalog shard, maps each bucket instance/generation/shard to one or more bucket sync obligations, and advances the full-sync marker. When the full index is consumed and the lease/bid are still valid, the shard marker state changes to `IncrementalSync` and the temporary full-sync index object is removed.

Incremental datalog sync repeatedly drains three inputs: out-of-band wakeup notifications, retry entries from the shard retry omap, and remote datalog entries. Each valid bucket shard entry is parsed into `rgw_bucket_shard` plus optional generation and passed to `data_sync_single_entry()`. That function obtains cached bucket-shard state and creates `RGWDataSyncSingleEntryCR`, which deduplicates concurrent obligations, runs the bucket source sync path, logs failures, schedules retries, and finishes the datalog marker through `RGWDataSyncShardMarkerTrack`.

Bucket sync begins by discovering pipes through `RGWGetBucketPeersCR`, using bucket sync policies and hints from source and target buckets. `RGWSyncBucketCR` loads source/destination bucket instance info, creates or reads the bucket-wide full status object, acquires a bucket lease for init/full/stopped transitions, fetches remote bilog info, initializes per-shard incremental markers, optionally performs a bucket full sync, then releases the bucket lease and runs incremental sync on a single bucket shard.

Bucket full sync lists remote objects with versions enabled, revalidates prefix policy markers, launches `RGWBucketSyncSingleEntryCR<rgw_obj_key, rgw_obj_key>` for handled objects, flushes the full marker, and writes `BucketSyncState::Incremental` on success. Bucket incremental sync lists bilog entries for the active generation, stops on `SYNCSTOP`, ignores `RESYNC`/cancel/incomplete/redundant entries, squashes older operations on the same object instance, serializes OLH operations on the same object name, and launches `RGWBucketSyncSingleEntryCR<string, rgw_obj_key>`. When a shard reaches the next log generation, `RGWBucketShardIsDoneCR` marks the shard done and advances the bucket generation once all shards complete.

Object operation coroutines route `ADD`/`LINK_OLH` to `sync_object()`, `DEL`/`UNLINK_INSTANCE` to `remove_object()`, and `LINK_OLH_DM` to `create_delete_marker()`. The default fetch path may read source object attributes to resolve tag-dependent pipe rules, validates user-mode permissions, applies ACL translation/storage-class options, and fetches the remote object with zone trace propagation. Precondition and permission failures are treated as skips rather than fatal object sync errors.

## State and Persistence Behavior

- Global data sync info is stored in `datalog.sync-status.<source_zone>` as `rgw_data_sync_info`, with states such as init, building full-sync maps, and sync.
- Per-datalog-shard markers are stored in `datalog.sync-status.shard.<source_zone>.<shard>` as `rgw_data_sync_marker`; marker fields track state, current marker, next-step marker, position, timestamp, and total full-sync entries.
- Full-sync bucket instance indexes are sharded omap objects named `data.full-sync.index.<source_zone>.<shard>`. They are built from remote bucket instance metadata and removed when full sync finishes for a datalog shard.
- Retry/error repositories use omap keys in `<datalog shard status oid>.retry`. Values encode timestamps; keys encode bucket shard plus optional generation, with compatibility handling for older unencoded string keys.
- Bucket-wide status objects are named `bucket.full-sync-status.<source_zone>:<dest_bucket>[:<source_bucket>]` and store `rgw_bucket_sync_status` with full marker, `BucketSyncState`, incremental generation, and per-shard completion bits.
- Per-bucket-shard incremental status objects are named `bucket.sync-status.<source_zone>:<dest/source shard>[:generation]` and store attributes with the `user.rgw.bucket-sync.` prefix for state and incremental marker. Legacy attr names without the prefix are decoded as fallback.
- Continuous leases protect global init, datalog shard ownership, and bucket init/full/stopped transitions. RADOS object version trackers (`RGWObjVersionTracker`) guard writes against races, and several code paths reread status after acquiring leases.
- Marker trackers (`RGWDataSyncShardMarkerTrack`, `RGWBucketFullSyncMarkerTrack`, `RGWBucketIncSyncShardMarkerTrack`) batch/order marker persistence and use last-caller-wins ordering to tolerate concurrent child completion.

## Dependencies and Integration Points

The file depends heavily on RGW coroutine infrastructure (`RGWCoroutine`, `RGWShardCollectCR`, `RGWBackoffControlCR`, `RGWSimpleCoroutine`), RADOS coroutine wrappers (`RGWSimpleRadosReadCR`, `RGWSimpleRadosWriteCR`, omap get/append/remove coroutines), REST wrappers (`RGWRESTReadResource`, `RGWReadRESTResourceCR`), and continuous lease/bid fairness helpers.

External integration surfaces include remote RGW admin APIs under `/admin/log`, remote bucket listing APIs, metadata sync for missing bucket instances, bucket sync policy handlers, bucket sync hints, datalog/bilog services, sync modules from `services/svc_sync_modules`, sync counters/perf guards, sync trace nodes, error logging for `radosgw-admin sync error list`, and SAL/RADOS store services.

Sync module integration is explicit through `RGWSyncModuleInstance::get_data_handler()`. Default and archive modules are implemented here, but data sync lifecycle calls (`init`, `init_sync`, `start_sync`) and object operation hooks make this file a framework for tier-specific behavior as well.

## Risks and Edge Cases

- Lease loss and bid loss are common control outcomes. Most long loops check both and return `-ECANCELED` or `-EBUSY`, so callers must preserve markers and retry without duplicating committed work.
- Marker advancement is subtle because child object syncs run concurrently. Duplicate markers, high-marker updates for skipped entries, OLH serialization, generation rollover, and flush-on-abort paths are high-risk areas.
- Error-repo handling can create persistent retry loops if generation information is stale, remote bucket info disappears, or old key formats are misdecoded. Some errors are intentionally ignored or converted to success to avoid wedging sync.
- Policy-dependent object routing can race with object rewrites or sync policy changes. `RGWFetchObjFilter_Sync` detects changed destination parameters and forces bounded retries, but repeated races fall back to `-EIO`.
- Bucket full sync prefix handling rewrites list markers to the next configured prefix. Incorrect prefix rules or marker revalidation could skip objects or loop unexpectedly.
- Bucket generation changes are guarded by `shards_done_with_gen`, but future-generation datalog entries may force previous-generation retries into the error repo. This is a correctness-sensitive workaround for missing datalog entries.
- Compatibility paths decode legacy bucket sync attrs, generation-zero status, and old retry keys. Removing or changing these paths risks breaking upgrades from older RGW deployments.
- The archive module intentionally changes object instance behavior and suppresses ordinary deletes; default-module assumptions should not be applied to archive zones.

## Test Signals

- Unit/encoding signals come from `generate_test_instances()` and the JSON/dump/decode helpers for data sync and bucket sync status types.
- Multisite integration tests should exercise global init, full-sync map construction, datalog shard transition to incremental sync, incremental datalog polling, wakeup notification handling, retry omap replay, and status reads.
- Bucket sync tests should cover policy-based source/target pipe discovery, missing local bucket metadata triggering metadata sync, bucket full sync, incremental bilog sync, generation rollover, stopped/resync transitions, manual `bucket sync run`, and status initialization/readback.
- Object-level tests should cover add/delete/delete-marker operations, versioned epochs, null version ids, OLH link/unlink serialization, tag-dependent rules, ACL translation, storage-class overrides, user-mode permission denies, redundant zone trace filtering, and archive sync semantics.
- Fault-injection knobs already referenced in the file (`rgw_sync_data_full_inject_err_probability`, `rgw_sync_data_inject_err_probability`, `rgw_inject_delay_sec`, `delay_bucket_full_sync_loop`) are useful for validating retry, lease-loss, and marker flush behavior.
- Operational test signals include `radosgw-admin sync error list`, sync status/datalog shard status commands, sync trace activity flags, sync counters for poll/poll errors and datalog delta, and observed cleanup of full-sync index and per-generation shard status objects.
