# sources/distributed-fs/ceph-client/net/core/sock_diag.c

## Purpose
This file implements the generic NETLINK_SOCK_DIAG dispatcher, socket diagnostic handler registry, diagnostic cookies, optional classic filter reporting, destroy-event multicast, and per-net diag netlink socket setup. It lets protocol-specific diag modules expose dump and destroy operations through a common netlink family.

## APIs, Types, and Functions
Cookie helpers are `__sock_gen_cookie()`, `sock_diag_check_cookie()`, and `sock_diag_save_cookie()`. Attribute helpers include `sock_diag_put_meminfo()` and `sock_diag_put_filterinfo()`. Handler registration uses `sock_diag_register()`, `sock_diag_unregister()`, `sock_diag_register_inet_compat()`, and `sock_diag_unregister_inet_compat()`. Message dispatch is implemented by `sock_diag_rcv_msg()`, `__sock_diag_cmd()`, and the compat `TCPDIAG_GETSOCK` path. Destroy support includes `sock_diag_destroy()`, `sock_diag_broadcast_destroy()`, and workqueue callback `sock_diag_broadcast_destroy_work()`.

## Control Flow, State, and Persistence
Incoming netlink messages are received by the per-net `diag_nlsk`, passed through `netlink_rcv_skb()`, decoded by type, and dispatched to a registered per-family handler under RCU plus module reference. Missing handlers trigger `sock_load_diag_module()`. Destroy requests require `CAP_NET_ADMIN` in the socket net namespace and a protocol `diag_destroy` callback.

Destroy event broadcasting is asynchronous because it can be initiated from interrupt context. `sock_diag_broadcast_destroy()` allocates a small work item, queues it on `broadcast_wq`, formats an inet diag message with optional protocol info, multicasts to the appropriate group, then resumes normal socket destruction. Cookie state is stored atomically in each socket and generated from a global `DEFINE_COOKIE(sock_cookie)` source.

## Dependencies and Integration
Depends on netlink, net namespaces, module reference management, inet diag UAPI structures, socket memory info from `sock.c`, BPF classic filter metadata, nospec array hardening, and protocol-specific sock_diag modules. The pernet operations create and release `net->diag_nlsk`, and the bind callback autoloads IPv4/IPv6 diag modules for destroy multicast groups.

## Risks and Test Signals
Risks include missing module references around handler calls, incorrect RCU registration/unregistration, destroy broadcasts racing socket free, insufficient netlink message sizing, leaking sockets when work allocation fails, and capability mistakes for cross-netns destroy. Test signals include `ss`/inet_diag dump coverage, SOCK_DESTROY permission tests, module autoload tests, destroy multicast listeners, filter-info reporting with and without privileges, and KASAN/RCU debug during handler unregister while diag traffic is active.
