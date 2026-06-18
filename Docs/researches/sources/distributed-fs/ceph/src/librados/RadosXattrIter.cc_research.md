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
