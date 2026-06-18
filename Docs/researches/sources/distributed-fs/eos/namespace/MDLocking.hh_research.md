## sources/distributed-fs/eos/namespace/MDLocking.hh

Purpose: Centralizes type aliases and factories for locking namespace file/container metadata objects, including individual and bulk locks.

Important APIs and types: exposes `ContainerReadLock`, `ContainerWriteLock`, `FileReadLock`, `FileWriteLock`, pointer aliases, bulk file/container locks, bulk mixed metadata locks, factory functions, and `FileOrContainerMDLocked` holder types.

Control flow: header declares type structure; implementation constructs locks. Bulk aliases integrate with try-lockers and multi-object lockers to avoid ad hoc locking in callers.

State and persistence: no persistence. Lock objects manage runtime access to metadata object mutexes exposed by `LockableNSObjMD`.

Dependencies and integration: depends on namespace macros, `LockableNSObject.hh`, raw pointer wrappers, `NSObjectLocker`, and metadata interfaces. It is included by interfaces and MGM xattr code.

Risks: aliases use raw pointer wrappers rather than shared ownership, so object lifetime remains external. Misordered manual locking can still deadlock; comments in `IView` warn about parent-container/file order. Bulk lock behavior should be preferred for multi-object operations.

Test signals: deadlock/regression tests for file/container order, bulk lock conflict tests, and static compile coverage where both `shared_ptr` and raw pointer usages are expected.
