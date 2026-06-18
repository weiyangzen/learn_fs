# sources/distributed-fs/ceph-client/net/netfilter/utils.c

Purpose: shared netfilter helpers for IPv4/IPv6 checksum verification, partial checksum checks, route dispatch, and IPv6 hop-by-hop length validation.

Important APIs/types/functions: exported `nf_ip_checksum()`, `nf_ip6_checksum()`, `nf_checksum()`, `nf_checksum_partial()`, `nf_route()`, and `nf_ip6_check_hbh_len()`.

Control flow: checksum helpers use `CHECKSUM_COMPLETE` fast paths for early hooks, otherwise seed pseudo-header checksums and call skb completion helpers. `nf_route()` dispatches by family. Hop-by-hop parsing pulls headers, walks TLVs, validates jumbo payload option shape, and returns errno on malformed input.

State and persistence: no persistent module state; functions mutate skb checksum metadata and may write jumbo payload length. Dependencies include skb checksum APIs, IP headers, route helpers, and IPv6 TLV constants. Risks: checksum metadata side effects, partial checksum length handling, malformed TLV overrun, and pull failure. Test signals: checksum-complete/none, TCP/UDP and non-TCP protocols, partial checks, route dispatch, valid jumbo option, and invalid TLV/alignment.
