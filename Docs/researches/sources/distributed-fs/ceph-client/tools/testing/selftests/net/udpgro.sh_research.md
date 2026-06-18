# sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgro.sh

Purpose: Functional UDP GRO test matrix over veth, validating unaggregated receive, GRO aggregation, UDP_GRO cmsg reporting, custom segment sizes, NAT-induced socket lookup behavior, and multiple GRO sockets for IPv4 and IPv6.

Important APIs/functions: uses `udpgso_bench_tx` as traffic generator and `udpgso_bench_rx` as receiver/verifier. `cfg_veth()` creates host plus peer namespace veth with IPv4/IPv6 addresses and enables GRO on peer. `run_one()`, `run_one_nat()`, and `run_one_2sock()` launch receiver(s), wait for UDP port readiness via `wait_local_port_listen`, run TX, and aggregate exit status using `check_err()`.

Control flow: no-arg `run_all()` executes IPv4 and IPv6 cases. Each case re-execs in a fresh namespace through `in_netns.sh` and a private peer namespace. It tests no GRO with ten 1400-byte packets, absence of UDP_GRO cmsg with `-S -1`, one aggregated GSO datagram, correct cmsg segment size, custom segment size 500, NAT lookup bypass using iptables/ip6tables DNAT, and two-socket delivery on different ports.

State and persistence: ephemeral namespaces, veths, iptables NAT rules, background receiver PIDs, and process-local `ret`. `trap cleanup EXIT` kills jobs and deletes the peer namespace.

Dependencies and integration: requires root, iproute2, ethtool, iptables/ip6tables NAT, compiled benchmark helpers, and `lib.sh`. Uses kselftest-style exit code via script status.

Risks: relies on veth NAPI timing for aggregation and on iptables availability. The string split around literal `rx` is simple but controlled by callers. Background receiver synchronization depends on local port readiness.

Test signals: expected packet count, length, UDP_GRO cmsg size, and exit status from RX/TX determine pass/fail. NAT and two-socket cases catch socket lookup and GRO destination matching regressions.
