# sources/distributed-fs/orangefs/src/common/llist/llist.c

Purpose: Implements a simple singly linked list abstraction with a sentinel head node for OrangeFS common code.

Important APIs/functions: `PINT_llist_new()`, `PINT_llist_empty()`, `PINT_llist_add_to_head()`, `PINT_llist_add_to_tail()`, `PINT_llist_head()`, `PINT_llist_tail()`, `PINT_llist_search()`, `PINT_llist_rem()`, `PINT_llist_count()`, `PINT_llist_doall()`, `PINT_llist_doall_arg()`, `PINT_llist_free()`, and `PINT_llist_next()`.

Control flow: Lists always start with a sentinel whose `item` is `NULL`; add/remove/search/count skip that sentinel. Search/removal use caller-provided comparison functions that return `0` on match. `doall` saves the next pointer before invoking callbacks so callbacks may destroy the current item.

State/persistence: Heap-allocated list nodes contain only `void *item` and `next`. The list does not own item memory except when `PINT_llist_free()` calls the provided free callback.

Dependencies/integration: Includes `llist.h` and `pvfs2-internal.h`. Used as a generic container in common code.

Risks: No internal locking. Tail insertion is O(n). `PINT_llist_free()` returns without freeing nodes if `free_item` is NULL, so callers cannot free a list of non-owned items with this API. `PINT_llist_next()` exposes internal nodes and can bypass abstraction safety.

Test signals: Empty-list operations, head/tail ordering, search/remove comparator semantics, callback deletion during `doall`, and freeing with owned item data.
