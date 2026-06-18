# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetNodesRespMsg.c

## Research
`GetNodesRespMsg.c` implements receive-only deserialization for node-list responses. Its ops install dummy serialization and parse a preprocessed raw node list, root metadata numeric ID, and `rootIsBuddyMirrored` boolean.

Control flow is sequential and stops on failed node-list, `NumNodeID`, or boolean parsing. State includes `rootNumID`, `rootIsBuddyMirrored`, and a `RawList` slice that is later materialized by `GetNodesRespMsg_parseNodeList`. Dependencies are `GetNodesRespMsg.h`, node-list serialization helpers, and `NumNodeID`. Integration points are management-node discovery and root-owner initialization. Risks include receive-buffer lifetime for `rawNodeList`, no release hook because parsing into `NodeList` is caller-managed, and dummy serialization misuse. Test signals are management responses with multiple nodes, root buddy-mirror flag propagation, and malformed list rejection.
