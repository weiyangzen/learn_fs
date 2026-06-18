<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/sysfs.h -->
# sources/distributed-fs/ceph-client/net/sunrpc/sysfs.h

Purpose: Declares the SUNRPC sysfs object wrappers and lifecycle hooks used by client transport and multipath code to publish live RPC client/xprt state under sysfs.

Important APIs/types/functions: `struct rpc_sysfs_xprt_switch` embeds a `kobject` and tracks `struct net *`, `struct rpc_xprt_switch *`, and an associated `struct rpc_xprt *`. `struct rpc_sysfs_xprt` embeds a `kobject` and links an individual `rpc_xprt` to its switch. Public functions cover global sysfs initialization/exit and setup/destroy for clients, switches, and xprts.

Control flow: `xprt_switch_alloc()` calls `rpc_sysfs_xprt_switch_setup()` and `rpc_sysfs_xprt_setup()`. `xprt_free()` calls `rpc_sysfs_xprt_destroy()`. RPC client creation/destruction calls the client setup/destroy APIs. The header does not implement logic; it defines the cross-file contract consumed by `sysfs.c`, `xprt.c`, and `xprtmultipath.c`.

State and persistence behavior: The declared structs are transient kobject containers with raw back-pointers to live RPC objects. Lifetime is coordinated externally by kobject reference counts and the RPC transport/switch teardown paths. No persistent state is defined here.

Dependencies and integration points: Requires SUNRPC client, xprt, xprt switch, kobject, and network namespace types from including translation units. It is the narrow include used to avoid exposing `sysfs.c` internals.

Risks: Because the header exposes back-pointer fields, users must preserve lifetime ordering and must not dereference after destroy. There are no stubs here for disabled sysfs configurations, so build coverage depends on the broader SUNRPC build selecting this file consistently.

Test signals: Compile-time checks that all setup/destroy declarations match `sysfs.c`, and runtime tests that xprt/switch/client allocation and free paths call the matching setup/destroy hooks exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/sysfs.h -->
