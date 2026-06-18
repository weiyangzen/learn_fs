# sources/distributed-fs/ceph-client/net/sunrpc/Kconfig

Purpose: Defines SUNRPC, RPC security, backchannel, swap, debugging, test, and RPC-over-RDMA configuration symbols used by NFS/RPC subsystems.

Important APIs/types/functions: `SUNRPC` and `SUNRPC_GSS` are tristate foundations gated by `MULTIUSER`. `RPCSEC_GSS_KRB5` selects Kerberos GSS support and crypto dependencies. AES-SHA1, Camellia-CMAC, and AES-SHA2 enctype symbols add crypto-specific support. `RPCSEC_GSS_KRB5_KUNIT_TEST` enables KUnit tests. `SUNRPC_DEBUG` and `SUNRPC_DEBUG_TRACE` expose debug controls. `SUNRPC_XPRT_RDMA` builds RPC-over-RDMA and selects `SG_POOL`.

Control flow: Kconfig dependency resolution controls whether SUNRPC core, auth_gss, Kerberos mechanisms, debug objects, proc/sysctl support, and RDMA transport objects are built. Defaults enable common Kerberos AES-SHA1 and RDMA when base requirements are available.

State and persistence behavior: No runtime state is stored here. Choices persist in the kernel configuration and determine which code and modules are built.

Dependencies and integration points: Integrates with NFS client/server code, crypto subsystem, OID registry, KUnit, tracing, debugfs/sysctl, InfiniBand address translation, and `net/sunrpc/Makefile`.

Risks and test signals: Risks include unmet crypto dependencies disabling expected security mechanisms, debug trace option flooding trace buffers, and RDMA defaults on systems without RDMA. Test representative configs: SUNRPC built-in/module, Kerberos with each enctype, debug on/off, KUnit, and RPC-over-RDMA enabled/disabled.
