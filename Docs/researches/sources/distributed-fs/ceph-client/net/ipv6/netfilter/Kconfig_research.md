# sources/distributed-fs/ceph-client/net/ipv6/netfilter/Kconfig

Purpose: Defines build-time configuration for IPv6 netfilter, including legacy ip6tables, nftables IPv6 support, socket/tproxy helpers, reject/log/dup cores, match modules, and target/table modules.

Important APIs/types/functions: Kconfig symbols include `IP6_NF_IPTABLES_LEGACY`, `NF_SOCKET_IPV6`, `NF_TPROXY_IPV6`, `NF_TABLES_IPV6`, `NFT_REJECT_IPV6`, `NFT_DUP_IPV6`, `NFT_FIB_IPV6`, `NF_DUP_IPV6`, `NF_REJECT_IPV6`, `NF_LOG_IPV6`, `IP6_NF_IPTABLES`, match symbols such as `IP6_NF_MATCH_AH`, `EUI64`, `FRAG`, `OPTS`, `IPV6HEADER`, `MH`, `RPFILTER`, `RT`, `SRH`, and targets/tables such as `IP6_NF_FILTER`, `IP6_NF_TARGET_REJECT`, `SYNPROXY`, `MANGLE`, `RAW`, `SECURITY`, `NAT`, `MASQUERADE`, and `NPT`.

Control flow: The file gates menu visibility on `INET && IPV6 && NETFILTER`, uses nested `if` blocks for nf_tables and ip6tables feature families, selects required common modules, and gives defaults for common non-advanced configurations.

State and persistence: Kconfig state persists as kernel build configuration and determines object inclusion, module availability, aliases, and dependency closure.

Dependencies/integration: Integrates with top-level kbuild, netfilter xtables/nftables, conntrack/NAT, security framework, and module autoload names referenced by ip6tables userspace.

Risks and test signals: Risks are dependency mismatches, symbols enabling objects without required core support, and legacy/nft compatibility confusion. Test signals include `allmodconfig`, `randconfig`, oldconfig migration, building with nft-only versus legacy iptables, and checking that every Makefile object in this subset is reachable from the expected symbol.
