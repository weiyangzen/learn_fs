<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/reuseport_bpf_cpu.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/reuseport_bpf_cpu.c

## Purpose

`reuseport_bpf_cpu.c` verifies CPU-aware `SO_REUSEPORT` selection. It creates one receiver socket per online CPU, attaches a classic BPF program returning `SKF_AD_CPU`, sends loopback traffic while pinned to each CPU, and checks that the socket matching the sending CPU receives the packet.

## Important APIs, Types, and Functions

Important helpers are `build_rcv_group`, `attach_bpf`, `send_from_cpu`, `receive_on_cpu`, `test`, and `setup_netns`. It uses `SO_REUSEPORT`, `SO_ATTACH_REUSEPORT_CBPF`, classic BPF ancillary load `SKF_AD_OFF + SKF_AD_CPU`, `sched_setaffinity`, `sysconf(_SC_NPROCESSORS_ONLN)`, epoll, TCP/UDP sockets, and namespace unshare.

## Control Flow

Main creates a network namespace, counts online CPUs, allocates receiver FD storage, and runs `test` for IPv4 UDP, IPv6 UDP, IPv4 TCP, and IPv6 TCP. Each `test` creates the reuseport group, attaches BPF to the first socket, registers all receivers in epoll, then sends and receives in forward CPU order, reverse order, even CPUs, and odd CPUs. A mismatch between CPU ID and receiving socket index is fatal.

## State and Persistence Behavior

State is a private network namespace, loopback up state, receiver sockets on port 8888, epoll FD, current process CPU affinity, and transient sender sockets. Affinity changes persist for the process but the process exits after the test.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies include enough privileges for network namespace setup, CPU affinity, IPv6, TCP/UDP loopback, and classic reuseport BPF support. Integration points are `skb->hash`/CPU ancillary exposure to CBPF and reuseport index selection. Risks include non-contiguous or disallowed CPU affinity masks, systems where loopback receive CPU does not equal sender CPU, large CPU counts causing many sockets, and fixed port conflicts if namespace setup fails. Signals are `send cpu X, receive socket X` for all permutations and final `SUCCESS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/reuseport_bpf_cpu.c -->
