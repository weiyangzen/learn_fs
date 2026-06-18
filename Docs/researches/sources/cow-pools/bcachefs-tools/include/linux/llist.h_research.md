# File Research: sources/cow-pools/bcachefs-tools/include/linux/llist.h

This header defines the Linux lockless singly-linked list API. `struct llist_head` stores the first node, and `struct llist_node` stores `next`.

It provides initialization, entry conversion, iteration over deleted batches, safe iteration, empty checks, `llist_add()` via external `llist_add_batch()`, `llist_del_all()` via atomic exchange, and external `llist_del_first()`/`llist_reverse_order()`.

The comments document concurrency rules: multiple producers may add while a consumer deletes all; multiple consumers require locking for `del_first` interactions.
