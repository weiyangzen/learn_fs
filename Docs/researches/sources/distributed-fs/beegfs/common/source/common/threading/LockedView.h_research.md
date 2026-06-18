<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/LockedView.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/LockedView.h

Purpose: Provides a small RAII wrapper for accessing a value protected by `std::mutex`.

Important APIs/types: `LockedView<T>` owns a `std::unique_lock<std::mutex>` and a raw pointer to `T`, exposing pointer-like operators and access to the unique lock. `MutexProtected<T>` stores a value and mutex and returns `lockedView()`.

Control flow/state/persistence: Lock acquisition happens in the `LockedView` constructor and is released by `unique_lock` destruction. No persistence.

Dependencies/integration: Uses standard C++ mutex types, distinct from BeeGFS pthread `Mutex`. Useful for new C++ code needing scoped access to state.

Risks/test signals: `LockedView` stores a raw pointer to state owned by `MutexProtected`; views must not outlive the owner. Tests should cover move behavior, const/non-const access expectations, and mutation under lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/LockedView.h -->
