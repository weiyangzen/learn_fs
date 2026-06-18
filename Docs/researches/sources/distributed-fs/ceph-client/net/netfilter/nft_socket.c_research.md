
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_socket.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_socket.c

## Purpose

`nft_socket.c` implements the nftables `socket` expression, which looks up the socket associated with a packet and stores socket attributes such as transparent flag, mark, wildcard bind status, or cgroup v2 id into a register.

## Important APIs, Types, and Functions

`struct nft_socket` stores key, cgroup level, output length, and destination register. `nft_socket_eval()` is the main evaluator. `nft_socket_do_lookup()` performs slow socket lookup for IPv4 or IPv6 when `skb->sk` is absent or from another net namespace. `nft_socket_wildcard()` checks whether the socket is bound to wildcard IPv4/IPv6 address. `nft_sock_get_eval_cgroupv2()` and `nft_socket_cgroup_subtree_level()` implement optional cgroup v2 extraction.

## Control Flow

Initialization restricts family to IPv4, IPv6, or inet, validates selected key, computes output size, and for cgroup v2 translates a user subtree level relative to the cgroup root visible in process context. Evaluation validates `skb->sk` namespace, falls back to nf_socket slow lookup using ingress device, breaks if no socket is found, then stores the selected attribute. Slow lookup references are released with `sock_gen_put()` when they are not the skb-owned socket.

## State and Persistence Behavior

The expression keeps static key/register/level configuration. It does not retain socket references after evaluation. Cgroup output is a copied 64-bit cgroup id; mark and transparent/wildcard reads are snapshots of live socket state.

## Dependencies and Integration Points

Dependencies include nf_tables, nf_socket lookup helpers, inet socket state, TCP headers indirectly through lookup, cgroup socket data when configured, and hook validation for prerouting, local-in, and local-out.

## Risks and Test Signals

Risks include reference leaks on slow lookup, use on packets without ingress device, net namespace mismatches, non-full sockets for mark/wildcard/cgroup reads, and cgroup level overflow. Test transparent proxy sockets, socket marks, wildcard binds for IPv4 and IPv6, cgroup v2 IDs, local-out packets with `skb->sk`, prerouting slow lookup, and unsupported family/hook rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_socket.c -->
