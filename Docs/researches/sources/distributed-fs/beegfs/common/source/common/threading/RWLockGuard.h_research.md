<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/RWLockGuard.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/RWLockGuard.h

Purpose: Provides a small RAII guard for `RWLock`.

Important APIs/types: `RWLockGuard` takes an `RWLock&` and `SafeRWLockType`, locks read or write in the constructor, and unlocks in the destructor.

Control flow/state/persistence: Scope lifetime controls lock ownership. No move/copy controls are visible, so intended usage is stack-only.

Dependencies/integration: Used by newer code such as `ExceededQuotaPerTarget` for concise read/write locking.

Risks/test signals: Copying a guard would double-unlock if not prevented by compiler behavior; usage should be audited. Tests should cover read/write acquisition and exception safety on early returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/RWLockGuard.h -->
