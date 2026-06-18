# sources/distributed-fs/ceph-client/include/net/netfilter/nf_tables_ipv4.h

Purpose: Provides IPv4 packet metadata setup and validation helpers for nftables packet evaluation.

Important APIs/types/functions: `nft_set_pktinfo_ipv4`, `__nft_set_pktinfo_ipv4_validate`, `nft_set_pktinfo_ipv4_validate`, and `nft_set_pktinfo_ipv4_ingress`.

Control flow: Base hooks initialize `nft_pktinfo` from `ip_hdr`. Validation paths safely fetch headers, verify IHL/version/total length/header length, set L4 protocol, ethertype, network/transport offsets, and fragment offset. Ingress validation increments IPv4 truncated/header-error stats on malformed packets.

State and persistence: Stateless helper; it mutates only the stack/current packet `nft_pktinfo` and IPv4 stats counters.

Dependencies/integration: Depends on `nf_tables.h`, `net/ip.h`, skbuff header access, `iph_totlen`, `pskb_may_pull`, and IP MIB stats.

Risks/test signals: Test short skbs, invalid IHL/version, total length shorter than header, fragments, ingress stats, non-zero network offsets for inner validation, and behavior falling back to `nft_set_pktinfo_unspec`.
