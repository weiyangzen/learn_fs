# sources/distributed-fs/beegfs/client_module/source/common/net/sock/RDMASocket.c

Purpose: Adapts the lower-level `IBVSocket` RDMA transport to the generic BeeGFS `Socket`/`PooledSocket` interface.

Important APIs/types/functions: `RDMASocket_init`, `_RDMASocket_uninit`, `RDMASocket_rdmaDevicesExist`, `_connectByIP`, `_bindToAddr`, `_listen`, `_shutdown`, `_shutdownAndRecvDisconnect`, `_recvT`, `_sendto`, and `RDMASocket_poll` delegate to `IBVSocket` while preserving socket peer/bound fields.

Control flow: Initialization sets RDMA defaults from client config and installs the RDMA `SocketOps`. Connect passes the configured buffer/key settings to `IBVSocket_connectByIP`; send ignores destination addresses because RDMA is connection-oriented.

State and persistence behavior: Owns an embedded `IBVSocket` and RDMA communication config for the socket lifetime. No durable persistence.

Dependencies and integration points: Bridges connection pools and message I/O to `IBVSocket`, `Config`, `SocketTk`, and `NicAddressStats`.

Risks: RDMA availability is compile/runtime dependent. The `RDMASocket_registerMr` inline in the header inverts the `IBVSocket_registerMr` return convention, so call sites must follow this wrapper’s semantics.

Test signals: RDMA-disabled builds, connection setup, send/receive delegation, config-derived buffers/timeouts, shutdown, and memory-registration paths.
