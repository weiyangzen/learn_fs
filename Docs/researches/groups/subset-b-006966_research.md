# subset-b-006966 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_bucket.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_bucket.cc

## Purpose
`rgw_bucket.cc` implements the RADOS-backed RGW bucket administration and bucket metadata control plane. It backs radosgw-admin bucket commands, metadata sync handlers for `bucket` and `bucket.instance`, owner bucket-directory maintenance, bucket index repair utilities, lifecycle/pubsub side effects, stale reshard instance cleanup, and archive-zone bucket metadata behavior.

## Important APIs, Types, and Functions
The admin path centers on `RGWBucket::init()`, `RGWBucket::check_index()`, `check_object_index()`, `check_index_olh()`, `check_index_unlinked()`, `check_bad_index_multipart()`, `chown()`, `set_quota()`, `sync()`, `remove_object()`, and `get_policy()`. Static `RGWBucketAdminOp` wrappers expose these to callers such as `radosgw-admin`, including `info()`, `remove_bucket()`, `link()`, `unlink()`, `limit_check()`, `list_stale_instances()`, `clear_stale_instances()`, `fix_lc_shards()`, and `fix_obj_expiry()`.

The metadata path defines `RGWBucketMetadataHandler` for bucket entrypoints, `RGWBucketInstanceMetadataHandler` for full bucket instance records, and archive variants that rename deleted buckets instead of physically removing metadata. `RGWBucketCtl` wraps service-layer bucket metadata operations and owner-directory updates. Helper functions include `rgw_bucket_object_check_filter()`, `rgw_remove_object()`, `rgw_find_bucket_by_id()`, `init_default_bucket_layout()`, `update_bucket_topic_mappings()`, and `check_bad_owner_bucket_mapping()`.

## Control Flow
Admin operations generally build an `RGWBucket` wrapper, call `init()` to load a bucket through `rgw::sal::Driver::load_bucket()`, optionally load the user, copy the loaded bucket into `RGWBucketAdminOpState`, then perform the requested mutation or report. Bucket names can carry an inline tenant prefix, and `init()` splits it before loading the bucket.

Index checking has several flows. `RGWBucketAdminOp::check_index()` emits a formatter object, optionally scans damaged multipart index entries, optionally lists real objects with `force_check_filter`, then compares and optionally rebuilds index stats through SAL `Bucket::check_index()` and `Bucket::rebuild_index()`. The multipart repair path scans the multipart namespace per shard, tracks part entries until a `.meta` entry appears, and optionally removes orphaned part index entries. The OLH repair path scans `BIIndexType::OLH` entries, clears pending-removal OLHs or applies pending logs. The unlinked-version repair path scans versioned instance entries, verifies they are not listable through cls bucket listing, applies a minimum-age guard, and optionally deletes the unlinked object version.

Several repair paths spawn Boost.Asio coroutines over bucket-index shards with a shared `next_shard` counter and then run `io_context::run()` synchronously. This gives shard-level concurrency for radosgw-admin while still blocking the caller. Formatter output is periodically flushed to bound buffered JSON size when dumping keys.

Metadata sync handlers follow a read/prepare/write/post pattern. `RGWBucketMetadataHandler::put()` reads the old entrypoint, stores the new entrypoint, unlinks the old owner if ownership changed or the entry became unlinked, and links the new owner if needed. `RGWBucketInstanceMetadataHandler::put()` reads any old instance, calls `put_prepare()` to preserve local layout for remote-zone writes and select placement for new buckets, stores the instance, then `put_post()` initializes the index and updates lifecycle and pubsub mappings.

## State and Persistence Behavior
Persistent bucket state is split between bucket entrypoint metadata and bucket instance metadata. Entrypoints carry bucket key, owner, creation time, linked state, and legacy embedded bucket info. Bucket instances carry `RGWBucketInfo`, layout, object version tracker state, attrs, owner, quota, sync flags, placement, lifecycle, and pubsub notification attributes. `RGWBucketCtl` converts legacy entrypoint-embedded bucket info into separate instance metadata through `convert_old_bucket_info()`.

Owner bucket lists are persisted in owner-specific bucket directory objects. `get_owner_buckets_obj()` selects either user buckets objects or account buckets objects, and `link_bucket()`/`unlink_bucket()` update those directory objects through `rgwrados::buckets::add/remove` plus optional entrypoint updates. `sync_owner_stats()` reads bucket index stats and writes them back to the owner directory.

Bucket instance writes can initialize bucket index shards, create deleted-log layouts for multisite cleanup, preserve local placement/layout on remote metadata replay, force versioning on archive zones, update lifecycle shard config, and add/remove bucket-topic mappings based on `RGW_ATTR_BUCKET_NOTIFICATION`. Bucket removal in archive metadata handlers renames metadata to an `-deleted-<md5>` bucket name, records original bucket metadata in `zone.archive.info`, links the renamed bucket, then removes the old entrypoint and instance.

## Dependencies and Integration Points
This file depends on SAL (`rgw_sal.h`, `rgw_sal_rados.h`), RGWRados bucket index operations, `RGWSI_Bucket`, `RGWSI_BucketIndex`, `RGWSI_Zone`, `RGWSI_User`, `RGWSI_Bucket_Sync`, `RGWDataChangesLog`, metadata listers, lifecycle services, pubsub, reshard locks, cls rgw bucket operations, and formatter/flusher output. It integrates directly with radosgw-admin command dispatch, metadata sync modules through `create_bucket_metadata_handler()` and `create_bucket_instance_metadata_handler()`, data sync filtering through `RGWBucketCtl::bucket_exports_data()`, owner/account bucket listings, lifecycle shard repair, and bucket deletion forwarding to the master zonegroup.

## Risks
Important risks are concurrency and partial-update behavior. Owner relink operations update bucket instance metadata, owner directory entries, ACL owner fields, and possibly old entrypoint/instance cleanup; failures midway can leave mismatched owner mappings. Index repair paths mutate bucket index/object state based on namespace scans and age heuristics, so filters, marker progression, and versioned-object assumptions are critical. The shard coroutine counters and aggregate counts are shared without explicit locking because execution is on the Asio context, and future asynchronous changes would need care. Archive-zone rename-on-delete relies on generated names and old metadata attrs and must remain idempotent under metadata replay.

## Test Signals
Useful tests should exercise radosgw-admin bucket info/list/stats, ACL policy fetch, quota/sync flag writes, link/unlink/chown across user and account owners, stale instance listing and clearing around reshard states, bucket check with multipart damage, OLH pending removal, unlinked versioned entries with `min_age`, object-expiry repair, and archive-zone deletion replay. Multisite tests should verify remote metadata replay preserves local layout, initializes indexes, writes deleted-log datalog entries, maintains lifecycle configs, updates bucket-topic mappings, and emits correct errors on non-RADOS drivers where RADOS-only commands are requested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_bucket.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_bucket.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_bucket.h

## Purpose
`rgw_bucket.h` declares the RADOS RGW bucket control/admin interface. It describes bucket metadata objects, user bucket lists, admin operation state, admin operation entry points, and `RGWBucketCtl`, the service-facing controller that reads/writes bucket entrypoint and instance metadata and keeps owner bucket directories and sync policy queries consistent.

## Important APIs, Types, and Functions
`RGWBucketCompleteInfo` packages `RGWBucketInfo` with raw metadata attrs for full bucket-instance metadata sync. `RGWBucketEntryMetadataObject` and `RGWBucketInstanceMetadataObject` adapt bucket entrypoint and instance state to `RGWMetadataObject`. `RGWUserBuckets` is an encodable map of bucket name to `RGWBucketEnt` with `owns()`, `add()`, `remove()`, and `count()`.

`RGWBucketAdminOpState` is the mutable parameter block for admin operations. It stores user/account identity, display name, bucket/object names, markers, flags for stats/index/delete/sync/dump behavior, concurrency and age thresholds, bucket pointer, quota, and rate-limit info. `RGWBucket` is the instance wrapper used by admin code, with methods for initialization, bucket index checks, ownership changes, quota updates, object removal, policy lookup, and sync toggling. `RGWBucketAdminOp` exposes static command-level APIs over a `rgw::sal::Driver`.

`RGWBucketCtl` declares entrypoint and instance `GetParams`, `PutParams`, and `RemoveParams`, plus operations for reading/storing/removing entrypoints and instances, resolving bucket info through entrypoint if needed, setting attrs, linking/unlinking buckets to owners, reading stats, syncing owner stats, and obtaining bucket sync policy handlers.

## Control Flow
Callers configure `RGWBucketAdminOpState`, then invoke `RGWBucketAdminOp` statics. Those statics construct `RGWBucket`, call `init()`, and delegate to instance methods or SAL calls. Lower-level services use `RGWBucketCtl` directly: callers pass a `rgw_bucket`, optional version/mtime/attrs/cache parameters, and the controller converts that into service metadata keys with `RGWSI_Bucket::get_entrypoint_meta_key()` or `get_bi_meta_key()`.

The controller separates three concepts: entrypoint metadata for name-to-instance resolution, bucket instance metadata for the authoritative bucket record, and owner bucket directory membership. This split is visible in APIs such as `read_bucket_info()`, where a bucket without `bucket_id` first reads the entrypoint before loading the instance.

## State and Persistence Behavior
The header makes object-version tracking explicit. Entrypoint and instance get/put/remove params can carry `RGWObjVersionTracker`, `mtime`, attrs, cache refresh versions, and exclusivity flags. Instance `PutParams::orig_info` distinguishes three states: original not fetched, original absent/new bucket, or original info available. That matters to overwrite hooks, metadata sync, and index/log side effects in the implementation.

`RGWBucketAdminOpState` owns an optional cloned SAL bucket once initialized, so subsequent operations can mutate or inspect a stable bucket object. `RGWBucketCtl::link_bucket()` and `unlink_bucket()` take a librados handle and an `rgw_owner` variant, making owner-directory persistence work for both users and accounts. `bucket_exports_data()` and `bucket_imports_data()` surface sync-policy persistence through `RGWBucketSyncPolicyHandler`.

## Dependencies and Integration Points
The declarations depend on RGW common bucket types, SAL driver/user/bucket/object abstractions, metadata handlers, formatter support, librados forward declarations, zone/bucket/user services, bucket sync services, and bucket index services. Factory functions create normal and archive metadata handlers for metadata sync. Global helpers `rgw_remove_object()`, `rgw_object_get_attr()`, `check_bad_owner_bucket_mapping()`, and `rgw_find_bucket_by_id()` are used by admin and repair code outside this translation unit.

## Risks
The API exposes many optional pointer parameters, so null handling and lifetime of out-params are important. `RGWBucketAdminOpState` mixes user, account, bucket, object, and operation flags; invalid combinations must be rejected by implementation. `RGWBucketCtl` methods are compiled under RADOS guards in the implementation, so callers must account for non-RADOS stores where some admin operations are unsupported. Version tracker propagation is subtle: passing the wrong tracker can cause stale-write failures or missed optimistic concurrency checks.

## Test Signals
Compile-time coverage should verify all declared admin methods match command dispatch and SAL/RADOS implementations. Behavioral tests should cover entrypoint-only bucket lookup, direct instance lookup, object version conflict paths, exclusive creates, owner link/unlink for users and accounts, legacy bucket conversion through `set_bucket_instance_attrs()`, sync policy imports/exports queries, and metadata-handler factories in normal and archive zones.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_bucket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_cr_rados.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_cr_rados.cc

## Purpose
`rgw_cr_rados.cc` implements coroutine and async request wrappers for RGW RADOS operations. It provides the worker-thread processor for blocking RADOS/SAL operations, direct librados AIO coroutines for raw objects, omap, locks, bucket instance metadata, bucket index log trimming, remote object fetch/stat/delete during sync, time-log operations, notifications, and remote bucket stat/list probes.

## Important APIs, Types, and Functions
`RGWAsyncRadosProcessor` owns a `ThreadPool`, throttled work queue, shutdown flag, and request deque. `RGWAsyncRadosRequest::send_request()` and `complete_immediate()` complete `RGWAioCompletionNotifier`s and preserve request reference counts. Implemented async requests include system object get/put/attrs, bucket instance get/put/remove, remote fetch/stat/remove object, and raw object stat.

Direct coroutine classes implement raw RADOS actions: `RGWSimpleRadosReadAttrsCR`, `RGWRadosSetOmapKeysCR`, `RGWRadosGetOmapKeysCR`, `RGWRadosGetOmapValsCR`, `RGWRadosRemoveOmapKeysCR`, `RGWRadosRemoveCR`, `RGWRadosRemoveOidCR`, `RGWSimpleRadosLockCR`, `RGWSimpleRadosUnlockCR`, `RGWRadosBILogTrimCR`, `RGWRadosTimelogAddCR`, `RGWRadosTimelogTrimCR`, `RGWSyncLogTrimCR`, `RGWRadosNotifyCR`, `RGWDataPostNotifyCR`, and `RGWStatRemoteBucketCR`. `RGWOmapAppend` batches string entries into omap keys.

## Control Flow
Thread-pool-backed requests are queued through `RGWAsyncRadosProcessor::queue()`. If shutdown has begun, the request is completed immediately with `-ECANCELED`; otherwise a throttle slot is acquired and the work queue processes the request by calling `req->send_request()`. The queue holds references while enqueued and releases them after processing. `stop()` drains the work queue, stops the thread pool, and drops queued references.

Most direct AIO coroutines follow the same pattern: resolve an `rgw_rados_ref` or `IoCtx`, build a `librados::ObjectReadOperation` or `ObjectWriteOperation`, create a stack completion notifier, issue `aio_operate()` or `aio_notify()`, then return the completion's return value in `request_complete()`. Versioned reads/writes call `RGWObjVersionTracker::prepare_op_for_read/write()` and some writes apply the write version on success.

Remote sync operations wrap higher-level RGWRados/SAL work in thread-pool requests. `RGWAsyncFetchRemoteObj::_send_request()` calls `fetch_remote_obj()`, tracks bytes transferred, emits object synced/replication notifications on successful changes, and updates sync perf counters. `RGWAsyncRemoveObj::_send_request()` loads object state atomically, optionally skips if the local object is newer, validates sync-pipe object parameters and user replicate-delete permission, decodes ACL/tag attrs, constructs a SAL delete operation with OLH/versioning/zones-trace parameters, and sends delete notifications on success.

`RGWContinuousLeaseCR::operate()` repeatedly locks a RADOS object with a generated cookie, updates optional latency counters, marks the caller awake after renewal, warns if renewal exceeded 90 percent of the interval, sleeps for half the interval, and unlocks when asked to go down. `RGWDataPostNotifyCR` posts data-log notification payloads to `/admin/log`, falling back from `notify2` to the older `notify` form on method-not-allowed.

## State and Persistence Behavior
The processor persists no cluster state itself but controls asynchronous execution and cancellation. Individual coroutines mutate RADOS raw objects, xattrs, omap keys, bucket instance metadata, bucket index logs, cls timelog records, object locks, remote-replicated objects, delete markers, and notification side effects. `RGWOmapAppend` buffers pending entries in memory until the window is full or shutdown, then writes them as empty omap values.

Remote object fetch/delete uses bucket/object metadata attrs, tags, ACLs, sync pipe rules, zone trace sets, and perf counters. Bucket instance get/put/remove delegates to RGWRados or `RGWBucketCtl`, so metadata object-version behavior is inherited from bucket control code. `RGWSyncLogTrimCR` treats `-ENODATA` as successful exhaustion and advances `last_trim_marker` when appropriate.

## Dependencies and Integration Points
This file integrates with `rgw_coroutine`, `RGWAioCompletionNotifier`, librados AIO, cls lock, cls rgw bucket index trim, cls timelog services, `RGWSI_SysObj`, `RGWBucketCtl`, `RGWRados::fetch_remote_obj()` and `stat_remote_obj()`, SAL bucket/object delete operations, pubsub notifications, sync counters, `RGWHTTPManager`, `RGWRESTConn`, and data-sync code that owns leases and calls fetch/remove/stat coroutines.

## Risks
Reference-count and notifier ownership are high-risk: requests can finish normally, be cleaned up by coroutine destructors, or be canceled during shutdown. Direct lock/unlock cleanup methods do not cancel outstanding AIO, so callers rely on coroutine lifecycle and completion handling. Remote delete can return permission/precondition failures based on sync-pipe filters and user permissions; tests need to distinguish real errors from intentional skips. `RGWStatRemoteBucketCR` logs a missing zone connection through an iterator that is invalid at `end()`, which is a code-review risk. Sync notifications happen after writes/deletes and can fail independently, so callers must not assume notification success from object operation success.

## Test Signals
Tests should cover processor enqueue/dequeue, shutdown cancellation, throttle release, direct AIO success/failure for read/write/remove/omap/xattrs/notify, version tracker application, omap append flush on window and finish, continuous lease renewal/unlock/abort/latency accounting, bilog and timelog trim marker behavior, remote fetch counters and notifications, remote delete permission and timestamp skip paths, and remote bucket stat fan-out/fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_cr_rados.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_cr_rados.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_cr_rados.h

## Purpose
`rgw_cr_rados.h` declares the coroutine-facing RADOS utility layer used by RGW metadata sync, data sync, log trimming, raw object operations, and remote bucket/object synchronization. It bridges RGW coroutine scheduling with either a dedicated async RADOS thread pool or librados asynchronous completions.

## Important APIs, Types, and Functions
`RGWAsyncRadosRequest` is the base ref-counted request with a virtual `_send_request()`, notifier completion, immediate cancellation, return status, and `finish()` cleanup. `RGWAsyncRadosProcessor` owns the queue and exposes `start()`, `stop()`, `queue()`, and `handle_request()`.

Template wrappers `RGWSimpleWriteOnlyAsyncCR<P>`, `RGWSimpleAsyncCR<P,R>`, and `RGWGenericAsyncCR` adapt arbitrary processor-backed requests/actions into `RGWSimpleCoroutine`. Template `RGWSimpleRadosReadCR<T>` and `RGWSimpleRadosWriteCR<T>` encode/decode typed RADOS object payloads. Dedicated declarations cover system objects, attrs, omap get/set/remove, raw object remove, locks, omap append managers, bucket instance get/put/remove, bilog trim, remote object fetch/stat/remove, latency monitoring, continuous leases, timelog add/trim, sync-log trim, raw object stat, RADOS notify, data-post notification, and remote bucket stat.

The remote bucket JSON structures `rgw_bucket_entry_owner`, `bucket_list_entry`, and `bucket_unordered_list_result` decode peer bucket listing responses. `bucket_list_entry::get_modify_op()` maps decoded delete-marker/version state to cls rgw modify operations.

## Control Flow
Processor-backed coroutine wrappers allocate a request in `send_request()`, pass a stack completion notifier to it, queue it on `RGWAsyncRadosProcessor`, and read `req->get_ret_status()` in `request_complete()`. Destructors call `request_cleanup()`, which calls `finish()` if a request is still outstanding, preventing leaked notifier references.

Direct librados wrappers do not use the processor. They build object operations in `send_request()`, issue AIO, and harvest the completion in `request_complete()`. `RGWOmapAppend` is a consumer coroutine: producers call `append()`, the coroutine consumes entries, batches them up to `window_size`, writes with `RGWRadosSetOmapKeysCR`, and `finish()` marks shutdown and flushes pending entries. `RGWShardedOmapCRManager` creates one append coroutine per shard and routes entries by shard id.

`RGWContinuousLeaseCR` is a long-lived coroutine wrapper around repeated `RGWSimpleRadosLockCR` calls and a final unlock. Callers can query `is_locked()`, set lock state, request shutdown with `go_down()`, or stop early with `abort()`.

## State and Persistence Behavior
The header defines in-memory state required for async safety: request pointers, completion notifier intrusive pointers, raw object refs, IoCtx ownership, result shared pointers, attrs maps, pending omap entries, lock names/cookies, lease timestamps, latency averages, and sync trace data. Persistent effects are produced by the implementation: object bodies, xattrs, omap entries, bucket instance metadata, bilog/timelog records, object locks, fetched remote objects, delete markers, and notification posts.

Versioned operations can carry `RGWObjVersionTracker` pointers to embed read/write assertions. `RGWAsyncFetchRemoteObj` and `RGWAsyncRemoveObj` preserve sync context such as source zone, destination bucket info, optional placement rule, versioned epoch, source trace, zones trace, object filters, user id, owner display name, timestamp comparisons, and tag-preservation flags.

## Dependencies and Integration Points
The declarations depend on `rgw_coroutine.h`, SAL and RADOS SAL types, bucket sync types, `WorkQueue`, `Throttle`, Ceph time helpers, sysobj/bucket services, cls lock and rgw client operations through the implementation, `RGWRESTConn`, and HTTP manager integration. Data-sync code uses these classes extensively for lock leasing, remote fetch/stat/remove, bucket stat checks, and notification delivery. Metadata-log services use the generic and system-object wrappers.

## Risks
The main risks are ownership and asynchronous lifetime. Many wrappers store raw pointers to caller-owned result buffers, attrs, counters, buckets, and trace sets; callers must keep them alive until completion. Some constructors take references to mutable bucket info or sync-pipe state, so concurrent mutation would be unsafe. Template wrappers rely on specializations of `_send_request()` existing elsewhere. `LatencyMonitor` is explicitly not thread-safe and assumes all participating coroutines share one thread. Remote JSON decode tolerates missing/invalid date parsing by leaving default fields, which can affect follow-up modify-op decisions.

## Test Signals
Compile tests should instantiate the template wrappers used by metadata and data sync. Behavioral tests should cover cleanup of outstanding processor-backed requests, cancellation on processor shutdown, direct AIO result propagation, empty-on-ENOENT typed reads, attr filtering versus raw attrs, omap pagination flags, sharded omap finish semantics, lock cookie generation and renewal windows, lease `is_locked()` expiry, sync-log trim marker advancement, remote bucket JSON decode including null version IDs, and remote object fetch/remove option propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_cr_rados.h -->
