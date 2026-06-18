# sources/distributed-fs/beegfs/client_module/source/components/AckManager.c

## Purpose
Implements the reliable TCP-based acknowledgment sender thread for metadata server acks queued by client operations.

## Important APIs and control flow
`AckManager_init` initializes the thread, app/config pointers, a 4096-byte vmalloc serialization buffer, queue mutex/condition, and pointer queue. `_AckManager_requestLoop` waits up to 2.5 seconds for entries and then processes the queue. `__AckManager_processAckQueue` locks the queue, references the target metadata node, serializes `AckMsgEx`, temporarily unlocks during socket acquisition/send, retries once, removes later queued acks for the same node if communication ultimately fails, frees the current entry, and advances safely with `PointerListIter_remove`. `AckManager_addAckToQueue` copies node ID and ack ID, appends an entry, and signals the condition.

## State, dependencies, integration
State is a thread, app/config pointers, static send buffer, mutex/condition, and `PointerList` of `AckQueueEntry`s. It depends on `NodeStoreEx`, `NodeConnPool`, `AckMsgEx`, `Socket_send_kernel`, and `StringTk`.

## Risks and test signals
Entries are dropped after send failure to avoid blocking later acks indefinitely. Queue uninit frees pending entries but assumes the thread is stopped. Tests should cover retry, missing node removal, serialization failure, concurrent enqueue while processing, and queue-size locking.
