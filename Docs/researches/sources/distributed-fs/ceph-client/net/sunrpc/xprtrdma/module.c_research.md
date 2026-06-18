<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/module.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/module.c

Purpose: Provides `rpcrdma.ko` module metadata, tracepoint definition, initialization, and cleanup for the combined RPC/RDMA client and server transport module.

Important APIs/types/functions: Module metadata declares author, description, dual BSD/GPL license, and aliases `svcrdma`, `xprtrdma`, and `rpcrdma6`. `rpc_rdma_init()` registers the RDMA ib_client, initializes server-side RDMA, then initializes client xprt RDMA. `rpc_rdma_cleanup()` tears down client xprt RDMA, server RDMA, and the ib_client in reverse order. `CREATE_TRACE_POINTS` instantiates rpcrdma tracepoints.

Control flow: Module init first calls `rpcrdma_ib_client_register()`. If server RDMA init fails, it unregisters the ib_client. If client transport init fails, it cleans up server RDMA and unregisters the ib_client. Cleanup reverses successful initialization order: client transport cleanup, server cleanup, ib_client unregister.

State and persistence behavior: Module-global state is whatever the three subsystems allocate/register during init. No file-local mutable state beyond module registration exists. All state is expected to be released on module exit.

Dependencies and integration points: Integrates `xprt_rdma_cleanup/init()`, `svc_rdma_cleanup/init()`, `rpcrdma_ib_client_register/unregister()`, SUNRPC RDMA headers, and rpcrdma trace events. Kbuild includes this file in `rpcrdma.o`.

Risks: Initialization order matters: RDMA device notifications must exist before transport setup, and cleanup must stop transports before unregistering device callbacks. Any partial-init failure path must mirror cleanup precisely to avoid registered transports without an ib_client or leaked server/client resources. Tracepoint creation in this module means duplicate `CREATE_TRACE_POINTS` elsewhere would conflict.

Test signals: Build and load/unload `rpcrdma.ko`, inject failures in each init stage to verify rollback, confirm module aliases autoload expected transports, validate tracepoint availability, and run client/server RDMA smoke tests before and after module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/module.c -->
