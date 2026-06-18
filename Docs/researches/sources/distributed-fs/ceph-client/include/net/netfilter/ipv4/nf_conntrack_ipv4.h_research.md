<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_conntrack_ipv4.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_conntrack_ipv4.h

## Purpose
`ipv4/nf_conntrack_ipv4.h` declares IPv4 L4 protocol trackers used by nf_conntrack.

## Important APIs, types, and functions
It exposes extern `nf_conntrack_l4proto` instances for TCP, UDP, ICMP, and optional SCTP/GRE.

## Control flow
The conntrack core and protocol initialization tables reference these declarations to parse IPv4 packets by L4 protocol.

## State and persistence
No state is stored here; protocol tracker objects are defined in implementation files.

## Dependencies and integration points
It depends on nf_conntrack L4 protocol definitions and CONFIG_NF_CT_PROTO_SCTP/GRE. It integrates IPv4 packet tracking with generic conntrack.

## Risks and test signals
Risks include missing optional protocol declarations in builds and mismatched protocol object initialization. Tests should build IPv4 conntrack with TCP/UDP/ICMP and optional SCTP/GRE modules.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_conntrack_ipv4.h` completely for this pass (23 lines, 754 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/ipv4/nf_conntrack_ipv4.h -->
