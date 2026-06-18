
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/ip_check_defrag.c

## Purpose

`ip_check_defrag.c` tests BPF-driven IP defragmentation/checksum behavior across IPv4 and IPv6 in a two-namespace topology.

## Important APIs, Types, and Functions

The file uses `ip_check_defrag.skel.h`, network namespace helpers, raw and UDP sockets, veth/topology setup, `start_server()`, `client_socket()`, manual packet buffers, and skeleton attach routines for IPv4/IPv6. It uses IP addressing constants, server/client ports, and BPF program state for observed defrag results.

## Control Flow and Data Flow

For each family, the harness loads the skeleton, builds ns0/ns1 topology, attaches the relevant BPF program, starts a UDP server in ns1, opens raw TX and UDP RX sockets in ns0, binds a chosen receive port, sends crafted fragmented traffic, and checks that expected payloads/ICMP or UDP replies are observed. Cleanup tears down sockets, links, and namespaces.

## State, Dependencies, Integration Points, Risks, and Test Signals

State includes netns topology, routes, raw sockets, UDP sockets, fragmented packet buffers, and skeleton counters. Dependencies are CAP_NET_ADMIN, raw sockets, IPv4/IPv6 stack support, and BPF helper support for defrag/checksum. Integration is BPF packet processing with kernel IP defragmentation and namespace routing. Risks are privilege gaps, timing in socket receive paths, route cleanup failures, and family-specific fragmentation differences. Test signals are successful topology/attach, received expected data, and no socket or packet assertions failing for both IPv4 and IPv6 subtests.
