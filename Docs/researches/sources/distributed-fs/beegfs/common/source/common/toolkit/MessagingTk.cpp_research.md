<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MessagingTk.cpp -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/MessagingTk.cpp

Purpose: Implements common request/response RPC helpers for BeeGFS nodes and targets.

Important APIs/functions: `requestResponse` wraps `requestResponseComm` with one retry on communication failure. `requestResponseNode` resolves nodes, mirror groups, and target states before sending. `requestResponseTarget` maps target IDs to owner nodes and sets message header target ID. `recvMsgBuf` receives bounded messages. `createMsgVec` serializes messages. `handleGenericResponse` maps generic control responses to operation errors.

Control flow/state/persistence: RPC flow acquires a stream socket from a node pool, serializes/sends, optionally sends extra data, receives/deserializes a response, releases reusable sockets on success, and invalidates sockets on failure. It does not persist state.

Dependencies/integration: Central integration point for `Node`, `NodeConnPool`, target mappers/states, mirror buddy mappers, net message factory, sockets, `PThread` app config, and logging.

Risks/test signals: Message size cap is 4 MiB; timeout can be environment-overridden. Tests should cover retries, wrong response type, generic TRYAGAIN/INDIRECTCOMMERR, offline target skipping, mirror mapping, socket invalidation, extra-data failures, and oversized messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MessagingTk.cpp -->
