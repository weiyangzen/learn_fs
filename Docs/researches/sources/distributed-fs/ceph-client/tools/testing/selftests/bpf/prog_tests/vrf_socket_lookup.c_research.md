# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/vrf_socket_lookup.c

## Purpose

Network namespace selftest proving TC/XDP socket lookup helpers are VRF-aware. It builds two veth paths between namespaces, places one path in a VRF, attaches lookup programs, opens servers inside/outside the VRF, and verifies lookup isolation. The source was read for this report and is part of the Linux BPF selftests subtree carried under the Ceph client source import.

## Important APIs, Types, and Functions

`start_server()`, `make_sockaddr()`, `SO_BINDTODEVICE`, `bpf_tc_hook_create()`, `bpf_tc_attach()`, `bpf_xdp_attach()`, `open_netns()`, `if_nametoindex()`, `connect()`/`sendto()`, and skeleton BSS controls `test_xdp`, `tcp_skc`, `lookup_status`.

## Control Flow

Setup creates namespaces, veth pairs, VRF `vrf1`, routes, and attaches TC/XDP programs to NS0 devices. Each subtest opens non-VRF and VRF-bound servers in NS0, switches to NS1, sends traffic to each IP/port combination, and expects lookup success only when packet ingress VRF matches server scope.

## State and Persistence Behavior

State is network namespaces, veth/VRF devices, attached BPF programs, server sockets, and skeleton BSS flags. `cleanup()` deletes namespaces before and after the test.

## Dependencies and Integration Points

It depends on the BPF selftest harness (`test_progs.h`), libbpf skeletons generated from paired `progs/` objects, and kernel facilities exercised by the specific test such as `bpf_prog_test_run_opts()`, BPF links, map update syscalls, network namespaces, TC hooks, XDP attach/query APIs, or key/fsverity interfaces. It requires iproute2 VRF support, namespace privileges, and TCP/UDP socket lookup helper behavior.

## Risks and Edge Cases

The subtest names claim TCP/UDP and `bpf_skc_lookup_tcp()` variations, but all calls currently pass `SOCK_STREAM` and `tcp_skc=false`, which narrows actual coverage. Namespace cleanup failures can affect later runs.

## Test Signals

For each traffic direction, `lookup_status` must be 1 only for in-to-in and out-to-out cases and 0 for VRF-crossing cases.
