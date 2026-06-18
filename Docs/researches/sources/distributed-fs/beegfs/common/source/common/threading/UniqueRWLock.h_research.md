<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/UniqueRWLock.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/UniqueRWLock.h

Purpose: Modern RAII/move-only wrapper for `RWLock`.

Important APIs/types: `UniqueRWLock` can be empty or constructed with a lock and mode, unlocks in its destructor when owned, supports move construction/assignment, `unlock`, `lock`, and `swap`.

Control flow/state/persistence: Unlike `SafeRWLock`, it always auto-unlocks when `locked` is true. The default constructor leaves `rwlock` null; callers must associate a lock before calling `lock`.

Dependencies/integration: Depends on `RWLock` and `SafeRWLockType`. Useful for exception-safe lock ownership in newer code.

Risks/test signals: Calling `lock` or `unlock` on a default/null instance will dereference null. Tests should cover move transfer, destructor unlock, manual unlock, and null-state misuse prevention in callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/UniqueRWLock.h -->
