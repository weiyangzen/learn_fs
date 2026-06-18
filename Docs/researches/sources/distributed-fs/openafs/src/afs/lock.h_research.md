# sources/distributed-fs/openafs/src/afs/lock.h

Purpose: defines OpenAFS kernel lock structures and fast inline lock operations used throughout the cache manager.

Important APIs/types: `struct afs_lock`/`afs_lock_t`/`afs_rwlock_t`, lock modes `READ_LOCK`, `WRITE_LOCK`, `SHARED_LOCK`, `BOOSTED_LOCK`, `EXCL_LOCKS`, and `MAX_LOCK_NUMBER`. Inline APIs include `ObtainReadLock`, `NBObtainReadLock`, `ObtainWriteLock`, `NBObtainWriteLock`, `ObtainSharedLock`, `NBObtainSharedLock`, `UpgradeSToWLock`, conversions from write/shared to weaker modes, release helpers, `LockWaiters`, `CheckLock`, and `WriteLocked`.

Control flow: fast paths update lock fields directly under the AFS global lock; contended paths call `Afs_Lock_Obtain`, `Afs_Lock_ReleaseR`, or `Afs_Lock_ReleaseW`. Shared locks are exclusive against other shared/write holders but allow readers; boosted locks upgrade shared to write once readers drain. Source indicators are recorded for write/shared/upgrade acquisitions.

State and persistence: lock state is in memory: waiting modes, exclusive mode, reader count, number waiting, timing/stat fields, last reader, writer, and source indicator.

Dependencies and integration points: requires `KERNEL`, platform-specific current-thread/process macros, `AFS_ASSERT_GLOCK`, `osi_Assert`, and optional ICL tracing. It underpins `afs_vcache.c`, `afs_volume.c`, disconnected queues, callback hashes, and most cache-manager shared structures.

Risks: all inline operations assume the AFS global lock is held. Incorrect release mode or missing conversion can violate assertions or deadlock. Duplicate source indicators reduce diagnostic value. Platform `MyPidxx` definitions are central to ownership assertions.

Test signals: contention tests for read/write/shared/upgrade modes, nonblocking failure paths, waiter wakeups, conversion behavior, GLOCK assertion failures in debug builds, and `findlocks -d` duplicate scans after new lock sites.
