<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/AcknowledgmentStore.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/AcknowledgmentStore.h

Purpose: Declares the acknowledgment wait-store data model.

Important APIs/types: `WaitAckNotification` owns a mutex and condition. `WaitAck` stores an ack ID. `AckStoreEntry` links an ID to a waiter map and notifier. `AcknowledgmentStore` exposes register, unregister, receive, and wait methods over `WaitAckMap`.

Control flow/state/persistence: Data structures are pointer-linked rather than owning waiter maps, so caller lifetime is important. Persistence is not involved.

Dependencies/integration: Includes BeeGFS mutex/condition wrappers and common map aliases. Used around RPC/control workflows that wait for distributed acknowledgments.

Risks/test signals: Raw pointers to waiter-owned maps/notifiers can dangle if unregister is missed. Tests should verify lifecycle and concurrent receipt before/after unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/AcknowledgmentStore.h -->
