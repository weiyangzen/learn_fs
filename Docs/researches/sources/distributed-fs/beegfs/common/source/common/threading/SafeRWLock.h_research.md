<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/SafeRWLock.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/SafeRWLock.h

Purpose: Stack-oriented wrapper around `RWLock` intended to catch forgotten unlocks in debug builds.

Important APIs/types: `SafeRWLock` can lock on construction or later via `lock`, and exposes `unlock`, `tryLock`, `timedReadLock`, and debug logging. `SafeRWLockType` selects read or write mode.

Control flow/state/persistence: In debug builds it tracks a `locked` flag and logs misuse, unlocking in the destructor if still locked. In release builds the destructor does not unlock, so callers must still call `unlock` explicitly.

Dependencies/integration: Used in older BeeGFS code where explicit unlocks are common, including quota stores.

Risks/test signals: Unlike typical RAII locks, release builds do not auto-unlock. Tests and code review should verify every path calls `unlock`, and debug builds should cover misuse logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/SafeRWLock.h -->
