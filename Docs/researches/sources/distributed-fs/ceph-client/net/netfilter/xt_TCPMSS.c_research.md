# sources/distributed-fs/ceph-client/net/netfilter/xt_TCPMSS.c

Purpose: `TCPMSS` target lowers or inserts TCP MSS options, commonly clamping SYN packets to path MTU.

Important APIs/types/functions: `tcpmss_mangle_packet()`, `tcpmss_reverse_mtu()`, `tcpmss_tg4()`, `tcpmss_tg6()`, hook/SYN check functions, and TCP checksum replacement helpers.

Control flow: runtime skips fragments, ensures skb writable, validates TCP header/options, computes MSS from configured value or min forward/reverse MTU, never increases existing MSS, inserts MSS only into data-less headers with room, and adjusts TCP/IP lengths and checksums. Checks enforce TCP SYN for legacy iptables and restrict PMTU clamp hooks.

State and persistence: no module state; packet TCP/IP headers mutate. Dependencies include TCP parsing, route lookup, dst MTU, IPv4/IPv6 headers, checksums, and x_tables match iteration. Risks: PMTU unknown drop, full-skb write/expand failure, max TCP header length, nft compat bypass of SYN check, and checksum correctness. Test signals: existing/lacking MSS, clamp PMTU, missing route, fragments, IPv6 extension headers, SYN enforcement, and length/checksum validation.
