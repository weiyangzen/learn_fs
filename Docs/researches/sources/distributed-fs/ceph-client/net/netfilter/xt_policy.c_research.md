<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_policy.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_policy.c

## Purpose
`xt_policy.c` implements matching on IPsec/xfrm policy and state. It can test whether a packet is protected or unprotected, inbound or outbound, and whether xfrm selectors match configured tunnel endpoints, SPI, protocol, mode, and reqid.

## Important APIs, Types, and Functions
`policy_mt()` is the top-level matcher. Helpers include `match_xfrm_state()`, `match_policy_in()`, and `match_policy_out()` operating on `struct xt_policy_info` and `struct xt_policy_elem`. `policy_mt_check_hooks()` and `policy_mt_check()` validate hook direction and element counts.

## Control Flow, State, and Persistence
For inbound packets the matcher inspects `skb_sec_path()` xfrm states. For outbound packets it checks the dst xfrm bundle. It supports strict ordered matching or any matching element, handles `XT_POLICY_MATCH_NONE`, and applies per-element inversion. The module persists no xfrm state.

## Dependencies and Integration Points
It depends on xfrm/IPsec state attached to skb security paths or dst entries, x_tables hook metadata, and IPv4/IPv6 address comparison. It is a filtering bridge into the kernel xfrm subsystem.

## Risks and Test Signals
Risks include hook direction mismatch, strict mode ordering, tunnel endpoint address family handling, bundle versus secpath differences, and packets with policy but no state or vice versa. Tests should cover inbound ESP/AH, outbound xfrm bundles, policy none, strict and non-strict multiple elements, reqid/SPI/proto/mode/tunnel addresses, inversion, IPv6, and invalid hook masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_policy.c -->
