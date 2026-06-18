<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/SynchronizationException.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/SynchronizationException.h

Purpose: Defines the common base exception for synchronization primitives.

Important APIs/types: `SynchronizationException` derives from `NamedException` and supplies the synchronization exception name.

Control flow/state/persistence: Exception construction delegates to `NamedException`; no other behavior.

Dependencies/integration: Base class for mutex, condition, pthread, and RW-lock exceptions.

Risks/test signals: Catch hierarchy stability matters for callers that handle all synchronization errors together. Tests should validate message/name behavior through base catches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/SynchronizationException.h -->
