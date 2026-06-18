<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/seg6.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/seg6.h

Purpose: defines base IPv6 Segment Routing Header (SRH) UAPI constants and structures.

Important APIs, types, and functions: `struct ipv6_sr_hdr` contains extension-header fields, SRH type, segments-left, first-segment, flags, tag, and flexible IPv6 segment list. `struct sr6_tlv` represents generic SRH TLVs. Constants define SRH flag bits and TLV types for ingress/egress timestamps, opaque container, padding, HMAC, and others.

Control flow: packet, tunnel, and routing code parse the SRH fixed header, iterate segment addresses and TLVs, update segments-left during forwarding, and optionally validate HMAC or local SID behavior.

State and persistence behavior: represented state is packet wire data or route encapsulation data. This header owns no runtime state.

Dependencies and integration points: depends on IPv6 address and Linux type definitions. It integrates with IPv6 SRv6 routing, lightweight tunnels, HMAC, local SID actions, iproute2, and netlink route attributes.

Risks and edge cases: SRH is variable length. Code must check `hdrlen`, segment count, TLV lengths, HMAC presence, and alignment before reading flexible data. Segment routing semantics may be disabled or policy-gated in forwarding paths.

Test signals: create and parse SRH packets with multiple segments and TLVs, verify HMAC TLVs, fuzz hdrlen/TLV lengths, and test SRv6 tunnel route dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/seg6.h -->
