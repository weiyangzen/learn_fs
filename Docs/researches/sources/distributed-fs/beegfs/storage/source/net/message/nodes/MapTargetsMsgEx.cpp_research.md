## sources/distributed-fs/beegfs/storage/source/net/message/nodes/MapTargetsMsgEx.cpp

### Purpose
`MapTargetsMsgEx.cpp` handles target-to-node mapping updates from management. It maps one or more storage target IDs to a storage node and storage pool.

### Important APIs, Types, And Functions
`processIncoming()` retrieves the requested node ID and target/pool map, calls `TargetMapper::mapTarget()` for each target, stores each `FhgfsOpsErr` in a results map, logs new mappings with non-success results when applicable, and either acknowledges or sends `MapTargetsRespMsg`.

### Control Flow, State, And Persistence
The target mapper is mutated for each requested target. The response path depends on `acknowledge(ctx)`: if the message was not acknowledged, a detailed response is sent.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `TargetMapper`, storage node store, map-target response messages, and acknowledgement behavior. Risks include partial success across targets, logging condition that may be counterintuitive, and caller handling of ack versus response mode. Tests should cover single and multi-target mapping, pool ID propagation, partial failures, ackable requests, and result-map contents.
