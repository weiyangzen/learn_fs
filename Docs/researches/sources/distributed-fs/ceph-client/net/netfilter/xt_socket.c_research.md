<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_socket.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_socket.c

## Purpose
`xt_socket.c` implements the `socket` match for transparent proxying. It matches packets that correspond to a local socket, optionally requiring transparent sockets, ignoring wildcard listeners, and restoring the socket mark to the skb.

## Important APIs, Types, and Functions
`socket_match()` handles IPv4, while `socket_mt6_v1_v2_v3()` handles IPv6. They use `nf_sk_lookup_slow_v4()` or `nf_sk_lookup_slow_v6()`, `sk_fullsock()`, `inet_sk_transparent()`, and `sock_gen_put()`. Checkentry functions `socket_mt_v1_check()`, `socket_mt_v2_check()`, and `socket_mt_v3_check()` validate flags and enable defragmentation through `socket_mt_enable_defrag()`.

## Control Flow, State, and Persistence
The matcher first uses `skb->sk` if it belongs to the current net namespace; otherwise it performs a socket lookup from packet tuple and input device. It rejects wildcard listeners unless `XT_SOCKET_NOWILDCARD` is set, rejects non-transparent sockets when requested, and can copy `sk_mark` into `skb->mark` with `XT_SOCKET_RESTORESKMARK`. Rule insertion enables IPv4/IPv6 defrag and destruction disables it. The module persists only defrag references.

## Dependencies and Integration Points
It integrates x_tables with socket lookup, TCP/UDP socket tables, transparent proxy socket options, skb marks, and nf_defrag for PREROUTING/LOCAL_IN hooks.

## Risks and Test Signals
Risks include socket reference handling, namespace mismatch, wildcard listener interception, transparent-only policy, mark restoration timing, and defrag enable/disable balancing. Tests should cover established sockets, nonzero-bound listeners, wildcard listeners with and without NOWILDCARD, transparent sockets, RESTORESKMARK, IPv4/IPv6, no socket match, namespace isolation, fragments requiring defrag, and invalid flag masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_socket.c -->
