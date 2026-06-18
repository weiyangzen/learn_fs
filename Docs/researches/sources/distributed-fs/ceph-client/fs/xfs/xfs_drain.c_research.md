# sources/distributed-fs/ceph-client/fs/xfs/xfs_drain.c

Purpose: Implements a passive drain counter so online fsck and exclusive metadata checkers can wait for deferred work intents targeting an allocation or realtime group to finish.

Important APIs, types, and functions: Defines static key `xfs_defer_drain_waiter_gate` and functions to enable/disable waiter checks, initialize/free drains, get/put group intents, drain a group, and test if a group is busy.

Control flow: Writers call `xfs_group_intent_get()` to hold a group and increment its intent count before queuing deferred updates. Completion calls `xfs_group_intent_put()` to decrement and wake waiters if the count reaches zero. Scrub/repair calls `xfs_group_intent_drain()` without holding locks needed by intent completion.

State and persistence: Maintains transient atomic counts and waitqueues in group structures; no disk state is changed.

Dependencies and integration points: Depends on group lookup/refcounting, deferred work lifecycle, waitqueues, static branches, tracepoints, and online fsck synchronization.

Risks and test signals: Risks include missed wakeups, unbalanced get/put, static-key calls under reclaim-sensitive locks, and deadlock if drain waiters hold AG/rt locks. Test scrub against long deferred chains, cancellation paths, signalable waits, lockdep, and teardown assertions.
