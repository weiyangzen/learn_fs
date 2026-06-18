<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_udp.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_udp.c

## Purpose
Implements UDP conntrack validation, stream promotion, timeout refresh, ctnetlink timeout policy support, and UDP tuple netlink integration.

## Important APIs, Types, and Functions
Main function is `nf_conntrack_udp_packet()`, supported by `udp_error()`, `udp_error_log()`, `udp_get_timeouts()`, `nf_conntrack_udp_init_net()`, and descriptor `nf_conntrack_l4proto_udp`. Default timeouts are 30 seconds unreplied and 120 seconds replied.

## Control Flow
`udp_error()` validates the UDP header, length field, and optional checksum on PREROUTING when checksum checking is enabled. The packet path initializes `ct->proto.udp.stream_ts` for new entries, refreshes the short timeout until reply traffic is seen and at least two seconds pass, then refreshes the stream timeout and sets `IPS_ASSURED` unless `IPS_NAT_CLASH` is present.

## State and Persistence
Per-connection UDP state is `stream_ts`, used to avoid promoting immediate bidirectional probes to long-lived streams. Per-net state is timeout array plus optional flow offload timeout.

## Dependencies and Integration Points
Depends on UDP headers, checksum helpers, conntrack events, timeout extension, port tuple netlink helpers, flow-table configuration, and standalone UDP sysctls.

## Risks
UDP has no handshake, so the two-second promotion threshold is the main heuristic. Bad length or checksum handling must avoid dropping valid checksum-offloaded traffic. NAT clash flows intentionally never become ASSURED.

## Test Signals
Validate one-way UDP expiration, bidirectional promotion after two seconds, immediate reply before stream threshold, zero checksum IPv4 packets, malformed lengths, bad checksums, NAT clash behavior, ctnetlink timeout policies, and flow offload timeout sysctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_proto_udp.c -->
