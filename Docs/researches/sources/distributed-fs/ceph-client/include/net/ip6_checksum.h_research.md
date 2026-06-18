# sources/distributed-fs/ceph-client/include/net/ip6_checksum.h

Purpose: declares IPv6 pseudo-header checksum helpers for TCP, UDP, GSO, and skb checksum setup.

Important APIs/functions: `csum_ipv6_magic()` computes the IPv6 pseudo-header checksum unless provided by architecture code. `ip6_compute_pseudo()` computes an skb pseudo checksum from IPv6 source/destination, payload length, and protocol. `tcp_v6_check()` and `udp_v6_check()` are protocol-specific wrappers. `__tcp_v6_send_check()` initializes a TCP checksum field and skb checksum start/offset for transmit offload. `tcp_v6_gso_csum_prep()` prepares a TCPv6 GSO skb by zeroing payload length and setting pseudo checksum for length zero. `udp6_set_csum()` configures UDPv6 checksum behavior, including no-check cases.

Control flow and state: transmit paths call these helpers before handing skbs to checksum offload or software checksum completion. State mutated is in packet headers and skb checksum metadata.

Dependencies and integration: depends on byteorder, generic checksums, `ip.h`, IPv6 and TCP headers. It integrates with TCPv6, UDPv6, GSO, GRO pseudo checksum validation, and device checksum offload.

Risks: IPv6 UDP checksums are generally mandatory, so no-check handling must be explicit. GSO length-zero pseudo checksums must match segmentation code. Tests should cover TCPv6/UDPv6 checksum correctness, CHECKSUM_PARTIAL setup, GSO prep, zero-length payloads, no-check UDP paths, and architecture-provided checksum variants.
