# sources/distributed-fs/ceph-client/net/sunrpc/Makefile

Purpose: Defines the SUNRPC kernel objects and conditional subdirectories built by Kbuild.

Important APIs/types/functions: `obj-$(CONFIG_SUNRPC) += sunrpc.o`, `obj-$(CONFIG_SUNRPC_GSS) += auth_gss/`, and `obj-$(CONFIG_SUNRPC_XPRT_RDMA) += xprtrdma/`. The `sunrpc-y` composite includes client, transport, socket, scheduler, auth, service, address, rpcbind, timer, XDR, cache, pipe, sysfs, service transport, and multipath objects. Conditional additions include debugfs, backchannel, proc stats, and sysctl.

Control flow: Kbuild links the listed objects into `sunrpc.o` when SUNRPC is enabled and descends into selected subdirectories for GSS and RDMA support.

State and persistence behavior: No runtime state. It controls build composition and module contents.

Dependencies and integration points: Mirrors symbols from `net/sunrpc/Kconfig` and wires `addr.o` into the core SUNRPC object, making the address conversion helpers available to RPC clients/servers.

Risks and test signals: Risks include missing object dependencies when Kconfig symbols change, conditional objects not matching feature code, and module link failures. Test allmodconfig/allyesconfig plus minimal SUNRPC builds, debug/proc/sysctl toggles, and RDMA/GSS module combinations.
