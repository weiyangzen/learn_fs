# sources/distributed-fs/beegfs/client_module/source/common/net/sock/ibv/IBVSocket.c

Purpose: Implements BeeGFS RDMA transport over Linux RDMA CM and InfiniBand verbs, including connection management, queue pairs, completion queues, flow control, send/receive, memory registration, and event handling.

Important APIs/types/functions: Public entry points include `IBVSocket_init`, `uninit`, `rdmaDevicesExist`, `connectByIP`, `bindToAddr`, `listen`, `shutdown`, `recvT`, `send`, `checkConnection`, timeout/TOS/failure-status setters, `getDevice`, and `registerMr`. Internal helpers create CM IDs, communication contexts, destination private data, CQs/QPs, post send/recv work requests, wait for completion events, enforce flow control, and handle RDMA CM/CQ/QP callbacks.

Control flow: Connect resolves address/route, creates context/QP/CQs/buffers, exchanges private data, transitions to established state, posts receives, then data path alternates posted receives/sends with completion handling and flow-control counters. Shutdown/disconnect tears down CM and verbs resources.

State and persistence behavior: Maintains CM ID, connection state, timeout config, completion counters, wait queues, QP/CQ/PD/MR objects, send/recv buffers, incomplete receive/send trackers, and NIC stats pointer. All state is kernel-memory lifetime only.

Dependencies and integration points: Integrates RDMA CM, ib verbs, BeeGFS `IBVBuffer`, `IpAddress`, `Time`, `NicAddressStats`, `RDMASocket`, and RDMA-capable connection pools.

Risks: This is concurrency- and hardware-sensitive code. Event ordering, timeout handling, stale connection rejection, flow-control counters, CQ notification arming, DMA key mode, and resource cleanup can cause hangs, leaks, or data corruption if changed casually.

Test signals: RDMA hardware/integration tests for connect/listen, disconnect races, timeout paths, flow-control exhaustion, partial receives, nonblocking send completion, MR registration, and RDMA-disabled fallback builds.
