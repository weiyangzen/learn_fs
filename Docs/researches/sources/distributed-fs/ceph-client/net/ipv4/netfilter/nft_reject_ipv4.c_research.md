# sources/distributed-fs/ceph-client/net/ipv4/netfilter/nft_reject_ipv4.c

## Purpose
IPv4 nftables `reject` expression. It sends ICMP unreachable or TCP reset replies and then drops the original packet.

## Important APIs, types, and functions
`nft_reject_ipv4_eval()` reads `struct nft_reject` private data and calls `nf_send_unreach()` for ICMP unreachable or `nf_send_reset()` for TCP reset. Generic nft reject init/dump/validate helpers manage netlink state. Module init/fini register the IPv4 reject expression type.

## Control flow
At evaluation, the configured reject type selects the reply helper with current skb, net namespace, socket, and hook. The expression unconditionally sets `regs->verdict.code = NF_DROP`.

## State and persistence
Only per-rule `struct nft_reject` state exists. The module keeps no runtime mutable state.

## Dependencies and integration points
Depends on nf_tables registration, generic nft reject validation/policy, and the IPv4 reject core in `nf_reject_ipv4.c`. Registered as family `NFPROTO_IPV4`, name `reject`.

## Risks
Correctness relies on lower-level reject code handling fragments, checksums, routes, bridge paths, and invalid packets. Since the expression always drops, validation must prevent unsupported configurations from being installed.

## Test signals
Install ICMP unreachable and TCP reset rules, verify generated replies and drops at relevant hooks, test invalid attributes, and cover conntrack/bridge interactions.
