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
