# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_nfct.c

## Purpose
Bridges IPVS connection state with Netfilter conntrack. It adjusts conntrack reply tuples for IPVS NAT, creates expectations for related flows, confirms conntracks in IPVS hooks, and drops conntrack entries when an IPVS connection terminates.

## Important APIs, Types, and Functions
`ip_vs_update_conntrack()` alters unconfirmed conntrack reply tuples for NATed IPVS connections. `ip_vs_confirm_conntrack()` wraps `nf_conntrack_confirm()`. `ip_vs_nfct_expect_related()` allocates and installs related-flow expectations with `ip_vs_nfct_expect_callback()` as the expectation callback. `ip_vs_conn_drop_conntrack()` searches and kills the original client-to-virtual conntrack tuple. Debug macros format conntrack and IPVS tuples.

## Control Flow
When a packet is associated with a NAT IPVS connection, `ip_vs_update_conntrack()` exits unless conntrack exists, is unconfirmed and alive, the forwarding method is MASQ, the connection is not one-packet, and the packet is in the original direction. For outbound-inbound and inbound-outbound cases it rewrites the reply source or destination tuple to match the real or virtual endpoint, then calls `nf_conntrack_alter_reply()`. Expectations are installed from IPVS app helpers with optional wildcard source port; when conntrack creates the related flow, the callback finds the matching IPVS connection in either direction and alters the reply tuple accordingly.

## State and Persistence
The file owns no standalone state. It mutates existing `struct nf_conn` tuples and optional sequence-adjust extensions, and it relies on existing `struct ip_vs_conn` fields for endpoints, ports, forwarding method, flags, and app binding. Expectations live in conntrack until consumed or expired.

## Dependencies and Integration Points
Depends on Netfilter conntrack core, expectation, helper, sequence adjustment, zones, and tuple APIs. It integrates with IPVS NAT and app helper paths, especially FTP-like related connections, and with IPVS connection expiration through `ip_vs_conn_drop_conntrack()`.

## Risks
Tuple alteration is valid only before conntrack confirmation; late calls are intentionally ignored. Related-flow correctness depends on conntrack helper modules being installed for the same protocol and ports. Sequence-adjust extension allocation can fail and blocks tuple update for TCP app helpers. Only MASQ connections are altered, so other forwarding methods must not expect NAT-aware conntrack replies. The drop path uses default conntrack zone only.

## Test Signals
Exercise NATed TCP/UDP services with conntrack enabled, FTP active/passive related flows, confirmed versus unconfirmed conntracks, one-packet UDP services, app helper sequence adjustment, and connection expiration causing conntrack kill. Observe conntrack table tuples before and after IPVS hook processing.
