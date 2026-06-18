# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_h323_main.c

## Purpose
This file implements the H.323 conntrack helper module. It understands the H.323 signaling stack enough to discover dynamic call-control and media endpoints and then installs conntrack expectations for related flows: RAS over UDP, Q.931/H.225 call signaling over TCP, H.245 control, RTP/RTCP media, and T.120 data channels. It also exposes the RCU-protected `nfct_h323_nat_hook` hook table so the NAT companion can rewrite embedded H.225/H.245 addresses when the master connection is NATed.

## Important APIs, Types, And Functions
The public integration points are `nfct_h323_nat_hook`, exported `get_h225_addr()`, the registered helpers `nf_conntrack_helper_h245`, `nf_conntrack_helper_q931[]`, and `nf_conntrack_helper_ras[]`, and the module init/exit functions `nf_conntrack_h323_init()` / `nf_conntrack_h323_fini()`. Runtime state is kept in `struct nf_ct_h323_master` through `nfct_help_data(ct)`, especially `tpkt_len[]`, `sig_port[]`, and `timeout`.

Packet parsing starts with `get_tpkt_data()` for TCP TPKT framing and `get_udp_data()` for RAS. Address extraction is split between `get_h245_addr()` for H.245 `TransportAddress` and `get_h225_addr()` for H.225 `TransportAddress`. Expectation creation is handled by `expect_rtp_rtcp()`, `expect_t120()`, `expect_h245()`, `expect_callforwarding()`, `expect_q931()`, plus RAS helpers such as `process_gcf()`, `process_rcf()`, `process_acf()`, and `process_lcf()`.

## Control Flow
The H.245 and Q.931 helpers only inspect established traffic in either direction. Both take `nf_h323_lock` because they use shared static decode buffers/objects and the global `h323_buffer`. They iterate over all TPKTs in the skb, decode with generated decoders such as `DecodeMultimediaSystemControlMessage()` or `DecodeQ931()`, and pass decoded objects to `process_h245()` or `process_q931()`. Decode failures are logged at debug level and accepted, but expectation/NAT failures drop the packet via `nf_ct_helper_log()`.

`process_h245()` recognizes open logical channel requests and acknowledgements. `process_olc()` and `process_olca()` inspect H.2250 logical channel parameters, creating RTP/RTCP UDP expectations for media and TCP expectations for T.120 separate stacks. Q.931 processing handles setup/call proceeding/connect/alerting/facility/progress messages, opening H.245 control expectations, processing tunneled H.245 controls, NAT-rewriting call signal addresses, and optionally filtering call forwarding by route comparison.

RAS is UDP-oriented and processed for each packet. `process_ras()` dispatches gatekeeper, registration, unregistration, admission, location, and info messages. Registration requests create permanent Q.931 expectations and set the RAS timeout from the RRQ TTL or `default_rrq_ttl`; registration confirms refresh the master connection and update expectation timers. Unregistration clears expectations and shortens the master timeout.

## State And Persistence
There is no disk persistence. State persists in conntrack entries, helper extensions, and expectation timers. The module parameters `default_rrq_ttl`, `gkrouted_only`, and `callforward_filter` change behavior at runtime. Expectations may be permanent for Q.931/T.120/multiple-call paths, but they still live only inside conntrack state and are removed when the master connection/helper is destroyed or RAS unregistration occurs.

## Dependencies And Integration Points
The file depends on the generated H.323 type decoders from `nf_conntrack_h323_types.c` and declarations in `linux/netfilter/nf_conntrack_h323.h`. It integrates with core conntrack helpers, expectations, zones, ecache logging, IPv4/IPv6 routing, and optional NAT via `struct nfct_h323_nat_hooks`. Helper registration ties names `RAS`, `Q.931`, and `H.245` to nf_conntrack's helper lookup and expectation assignment.

## Risks
The helper parses complex ASN.1/PER data from packets in softirq context, so bounds handling, shared buffer locking, and decode/object layout must stay exact. Incomplete or split TPKTs are mostly accepted without inspection; this avoids false drops but may miss expectations. NAT rewriting is IPv4-only in the checked paths. Call forwarding route filtering depends on current routing decisions and could misclassify unusual policy routing. Broad permanent expectations are necessary for H.323 but increase exposure if embedded addresses are forged; most expectation creation verifies that advertised addresses match the signaling source before accepting them.

## Test Signals
Useful tests include module load/unload with helper registration conflicts, H.323 calls with direct and gatekeeper-routed signaling, fragmented/separate TPKT header traffic, fastStart media offers in Q.931, standalone H.245 OLC/OLCA flows, RRQ/RCF TTL propagation, URQ cleanup, NATed IPv4 calls with embedded address rewriting, IPv6 non-NAT calls, forged embedded address rejection, and expectation table contents for RTP/RTCP port pairing.
