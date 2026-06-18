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
