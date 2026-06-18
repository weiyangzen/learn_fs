# sources/distributed-fs/eos/namespace/locking/NSObjectLocker.hh

Purpose: defines the RAII lock wrappers for individual namespace metadata objects, covering blocking and try-lock modes.

Important APIs/types/functions: `NSObjectMDBaseLock<ObjectMDPtr, LockType>` validates the pointer, constructs a deferred lock on `objectMDPtr->getMutex()`, and exposes `operator->` plus `getUnderlyingPtr`. `NSObjectMDLock` calls the object’s `lock` helper in the constructor and unregisters in the destructor. `NSObjectMDTryLock` calls `tryLock`, exposes `locked()`, and unregisters only when acquisition succeeded.

Control flow: construction throws `MDException(ENOENT)` for null metadata pointers. Successful wrappers delegate actual lock acquisition and recursive tracking to `LockableNSObjMD`. Destruction unregisters the lock tracker before the underlying `LockType` releases on its own destruction.

State and persistence: in-memory RAII state only: a metadata shared pointer and a lock object. The member order intentionally destroys the lock before the shared pointer to avoid metadata destruction while locking machinery may still be active.

Dependencies and integration: included by `MDLocking.hh` aliases for container/file read/write locks and try-locks. Integrates tightly with `LockableNSObject.hh`.

Risks: callers must check `locked()` for try locks before dereferencing for protected mutation. The wrappers rely on derived metadata objects implementing `getMutex`, `registerLock`, and `unregisterLock` consistently. Pointer lifetime and lock lifetime ordering is intentionally delicate.

Test signals: indirectly covered by metadata service operations and directly by bulk locking tests that instantiate try-lock wrappers.
