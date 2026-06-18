# sources/distributed-fs/ceph-client/include/linux/sunrpc/bc_xprt.h

Purpose: declares SUNRPC backchannel transport setup and request management used by protocols such as NFSv4.1 callbacks over an existing client connection.

Important APIs and types: when `CONFIG_SUNRPC_BACKCHANNEL` is enabled, APIs include `xprt_lookup_bc_request()`, `xprt_complete_bc_request()`, `xprt_init_bc_request()`, `xprt_free_bc_request()`, `xprt_setup_backchannel()`, `xprt_destroy_backchannel()`, `xprt_enqueue_bc_request()`, socket-specific `xprt_setup_bc()`, `xprt_destroy_bc()`, `xprt_free_bc_rqst()`, `xprt_bc_max_slots()`, and `xprt_svc_destroy_nullify_bc()`. Inline helpers check or set `sv_bc_enabled`.

Control flow: a transport allocates/prepares backchannel request slots, incoming callback replies are matched by XID, completed, and returned to the preallocation pool. Disabled builds compile to inert setup/destroy helpers.

State and persistence: state is held in `rpc_xprt`, `rpc_rqst`, and `svc_serv` backchannel fields; it is connection lifetime, not persistent.

Dependencies and integration points: integrates `xprt.h`, `sched.h`, `svcsock.h`, NFS callback services, and transport-specific backchannel methods.

Risks and test signals: risks include XID mismatches, preallocated slot leaks, disabled-config behavior drift, and service destruction while callbacks are active. Test with NFSv4.1 callback traffic, backchannel teardown, reconnects, and builds with and without `CONFIG_SUNRPC_BACKCHANNEL`.
