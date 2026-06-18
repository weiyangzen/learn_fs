<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/AcknowledgmentStore.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/AcknowledgmentStore.cpp

Purpose: Implements wait/notify tracking for string-identified acknowledgments.

Important APIs/functions: `registerWaitAcks` registers pending ack IDs and immediately separates already received acks. `unregisterWaitAcks` removes waiter entries. `receivedAck` marks or stores an ack and signals waiters. `waitForAckCompletion` waits until a pending map becomes empty or times out.

Control flow/state/persistence: The global `ackStore` map is protected by `mutex`; each waiter has its own `waitAcksMutex` and `Condition`. Acks can arrive before or after registration. State is memory-only.

Dependencies/integration: Uses BeeGFS `Mutex`, `Condition`, and `WaitAckMap` structures. Used by messaging or management workflows that need asynchronous acknowledgment completion.

Risks/test signals: Lock ordering between store mutex and waiter mutex must remain stable. Tests should cover pre-received acks, partial completion, timeout, unregister during wait, duplicate ack IDs, and concurrent receivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/AcknowledgmentStore.cpp -->
