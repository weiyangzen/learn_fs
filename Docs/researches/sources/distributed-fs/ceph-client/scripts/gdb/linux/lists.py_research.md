# sources/distributed-fs/ceph-client/scripts/gdb/linux/lists.py

## Purpose
`lists.py` provides shared traversal and validation helpers for Linux `list_head` and `hlist` structures, plus the `lx-list-check` diagnostic command.

## Important APIs, Types, and Functions
`list_for_each()` yields node addresses from a circular `struct list_head`. `list_for_each_entry()` wraps nodes with `container_of()`. `hlist_for_each()` and `hlist_for_each_entry()` do the same for `hlist_head`. `list_check()` verifies `prev->next` and `next->prev` integrity.

## Control Flow
Traversal resolves pointer-vs-value inputs, checks type compatibility, handles a null `next` as an uninitialized empty list, then follows links until it reaches the head. `LxListChk.invoke()` parses one expression and calls `list_check()`.

## State and Persistence Behavior
All helpers are read-only and stateless aside from `CachedType` invalidation. Iterators expose live memory directly and do not snapshot the list.

## Dependencies and Integration Points
Many other GDB helpers use this file for task lists, module lists, genpd lists, slab lists, and vmalloc lists. It depends on `linux.utils.container_of()`.

## Risks and Test Signals
Corrupt non-circular lists can loop forever unless a bad pointer triggers `gdb.MemoryError`. `hlist_for_each()` dereferences `first` before checking null-like state. Test with known good lists and intentionally corrupted list fixtures under GDB.
