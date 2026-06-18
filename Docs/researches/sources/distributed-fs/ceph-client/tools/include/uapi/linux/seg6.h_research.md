<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/seg6.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/seg6.h

Purpose: this header defines the userspace-visible IPv6 Segment Routing Header (SRH) layout and basic SRv6 TLV constants.

Important APIs/types: `struct ipv6_sr_hdr` models the SRH fixed header followed by a flexible array of `struct in6_addr` segments. Flags include protected, OAM, alert, and HMAC bits. TLV IDs include ingress, egress, opaque, padding, and HMAC. `sr_has_hmac(srh)` checks the HMAC flag. `struct sr6_tlv` represents generic type/length/data TLVs.

Control flow: networking tools and kernel netlink attribute parsers serialize or inspect SRHs using this layout. The header itself performs no parsing beyond the `sr_has_hmac` macro; callers must walk segments and TLVs using lengths from the IPv6 extension header.

State and persistence: SR state is packet-local or route configuration state elsewhere; this header only fixes wire/control-plane structures.

Dependencies/integration: depends on `linux/types.h` and `linux/in6.h`; integrated by SRv6 route actions, encapsulation attributes, packet parsers, and `seg6_local.h`.

Risks and test signals: risks include malformed `hdrlen`, flexible-array bounds, HMAC TLV handling, and network byte order for fields. Tests should build SRHs with/without HMAC, validate TLV iteration, and round-trip SRv6 route attributes through rtnetlink.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/seg6.h -->
