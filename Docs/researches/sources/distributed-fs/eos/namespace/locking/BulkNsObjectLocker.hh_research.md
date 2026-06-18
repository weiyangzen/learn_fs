# sources/distributed-fs/eos/namespace/locking/BulkNsObjectLocker.hh

Purpose: implements bulk RAII locking for multiple namespace metadata objects while imposing deterministic lock ordering to reduce deadlock risk.

Important APIs/types/functions: `BulkNsObjectLocker<TryLockerType>` accepts objects via `add` and acquires them with `lockAll`. Its nested `LocksVector` owns `std::unique_ptr<TryLockerType>` entries and destroys them in reverse insertion order. `BulkMultiNsObjectLocker<ContainerTryLockerType, FileTryLockerType>` locks container and file sets together, returning nested `Locks` that releases files before containers.

Control flow: single-type bulk locking stores objects in a `std::map` keyed by metadata identifier, so `lockAll` tries locks in ascending id order. If any try-lock fails, callers release accumulated locks and retry until all are held. Multi-locking first tries all containers, then all files; on file failure it releases file locks then container locks and retries with exponential backoff from 10 microseconds to 10 milliseconds.

State and persistence: in-memory only. The locker stores object shared pointers until locking; returned `LocksVector`/`Locks` own the active lock wrappers.

Dependencies and integration: depends on `IContainerMD`, `IFileMD`, and `MDLocking.hh` lock typedefs. It composes with `NSObjectMDTryLock` and the thread-local reentrant tracking in `LockableNSObject.hh`. Used by hierarchical namespace operations that need consistent multi-object locking.

Risks: retry loops can spin indefinitely if another thread continuously holds conflicting locks. Identifier ordering prevents many but not all logical deadlocks when callers mix bulk and non-bulk locking. Duplicate ids collapse in the map, so callers should not expect repeated locks. Move assignment for `Locks` lacks an explicit return statement, which is a C++ correctness warning/risk if used.

Test signals: targeted by `BulkNsObjectLocker` and `BulkNsObjectLockerTryLock` tests in `sources/distributed-fs/eos/namespace/ns_quarkdb/tests/HierarchicalViewTest.cc`, with mock metadata types in `MockContainerMD.hh`.
