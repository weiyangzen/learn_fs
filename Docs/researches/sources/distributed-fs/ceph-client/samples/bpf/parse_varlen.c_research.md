# sources/distributed-fs/ceph-client/samples/bpf/parse_varlen.c

Purpose: packet parser sample handling variable-length headers such as VLAN tags, IPv4 IHL, IPv6, TCP, and UDP.

Important APIs/types/functions: helpers `tcp`, `udp`, `parse_ipv4`, `parse_ipv6`, and `SEC("varlen") int handle_ingress`. Defines protocol constants and optional debug.

Control flow: starts at Ethernet header, safely advances through one or more VLAN headers, dispatches to IPv4 or IPv6 parsing, handles fragments, computes transport offsets, validates TCP/UDP bounds, and returns verdicts based on selected port/protocol checks.

State and persistence: stateless per packet.

Dependencies and integration: uses BPF direct packet access and kernel networking headers; built by sample Makefile for parser demonstrations.

Risks: bounded parsing must satisfy the verifier, so loop/branch changes are sensitive. Protocol coverage is still sample-level, not a complete production parser. Fragmented or extension-header-heavy packets may bypass transport parsing.

Test signals: attach and send VLAN/non-VLAN IPv4/IPv6 TCP/UDP packets, confirm verifier acceptance and expected classification.
