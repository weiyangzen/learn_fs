# File Research: sources/cow-pools/openzfs/module/zfs/objlist.c

## Scope

Small ascending object-number list utility. It stores object IDs in increasing order and supports monotonic lookup that discards already-passed entries.

## Main Interfaces

- `objlist_create()` allocates and initializes an empty `objlist_t`.
- `objlist_destroy()` frees all remaining nodes and the list.
- `objlist_insert()` appends a new object number, with debug assertion that insertions are strictly ascending.
- `objlist_exists()` tests whether an object exists while pruning all list entries smaller than the lookup object.

## State And Control Flow

`objlist_t` wraps a `list_t` of `objlist_node_t` and records `ol_last_lookup`. Insertions append to the tail and must be in ascending order. Lookups must also be ascending: `objlist_exists()` asserts the requested object is at least the last lookup, removes and frees all head nodes smaller than the requested object, then returns whether the head equals the requested object.

## Dependencies

Uses OpenZFS list primitives, `kmem_alloc()` / `kmem_zalloc()` / `kmem_free()`, and debug assertions.

## Correctness Notes

This is a streaming membership structure, not a general set. Looking up object `N` permanently discards all stored objects smaller than `N`, and later lookup of a smaller object is invalid. Callers rely on sorted insert and sorted lookup for O(total nodes) behavior across a scan.
