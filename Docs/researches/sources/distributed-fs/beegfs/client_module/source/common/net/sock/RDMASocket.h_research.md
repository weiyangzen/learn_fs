# sources/distributed-fs/beegfs/client_module/source/common/net/sock/RDMASocket.h

Purpose: Declares the RDMA socket wrapper that embeds `PooledSocket` plus `IBVSocket` and exposes it through the generic BeeGFS socket API.

Important APIs/types/functions: Construction/init/uninit, RDMA device discovery, virtual socket operations, polling, `RDMASocket_setBuffers`, timeout/TOS/failure-status setters, device/rkey getters, `RDMASocket_isRkeyGlobal`, key-type conversion, and memory-registration wrapper.

Control flow: Callers tune unconnected sockets with buffer count/size/fragment/key type, then connect through the socket vtable. Inline getters forward to `IBVSocket`.

State and persistence behavior: Stores `IBVCommConfig` and embedded IBV state for one RDMA connection/listener. No persistence beyond process memory.

Dependencies and integration points: Used by NIC RDMA probing, connection pools, and RDMA read/write messages. Depends on BeeGFS config and RDMA key-type policy.

Risks: Settings only affect unconnected sockets; late changes may be ignored. Global/unsafe DMA key modes carry security/isolation tradeoffs compared with registered memory keys.

Test signals: Key-type mapping, buffer config propagation, device/rkey getters, and both RDMA-enabled and disabled build variants.
