# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/darray.c

This file implements dynamic-array resize backing for the macro API in `darray.h`.

Core function:
- `__bch2_darray_resize_noprof()`:
  - grows only when `new_size > d->size`
  - rounds capacity to a power of two
  - checks multiplication overflow for `new_size * element_size`
  - uses `kvmalloc` for allocations below kernel limits and `vmalloc` for larger allocations
  - copies old elements
  - publishes new data pointer with `rcu_assign_pointer()`
  - frees old allocation normally or via RCU depending on caller
  - preserves embedded preallocated storage when present

Important behavior:
- The implementation supports arrays with inline preallocated storage.
- `have_prealloc` prevents freeing embedded storage.
- RCU resize mode delays freeing old backing storage.

Research notes:
- This file is the only non-macro implementation point for darrays.
- The version check handles Linux allocation API differences around 6.18.
