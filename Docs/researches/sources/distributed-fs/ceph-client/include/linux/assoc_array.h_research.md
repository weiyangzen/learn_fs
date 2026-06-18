# sources/distributed-fs/ceph-client/include/linux/assoc_array.h

## Purpose
Declares the public generic associative-array API used for key-indexed object storage.

## Important APIs, Types, And Functions
With `CONFIG_ASSOCIATIVE_ARRAY`, `struct assoc_array` holds the root pointer and leaf count. `struct assoc_array_ops` supplies key chunk extraction, object key chunk extraction, object comparison, object difference, and object free callbacks. APIs include `assoc_array_init()`, `assoc_array_iterate()`, `assoc_array_find()`, `assoc_array_destroy()`, `assoc_array_insert()`, `assoc_array_insert_set_object()`, `assoc_array_delete()`, `assoc_array_clear()`, `assoc_array_apply_edit()`, `assoc_array_cancel_edit()`, and `assoc_array_gc()`.

## Control Flow, State, And Persistence
Edits are prepared as `struct assoc_array_edit` objects, then either applied or canceled. The array persists through its root pointer and leaf count. Insert/delete/clear/GC mutate the tree only when edits are applied, allowing preallocation and rollback.

## Dependencies And Integration Points
Depends on `linux/types.h` and the private implementation. Integrated by keyrings and other kernel subsystems needing RCU-friendly associative lookup over caller-defined keys.

## Risks And Test Signals
Callback consistency is critical: `get_key_chunk`, `compare_object`, and `diff_objects` must describe the same key space. Tests should cover insert/find/delete, duplicate insertion, edit cancellation, GC filtering, destroy freeing, iteration ordering expectations, and config-disabled builds.
