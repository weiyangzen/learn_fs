<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/reuseport_bpf_numa.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/reuseport_bpf_numa.c

## Purpose

`reuseport_bpf_numa.c` is the NUMA-node variant of the reuseport BPF selector test. It creates one socket per NUMA node and uses an EBPF socket-filter program calling `bpf_get_numa_node_id()` to select the receiver socket corresponding to the node on which traffic is sent.

## Important APIs, Types, and Functions

Important helpers are `build_rcv_group`, `attach_bpf`, `send_from_node`, `receive_on_node`, `test`, and `setup_netns`. It uses `SO_REUSEPORT`, `SO_ATTACH_REUSEPORT_EBPF`, `bpf(BPF_PROG_LOAD)`, helper `BPF_FUNC_get_numa_node_id`, libnuma APIs `numa_available`, `numa_max_node`, `numa_run_on_node`, and `numa_bitmask_isbitset`, plus epoll and TCP/UDP sockets.

## Control Flow

Main unshares a network namespace, skips via `ksft_exit_skip` if NUMA is unavailable, allocates one receiver slot per possible node, and tests IPv4 UDP, IPv6 UDP, IPv4 TCP, and IPv6 TCP. Each test attaches the EBPF program, registers receivers, iterates available nodes forward and backward, pins the process to the node for sending, and verifies that the receiving socket index equals the NUMA node ID.

## State and Persistence Behavior

State is a private netns, loopback up state, receiver sockets on port 8888, a loaded EBPF selector, epoll state, libnuma CPU placement of the current process, and transient sender sockets. All sockets and BPF FDs are closed normally.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies include libnuma, NUMA-capable kernel/userspace, EBPF socket filter support, helper availability, namespace privileges, and TCP/UDP IPv4/IPv6 loopback. Integration points are `bpf_get_numa_node_id()` in socket filters and reuseport index selection. Risks include sparse node IDs requiring enough sockets for holes, loopback receive path not preserving node expectations, no NUMA API causing a skip, and BPF permission/memlock failures. Signals are `send node X, receive socket X` for available nodes and final `SUCCESS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/reuseport_bpf_numa.c -->
