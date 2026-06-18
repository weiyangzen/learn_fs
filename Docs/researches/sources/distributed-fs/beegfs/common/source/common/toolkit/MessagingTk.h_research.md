<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MessagingTk.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/MessagingTk.h

Purpose: Declares the common BeeGFS RPC helper facade.

Important APIs/types: `MessagingTk` exposes request/response helpers for direct nodes, node wrappers, target wrappers, message receive buffers, and message serialization vectors. Private helpers handle lower-level communication and generic responses.

Control flow/state/persistence: Interface is stateless and static. Callers supply `RequestResponseArgs`, `RequestResponseNode`, or `RequestResponseTarget` structures to control routing and behavior.

Dependencies/integration: Includes node, socket, message, target state, and messaging argument types. Used across storage, metadata, management, fsck, and ctl paths.

Risks/test signals: Callers must initialize argument structs correctly, especially `rrArgs->node` ownership/nullness. Integration tests should exercise node and target paths with mocked stores and sockets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/MessagingTk.h -->
