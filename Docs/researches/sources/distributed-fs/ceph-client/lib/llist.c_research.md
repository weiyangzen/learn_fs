# sources/distributed-fs/ceph-client/lib/llist.c

Purpose: lockless singly linked list consumer helpers.

Important APIs/types/functions: `llist_del_first()`, `llist_del_first_this()`, and `llist_reverse_order()`.

Control flow: delete-first uses acquire load of `head->first`, reads the next pointer, and retries `try_cmpxchg()` until it removes the observed head or sees empty. Delete-first-this removes only if the current head is the supplied node. Reverse walks a null-terminated chain and reverses next pointers.

State/persistence: atomically updates `struct llist_head->first`; reverse mutates the supplied chain's next pointers.

Dependencies/integration: exported GPL symbols used by lockless producer/single-consumer queue patterns such as `lwq.c`. Requires architecture cmpxchg properties described in the file comment for NMI usage.

Risks: `llist_del_first()` supports only one simultaneous consumer without external locking. Concurrent multiple consumers can corrupt assumptions around `head->first->next`. `llist_reverse_order()` is not concurrency-safe on a live list.

Test signals: no direct tests in this subset. Correctness signals are LIFO removal from llist head, conditional removal only for matching head, and reversed batch order.
