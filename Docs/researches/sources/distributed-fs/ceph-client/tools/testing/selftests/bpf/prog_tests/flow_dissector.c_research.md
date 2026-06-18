
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/flow_dissector.c

## Purpose

`flow_dissector.c` validates BPF flow dissector behavior in three modes: namespace attachment exclusivity, direct/indirect skb-less attach through a TAP interface, and skb-mode `bpf_prog_test_run_opts()` packet parsing. It exercises IPv4, IPv6, VLAN, fragments, flow labels, IPIP, GRE, encapsulation stop flags, and `BPF_FLOW_DISSECTOR_CONTINUE`.

## Important APIs, Types, and Functions

The file defines packed packet layouts (`ipv4_pkt`, `ipv6_pkt`, VLAN, fragment, IPIP, GRE) and a `struct test` table with expected `struct bpf_flow_keys`. It uses `bpf_flow.skel.h`, `bpf_prog_attach()`, `bpf_prog_detach2()`, `bpf_program__attach_netns()`, `bpf_prog_test_run_opts()`, `bpf_map_update_elem()`, `bpf_map_lookup_elem()`, TAP ioctls, and network namespace helpers. Key helpers are `init_prog_array()`, `create_tap()`, `ifup()`, `run_tests_skb_less()`, and the three public test entry points.

## Control Flow and Data Flow

The namespace test proves root and non-root netns flow dissector attach mutual exclusion. The skb-less tests create a private netns, load the dissector, populate the program array jump table, attach directly or via a netns link, send crafted frames through `tap0`, and read stored flow keys from `last_dissection`. The skb test runs each packet fixture directly against the dissector and compares returned flow keys.

## State, Dependencies, Integration Points, Risks, and Test Signals

State lives in the kernel flow-dissector attachment slot, the skeleton jump-table map, the `last_dissection` map, and temporary netns/TAP devices. Dependencies include `/dev/net/tun`, CAP_NET_ADMIN, namespace support, libbpf netns links, and packet layout definitions from kernel headers. Integration points are BPF flow dissector attach semantics, map-in-map tail calls, and flow key ABI. Risks are namespace cleanup leaks, TAP availability, endianness/packed layout mistakes, and skipped skb-less cases whose flags cannot be supplied. Test signals are correct `bpf_flow_keys`, attach rejection with `EEXIST`, clean detach, and exact `BPF_OK`/`BPF_FLOW_DISSECTOR_CONTINUE` return values.
