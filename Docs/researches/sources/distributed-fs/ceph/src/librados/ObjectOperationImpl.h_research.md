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
