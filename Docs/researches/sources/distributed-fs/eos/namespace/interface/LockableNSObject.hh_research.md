# sources/distributed-fs/eos/namespace/interface/LockableNSObject.hh

Purpose: defines the lockable base for namespace metadata objects, providing read/write lock aliases, per-thread lock tracking, and reentrant-safe helper methods used by file and container metadata implementations.

Important APIs/types/functions: `MDWriteLock` and `MDReadLock` alias `std::unique_lock<std::shared_timed_mutex>` and `std::shared_lock<std::shared_timed_mutex>`. `MapLockTracker` plus thread-local `mThreadIdWriteLockMap` and `mThreadIdReadLockMap` track how many times the current thread has registered a lock for a metadata object address. `LockableNSObjMD` exposes protected `runWriteOp`, `runReadOp`, `lock`, `tryLock`, `registerLock`, `unregisterLock`, `isLocked`, and pure virtual `getMutex`.

Control flow: `runWriteOp` and `runReadOp` check the thread-local tracker before taking the object mutex, avoiding self-deadlock when a locked method calls another locked getter or setter. `lock` acquires only when the object is not already tracked for the requested access and then registers the lock. `tryLock` returns false only when the underlying try-lock fails and otherwise registers recursive ownership. A write lock is also registered as a read lock so reads inside write-locked sections do not attempt to reacquire the mutex.

State and persistence: no persistent state. The only state is thread-local recursion counters keyed by `std::uintptr_t(this)`, plus each derived object’s shared timed mutex.

Dependencies and integration: used by `NSObjectLocker.hh` and by metadata classes implementing `IFileMD` or `IContainerMD`, including `QuarkFileMD` and `QuarkContainerMD`. Depends on `Namespace.hh` and `MDException.hh` for EOS namespace/error conventions.

Risks: tracking by raw object address assumes object lifetime outlives registered locks and that all lock wrappers correctly unregister. Counter imbalance can cause later operations in the same thread to skip real locking. Write locks register in both maps, so unregister ordering must remain symmetric. `std::shared_timed_mutex` semantics do not permit upgrades, so calling write paths while only read-locked remains unsafe.

Test signals: exercised indirectly by QuarkDB metadata tests and specifically by locking-focused test fixtures using `MockContainerMD` plus `BulkNsObjectLocker` tests in `sources/distributed-fs/eos/namespace/ns_quarkdb/tests/HierarchicalViewTest.cc` and `OtherTests.cc`.
