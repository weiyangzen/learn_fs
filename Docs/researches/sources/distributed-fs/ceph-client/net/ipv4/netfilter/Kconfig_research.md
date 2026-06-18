# sources/distributed-fs/ceph-client/net/ipv4/netfilter/Kconfig

## Purpose
This Kconfig file declares IPv4 and ARP netfilter build options: defrag, legacy iptables/arptables, nftables IPv4/ARP support, IPv4 NAT helpers, duplicate/reject/log/socket/tproxy helpers, and legacy match/target/table modules.

## Important APIs, Types, And Functions
It defines options such as `NF_DEFRAG_IPV4`, `IP_NF_IPTABLES_LEGACY`, `IP_NF_IPTABLES`, `IP_NF_FILTER`, `IP_NF_NAT`, `IP_NF_MANGLE`, `IP_NF_RAW`, `IP_NF_SECURITY`, `IP_NF_ARPTABLES`, `IP_NF_ARPFILTER`, `IP_NF_ARP_MANGLE`, `NFT_*_IPV4`, `NF_NAT_H323`, and compatibility selectors for old target/match names.

## Control Flow
The file is declarative. Menu visibility depends on `INET && NETFILTER`; nftables entries are nested under `NF_TABLES`; legacy iptables tables are nested under `IP_NF_IPTABLES`; NAT helpers are nested under `NF_NAT`; ARP legacy options are separate at the end.

## State And Persistence
Kconfig choices persist in kernel configuration and determine whether corresponding objects are built-in, modular, or absent.

## Dependencies And Integration Points
It coordinates with the sibling Makefile and wider netfilter symbols such as `NETFILTER_XTABLES`, `NETFILTER_XTABLES_LEGACY`, `NF_CONNTRACK`, `NF_NAT`, `SECURITY`, `NFT_COMPAT`, and `SYN_COOKIES`.

## Risks
Risks include dependency cycles, accidentally enabling legacy modules when nftables-only configurations expect not to, missing selectors for helper functionality, and changing defaults that affect distro kernel module availability.

## Test Signals
Run representative `allnoconfig`, `defconfig`, legacy iptables, nftables-only, NAT-helper, and ARP-table configurations; verify expected modules appear in `.config` and Makefile object expansion.
