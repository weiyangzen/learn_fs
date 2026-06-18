<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/RWLock.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/RWLock.h

Purpose: Wraps `pthread_rwlock_t` with optional deadlock-debug tracking.

Important APIs/types: `RWLock` initializes pthread RW attributes, exposes `writeLock`, `readLock`, timed/try variants, `unlock`, raw access, and debug-state queries. `RWLockLockType` records none/read/write state for debug builds.

Control flow/state/persistence: In normal builds it delegates to pthread RW locks. With `DEBUG_MUTEX_LOCKING`, it tracks lock state and owner thread to detect recursive or invalid usage and can log/throw on suspicious behavior.

Dependencies/integration: Used by quota stores, target maps, and shared state requiring read-heavy synchronization. Depends on `System`, `PThread`, and `RWLockException`.

Risks/test signals: Debug tracking is not a substitute for ownership in release builds. Tests should cover read/write mutual exclusion, try locks, timed reads, recursive locking behavior in debug mode, and unlock error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/RWLock.h -->
