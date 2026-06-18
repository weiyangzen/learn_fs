# sources/distributed-fs/ceph-client/include/linux/rculist.h

Purpose: provides RCU-safe list and hlist mutation/traversal primitives for regular doubly linked lists and hash lists, including SRCU, lockless, bidirectional, splice, replace, and tracing variants.

Important APIs and types: initialization and pointer helpers include `INIT_LIST_HEAD_RCU()`, `list_next_rcu()`, `list_bidir_prev_rcu()`, `list_tail_rcu()`, `hlist_first_rcu()`, `hlist_next_rcu()`, and `hlist_pprev_rcu()`. Mutators include `list_add_rcu()`, `list_add_tail_rcu()`, `list_del_rcu()`, `list_bidir_del_rcu()`, `list_replace_rcu()`, RCU splice helpers, `hlist_add_head_rcu()`, tail/before/behind add helpers, `hlist_del_rcu()`, `hlist_del_init_rcu()`, `hlist_replace_rcu()`, and `hlists_swap_heads_rcu()`. Traversal macros cover list/hlist RCU, SRCU, lockless, continue/from, BH, and notrace variants.

Control flow: writers serialize with other writers, update links with `rcu_assign_pointer()` where readers may observe them, and defer freeing deleted nodes until a grace period. Readers traverse under `rcu_read_lock()` or an explicitly validated alternate protection condition. Splice-init first hides the source list from new readers, waits for a grace period, then attaches the old body to a new list.

State and persistence: state is caller-owned list/hlist nodes and heads in memory. Deleted nodes remain reachable to old readers until grace-period cleanup.

Dependencies and integration points: depends on generic list APIs and `rcupdate.h`. It is used throughout networking, VFS, device, and core kernel tables needing lockless read traversal.

Risks and test signals: risks include immediate free after deletion, mixing `list_del_rcu()` with bidirectional traversal, missing reader lock, hlist `pprev` poisoning surprises, unsafe empty-then-first patterns, and writer-writer races. Test lockdep RCU-list checks, concurrent add/delete/traverse, splice with active readers, replace/swap heads, hlist tail insertion, and SRCU-protected traversals.
