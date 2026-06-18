# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipv6_route_update_soft_lockup.sh

Purpose: Stress test for soft lockups during rapid IPv6 route replacement under heavy outgoing TCP traffic.

Important commands and state: Sources `lib.sh`; uses `iperf3`, veth namespaces, many IPv6 nexthop addresses, route add/delete loops with weighted multipath nexthops, `wait_local_port_listen`, `bc`, `nproc`, and host sysctl `kernel.softlockup_panic`.

Control flow: The script checks for `iperf3` and multicore availability, saves and sets `kernel.softlockup_panic=1`, schedules a SIGALRM after `TEST_DURATION`, creates source and sink namespaces, assigns a source address and 128 sink nexthop addresses, builds a long nexthop list, starts restart loops for iperf3 servers and clients on half the CPU count, and in parallel loops adding and deleting a route to the sink loopback address every 0.01 seconds. Cleanup kills namespace processes, detects unkillable iperf3 as soft-lockup evidence, removes namespaces, restores the sysctl, and reports pass on timeout.

State and persistence: Temporary namespaces plus a host-wide softlockup sysctl that is restored. Background loops are killed during cleanup.

Dependencies and integration: Requires root, `iperf3`, `bc`, multipath IPv6 routing, and enough CPU capacity.

Risks: It intentionally destabilizes buggy kernels by converting soft lockup into panic. Virtualized or slow machines may produce false negatives unless duration is increased.

Test signals: SIGALRM cleanup reports pass after the full duration without soft lockup; inability to terminate iperf3 or host panic indicates regression.
