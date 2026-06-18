# sources/distributed-fs/ceph-client/net/netfilter/nf_nat_sip.c

## Purpose

`nf_nat_sip.c` is the NAT-side companion for the SIP conntrack helper. It rewrites SIP signalling headers and SDP bodies so that addresses and ports advertised inside SIP payloads match the conntrack/NAT mapping, then installs NAT-aware expectations for related signalling, RTP, and RTCP flows. It is registered as the `"sip"` NAT helper and publishes a `struct nf_nat_sip_hooks` table through the global RCU pointer `nf_nat_sip_hooks`.

## Important APIs, types, and functions

- `mangle_packet()` is the central payload rewrite helper. It computes the payload-relative offset differently for TCP and UDP, calls `__nf_nat_mangle_tcp_packet()` or `nf_nat_mangle_udp_packet()`, refreshes `*dptr`, and adjusts `*datalen`.
- `sip_sprintf_addr()` and `sip_sprintf_addr_port()` format IPv4 and IPv6 literals for SIP and SDP, including bracketed IPv6 forms where URI syntax requires them.
- `map_addr()` compares parsed SIP URI addresses against the current conntrack tuple, chooses the opposite-direction mapped address and port, and rewrites the matched URI if NAT changed it.
- `nf_nat_sip()` rewrites the SIP request URI, Via header and parameters, Contact headers, From, To, and Cisco-style forced reply destination ports.
- `nf_nat_sip_seq_adjust()` records TCP sequence adjustment after payload length changes.
- `nf_nat_sip_expect()` and `nf_nat_sip_expected()` prepare and apply NAT for expected related SIP signalling connections.
- `nf_nat_sdp_addr()`, `nf_nat_sdp_port()`, `nf_nat_sdp_session()`, and `nf_nat_sdp_media()` rewrite SDP owner, connection, and media information and keep `Content-Length` consistent.
- `sip_hooks` binds all exported hook callbacks used by `nf_conntrack_sip`.

## Control flow

Module init registers `nat_helper_sip`, assigns `nf_nat_sip_hooks`, and registers the `"sip"` expectation function. The conntrack SIP helper calls these hooks while parsing SIP messages. `nf_nat_sip()` first distinguishes requests from responses by checking for the `SIP/2.0` status line. Requests may have their request URI rewritten with `ct_sip_parse_request()` plus `map_addr()`. The topmost Via URI is then parsed as UDP or TCP and rewritten only when it belongs to the current flow side. The code also rewrites `maddr=`, `received=`, and `rport=` parameters when they expose pre-NAT addresses or ports.

After Via handling, the helper iterates all Contact headers, then rewrites From and To URIs if they map to translated tuple endpoints. For Cisco forced destination ports, reply-direction UDP packets have `uh->dest` changed and checksums fixed through the NAT mangle path. SDP hooks are invoked by the SIP helper after it has parsed expectations from the body. `nf_nat_sdp_media()` searches for an available even RTP port and matching RTCP port, installs expectations, and rewrites the SDP media port if NAT had to move it.

## State and persistence behavior

The file has no durable storage. Runtime state lives in conntrack objects, conntrack helper private data, and expectations. `struct nf_ct_sip_master` supplies `forced_dport`; expectation fields such as `saved_addr`, `saved_proto`, `dir`, and `expectfn` preserve original values and tell the NAT expectation callback how to map the eventual related connection. TCP sequence state is persisted in the conntrack sequence-adjust extension by `nf_ct_seqadj_set()`. Registration state is held in RCU globals and helper registries until module exit clears them and waits for readers with `synchronize_rcu()`.

## Dependencies and integration points

This file depends heavily on `nf_conntrack_sip` parsing helpers, conntrack expectation APIs, NAT helper APIs, sequence adjustment, and skb payload mutation helpers. It integrates with netfilter through `nf_nat_helper_register()`, `nf_ct_helper_expectfn_register()`, and the RCU `nf_nat_sip_hooks` pointer consumed by the SIP conntrack helper. It handles both IPv4 and IPv6 formatting and both TCP and UDP SIP transports. Related media flows are integrated through conntrack expectations and later NAT setup in `nf_nat_sip_expected()`.

## Risks

Payload rewriting is offset-sensitive: every successful mangle must refresh `*dptr` and adjust `*datalen`, or later parser offsets can target stale memory. SDP rewrites must keep `Content-Length` correct, especially when IPv4 to IPv6 address text changes length. Expectation pairing for RTP/RTCP is protected by `nf_conntrack_expect_lock`; incorrect matching can apply source NAT to the wrong media stream. Port allocation failures intentionally drop packets, so high expectation pressure can affect call setup. SIP is syntactically flexible, so malformed or uncommon headers may bypass rewriting if the parser does not recognize them.

## Test signals

Useful tests include SIP over UDP and TCP through NAT with IPv4 and IPv6, request and response rewriting of Via, Contact, From, To, `maddr`, `received`, and `rport`; SDP session and per-media address changes; RTP/RTCP expectation allocation when default ports are free and when collisions force new ports; Cisco forced destination port behavior; TCP sequence adjustment after length-changing rewrites; and failure paths where mangle or expectation insertion returns an error and the packet is dropped with helper logging.
