<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/llist.h -->
# sources/distributed-fs/ceph-client/include/linux/llist.h

## Purpose
This header implements lockless NULL-terminated singly linked lists for multiple-producer/single-consumer and batch-drain patterns. It is intended for low-overhead enqueue and delete-all workflows.

## Important APIs, Types, and Functions
`struct llist_head` stores the first node; `struct llist_node` stores `next`. APIs include `LLIST_HEAD_INIT`, `LLIST_HEAD`, `init_llist_head`, `init_llist_node`, `llist_on_list`, `llist_entry`, traversal macros for deleted lists, `llist_empty`, `llist_next`, `llist_add_batch`, `__llist_add_batch`, `llist_add`, `llist_del_all`, `__llist_del_all`, `llist_del_first`, `llist_del_first_init`, `llist_del_first_this`, and `llist_reverse_order`.

## Control Flow
Producers push nodes with cmpxchg on `head->first`; batch add links the batch tail to the observed first pointer until the exchange succeeds. `llist_del_all` atomically swaps the head to NULL and returns a newest-to-oldest chain. Single-item delete uses external implementation and has stricter consumer concurrency rules.

## State and Persistence Behavior
State is volatile list links in caller-owned nodes. `init_llist_node` uses a self pointer to mark a node as off-list. The API has no persistence and generally permits traversal only after nodes have been removed from the live list.

## Dependencies and Integration Points
It depends on atomics, `try_cmpxchg`, `xchg`, `container_of`, and `WRITE_ONCE`/`READ_ONCE`. It integrates with work queues, deferred frees, and fast producer paths.

## Risks and Test Signals
Risks include multiple consumers using `llist_del_first` without locks, traversing live lists, ABA-like sequences described in the header, and NMI use on architectures lacking NMI-safe cmpxchg. Test signals are producer/consumer stress tests, KCSAN, architecture config checks, and order validation after `llist_reverse_order`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/llist.h -->
