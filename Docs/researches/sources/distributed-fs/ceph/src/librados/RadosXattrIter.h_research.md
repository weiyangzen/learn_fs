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
