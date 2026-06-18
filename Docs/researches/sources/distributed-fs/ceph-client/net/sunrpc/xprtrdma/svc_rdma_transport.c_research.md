# sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/svc_rdma_transport.c

## Purpose
`svc_rdma_transport.c` implements the server-side RPC/RDMA transport class: listener setup, RDMA CM event handling, connection acceptance, queue-pair and resource sizing, transport detachment/free, and write-space signaling. It bridges the generic SunRPC service transport interface with RDMA CM and verbs resources.

## Important APIs, types, and functions
The central exported integration object is `svc_rdma_class`, whose operations are implemented by this file and by the receive/send modules. `svc_rdma_create()` creates listener transports; `svc_rdma_accept()` accepts RDMA CM child connections and initializes `struct svcxprt_rdma`; `svc_rdma_detach()` and `svc_rdma_free()` tear down transports. `qp_event_handler()` and RDMA CM event callbacks translate provider events into service transport state. `svc_rdma_has_wspace()` reports write-space availability from SQ waiters. `svc_rdma_kill_temp_xprt()` is present as the class hook but is empty in this snapshot.

## Control flow
Listener creation binds an RDMA CM ID to the requested address and starts listening. CM connection requests create temporary transport state, negotiate private data and limits, allocate protection domain, CQs, QP, receive/send/RW context pools, and post initial Receives. `svc_rdma_accept()` promotes a queued temporary connection to a service xprt, copies peer/local addresses, initializes credit and SQ accounting, accepts the CM connection, and hands it to the SunRPC service layer. Disconnect, device removal, QP fatal, or service close paths mark the xprt closing, disconnect RDMA CM, flush receive queues, destroy contexts, and release references.

## State and persistence behavior
All state is runtime transport state: RDMA CM IDs, QPs, CQs, PDs, queue depths, credit counts, flags, locks, wait queues, and context pools. Temporary transports exist between CM request and service accept. Established transports track pending receives, send queue availability, registered context caches, and backchannel association. No disk persistence is involved.

## Dependencies and integration points
This file depends on RDMA CM, IB verbs, SunRPC `svc_xprt` lifecycle helpers, server tunables from `svc_rdma.c`, receive setup from `svc_rdma_recvfrom.c`, send context cleanup from `svc_rdma_sendto.c`, and RW context cleanup from `svc_rdma_rw.c`. It is the file that makes the other `svc_rdma_*` data-path operations reachable through the service transport class.

## Risks and edge cases
Connection negotiation must cap advertised credits and inline sizes to device and sysctl limits. Resource setup failures need precise unwind so QP/CQ/PD/CM IDs and context pools do not leak. Accept races with disconnect and device removal are high risk because temporary transports can be killed before promotion. SQ depth and receive depth must leave headroom for backchannel and batching. `svc_rdma_free()` must coordinate with completions and async work so no context is freed while provider callbacks can still run.

## Test signals
Coverage should include listener bind/listen failure, CM request rejection, accept success, private-data negotiation, low device limits, QP event errors, disconnect before accept, device removal notification, receive-post failure during setup, backchannel credit sizing, `svc_rdma_has_wspace()` under SQ pressure, and teardown with outstanding Read/Write/Send/Receive completions. Runtime evidence comes from transport class registration, RDMA CM traces, queue-depth counters, service xprt flags, and resource leak detectors.
