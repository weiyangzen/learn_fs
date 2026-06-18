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
