<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/list.h -->
# sources/distributed-fs/ceph-client/include/linux/list.h

## Purpose
This is the kernel's generic intrusive linked-list API. It provides circular doubly linked `struct list_head` lists and single-pointer `struct hlist_head` hash lists, along with initializer, mutation, traversal, and container-conversion helpers used throughout the kernel.

## Important APIs, Types, and Functions
The list API includes `LIST_HEAD_INIT`, `LIST_HEAD`, `INIT_LIST_HEAD`, `list_add`, `list_add_tail`, `list_del`, `list_del_init`, `list_replace`, `list_swap`, `list_move`, `list_bulk_move_tail`, `list_cut_position`, `list_splice*`, and typed iteration macros such as `list_for_each_entry_safe`. Hardened builds route through `__list_add_valid()` and `__list_del_entry_valid()` and slowpath reporters. The hlist API includes `INIT_HLIST_NODE`, `hlist_unhashed`, `hlist_add_head`, `hlist_del_init`, `hlist_move_list`, `hlist_splice_init`, and typed hlist traversal macros.

## Control Flow
Most operations rewrite adjacent `next` and `prev` pointers inline. The circular list head is both sentinel and empty-list representation. Safe iterators prefetch the next node before user code may delete the current one. Hlist deletion uses the `pprev` backlink to update either a head pointer or predecessor `next` pointer without a two-pointer head.

## State and Persistence Behavior
The only state is embedded in caller-owned list nodes. Deleted regular list nodes are poisoned by `list_del`; `list_del_init` returns them to self-linked empty state. The API does not lock; callers must serialize concurrent mutation or use RCU-specific variants elsewhere.

## Dependencies and Integration Points
It depends on `container_of`, `WRITE_ONCE`, `READ_ONCE`, `poison.h`, and memory barriers for careful empty checks. It is a foundational dependency for cache, filesystem, networking, LSM, lockdep, livepatch, and driver structures.

## Risks and Test Signals
Common failures are double add, double delete, stale iterators, using unsafe iteration while deleting, and assuming `list_empty()` is a synchronization primitive. Useful signals are `CONFIG_LIST_HARDENED`, `CONFIG_DEBUG_LIST`, KASAN/UAF reports, lockdep coverage around caller locks, and targeted tests that exercise add/delete/splice/cut paths under the intended synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/list.h -->
