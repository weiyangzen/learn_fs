# sources/distributed-fs/ceph-client/net/netfilter/nft_masq.c

Purpose: implements nftables `masq` NAT expression for IPv4, IPv6, and inet families, using the outgoing interface address with optional protocol port ranges.

Important APIs/types/functions: `struct nft_masq` stores NAT flags and optional proto min/max source registers. `nft_masq_eval()` builds `nf_nat_range2` and calls `nf_nat_masquerade_ipv4()` or `nf_nat_masquerade_ipv6()`. Family-specific destroy functions release conntrack namespace references. Module init registers IPv6 and inet variants conditionally, IPv4 always, and masquerade inet notifiers.

Control flow: validate requires NAT chain dependency and postrouting hook. Init parses range flags, optional proto registers, defaults max to min, and gets conntrack namespace support for the expression family. Eval loads proto range if configured and dispatches by packet family. Dump emits flags and registers. Init rollback unregisters previously registered families and notifiers on failure.

State/persistence: state is fixed expression metadata and conntrack namespace reference; NAT binding is stored in conntrack by nf_nat masquerade helpers. Dependencies include nf_nat, nf_nat_masquerade, conntrack netns support, NAT chain validation, and family config options. Risks include notifier registration ordering bugs, unsupported family warning path, proto register width mistakes, NAT hook misuse, and IPv6/inet conditional registration inconsistencies. Test signals: IPv4/IPv6/inet masquerade, proto range min-only and min/max, postrouting-only validation, non-NAT chain rejection, notifier cleanup on module unload, interface address changes, and dump/restore.
