# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/list.c

Generic intrusive doubly linked list implementation for the SPL.

Provides:
- List lifecycle: `list_create()`, `list_destroy()`.
- Insertion: head, tail, before, after.
- Removal: object, head, tail.
- Traversal: head, tail, next, previous.
- Bulk/link helpers: `list_move_tail()`, `list_link_replace()`, `list_link_init()`, `list_link_active()`, `list_is_empty()`.

The list stores the object-to-node offset and uses a sentinel head node. Assertions validate offsets and active links.
