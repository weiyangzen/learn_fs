# sources/distributed-fs/ceph-client/scripts/gdb/linux/xarray.py

## Purpose
`xarray.py` contains small tagged-entry predicates used by radix tree and maple tree helpers.

## Important APIs, Types, and Functions
`xa_is_internal()` checks low tag bits, `xa_mk_internal()` constructs an internal entry, `xa_is_zero()` detects the zero entry, and `xa_is_node()` detects node-like internal entries above the low-address threshold.

## Control Flow
Each helper casts the GDB value to unsigned long and applies xarray tag constants and bit masks.

## State and Persistence Behavior
No state is stored or modified.

## Dependencies and Integration Points
`mapletree.py` uses `xa_is_node()` and `xa_is_zero()`. `radixtree.py` carries related xarray retry-entry logic. The file depends on `utils.get_ulong_type()`.

## Risks and Test Signals
Tagged pointer conventions are architecture and kernel-layout dependent. Test with known xarray zero entries, retry entries, direct values, and node pointers.
