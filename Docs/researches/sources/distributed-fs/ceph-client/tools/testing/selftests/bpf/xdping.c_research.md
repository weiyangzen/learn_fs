# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xdping.c

## Purpose

`xdping.c` is a userspace runner for XDP ICMP ping acceleration tests. It loads a companion BPF object, attaches either client or server XDP program to an interface, drives ordinary `ping`, and reads an eBPF map containing XDP-measured RTT samples.

## Important APIs, Types, and Functions

Global state is `ifindex` and `xdp_flags`. Functions are `cleanup`, `get_stats`, `show_usage`, and `main`. It uses libbpf strict mode, `bpf_prog_test_load`, `bpf_object__find_program_by_name`, `bpf_xdp_attach/detach`, BPF map lookup/update/delete, `getaddrinfo`, and the shared `struct pinginfo` from `xdping.h`.

## Control Flow

`main` parses count, interface, driver/SKB mode, and server/client mode. It resolves the destination in client mode, loads `<argv0>_kern.bpf.o`, selects `xdping_server` or `xdping_client`, finds the first map, installs signal cleanup, attaches XDP, and either idles forever in server mode or seeds the map with remote address/count, waits for setup, runs system `ping`, then prints XDP RTT data from the map and detaches.

## State and Persistence Behavior

State includes the temporary XDP attachment and map entry keyed by remote IPv4 address. Cleanup detaches XDP and client mode deletes the map entry after reading stats.

## Dependencies and Integration Points

It depends on the companion BPF object, ICMP traffic through the selected interface, IPv4-only name resolution, libbpf, shell `ping`, and XDP attach mode support. It integrates userspace orchestration with BPF RTT measurement state.

## Risks and Test Signals

Risks include network disruption from XDP attach, command construction through `system`, relying on final regular ping RTT behavior, map discovery by first-map order, and stale attachment on abrupt process death. Signals are successful attach, normal ping success, exactly `count` nonzero RTT samples, and map entry deletion.
