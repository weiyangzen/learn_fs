## sources/distributed-fs/ceph-client/tools/lib/list_sort.c

Purpose: Implements stable in-place sorting for Linux `struct list_head` doubly-linked lists using bottom-up mergesort.

Important APIs/functions: Public `list_sort(void *priv, struct list_head *head, list_cmp_func_t cmp)`. Internal `merge()` merges null-terminated singly-linked runs, and `merge_final()` performs final merge while restoring `prev` links and circular list structure.

Control flow: The input circular doubly-linked list is converted to a null-terminated singly-linked list. The algorithm maintains pending sorted sublists controlled by the bit pattern of an element count, eagerly merging balanced runs. At end it merges remaining runs from smallest to largest and restores the canonical doubly-linked ring.

State/persistence: Mutates the caller-owned list links only; no allocation.

Dependencies/integration: Uses Linux list APIs, compiler annotations, export symbol macro, and a caller-supplied comparator that returns positive when `a` sorts after `b`.

Risks: Comparator contract is subtle: returning `<=0` preserves input order and enables stability. Corrupt input list links can loop or crash. The algorithm temporarily invalidates `prev` links until final merge.

Test signals: Cover empty/single lists, already sorted/reverse lists, duplicate keys preserving order, boolean and tri-state comparators, large lists, and list integrity after sort.
