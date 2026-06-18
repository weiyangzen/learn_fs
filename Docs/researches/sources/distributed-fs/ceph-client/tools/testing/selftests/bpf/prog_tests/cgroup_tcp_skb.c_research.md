# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_tcp_skb.c

## Purpose
Tests cgroup skb ingress/egress programs on TCP connection setup, data transfer, and teardown. It exercises four combinations of client/server placement and close initiator placement relative to a test cgroup, validating observed TCP packet sequences and final socket states.

## Important APIs, types, and functions
Uses `cgroup_tcp_skb.skel.h`, `cgroup_tcp_skb.h`, `cgroup_helpers.h`, and `network_helpers.h`. `install_filters()` attaches egress and ingress programs with `bpf_program__attach_cgroup()` and resets skeleton BSS counters. `talk_to_cgroup()` and `talk_to_outside()` create IPv6 stream sockets, move the current task between root and test cgroup, connect with `connect_fd_to_fd()`, accept, write, and read. `close_connection()` performs half-close/full-close sequencing and waits for packet counters to settle. `test_cgroup_tcp_skb()` orchestrates all scenarios and checks BSS `g_unexpected` and `g_sock_state`.

## Control flow and state
The test creates `/test_cgroup_tcp_skb`, loads the skeleton, attaches a different ingress/egress program pair per scenario, performs connection traffic, validates BPF-observed TCP state, then destroys links before the next scenario. Persistent state is only runtime test state: socket FDs, cgroup FD, BPF links, and skeleton BSS fields (`g_sock_port`, `g_packet_count`, `g_sock_state`, `g_unexpected`). Cleanup closes all FDs, destroys links, cleans cgroup environment, and destroys the skeleton.

## Dependencies and integration points
Depends on cgroup v2 test helpers, IPv6 loopback sockets, generated BPF programs that implement server/client ingress/egress state machines, and test harness assertions. Integrates with the BPF selftest runner through `test_cgroup_tcp_skb()`.

## Risks and test signals
Timing is sensitive around ACK/FIN observation; `close_connection()` uses bounded sleeps and counter stabilization. Failures signal cgroup attachment problems, missed skb hooks, TCP state regression, or unexpected packet classification. The strongest signals are `g_unexpected == 0`, expected `CLOSED`/`TIME_WAIT`, and successful socket IO in each scenario.
