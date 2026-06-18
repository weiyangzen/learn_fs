# sources/distributed-fs/ceph-client/net/netfilter/nft_chain_nat.c

## Purpose
`nft_chain_nat.c` registers nftables `nat` chain types for IPv4, IPv6, and inet families. NAT chain hooks prepare nft packet info and run `nft_do_chain()`, while chain type registration uses NAT-specific hook registration functions so nft NAT chains integrate with conntrack/NAT ordering.

## Important APIs, Types, and Functions
The hook wrapper is `nft_nat_do_chain()`. Chain type descriptors are `nft_chain_nat_ipv4`, `nft_chain_nat_ipv6`, and `nft_chain_nat_inet`, compiled by configuration. Module lifecycle is `nft_chain_nat_init()` and `nft_chain_nat_exit()`. Inet wrappers `nft_nat_inet_reg()` and `nft_nat_inet_unreg()` call `nf_nat_inet_register_fn()` and `nf_nat_inet_unregister_fn()`.

## Control Flow, State, and Persistence
`nft_nat_do_chain()` initializes generic packet info, switches on `state->pf`, and applies IPv4 or IPv6 packet-info parsing before invoking the nftables interpreter. IPv4 and IPv6 chain types support prerouting, postrouting, local-out, and local-in hooks. Inet NAT supports the same logical hooks for dual-stack tables and delegates registration to inet NAT helpers.

Module initialization registers enabled chain types; exit unregisters them. State is limited to registered chain type metadata and any hooks created by nftables core when users create NAT base chains.

## Dependencies and Integration Points
The file depends on nftables core, IPv4/IPv6 packet-info helpers, and NAT registration helpers from `nf_nat`. It is loaded through nft chain aliases for family-specific `nat` chain creation.

## Risks and Test Signals
Risks include hook-mask mismatch with NAT core expectations, IPv4/IPv6 packet-info setup before NAT expressions, inet registration symmetry, and optional-family build coverage. Tests should create NAT chains in IPv4, IPv6, and inet tables; exercise all supported hooks; verify module autoload aliases; confirm cleanup unregisters types; and test NAT rule execution on packets requiring conntrack/NAT state.
