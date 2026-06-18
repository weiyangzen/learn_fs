# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RemoveNodeMsgEx.c

## Research
`RemoveNodeMsgEx.c` implements remove-node message serialization, deserialization, and incoming processing. Payload fields are node type, node numeric ID, and ack ID. On receive, it logs debug details, deletes metadata or storage nodes from the corresponding `NodeStoreEx`, warns for invalid node types, and sends either an ack response or a `RemoveNodeRespMsg` fallback response.

Control flow branches by node type and by whether `MsgHelperAck_respondToAckRequest` handled the response. State changes remove nodes from app node stores, affecting future routing and connection use. Dependencies include `App`, `NodeStoreEx`, `DatagramListener`, `Socket`, `MsgHelperAck`, `RemoveNodeRespMsg`, and serialization helpers. Risks are deleting active nodes while operations are in flight, invalid node-type handling, fallback response serialization buffer size, and no support for management/client node deletion here. Test signals are management remove notifications removing nodes from stores, ack behavior, fallback response send path, and invalid-type logging without crashes.
