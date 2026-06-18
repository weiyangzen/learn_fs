# sources/distributed-fs/ceph-client/include/linux/iova_bitmap.h

## Purpose
`iova_bitmap.h` declares the optional IOVA dirty/coverage bitmap helper used by IOMMUFD driver code. It gives callers an opaque bitmap object for a starting IOVA range, page size, and user buffer, then lets them mark subranges and iterate populated entries.

## Important APIs, types, and functions
The public contract is `struct iova_bitmap`, `iova_bitmap_fn_t`, `iova_bitmap_alloc`, `iova_bitmap_free`, `iova_bitmap_for_each`, and `iova_bitmap_set`. Disabled builds provide stubs returning `NULL`, `-EOPNOTSUPP`, or no-op behavior.

## Control flow
Callers allocate a bitmap, set IOVA intervals, iterate them through a callback, and free the object. The header gates all real work on `CONFIG_IOMMUFD_DRIVER`.

## State and persistence
State is entirely in the opaque bitmap and the user-provided bitmap storage. There is no persistent state.

## Dependencies and integration points
It depends on Linux integer types, `errno`, `__user` pointers, and the IOMMUFD driver implementation.

## Risks and test signals
Risks are page-size/range alignment mistakes, unsafe user-buffer access in the implementation, and callers not handling disabled stubs. Tests should cover disabled configs, empty bitmaps, partial ranges, large IOVA spans, and callback error propagation.
