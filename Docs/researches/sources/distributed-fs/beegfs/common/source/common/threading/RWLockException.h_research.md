<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/RWLockException.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/RWLockException.h

Purpose: Defines the named exception for reader/writer lock failures.

Important APIs/types: `RWLockException` derives from `SynchronizationException`.

Control flow/state/persistence: Exception-only header with inherited message behavior.

Dependencies/integration: Thrown by `RWLock` initialization and lock operations.

Risks/test signals: Tests should verify catch-by-base compatibility and stable error messages for lock initialization failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/RWLockException.h -->
