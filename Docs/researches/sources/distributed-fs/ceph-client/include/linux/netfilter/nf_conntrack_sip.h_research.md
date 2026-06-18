# sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_sip.h

Purpose: Declares the SIP conntrack helper interface: SIP/SDP header descriptors, parser entry points, expectation classes, and NAT hook callbacks for SIP payload rewriting.

Important APIs, types, and functions: Key types include `struct nf_ct_sip_master`, `struct sdp_media_type`, `struct sip_handler`, `struct sip_header`, `enum sip_header_types`, `enum sdp_header_types`, and `struct nf_nat_sip_hooks`. Parser APIs include `ct_sip_parse_request()`, `ct_sip_get_header()`, URI/address/numerical parameter parsers, and SDP header lookup. Detected source surface: 198 lines; includes `linux/skbuff.h`, `linux/types.h`, `net/netfilter/nf_conntrack_expect.h`; macros `SDP_HDR`, `SDP_MEDIA_TYPE`, `SIP_EXPECT_MAX`, `SIP_HANDLER`, `SIP_HDR`, `SIP_PORT`, `SIP_TIMEOUT`, `__NF_CONNTRACK_SIP_H__`, `__SIP_HDR`; structs `nf_conntrack_expect`, `nf_ct_sip_master`, `nf_nat_sip_hooks`, `sdp_media_type`, `sip_handler`, `sip_header`; enums `sdp_header_types`, `sip_expectation_classes`, `sip_header_types`; typedefs none; function-like declarations/helpers `ct_sip_get_header`, `ct_sip_get_sdp_header`, `ct_sip_parse_address_param`, `ct_sip_parse_header_uri`, `ct_sip_parse_numerical_param`, `ct_sip_parse_request`, `int`.

Control flow: The helper parses SIP control messages on port 5060, finds request/response methods, extracts headers and SDP media addresses, creates media expectations, and optionally calls NAT hooks to rewrite addresses, ports, Via/Contact records, SDP owners, and content length.

State and persistence behavior: Master state keeps direct media and signaling expectations. NAT hooks are RCU-protected and protocol header descriptors are static metadata used by parsers.

Dependencies and integration points: Depends on skb data, type definitions, and conntrack expectations. It integrates tightly with SIP NAT, UDP/TCP conntrack, and RTP/RTCP expectation handling.

Risks and test signals: SIP is text-heavy and ambiguous, so risks include parser desync, folded headers, short payloads, IPv6 literal handling, content-length mismatch after NAT, and expectation leaks. Test UDP/TCP SIP, SDP media negotiation, NAT rewriting, fragmented payloads, and malformed headers.
