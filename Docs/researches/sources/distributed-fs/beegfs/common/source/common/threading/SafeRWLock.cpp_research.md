<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/SafeRWLock.cpp -->
## sources/distributed-fs/beegfs/common/source/common/threading/SafeRWLock.cpp

Purpose: Implements debug logging helpers for `SafeRWLock` misuse.

Important APIs/functions: `errRWLockStillLocked`, `errRWLockAlreadyUnlocked`, and `errRWLockAlreadyLocked` log error messages through `LogContext("SafeRWLock")`.

Control flow/state/persistence: No locking occurs here; these helpers are invoked from `SafeRWLock` when `DEBUG_MUTEX_LOCKING` detects misuse.

Dependencies/integration: Depends on `SafeRWLock.h` and BeeGFS logging. Supports lock debugging in quota and other shared-state code.

Risks/test signals: In release builds most `SafeRWLock` misuse tracking is disabled. Tests with debug locking enabled should assert warnings fire for double unlock, double lock, and destructor-with-lock cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/SafeRWLock.cpp -->
