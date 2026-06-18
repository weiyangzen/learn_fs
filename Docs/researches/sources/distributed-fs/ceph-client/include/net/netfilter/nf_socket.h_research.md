# sources/distributed-fs/ceph-client/include/net/netfilter/nf_socket.h

Purpose: Declares slow socket lookup helpers used by netfilter socket matching and transparent proxy paths.

Important APIs/types/functions: `nf_sk_lookup_slow_v4(struct net *net, const struct sk_buff *skb, const struct net_device *indev)` and `nf_sk_lookup_slow_v6(...)` return matching sockets for IPv4 or IPv6 packets.

Control flow: Netfilter expressions or matches first try faster skb/socket hints when available, then call these slow lookup helpers to search protocol socket tables using packet tuple and ingress device.

State and persistence: No state is defined here; looked-up sockets are existing kernel socket objects whose references are managed by implementation callers.

Dependencies/integration: Depends on `net/sock.h`, skbuff tuple parsing, network namespace socket tables, ingress device context, nft socket expression, xt socket match, and tproxy.

Risks/test signals: Risks are socket reference leaks, incorrect namespace/device scoping, fragment handling, and transparent socket matching differences. Test IPv4/IPv6 established and listener sockets, wildcard binds, VRF/l3mdev, transparent sockets, and no-socket fallback.
