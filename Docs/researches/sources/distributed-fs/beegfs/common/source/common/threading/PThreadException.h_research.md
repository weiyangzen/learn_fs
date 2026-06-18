<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/PThreadException.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/PThreadException.h

Purpose: Defines the base named exception for BeeGFS pthread wrapper failures.

Important APIs/types: `PThreadException` derives from `SynchronizationException`.

Control flow/state/persistence: Pure exception type with inherited message/name behavior.

Dependencies/integration: Used by `PThread`, `Barrier`, and derived create exceptions.

Risks/test signals: Verify exception names and `what()` content remain stable for log/error-reporting code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/PThreadException.h -->
