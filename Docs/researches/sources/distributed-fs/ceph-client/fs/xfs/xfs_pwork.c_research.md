# sources/distributed-fs/ceph-client/fs/xfs/xfs_pwork.c

Purpose: Provides a small parallel workqueue abstraction for XFS tasks that can be split across CPUs while collecting the first error and offering polling that keeps the soft lockup watchdog alive.

Important APIs, types, and functions: `xfs_pwork_init` allocates an unbound, sysfs-visible, freezable workqueue and initializes `struct xfs_pwork_ctl`. `xfs_pwork_queue` initializes and queues an embedded `struct xfs_pwork`. `xfs_pwork_poll` waits for completion with periodic watchdog touches. `xfs_pwork_destroy` destroys the workqueue and returns the recorded error. Internal `xfs_pwork_work` invokes the caller work function, records the first error, decrements the work count, and wakes waiters.

Control flow: Callers initialize a control object with mount, callback, and tag; queue work items embedded in caller-owned structures; optionally poll until `nr_work` reaches zero; then destroy the workqueue to flush and retrieve the first error. DEBUG builds can override the worker count via `xfs_globals.pwork_threads`; otherwise allocation uses no explicit concurrency limit.

State and persistence behavior: State is memory-only in `xfs_pwork_ctl`: workqueue pointer, mount pointer, callback, waitqueue, atomic pending-work count, and first error. No disk state is changed by this layer, though callbacks may perform filesystem work.

Dependencies and integration points: Uses Linux workqueues, waitqueues, atomics, NMI softlockup watchdog touch, XFS tracing, and global sysctl/debug settings. `xfs_iwalk` is a visible user for parallel AG inode walking.

Risks: The first error does not stop already queued work; callbacks must call `xfs_pwork_want_abort` or `xfs_pwork_ctl_want_abort` to cooperate. `xfs_pwork_destroy` relies on workqueue destruction to flush outstanding work, so callers must not free embedded work items early. Polling is intended for lock-heavy mount-like callers and should not replace normal flush semantics blindly.

Test signals: Queue multiple successful and failing work items; confirm first-error retention, wait wakeups, destroy flush, DEBUG thread override, and cooperative abort checks. Exercise mount-time users under soft-lockup-sensitive conditions to verify `xfs_pwork_poll` touches the watchdog while waiting.
