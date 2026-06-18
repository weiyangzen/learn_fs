# sources/distributed-fs/beegfs/client_module/source/common/net/sock/ibv/IBVSocket.h

Purpose: Declares the BeeGFS RDMA socket API, connection states, timeout/config structures, communication context, destination metadata, and internal helpers used by `IBVSocket.c`.

Important APIs/types/functions: Public APIs cover init/uninit, device discovery, connect/bind/listen/shutdown, send/recv, connection checks, polling, timeouts/TOS/failure status, NIC stats, rkey/device getters, and MR registration. Under `BEEGFS_RDMA`, it declares `IBVCommConfig`, `IBVTimeoutConfig`, `IBVCommContext`, incomplete send/recv state, connection states, CM/CQ handlers, posting and wait helpers, and private-data constants.

Control flow: The header defines the state machine names from unconnected through address/route resolved, established, failed, and rejected-stale, which the C file drives through RDMA CM events and completion handling.

State and persistence behavior: Struct declarations show all per-connection kernel resources and counters; none are durable.

Dependencies and integration points: Shared by `RDMASocket`, `IBVBuffer`, NIC probing, and RDMA build guards.

Risks: Internal structs are tightly coupled to verbs lifetimes and callback synchronization. Build guards mean non-RDMA consumers must avoid depending on RDMA-only fields.

Test signals: Compile both RDMA and non-RDMA builds, validate state transitions, context teardown, and public wrapper behavior.
