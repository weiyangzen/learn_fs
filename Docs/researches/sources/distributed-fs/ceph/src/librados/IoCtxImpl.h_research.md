# sources/distributed-fs/ceph/src/librados/IoCtxImpl.h

## Purpose

`IoCtxImpl.h` declares the internal implementation behind librados `IoCtx`, the per-pool handle used by both the C and C++ APIs for object I/O. It binds a `RadosClient`, an `Objecter`, a pool id, snapshot read/write context, object locator state, object-version tracking, notification settings, operation flag overrides, and async write flush bookkeeping into one object that exported APIs can retain and pass around as an opaque `rados_ioctx_t`.

## Important APIs, Types, and Functions

The central type is `librados::IoCtxImpl`. Its public fields are part of the local implementation contract: `ref_cnt`, `client`, `poolid`, `snap_seq`, `snapc`, `assert_ver`, `last_objver`, `notify_timeout`, `no_version_on_read`, `oloc`, `extra_op_flags`, `objclass_flags_mask`, `objecter`, and the AIO write tracking structures. `get()` and `put()` implement intrusive lifetime management; `dup()` copies pool and operation state while deliberately excluding the reference count.

The API surface is broad. Snapshot methods include pool snapshots, self-managed snapshots, async self-managed create/remove, and rollback. Object data methods include create, write, append, write_full, writesame, read, mapext, sparse_read, checksum, remove, stat/stat2, trunc, compare extent, tmap update, class exec, xattrs, and generic `operate`/`operate_read`. Async counterparts cover reads, writes, xattrs, stat, exec, compare, cancellation, and flush. Watch/notify APIs manage watch cookies, notify payloads, acknowledgements, async watch/unwatch/notify, and callback flushing. Pool application metadata and cache pin/unpin helpers are also routed through this class.

## Control Flow and Data Flow

Most callers enter through C wrappers in `librados_c.cc` or C++ wrappers in `librados_cxx.cc`, cast or unwrap an `IoCtxImpl`, build an `object_t` and `bufferlist`, and call one of these methods. The implementation, in companion source files, converts the request into `ObjectOperation` work submitted through `Objecter`. `prepare_assert_ops()` adds version assertions when `assert_ver` is set. `get_objver_for_read()` centralizes whether read operations update `last_objver`, allowing `no_version_on_read` to suppress read-side version tracking.

Async writes are additionally registered in `aio_write_list` with monotonically increasing `aio_write_seq`. `flush_aio_writes()` and `flush_aio_writes_async()` wait for or complete after all prior writes have drained, using `aio_write_cond` and `aio_write_waiters`.

## State and Persistence Behavior

`IoCtxImpl` itself is process-local state, but many fields influence persisted cluster state: snapshot contexts select object versions, `oloc` selects namespace and locator key, `extra_op_flags` affects full-pool behavior, xattr/omap/class operations mutate object metadata, and application metadata writes pool-level metadata. `last_objver` is a local observation cache, not persistent. Lifetime is manual: users of `rados_ioctx_t` must balance creation with `put()` via destroy wrappers, and async operations must keep the implementation alive indirectly until completion.

## Dependencies and Integration Points

The file depends on Ceph common primitives, `SnapContext`, `object_locator_t`, `Objecter`, `ObjectOperation`, librados public headers, tracing types, and `AioCompletionImpl`/`PoolAsyncCompletionImpl`. It integrates directly with `RadosClient::create_ioctx()`, the exported C ABI, the C++ `IoCtx` class, object listing (`ListObjectImpl.h`), watch/notify infrastructure in `Objecter`, and monitor/mgr pool metadata commands reached through `RadosClient`.

## Risks and Edge Cases

The main risks are lifetime and ordering. `ref_cnt` is atomic but deletion is manual, so stale opaque handles or async callbacks using released contexts are hazardous. Snapshot state is mutable on the context, so concurrent users sharing one `IoCtxImpl` can race semantic settings such as read snap, namespace, locator, assert version, and flags. `dup()` intentionally does not copy every field; notably `no_version_on_read` and `objclass_flags_mask` are not copied, which matters if new settings are added. AIO flush correctness depends on every async write being queued and completed exactly once.

## Test Signals

Useful tests include create/destroy refcount balance, sync and async read/write/stat/xattr paths, `last_version()` changes after writes and reads with/without `set_no_version_on_read`, snapshot read/write context behavior, namespace and locator isolation, full-try flag propagation, async flush ordering, watch/notify callbacks and flush, application metadata round trips, and cancellation/error propagation through `AioCompletionImpl`.
