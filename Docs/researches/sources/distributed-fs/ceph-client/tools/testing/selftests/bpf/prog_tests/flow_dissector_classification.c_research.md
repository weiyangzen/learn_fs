
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/flow_dissector_classification.c

## Purpose

`flow_dissector_classification.c` performs end-to-end classification checks showing that a BPF flow dissector feeds kernel packet classification consistently for plain IPv4/IPv6 UDP, `BPF_FLOW_DISSECTOR_CONTINUE`, IPIP, GRE, and port-range flower filters.

## Important APIs, Types, and Functions

The harness builds packets with IPv4, IPv6, UDP, GUE, GRE, and optional extra encapsulation headers. It uses `bpf_flow.skel.h`, `bpf_prog_attach()`, program-array setup, raw and UDP sockets, `tc qdisc/filter` commands through `SYS`, network namespace helpers, checksum helpers, and `write_sysctl()`. `struct test_configuration` captures setup/teardown callbacks, source ports, address families, inner/outer addresses, encapsulation protocol, and DS fields.

## Control Flow and Data Flow

`test_global_init()` loads the dissector, enters an isolated netns, disables rp_filter, attaches and populates the program array. Each table entry sets qdisc/filter and tunnel state, sends ten packets from three source ports, receives UDP payloads, and expects pass/drop/pass behavior. Packet data is built from inside out so UDP checksums cover correct pseudo headers.

## State, Dependencies, Integration Points, Risks, and Test Signals

State includes netns configuration, loopback addresses, qdiscs, flower filters, IPIP/GRE devices, sockets, and the attached dissector. Dependencies are CAP_NET_ADMIN, `ip`/`tc`, raw sockets, loopback tunnel support, sysctl write access, and BPF flow dissector support. Integration points are dissector-to-flower classification and tunnel decapsulation. Risks include cleanup failures leaving qdiscs/tunnels, timing in receive polling, checksum mistakes, and environmental lack of modules or privileges. Test signals are `TEST_PACKETS_COUNT, 0, TEST_PACKETS_COUNT` receive counts for the three source-port cases across all configurations.
