<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/Mutex.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/Mutex.h

Purpose: Wraps `pthread_mutex_t` for BeeGFS synchronization.

Important APIs/types: `Mutex` initializes/destroys a pthread mutex and exposes `lock`, `tryLock`, `unlock`, and raw `getMutex` for condition waits.

Control flow/state/persistence: `lock` throws `MutexException` on pthread errors; `tryLock` returns false on busy/error; `unlock` delegates directly. The object is non-persistent and owns its pthread mutex.

Dependencies/integration: Used by `Condition`, quota stores, candidate queues, ack stores, and many older BeeGFS components.

Risks/test signals: Copying is not explicitly deleted here, so accidental copies would duplicate pthread state incorrectly if allowed by compiler rules. Tests should cover lock/unlock, try-lock contention, and error handling in debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/Mutex.h -->
