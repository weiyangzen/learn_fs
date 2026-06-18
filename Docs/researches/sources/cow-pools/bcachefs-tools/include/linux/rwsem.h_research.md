# File Research: sources/cow-pools/bcachefs-tools/include/linux/rwsem.h

Provides a userspace `struct rw_semaphore` backed by `pthread_rwlock_t`. It implements `init_rwsem`, read/write lock, trylock, interruptible/killable read variants that always return success after blocking, and cleanup guard macros for scoped locking.

This is a compatibility shim, not a signal-aware kernel rwsem. Interruptible/killable semantics are collapsed to non-interruptible pthread locking.
