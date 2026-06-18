# sources/distributed-fs/ceph-client/include/linux/sunrpc/rdma_rn.h

Purpose: declares a small RPC/RDMA removal-notification API used to detect RDMA device/resource removal.

Important APIs and types: `struct rpcrdma_notification` stores an `rn_done` callback and provider index. APIs include `rpcrdma_rn_register()`, `rpcrdma_rn_unregister()`, `rpcrdma_ib_client_register()`, and `rpcrdma_ib_client_unregister()`.

Control flow: RPC/RDMA code registers a notification object against an `ib_device`; when the RDMA core reports removal, the callback is invoked so transports can tear down or mark resources unavailable.

State and persistence: notification registration state is runtime state associated with RDMA devices and RPC/RDMA transports.

Dependencies and integration points: depends on RDMA `ib_verbs.h` and is used by client/server RPC/RDMA transport code, including `svc_rdma.h`.

Risks and test signals: risks include callback after transport free, unregister races, missing device removal events, and index reuse confusion. Test with RDMA device hot-remove, module unload, failed registration, and active RPC/RDMA traffic during teardown.
