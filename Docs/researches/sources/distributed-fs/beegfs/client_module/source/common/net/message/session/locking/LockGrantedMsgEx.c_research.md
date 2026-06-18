# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/LockGrantedMsgEx.c

## Research
`LockGrantedMsgEx.c` implements receive-only handling for asynchronous lock grant notifications. The payload contains aligned lock ack ID, aligned ack ID, and granter node numeric ID. Processing records the lock ack in `AcknowledgmentStore`; if a waiter was registered, it sends an ack response and queues an ack through `AckManager` for the granter node.

Control flow intentionally sends acknowledgement only when a waiter still exists, simplifying interrupted lock waits. State changes occur in the acknowledgment store and ack manager queue. Dependencies include `App`, `AckManager`, `AcknowledgmentStore`, `MsgHelperAck`, `SocketTk`, and `NumNodeID`. Risks include lost grants if ack IDs mismatch, not acking after interrupted waits by design, receive-buffer string lifetime, and duplicate grant messages. Test signals are blocked lock waiters waking, ack queue entries for granter nodes, and no response when no waiter remains.
