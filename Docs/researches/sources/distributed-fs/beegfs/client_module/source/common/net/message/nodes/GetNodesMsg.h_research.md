# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetNodesMsg.h

## Research
`GetNodesMsg.h` declares the request used to ask management for nodes of a given type. It wraps `SimpleIntMsg` with `NETMSGTYPE_GetNodes`; `GetNodesMsg_initFromValue` stores a `NODETYPE_*` integer.

Control flow is inline initialization only. State is a single integer payload. Dependencies are `SimpleIntMsg.h`. Integration points are node discovery during startup, heartbeat handling, and syncer refreshes that need metadata, storage, management, or client node lists. Risks are invalid node-type values and relying on callers to choose the correct response parser. Test signals are successful `GetNodesRespMsg` parsing, root metadata owner discovery, and node-store population after management queries.
