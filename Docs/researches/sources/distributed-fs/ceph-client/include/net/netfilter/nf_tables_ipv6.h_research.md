# sources/distributed-fs/ceph-client/include/net/netfilter/nf_tables_ipv6.h

Purpose: Provides IPv6 packet metadata setup and validation helpers for nftables, including extension-header traversal.

Important APIs/types/functions: `nft_set_pktinfo_ipv6`, `__nft_set_pktinfo_ipv6_validate`, `nft_set_pktinfo_ipv6_validate`, and `nft_set_pktinfo_ipv6_ingress`.

Control flow: Helpers verify IPv6 version and payload length, then use `ipv6_find_hdr` with auth-header handling to find the transport protocol and offset. Invalid packets reset packet info to unspecified or increment IPv6 truncated/header-error stats in ingress path.

State and persistence: Stateless except for updating `nft_pktinfo` and IPv6 per-interface/per-net stats.

Dependencies/integration: Depends on IPv6 support, `ipv6_payload_len`, `ipv6_find_hdr`, `inet6_dev`, netfilter packet info, and IPv6 MIB counters. Disabled IPv6 builds return failure from validation helpers.

Risks/test signals: Exercise extension header chains, fragments, auth headers, jumbo/truncated payloads, `thoff > U16_MAX`, disabled IPv6 config, ingress stats, and fallback to unspecified packet info.
