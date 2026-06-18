# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/darray.h

This header provides typed dynamic-array macros used widely throughout bcachefs.

Core abstractions:
- `DARRAY(type)` and `DARRAY_PREALLOCATED(type, nr)`.
- Named type generation:
  - `DEFINE_DARRAY_NAMED`
  - `DEFINE_DARRAY`
  - free-item variants
- Built-in darray typedefs for integer types and string arrays.

Operations:
- Initialization and cleanup:
  - `darray_init()`
  - `darray_exit()`
  - `darray_exit_free_item()`
- Iteration:
  - forward
  - reverse
  - from pointer
  - bounded max
- Resize:
  - `darray_resize_gfp()`
  - `darray_resize()`
  - `darray_resize_rcu()`
  - make-room variants
- Mutation:
  - `darray_push_gfp()`
  - `darray_push()`
  - `darray_pop()`
  - insert/remove helpers
- Search:
  - `darray_find_p()`
  - `darray_find()`
- Sorting/search layout:
  - normal sort
  - Eytzinger sort/find with one-based layout

Important invariants:
- Arrays track `nr`, `size`, `data`, and optional inline storage.
- Capacity is managed in element counts, not bytes.
- RCU resize requires callers to use the RCU-specific resize path.
- Eytzinger one-based helpers assume element 0 is reserved by caller; users push an empty sentinel before sorting.

Research notes:
- This macro library underpins snapshot ID lists, deletion lists, printbuf alignment scratch arrays, and many other bcachefs internals.
