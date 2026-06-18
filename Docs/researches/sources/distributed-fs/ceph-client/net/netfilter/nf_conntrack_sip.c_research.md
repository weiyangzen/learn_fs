<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_sip.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_sip.c

## Purpose
Implements the SIP conntrack helper for UDP and TCP. It parses SIP headers and SDP bodies, maintains SIP master state, creates expectations for signalling and RTP/RTCP media flows, refreshes registration expectations, and delegates SIP/SDP mangling to optional NAT hooks.

## Important APIs, Types, and Functions
Exports SIP parser helpers used by NAT: `ct_sip_parse_request()`, `ct_sip_get_header()`, `ct_sip_parse_header_uri()`, `ct_sip_parse_address_param()`, `ct_sip_parse_numerical_param()`, and `ct_sip_get_sdp_header()`. Main runtime functions are `sip_help_udp()`, `sip_help_tcp()`, `process_sip_msg()`, `process_sip_request()`, `process_sip_response()`, `process_sdp()`, `set_expected_rtp_rtcp()`, `process_register_request()`, and `process_register_response()`. `nf_nat_sip_hooks` is the exported RCU NAT hook table.

## Control Flow
UDP helper linearizes one datagram and processes one SIP message. TCP helper linearizes the skb and walks one or more SIP messages using `Content-Length`, tracking total payload-size changes for NAT seqadj. Request/response dispatch uses method handlers for INVITE, UPDATE, ACK, PRACK, BYE, and REGISTER. SDP processing locates session/media connection addresses and media ports, creates RTP/RTCP expectations, and asks NAT hooks to rewrite media/session addresses when required.

## State and Persistence
Per-flow `struct nf_ct_sip_master` stores invite/register CSeq and forced destination port learned from Via headers. Expectations persist for signalling, audio, video, and image classes with separate policies. Permanent inactive REGISTER expectations are activated/refreshed by successful registrar responses. Module parameters control helper ports, SIP master timeout, direct signalling/media restrictions, and external media behavior.

## Dependencies and Integration Points
Depends on conntrack helper/expectation APIs, routing lookups for external media decisions, SIP header definitions, IPv4/IPv6 address parsers, zones, and optional NAT SIP hooks for message, SDP, expectation, and sequence adjustment rewrites. Registers IPv4/IPv6 UDP/TCP helpers per configured port.

## Risks
Text parsing is complex: folded headers, comma-separated contacts, URI userinfo, IPv6 delimiters, malformed ports, and TCP message framing all affect correctness. Expectation conflicts across calls are handled with `-EALREADY`, but media reuse can still be surprising. NAT hooks mutate buffers and lengths, making TCP seqadj essential. Third-party registrations and external media are intentionally constrained by module parameters.

## Test Signals
Test UDP/TCP SIP, multiple TCP messages per skb, INVITE/UPDATE/PRACK/ACK SDP media expectations, failed responses flushing media expectations, BYE cleanup, REGISTER success/expiry/flush, IPv4/IPv6 Contact/Via/SDP parsing, direct/external media modes, NAT SIP rewrites, malformed headers, invalid ports, and RELATED RTP/RTCP flow creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_sip.c -->
