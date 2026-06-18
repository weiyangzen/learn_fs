## sources/distributed-fs/beegfs/storage/source/net/message/nodes/RemoveNodeMsgEx.cpp

### Purpose
`RemoveNodeMsgEx.cpp` handles requests to remove a node from the storage daemon's runtime node store. The implementation only acts on storage nodes.

### Important APIs, Types, And Functions
`processIncoming()` logs the numeric node ID, references and deletes the node from `StorageNodes` when `getNodeType() == NODETYPE_Storage`, logs cluster node counts on success, acknowledges or sends `RemoveNodeRespMsg(0)`, and updates `StorageOpCounter_REMOVENODE`.

### Control Flow, State, And Persistence
Runtime cluster membership in `NodeStoreServers` is mutated. Non-storage node types are effectively acknowledged without store deletion.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on storage node store, common remove response, acknowledgement behavior, and op stats. Risks include dereferencing `node` in the success log if `referenceNode()` failed but `deleteNode()` returned true, and ignoring meta/mgmt removals. Tests should cover storage deletion success/failure, non-storage request, ack versus response mode, and op stats.
