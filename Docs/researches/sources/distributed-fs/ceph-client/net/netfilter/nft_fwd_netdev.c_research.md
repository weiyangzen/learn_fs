# sources/distributed-fs/ceph-client/net/netfilter/nft_fwd_netdev.c

Purpose: implements netdev-family `fwd` expressions for redirecting packets to an egress device or forwarding through neighbor resolution to a supplied next-hop address.

Important APIs/types/functions: `struct nft_fwd_netdev` stores the output ifindex register; `nft_fwd_netdev_eval()` calls `nf_fwd_netdev_egress()` and returns `NF_STOLEN`. `struct nft_fwd_neigh` stores device, address, and nfproto registers; `nft_fwd_neigh_eval()` decrements IPv4 TTL or IPv6 hop limit, resolves the device, adjusts headroom, and calls `neigh_xmit()`. Offload uses `nft_fwd_dup_netdev_offload()` with `FLOW_ACTION_REDIRECT`.

Control flow: `nft_fwd_select_ops()` chooses neighbor forwarding when `NFTA_FWD_SREG_ADDR` is present, otherwise simple netdev forwarding. Simple init only parses device register. Neighbor init requires device, address, and nfproto, validates IPv4/IPv6 address width, then parses registers. Validate restricts hooks to netdev ingress/egress.

State/persistence: state is register metadata only; packet path mutates skb device, redirected flag, ingress ifindex, TTL/hop-limit, timestamp, and ownership via stolen verdict/neigh transmit. Dependencies include nf_dup_netdev helpers, neighbor tables, RCU dev lookup, flow offload structures, and netdev hooks. Risks include recursion limit handling, skb headroom expansion stealing/dropping semantics, TTL/hop-limit underflow, invalid ifindex, and software/offload redirect mismatch. Test signals: ifb-style redirect, neighbor forwarding for IPv4/IPv6, nonmatching protocol breaks, TTL one drops, invalid device drops, headroom expansion failure, ingress/egress validation, and hardware offload generation.
