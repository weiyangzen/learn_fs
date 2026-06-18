
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_rt.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_rt.c

## Purpose

`nft_rt.c` implements the nftables `rt` expression, which reads route-derived metadata into registers: route class id, IPv4 or IPv6 nexthop, TCP MSS estimate, and optional XFRM presence.

## Important APIs, Types, and Functions

`struct nft_rt` stores selected `enum nft_rt_keys` and destination register. `nft_rt_get_eval()` reads `skb_dst()` and fills the register. `get_tcpmss()` derives a conservative MSS from the current dst MTU and a reverse route lookup to the packet source. `nft_rt_get_init()` maps keys to register store lengths. `nft_rt_validate()` restricts families and TCPMSS hook placement.

## Control Flow

Evaluation fails with `NFT_BREAK` when the skb has no dst or the key is incompatible with packet family. Nexthop reads use `rt_nexthop()` for IPv4 and `rt6_nexthop()` for IPv6. TCPMSS computes a minimum of current route MTU and reverse-route MTU, subtracting minimum IP+TCP header sizes, with `TCP_MSS_DEFAULT` fallback. Initialization rejects unsupported compile-time keys when their configs are absent.

## State and Persistence Behavior

The expression stores static key/register configuration only. It reads live route state from dst entries and may perform a transient route lookup. It does not retain dst references beyond the helper-local reverse lookup release.

## Dependencies and Integration Points

Dependencies include dst entries, IPv4 and IPv6 routing, XFRM conditional fields, nf_tables register validation, and chain hook validation. It is normally used before comparisons or payload modification rules.

## Risks and Test Signals

Risks include missing dst metadata in early hooks, stale route assumptions, TCPMSS use in hooks without meaningful egress route state, and conditional build coverage for classid/XFRM. Test IPv4/IPv6 nexthop reads, TCPMSS in forward/local-out/postrouting, no-dst packets, XFRM-enabled routes, and config variants without route classid or XFRM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_rt.c -->
