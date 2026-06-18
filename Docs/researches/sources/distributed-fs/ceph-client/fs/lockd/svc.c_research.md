# sources/distributed-fs/ceph-client/fs/lockd/svc.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/svc.c` is the central Linux lockd service implementation. It owns the NLM RPC service process, per-network-namespace lockd lifecycle, grace period scheduling, socket listener setup, module/sysctl/netlink configuration, request dispatch, and registration of NLM protocol versions. The source was read as a complete 791-line file for this report.

## Important APIs, Types, and Functions

Important globals are `nlmsvc_ops`, `nlmsvc_mutex`, `nlmsvc_users`, `nlmsvc_serv`, `nlmsvc_retry`, `lockd_net_id`, `nlm_timeout`, `nlm_udpport`, and `nlm_tcpport`. Public/exported entry points are `lockd_up`, `lockd_down`, and `nlmsvc_dispatch`; generic-netlink entry points are `lockd_nl_server_set_doit` and `lockd_nl_server_get_doit`. Core helpers include `get_lockd_grace_period`, `set_grace_period`, `lockd`, `make_socks`, `lockd_up_net`, `lockd_down_net`, `lockd_get`, `lockd_put`, `lockd_authenticate`, `lockd_init_net`, `init_nlm`, and `exit_nlm`. Static data includes the `nlm_sysctls` table, `lockd_net_ops`, `nlmsvc_version[]`, and `nlmsvc_program`.

## Control Flow

Module initialization registers sysctls, pernet state, the lockd netlink family, and procfs. `lockd_up` serializes with `nlmsvc_mutex`, creates the single `svc_serv` and kernel service thread on first user, then binds listeners and starts the per-net grace period. The lockd thread loops until stopped, retrying blocked locks via `nlmsvc_retry_blocked` and receiving RPCs with `svc_recv`. `nlmsvc_dispatch` decodes a request through the selected `svc_procedure`, calls the procedure function, optionally drops the reply, and encodes a response. `lockd_down` decrements per-net and global users, destroys xprts, ends grace, stops the service thread, deletes the retry timer, and releases the service.

## State and Persistence Behavior

State is in memory: global service references, per-net `struct lockd_net` values, delayed grace work, xprt listeners, and module/sysctl/netlink configuration. There is no file-backed persistence here. Grace state is persisted only for the lifetime of a net namespace and is terminated by delayed work or shutdown. Per-net netlink updates can mirror into legacy global module/sysctl values when operating on `init_net`.

## Dependencies and Integration Points

The file integrates SUNRPC server infrastructure, svc sockets/xprts, net namespaces, procfs, generic netlink, sysctl/module parameters, network address notifiers, NFS export callbacks through `nlmsvc_ops`, and the VFS lock grace API through `locks_start_grace` and `locks_end_grace`. It exposes lockd lifecycle to NFS client/server code through exported `lockd_up` and `lockd_down`.

## Risks and Edge Cases

Lifecycle correctness depends on balanced global and per-net user counts. Listener creation failures must destroy partially-created xprts. Address removal notifiers age temporary transports while the service may be concurrently stopping. Grace-period values are bounded, but per-net and legacy global values must stay consistent for `init_net`. Authentication intentionally allows callback procedures without resolving an export client, leaving each procedure responsible for host lookup.

## Test Signals

Useful signals are lockd module load/unload with sysctls enabled, `lockd_up`/`lockd_down` refcount stress across multiple net namespaces, RPC NULL calls for NLM versions 1/3/4, netlink set/get of grace and ports, listener creation on IPv4/IPv6 including `-EAFNOSUPPORT`, network-address removal aging xprts, grace-period behavior after startup, and decode/encode failure paths in `nlmsvc_dispatch`.
