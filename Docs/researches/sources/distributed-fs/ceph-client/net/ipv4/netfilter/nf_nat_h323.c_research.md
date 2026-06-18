# sources/distributed-fs/ceph-client/net/ipv4/netfilter/nf_nat_h323.c

## Purpose
`nf_nat_h323.c` implements NAT payload rewriting and expectation setup for the H.323 conntrack helper, covering H.225/Q.931, H.245, RTP/RTCP, T.120, RAS, and call-forwarding addresses.

## Important APIs, Types, And Functions
The module publishes `nathooks` through `nfct_h323_nat_hook`. Key functions are `set_addr()`, `set_h225_addr()`, `set_h245_addr()`, `set_sig_addr()`, `set_ras_addr()`, `nat_rtp_rtcp()`, `nat_t120()`, `nat_h245()`, `nat_q931()`, `nat_callforwarding()`, and expectation callbacks `ip_nat_q931_expect()` and `ip_nat_callforwarding_expect()`.

## Control Flow
Payload rewriting uses TCP or UDP NAT mangle helpers and relocates data pointers after possible skb reallocation. Signaling helpers locate embedded transport addresses matching the current connection tuple and rewrite them to NAT-facing tuple addresses/ports. Media/control helpers configure conntrack expectations, allocate NAT ports, rewrite advertised addresses, and save mapped ports in H.323 master helper data. Expect callbacks apply source and destination NAT to related connections when they appear.

## State And Persistence
Persistent state includes registered helper expectation functions, the RCU NAT hook pointer, per-connection H.323 helper data (`sig_port`, `rtp_port` arrays), and conntrack expectation objects. No independent table or namespace state is owned here.

## Dependencies And Integration Points
It integrates tightly with `nf_conntrack_h323`, `nf_nat`, NAT mangle helpers, conntrack expectations, TCP/UDP payload parsing, RCU hook publication, and helper expectation function registry.

## Risks
Risks are high because this rewrites application payloads. Important risks include stale data pointers after mangle, failed paired RTP/RTCP expectation cleanup, NAT port exhaustion, incorrect direction handling, loopback-address workaround regressions, expectation callback NAT mistakes, and races around RCU hook unregister.

## Test Signals
Test TCP and UDP payload rewriting, H.225/H.245 address replacement, RAS signal address replacement, RTP/RTCP paired expectations including busy-port retries and cleanup, T.120 and Q.931 expectations, call forwarding expectations, port exhaustion, malformed payloads, helper unload with active readers, and related connection NAT mapping.
