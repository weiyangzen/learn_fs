<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/Makefile -->
# sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/Makefile

Purpose: Defines the kernel build composition for the RPC/RDMA transport module `rpcrdma.o`.

Important APIs/types/functions: The Makefile adds `rpcrdma.o` when `CONFIG_SUNRPC_XPRT_RDMA` is enabled. `rpcrdma-y` links client transport, RPC/RDMA protocol, verbs, FRWR operations, IB client notifications, server RDMA transport/send/receive/RW/pcl code, and module initialization. `rpcrdma-$(CONFIG_SUNRPC_BACKCHANNEL)` conditionally adds `backchannel.o`.

Control flow: Kbuild compiles the listed objects into one module/built-in object according to kernel config. Backchannel support is included only when `CONFIG_SUNRPC_BACKCHANNEL` is set.

State and persistence behavior: No runtime state. Build-time configuration controls which object code is present.

Dependencies and integration points: Integrates xprtrdma with SUNRPC client/server RDMA support and the kernel Kbuild system. The object list must match symbols referenced by `module.c`, client/server RDMA paths, and optional backchannel ops.

Risks: Missing an object from `rpcrdma-y` produces link failures or feature omissions. Backchannel symbols must remain guarded consistently with `CONFIG_SUNRPC_BACKCHANNEL`. Object ordering is usually not semantically important but module init/exit symbols must be included exactly once.

Test signals: Build with `CONFIG_SUNRPC_XPRT_RDMA=m/y`, with and without `CONFIG_SUNRPC_BACKCHANNEL`, and run module load/unload or built-in boot smoke tests to catch unresolved symbols and init ordering issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/Makefile -->
