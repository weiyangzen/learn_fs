# subset-b-006906 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/IoCtxImpl.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/IoCtxImpl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/ListObjectImpl.h -->
# sources/distributed-fs/ceph/src/librados/ListObjectImpl.h

## Purpose

`ListObjectImpl.h` defines the internal object-listing value type and iterator implementation used by librados object enumeration. It bridges `Objecter::NListContext` results to the public C++ `ListObject` and `NObjectIterator` abstractions, preserving object namespace, object id, and locator in each listed entry.

## Important APIs, Types, and Functions

`librados::ListObjectImpl` stores `nspace`, `oid`, and `locator`, exposes getters for each, has a defaulted three-way comparison operator, and has an `operator<<` formatter that prints `namespace/oid@locator` when optional fields are present. `NObjectIteratorImpl` owns a `std::shared_ptr<ObjListCtx> ctx` and the current `ListObject cur_obj`. It implements copy/assignment, equality, dereference, arrow, pre/post increment, `get_listobjectp()`, `get_pg_hash_position()`, hash-position and cursor seeks, `get_cursor()`, `set_filter()`, construction from `ObjListCtx*`, and `get_next()`.

## Control Flow and Data Flow

The iterator is constructed around an `ObjListCtx`, whose `Objecter::NListContext` stores batched list results. Increment calls eventually fetch more entries through `IoCtxImpl::nlist()` when the current batch is exhausted. Seek operations delegate to `IoCtxImpl::nlist_seek()` and cursor conversion helpers. The formatter is only diagnostic/user-facing; the actual enumeration state remains in `NListContext`.

## State and Persistence Behavior

The file manages only client-side iteration state. It does not persist data and does not mutate cluster objects. Its cursor and hash-position methods are externally visible state, however: callers can save cursor positions to resume or partition scans, and those positions depend on OSD map and PG hashing semantics.

## Dependencies and Integration Points

It depends on `include/rados/librados.hpp` for public `ListObject`, `NObjectIterator`, `ObjListCtx`, and `ObjectCursor` declarations, and on `Objecter::NListContext` through `ObjListCtx`. It is used by `librados_cxx.cc` for C++ iteration and by `librados_c.cc` through object listing/open/next/seek wrappers.

## Risks and Edge Cases

Iterator equality and copy behavior depend on shared context semantics; copies can share traversal state if not carefully implemented in the source file. Cursor seeks are rounded to placement-group boundaries, so callers expecting exact hash offsets may see coarser positioning. Namespace and locator strings are optional and can be empty, so formatting and C ABI conversions must preserve empty values distinctly from null pointers where the API requires it.

## Test Signals

Tests should cover listing empty and non-empty pools, namespace-filtered listing, objects with locator keys, iterator copy/increment/dereference behavior, cursor seek/resume, PG hash position rounding, filter buffer propagation, and formatted output for all combinations of namespace and locator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/ListObjectImpl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/ObjectOperationImpl.h -->
# sources/distributed-fs/ceph/src/librados/ObjectOperationImpl.h

## Purpose

`ObjectOperationImpl.h` provides the internal C-ABI write-operation wrapper for `Objecter` operations that may also carry an optional modification time. The public C write-op handle is opaque, but internally it needs both the actual `::ObjectOperation` and stable storage for a `ceph::real_time` value referenced during operation submission.

## Important APIs, Types, and Functions

The only type is `librados::ObjectOperationImpl`. It contains `::ObjectOperation o`, `ceph::real_time rt`, and `ceph::real_time *prt = nullptr`. `librados_c.cc` allocates this type in `rados_create_write_op()`, converts it with `to_object_operation()`, appends write, xattr, omap, assertion, class, and allocation-hint subops to `o`, and sets `rt`/`prt` in `rados_write_op_operate*()` and `rados_aio_write_op_operate*()` when callers provide `time_t` or `timespec` mtimes.

## Control Flow and Data Flow

The wrapper is created before a compound write operation is assembled. Each `rados_write_op_*` builder mutates `o`. At submission, the C layer converts caller mtime into `rt`, points `prt` at it, and passes `&o` plus `prt` to `IoCtxImpl::operate()` or `IoCtxImpl::aio_operate()`. The dedicated storage prevents a pointer to a stack-converted mtime from escaping the wrapper call.

## State and Persistence Behavior

`ObjectOperationImpl` is transient client-side state, but the suboperations in `o` can create, mutate, truncate, remove, or annotate persistent RADOS objects. `rt` is used to request a persisted object mtime when supplied. The wrapper is owned by the caller until `rados_release_write_op()` deletes it.

## Dependencies and Integration Points

It depends on `common/ceph_time.h` and `osdc/Objecter.h`. Its integration point is almost entirely `librados_c.cc`; the C++ API generally uses higher-level operation objects. It also depends on `IoCtxImpl` submission semantics and `Objecter`'s interpretation of `ObjectOperation`.

## Risks and Edge Cases

The wrapper stores only one mtime pointer for the whole compound operation, so repeated submission of the same write op with different mtimes mutates shared state. Callers must not use a write-op after release or concurrently mutate and submit it. If a new C write-op path bypasses `ObjectOperationImpl` and uses raw `ObjectOperation`, mtime support can be lost.

## Test Signals

Tests should assemble compound write ops with assertions, writes, omap, xattrs, class calls, and mtimes; submit both sync and async variants; confirm release frees without leaks; and verify object mtimes match supplied `time_t`/`timespec` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/ObjectOperationImpl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/PoolAsyncCompletionImpl.h -->
# sources/distributed-fs/ceph/src/librados/PoolAsyncCompletionImpl.h

## Purpose

`PoolAsyncCompletionImpl.h` implements the small completion object used for asynchronous pool-level operations such as pool creation, deletion, and application enable. It is separate from object `AioCompletionImpl` and supports wait, completion status, return-value retrieval, callback dispatch, and intrusive reference ownership.

## Important APIs, Types, and Functions

`librados::PoolAsyncCompletionImpl` stores `lock`, `cond`, `ref`, `rval`, `released`, `done`, `callback`, and `callback_arg`. Methods include `set_callback()`, `wait()`, `is_complete()`, `get_return_value()`, `get()`, `release()`, and `put()`. `intrusive_ptr_add_ref()` and `intrusive_ptr_release()` make it usable with `boost::intrusive_ptr`. `CB_PoolAsync_Safe` captures an intrusive pointer and, when invoked with an integer result, marks the completion done, wakes waiters, and calls the registered C callback outside the lock.

## Control Flow and Data Flow

Async pool functions create or receive a `PoolAsyncCompletionImpl`, wrap it in `CB_PoolAsync_Safe`, and pass a lambda context to `Objecter` or manager operations. When the lower layer completes, `operator()(int r)` moves the intrusive pointer into local ownership, sets `rval` and `done`, notifies `cond`, copies callback pointers, unlocks, invokes the callback, and then relocks before exiting.

## State and Persistence Behavior

The completion object is process-local synchronization state. The operations it represents mutate persistent pool or application metadata, but the completion itself persists only `rval` and `done` until released. `released` tracks the user-facing release contract separately from reference count, while `ref` controls deletion.

## Dependencies and Integration Points

It depends on Ceph mutex/condition primitives, librados C callback types, and `boost::intrusive_ptr`. `RadosClient::pool_create_async()` and `pool_delete_async()`, plus `IoCtxImpl::application_enable_async()`, integrate with this completion type.

## Risks and Edge Cases

The callback may call back into completion APIs while the object is still alive, so invoking it outside the lock is important. `release()` asserts it is only called once but does not decrement `ref`; callers still need the intrusive/user release path. `wait()` returns only wait success, not the operation result; callers must use `get_return_value()`. Missing callback registration before completion is legal but means no callback is fired.

## Test Signals

Tests should cover callback-before-completion and callback-after-creation ordering, wait waking, result retrieval, no-callback completions, double release assertions in debug builds, intrusive pointer lifetime during callback, and async pool create/delete error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/PoolAsyncCompletionImpl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/RadosClient.cc -->
# sources/distributed-fs/ceph/src/librados/RadosClient.cc

## Purpose

`RadosClient.cc` implements the cluster-level librados client. It owns connection setup and teardown, monitor and manager clients, messenger, `Objecter`, OSD map waiting, pool lookup and management, command dispatch, monitor log subscription, service-daemon registration, and runtime config observation for librados threading and monitor-operation timeout.

## Important APIs, Types, and Functions

The implementation covers `RadosClient::connect()`, `shutdown()`, destructor, `create_ioctx()`, `lookup_pool()`, `pool_get_name()`, pool alignment helpers, `get_fsid()`, `ping_monitor()`, `watch_flush()` and async watch flush, compatibility queries, dispatcher callbacks, `wait_for_osdmap()`, `wait_for_latest_osdmap()`, pool list/stats/create/delete/base-tier/self-managed-snap-mode helpers, `get_fs_stats()`, refcount `get()`/`put()`, blocklist helpers, mon/mgr/osd/pg command wrappers, monitor log subscription and delivery, service-daemon registration/update, inconsistent-PG query parsing, and `handle_conf_change()`.

## Control Flow and Data Flow

`connect()` transitions `DISCONNECTED -> CONNECTING -> CONNECTED`. It starts logging, bootstraps monmap/config, starts the async IO context pool, builds the initial monmap, creates a client messenger, requires `CEPH_FEATURE_OSDREPLYMUX`, constructs and starts `Objecter`, wires dispatchers, initializes and authenticates `MonClient`, configures `MgrClient`, starts subscriptions, optionally registers service metadata, starts `Objecter`, and records the monitor-assigned global id. On error it resets state and deletes partially created `Objecter`/messenger.

Normal operations first ensure a valid OSD map with `wait_for_osdmap()` or request the latest map with `wait_for_latest_osdmap()`. Pool and stats calls read `OSDMap` under `objecter->with_osdmap()` or issue Objecter requests with blocked completions. Command wrappers marshal vectors and bufferlists to MonClient, MgrClient, or Objecter and translate `boost::system::error_code` to negative errno. Message dispatch handles OSD map notifications by waking waiters and monitor log messages by invoking registered callbacks.

## State and Persistence Behavior

The object is process-local but controls persistent cluster operations: pool create/delete, blocklist entries, manager service records, monitor commands, and OSD/PG commands. Persistent identity is `instance_id`, the monitor global id assigned after authentication. Local state includes connection state, messenger and objecter pointers, log subscription state, daemon registration metadata, reference count, timeout, and thread pool. `shutdown()` flushes watch callbacks before stopping Objecter, manager, monitor, messenger, and pool threads.

## Dependencies and Integration Points

Dependencies include `CephContext`, `ConfigProxy`, `MonClient`, `MgrClient`, `Messenger`, `Objecter`, Ceph async blocked completions, JSON parsing, message types such as `MLog`, and librados completion types. It integrates with `librados_c.cc` cluster functions, C++ `Rados`, `IoCtxImpl`, watch/notify callback flushing, service-daemon status, monitor log subscriptions, and config observer infrastructure.

## Risks and Edge Cases

State transitions are sensitive: some methods assume `state == CONNECTED`, and `wait_for_osdmap()` returns `-ENOTCONN` otherwise. `connect()` mutates state without holding `lock` throughout, so callers must respect external connection serialization. `mgr_command()` manually unlocks/relocks around waits while using a `lock_guard`, which is unusual and relies on Ceph mutex semantics/macros. OSD map waits can block indefinitely when timeout is zero. Monitor log delivery runs under client lock, so callbacks must avoid deadlocks. `blocklist_add()` falls back to legacy blacklist command on `-EINVAL`.

## Test Signals

Tests should cover connect/shutdown success and injected failures, double connect return codes, create_ioctx by name and id, pool lookup retry after latest map, OSD map wait timeout, pool stats mapping, pool create/delete async completions, mon/mgr/osd/pg commands, monitor log callback versions and stop behavior, blocklist fallback, service registration before and after connect, inconsistent-PG JSON variants, and config changes resizing `poolctx`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/RadosClient.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/RadosClient.h -->
# sources/distributed-fs/ceph/src/librados/RadosClient.h

## Purpose

`RadosClient.h` declares the internal cluster client class that underpins librados C and C++ APIs. It exposes cluster lifecycle, pool lookup/management, command routing, watch flushing, service-daemon status, monitor-log subscription, configuration observation, and creation of per-pool `IoCtxImpl` handles.

## Important APIs, Types, and Functions

`librados::RadosClient` inherits from `Dispatcher` and `md_config_obs_t`. Key members are `CephContext` ownership through `cct_deleter`, `conf`, `poolctx`, connection `state`, `MonClient`, `MgrClient`, `Messenger*`, `instance_id`, `Objecter*`, `lock`, `cond`, `refcnt`, monitor-log callback fields, service-daemon metadata, and `rados_mon_op_timeout`. Public methods include `connect()`, `shutdown()`, `ping_monitor()`, `watch_flush()`, `async_watch_flush()`, compatibility queries, `wait_for_latest_osdmap()`, `create_ioctx()`, fsid/pool lookup and alignment helpers, pool list/stats/create/delete, command wrappers, log monitoring, intrusive `get()`/`put()`, blocklist, service-daemon calls, monitor feature query, inconsistent-PG lookup, and config observer overrides.

## Control Flow and Data Flow

The header makes `RadosClient` the owner of the network path. Messages arrive through `Dispatcher` overrides, are filtered by connection state, and are routed to `_dispatch()`. Public wrappers typically validate state, wait for OSD maps, then read from `OSDMap` or submit commands through MonClient, MgrClient, or Objecter. `create_ioctx()` transfers the client/objecter/pool identity into a new `IoCtxImpl`.

## State and Persistence Behavior

Persistent cluster effects are exposed through methods but not stored in the class except as local identity and subscription metadata. The class owns long-lived runtime resources: messenger, objecter, monitor/mgr clients, async thread pool, config observer registration, monitor log watch string, callback pointers, and optional service-daemon metadata that can be registered after connect.

## Dependencies and Integration Points

It depends on Ceph messenger, monitor and manager clients, config observer APIs, common mutex/condition/time helpers, librados public headers, and `IoCtxImpl.h`. It grants friendship to `neorados::detail::RadosClient`, indicating newer neorados internals share access. It is included by `librados_c.cc`, `librados_cxx.cc`, and other librados internals.

## Risks and Edge Cases

The class mixes manual pointer ownership (`messenger`, `objecter`) with RAII ownership (`cct_deleter`), so shutdown/destructor ordering matters. `refcnt` is protected by `lock` and separate from object lifetime controlled by callers. Callback pointers for monitor logs are raw C function pointers and arguments. Methods that expose `rados_t`/`rados_config_t` must not outlive the client. Config changes can stop/start the IO pool while operations are active.

## Test Signals

Header-level coverage comes from API and integration tests that exercise each declared method: connection lifecycle, IoCtx creation, pool metadata, command routing, watch flushing, logging callbacks, service registration, refcount balance, config-change observer behavior, and message dispatch under disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/RadosClient.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/RadosXattrIter.cc -->
# sources/distributed-fs/ceph/src/librados/RadosXattrIter.cc

## Purpose

`RadosXattrIter.cc` implements construction and destruction for the xattr iterator object used by the librados C interface. It provides the small amount of memory-management behavior needed when C callers iterate attribute names and values returned from C++ maps and bufferlists.

## Important APIs, Types, and Functions

The file defines `librados::RadosXattrsIter::RadosXattrsIter()` and `~RadosXattrsIter()`. The constructor initializes `val` to `NULL` and sets `i` to `attrset.end()`. The destructor frees the most recently allocated `val` buffer, then clears the pointer.

## Control Flow and Data Flow

`librados_c.cc` allocates this iterator for `rados_getxattrs()`, async xattr completion, and read-op getxattrs. The C wrapper populates `attrset`, sets `i = attrset.begin()`, and each `rados_getxattrs_next()` call frees any previous `val`, allocates/copies the next bufferlist into `val`, returns pointers to the map key and copied value, and advances `i`. This source file supplies the initial and final cleanup states for that flow.

## State and Persistence Behavior

All state is client-side and transient. `attrset` owns the map of xattrs fetched from an object at one point in time. `val` is a per-step heap copy exposed to C callers and must be freed on the next iteration or end.

## Dependencies and Integration Points

The implementation includes `<stdlib.h>` for `free()` and `RadosXattrIter.h` for the struct. Its only integration point is the C xattr iterator ABI in `librados_c.cc`.

## Risks and Edge Cases

The returned value pointer is invalidated on the next `next()` call or iterator end. Empty xattr values return `NULL` because `malloc(0)` is not portable. Constructor sets the iterator to end before population, so callers must set `i` after filling `attrset`. Any wrapper that overwrites `val` without freeing would leak.

## Test Signals

Tests should iterate zero, one, and many xattrs; include empty values and binary values; verify values remain valid until the next call; check end returns null name/value and zero length; and run leak checks over early iterator destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/RadosXattrIter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/RadosXattrIter.h -->
# sources/distributed-fs/ceph/src/librados/RadosXattrIter.h

## Purpose

`RadosXattrIter.h` declares the internal iterator used to expose object xattrs through the C ABI. It stores the fetched attributes in C++ containers while allowing `librados_c.cc` to return stable C pointers for one iteration step at a time.

## Important APIs, Types, and Functions

`librados::RadosXattrsIter` has a constructor, destructor, `std::map<std::string, bufferlist> attrset`, map iterator `i`, and `char *val`. `attrset` owns fetched xattr values, `i` records the next item to return, and `val` owns the current heap-copied value buffer exposed to C.

## Control Flow and Data Flow

Callers allocate the struct, populate `attrset` from `IoCtxImpl::getxattrs()` or a read op, set `i`, and then repeatedly call C wrapper iteration functions. Those functions expose `i->first.c_str()` for the name and copy `i->second` to `val` for the value. End functions delete the iterator and trigger destructor cleanup.

## State and Persistence Behavior

The iterator is a snapshot of xattrs returned by one operation. It does not track later object changes. `val` has iteration-step lifetime, not object lifetime. No persistent state is written.

## Dependencies and Integration Points

It depends on `include/buffer.h` for `bufferlist` and standard `map`/`string`. It integrates with `librados_c.cc` xattr functions and read-op completion handlers.

## Risks and Edge Cases

Because names point into `attrset`, they are invalid after iterator deletion. Because values point to `val`, only one value pointer is valid at a time. Binary xattrs can contain null bytes, so callers must use returned lengths rather than C-string semantics. Null/empty value differences are constrained by the C ABI's portable allocation handling.

## Test Signals

Tests should cover pointer lifetime, binary values with embedded nulls, empty values, repeated `next()` calls, deletion before full consumption, and async getxattrs transferring iterator ownership only on success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/RadosXattrIter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/librados_asio.h -->
# sources/distributed-fs/ceph/src/librados/librados_asio.h

## Purpose

`librados_asio.h` adapts librados asynchronous object/watch/notify operations to Boost.Asio's asynchronous operation model. It lets callers use completion tokens, associated executors, and cancellation slots while internally driving regular librados `AioCompletion` callbacks.

## Important APIs, Types, and Functions

Important detail types are `AioCompletionDeleter`, `unique_aio_completion_ptr`, `Invoker<Result>` and its `void` specialization, `AsyncHandler<Handler>`, and `AsyncOp<Result>`. `AsyncOp` owns the `AioCompletion`, registers `aio_dispatch()` as the librados callback, extracts return value and object version directly from `AioCompletionImpl`, converts negative errno to `boost::system::error_code`, and dispatches the user handler. `op_cancellation` maps Asio cancellation to `AioCompletion::cancel()`, allowing all cancellation types for reads and only terminal cancellation for writes.

Public templates include `async_read()`, `async_write()`, read and write overloads of `async_operate()`, `async_watch()`, `async_unwatch()`, and `async_notify()`. They all use `boost::asio::async_initiate`, create an `AsyncOp`, call the matching `IoCtx::aio_*` method, post immediate errors, and release completion ownership until callback.

## Control Flow and Data Flow

The user calls an `async_*` helper with an executor, `IoCtx`, operation arguments, and completion token. The initiating lambda creates a Ceph async `Completion` carrying the wrapped handler and an owned librados `AioCompletion`. On successful submission, ownership is released to the librados callback. On completion, `aio_dispatch()` reclaims the `Completion`, moves result storage out, reads `rval` and `objver`, creates an error code when needed, and dispatches the handler with `(error_code, version_t[, result])`. `AsyncHandler` clears the cancellation slot before destroying the `AioCompletion`, preventing a cancellation handler from referencing a freed completion.

## State and Persistence Behavior

The file manages transient async state only. Persistent RADOS effects are those of the submitted write, operate, watch, unwatch, or notify operation. Result-bearing operations store a `bufferlist` until handler dispatch. Object version is returned as local completion metadata.

## Dependencies and Integration Points

It depends on Boost.Asio cancellation/associator/executor support, public librados C++ API, Ceph async completion utilities, and `AioCompletionImpl`. It integrates with `IoCtx` async methods and can be used by applications that already run Boost.Asio event loops.

## Risks and Edge Cases

The template signatures include a `trace_ctx` parameter for `async_operate()` read overload but the initiating lambda does not forward it; write operate does forward it. The comments say an `IoCtx` reference need not remain valid, but some `IoCtx` instance must keep the underlying implementation alive, so applications can still create lifetime bugs. Direct access to `AioCompletionImpl` avoids locking and assumes callback-time stability. Cancellation semantics differ for read and write because writes may already have side effects.

## Test Signals

Tests should use callback, future, coroutine, and custom token styles; verify executor association; confirm immediate submission errors are posted; check version and error-code mapping; test read bufferlist results; exercise cancellation before and after submission; verify write cancellation only responds to terminal cancellation; and run lifetime tests where the initiating `IoCtx` wrapper is destroyed while another reference keeps the implementation alive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/librados_asio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/librados_c.cc -->
# sources/distributed-fs/ceph/src/librados/librados_c.cc

## Purpose

`librados_c.cc` is the implementation of the exported C ABI declared in `include/rados/librados.h`. It translates opaque C handles and C buffers into `RadosClient`, `IoCtxImpl`, `ObjectOperation`, `AioCompletionImpl`, and C++ `IoCtx` calls, while preserving symbol-version compatibility, tracepoints, errno-style return values, and C ownership rules.

## Important APIs, Types, and Functions

The file starts with symbol-version macros (`LIBRADOS_C_API_*`) that emit base/default symbol versions when building shared librados. `rados_create_cct()` initializes a library `CephContext` without global daemon state and initializes tracepoints. Cluster APIs include create/create2/create_with_context, connect, shutdown, cct, version, config parsing/get/set, fsid, pool lookup/list/reverse lookup, stats, blocklist/blacklist, address retrieval, command routing, monitor log, and service registration.

IoCtx APIs create/destroy pool handles, expose pool stats, snapshots, namespace/locator, pool alignment, full-try flags, application metadata, sync object I/O, xattrs, stat, class exec, object listing, and allocation hints. Async APIs create/wait/query/release completions and submit async object, xattr, stat, exec, snap, flush, watch, notify, and operation calls. Watch/notify wrappers adapt C callbacks into `WatchCtx`/`WatchCtx2` subclasses and decode notify replies into C arrays. Compound write/read operation APIs allocate operation objects, add assertions and subops, execute sync/async, and provide omap/xattr/read result iterators. Lock APIs adapt C calls to C++ `IoCtx` lock methods.

## Control Flow and Data Flow

Most functions follow a simple bridge pattern: cast an opaque handle, validate selected arguments, build `object_t`, `bufferlist`, vectors, maps, or sets, call an internal method, copy results into caller buffers or allocate output buffers, emit tracepoints, and return negative errno or positive byte/count results. Output-buffer helpers allocate with `malloc()` for C callers and are paired with `rados_buffer_free()`. Iterator APIs allocate C++ iterator structs and expose pointers valid until the next iteration/end call.

Compound operations are staged: create op, append subops to `ObjectOperation`, then submit through `IoCtxImpl::operate()`/`operate_read()` or async variants. Some read subops install `Context` handlers (`C_bl_to_buf`, `C_out_buffer`, `C_OmapIter`, `C_XattrsIter`) so that after Objecter completion, output buffers or iterators are populated.

## State and Persistence Behavior

The file itself stores almost no global state beyond tracepoint traits. It creates persistent effects through cluster commands, pool lifecycle, object writes/removes/truncates/xattrs/omap/class calls, locks, watch registrations, notify acknowledgements, and metadata updates. Local state is represented by opaque handles: `rados_t` owns a `RadosClient`, `rados_ioctx_t` owns an `IoCtxImpl` ref, completion handles own `AioCompletionImpl`, iterators own result snapshots, and op handles own assembled operations.

## Dependencies and Integration Points

It depends on Ceph config/common init, tracepoints, `hobject_t`, async waiters, public C header, `AioCompletionImpl`, `IoCtxImpl`, `ObjectOperationImpl`, `RadosClient`, `RadosXattrIter`, `ListObjectImpl`, and `librados_util.h`. It is the ABI boundary used by external C callers and also by parts of the C++ API that implement behavior in terms of C wrappers.

## Risks and Edge Cases

ABI compatibility is a major risk: symbol versions preserve old struct layouts such as base `rados_ioctx_pool_stat`, and deprecated tmap base/default behavior differs intentionally. Buffer sizing must return `-ERANGE` and required lengths consistently. Several APIs return borrowed pointers into iterator-owned maps or one-step heap buffers, so lifetime documentation and tests matter. Null-pointer validation is uneven because older ABI behavior may be preserved. Async wrappers that allocate intermediate completions/data must release them on every completion path. Compound ops can be reused/mutated by callers, so concurrent use is unsafe. `rados_aio_writesame()` passes `o` where the local `oid` object was built, relying on implicit conversion and deserving regression coverage.

## Test Signals

Coverage should include C ABI symbol/version checks, create/connect/shutdown, config parsing, pool and cluster stats, pool create/delete and async variants, all sync object I/O paths, user-buffer and allocated-buffer outputs, xattr and omap iterators, object listing cursor/slice APIs, async completion state/callback ordering, watch/notify including reply decoding/freeing, lock/list/break lock, compound read/write operations, error paths for too-small buffers and invalid inputs, and LTTNG tracepoint builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/librados_c.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/librados_c.h -->
# sources/distributed-fs/ceph/src/librados/librados_c.h

## Purpose

`librados_c.h` is a small internal compatibility header for the C ABI implementation. It defines the legacy/base pool-stat layout used by older symbol versions of `rados_ioctx_pool_stat`, allowing `librados_c.cc` to expose both the current public struct and the older base ABI.

## Important APIs, Types, and Functions

The only declared type is `__librados_base::rados_pool_stat_t`, with fields for bytes, kilobytes, object counts, clone/copy counts, degraded/missing/unfound counts, and read/write operation and kilobyte counters. It intentionally omits newer fields present in the current public `rados_pool_stat_t`, such as user bytes and compression stats.

## Control Flow and Data Flow

There is no runtime control flow. `librados_c.cc` includes this header, computes current pool stats into the modern `rados_pool_stat_t`, then copies the subset of fields into `__librados_base::rados_pool_stat_t` for the base symbol implementation.

## State and Persistence Behavior

The header defines ABI data shape only. It does not store state or mutate cluster data. Its field ordering and sizes are effectively persistent ABI contract for old clients linked against base librados symbols.

## Dependencies and Integration Points

It depends on `include/types.h` and public `include/rados/librados.h`. Its integration point is the versioned C API implementation in `librados_c.cc` and the build's symbol-version support.

## Risks and Edge Cases

Changing this struct would break old binary clients. Removing it would break the base symbol path. Adding current fields here would also be wrong because base callers allocated the old size. Tests must ensure the default symbol uses the modern struct while the base symbol copies exactly the legacy subset.

## Test Signals

Tests should verify ABI size/layout where possible, symbol-version availability, old pool-stat callers receiving correct legacy fields, and current callers receiving additional user/compression fields through the default symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/librados/librados_c.h -->
