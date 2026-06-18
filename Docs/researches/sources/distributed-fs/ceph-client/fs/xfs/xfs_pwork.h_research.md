# sources/distributed-fs/ceph-client/fs/xfs/xfs_pwork.h

Purpose: Declares the XFS parallel work abstraction, including caller-visible control and embedded work structures plus helper functions for queuing, waiting, teardown, and cooperative abort checks.

Important APIs, types, and functions: `xfs_pwork_work_fn` is the callback signature. `struct xfs_pwork_ctl` stores the workqueue, mount, callback, waitqueue, pending count, and first error. `struct xfs_pwork` embeds Linux `work_struct` and a backpointer to the control object. `XFS_PWORK_SINGLE_THREADED` supports callers that need a sentinel pwork object without a control. Inline `xfs_pwork_ctl_want_abort` and `xfs_pwork_want_abort` report whether an error has been recorded.

Control flow: Callers embed `struct xfs_pwork`, initialize a control object, queue embedded work, check abort helpers from callbacks, poll or destroy when done, and consume the returned error.

State and persistence behavior: Header state is transient and memory-only. Error propagation is cooperative and non-atomic beyond simple integer storage; it assumes the workqueue use pattern tolerates first-writer wins without strict ordering.

Dependencies and integration points: Depends on Linux workqueues, waitqueues, and atomics. Used by XFS parallel scans and mount-time work that wants a common kernel-side analogue to xfsprogs workqueues.

Risks: Work item lifetime is caller-owned; freeing containers before workqueue drain is unsafe. The single-threaded sentinel has `.pctl = NULL`, so helpers must tolerate NULL only where intended. Callback implementations must poll abort helpers or work continues after failures.

Test signals: Compile all users with sparse and lockdep; exercise queued and sentinel paths; verify callbacks that detect abort exit promptly and that callers always destroy initialized controls.
