# sources/distributed-fs/ceph-client/lib/klist.c

Purpose: implements `klist`, a refcounted and lock-protected list abstraction safe for iteration while nodes are being removed.

Important APIs/types: `struct klist`, `struct klist_node`, `struct klist_iter`, `klist_init`, add helpers (`klist_add_head`, `klist_add_tail`, `klist_add_behind`, `klist_add_before`), removal (`klist_del`, `klist_remove`), attachment test, iterator setup/exit, and directional iteration (`klist_next`, `klist_prev`). Internal low bit `KNODE_DEAD` marks nodes logically dead.

Control flow: add initializes the node kref, owner klist pointer, and optional embedder `get()` ref, then inserts under the klist spinlock. Iteration drops the previous node ref and takes the next/prev live node ref under lock, skipping dead nodes. `klist_del()` marks dead and drops a ref; actual list deletion happens when the kref reaches zero. `klist_remove()` installs a waiter and sleeps until release wakes it.

State and persistence: list membership, node kref counts, dead bit, and global removal waiter list are persistent kernel state until callers remove nodes and exit iterators.

Dependencies and integration: depends on list, kref, spinlocks, scheduler sleep/wake, and exported GPL symbols. Device core uses this pattern for safe lists of devices/drivers.

Risks: callers must call `klist_iter_exit()` to drop held refs; embedding object get/put callbacks must be valid outside the lock; removal waits uninterruptibly; low-bit pointer tagging requires aligned klist pointers; double kill and uninitialized nodes warn.

Test signals: concurrent iteration/removal stress, waiter wake tests, lockdep, reference leak detection, and device core hotplug tests.
