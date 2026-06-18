# sources/distributed-fs/ceph-client/net/netfilter/nft_chain_filter.c

## Purpose
`nft_chain_filter.c` registers nftables `filter` chain types for IPv4, IPv6, ARP, inet, bridge, and netdev families. Each hook wrapper prepares `struct nft_pktinfo` for the packet family and then delegates to `nft_do_chain()`. The netdev support also tracks device register/unregister/rename events for chains bound by interface name.

## Important APIs, Types, and Functions
Top-level lifecycle APIs are `nft_chain_filter_init()` and `nft_chain_filter_fini()`. Hook wrappers include `nft_do_chain_ipv4()`, `nft_do_chain_ipv6()`, `nft_do_chain_arp()`, `nft_do_chain_inet()`, `nft_do_chain_inet_ingress()`, `nft_do_chain_bridge()`, and `nft_do_chain_netdev()`.

The registered objects are `struct nft_chain_type` instances for filter chains in each enabled family. Netdev lifecycle helpers are `nft_netdev_event()`, `__nf_tables_netdev_event()`, `nf_tables_netdev_event()`, and the `nf_tables_netdev_notifier`.

## Control Flow, State, and Persistence
Family-specific hook functions initialize packet info from the netfilter hook state, then parse or validate protocol headers. IPv4 and IPv6 use dedicated `nft_set_pktinfo_*` helpers. ARP uses unspecific packet info. Inet regular hooks switch on `state->pf`; inet ingress starts from a netdev ingress state, maps Ethernet protocol to IPv4 or IPv6, rewrites the temporary hook state to `NF_INET_INGRESS`, and accepts non-IP packets. Bridge and netdev hooks inspect the Ethernet protocol and validate IPv4/IPv6 headers when present, otherwise falling back to unspecific packet info.

Initialization registers netdev first, then IPv4, IPv6, ARP, inet, and bridge chain types. Fini unregisters in reverse order. Netdev notifier operations walk nftables tables under `commit_mutex`, find netdev-family chains and inet ingress chains, and create or remove per-device `nf_hook_ops` entries when devices matching stored interface names appear, disappear, or change name. Dormant tables skip hook register/unregister but still maintain the ops list.

Persistent state is chain type registration plus per-base-chain hook ops lists for bound devices and a netdevice notifier.

## Dependencies and Integration Points
This file connects nftables to netfilter hooks for all filter-capable families and depends on packet-info helpers from IPv4/IPv6 nft headers, bridge/netdev hook constants, netdevice notifiers, and nftables per-net table/chain lists. The wrappers call the core interpreter in `nf_tables_core.c`.

## Risks and Test Signals
Risks include ingress family remapping, short/invalid IP header validation, netdev rename matching, ops list lifetime under RCU, dormant table behavior, and registration ordering across optional config blocks. Tests should create filter chains for every enabled family/hook, process IPv4/IPv6/non-IP ingress and bridge packets, bind chains to devices before and after device registration, rename devices, unregister devices, toggle dormant tables, and verify reverse-order cleanup.
