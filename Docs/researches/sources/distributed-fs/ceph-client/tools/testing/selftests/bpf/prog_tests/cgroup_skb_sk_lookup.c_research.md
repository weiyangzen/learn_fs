# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_skb_sk_lookup.c

## Purpose
This test validates `sk_lookup` behavior from a cgroup skb ingress program, ensuring clients in the attached cgroup can be steered to a listening socket while a socket created outside the cgroup does not connect normally.

## APIs, Types, and Functions
It uses `cgroup_skb_sk_lookup_kern.skel.h`, `bpf_program__attach_cgroup`, `test__join_cgroup`, and network helpers such as `start_server`, `connect_fd_to_fd`, `connect_to_fd`, and `accept`.

## Control Flow
The entry creates an IPv6 TCP socket before joining the test cgroup so it retains the outside cgroup association. `run_cgroup_bpf_test` loads the skeleton, joins `/foo`, attaches the ingress lookup program, and calls `run_lookup_test`. That helper starts a server, stores its port in BPF BSS, verifies the outside socket times out with `EINPROGRESS`, then verifies an inside-cgroup client connects and is accepted.

## State, Dependencies, and Integration
State includes sockets, cgroup membership, attached link, and skeleton BSS server port. Cleanup closes all sockets/Fds and destroys the skeleton.

## Risks and Test Signals
Signals are outside connection failure and inside connection success. Risks include IPv6 availability, TCP timing, socket cgroup association semantics, and sk_lookup helper behavior.
