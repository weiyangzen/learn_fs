# sources/distributed-fs/coda/coda-src/vol/lockqueue.h

Purpose: declares the volume lock queue facility and maps volume lock constants onto Coda/LWP lock levels.

Important APIs/classes: `VOL_NO_LOCK`, `VOL_SHARED_LOCK`, and `VOL_EXCL_LOCK`; `ForceUnlockVol`; `lqman` queue manager; `lq_iterator`; and private `lqent` queue entries. `lqent` grants friendship to volume object helpers and RPC lock/unlock entry points, allowing those paths to manipulate its private volume id, timestamp, and dequeue flag.

Control flow/state: consumers create an `lqman`, add `lqent` objects for lock holders, search or mark entries during unlock, and print queue contents. `lqman::func` is private and invoked through `LQman_init`.

Dependencies/integration: depends on LWP locks, RPC2, `vice.h`, and `dlist`. The lock queue is an integration point between file-server RPC lock APIs and lower-level volume object locking. Risks are friend-heavy encapsulation, global `LockQueueMan`, and reliance on C-style lock constants. Test signals: compile RPC lock/unlock users, queue print output, timeout manager behavior, and lock-level mapping in `GetVolObj`/`PutVolObj`.
