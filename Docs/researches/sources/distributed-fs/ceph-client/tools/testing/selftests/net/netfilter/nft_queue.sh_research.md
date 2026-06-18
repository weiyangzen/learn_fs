<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_queue.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_queue.sh

## Purpose
This kselftest validates nftables `queue`/NFQUEUE behavior across all major hooks and multiple protocols. It checks queue bypass, packet drops without listeners, multi-chain queueing, TCP forwarding and loopback queueing, requeueing, SCTP with GSO, UDP NAT races, UDP GRO conntrack retention, stress behavior, VRF output/postrouting queueing, and cleanup while packets are queued.

## Important APIs, Types, And Functions
The script uses `lib.sh`, `nft`, `ip`, `ss`, `socat`, `conntrack`, `ethtool`, `modprobe sctp`, compiled helpers `./nf_queue` and `./connect_close`, and many shell helpers: `load_ruleset()`, `load_counter_ruleset()`, `test_ping()`, `test_queue_blackhole()`, `nf_queue_wait()`, `test_queue()`, `test_tcp_*()`, `test_sctp_*()`, `test_udp_nat_race()`, `test_udp_gro_ct()`, `test_queue_stress()`, `test_queue_removal()`, and `test_icmp_vrf()`.

## Control Flow
It builds a router with three endpoint namespaces and IPv4/IPv6 routes. Initial rules queue ICMP/ICMPv6 across prerouting/input/forward/output/postrouting with bypass, then blackhole tests prove queues without bypass drop traffic. Dedicated phases start NFQUEUE listener programs, generate traffic with ping, `socat`, and helper binaries, compare output files, inspect nft counters, and validate conntrack. The script ends with stress and taint checks, VRF-specific queue counters, and queued-packet removal behavior.

## State, Persistence, And Dependencies
State includes namespaces, large sparse temp files, nft rulesets, NFQUEUE listener processes, conntrack entries, socket listeners, ethtool GRO settings, VRF devices, and kernel taint snapshots. Cleanup kills namespace processes, removes temp files, and removes namespaces. The test requires nftables queue support, nfnetlink_queue, veth, `socat`, `conntrack`, helper binaries from the selftest build, and optional SCTP/GRO support for full coverage.

## Integration Points
This is a high-value integration test for netfilter queue reinjection semantics, userspace NFQUEUE helpers, conntrack interaction with NAT/GRO, and routing/VRF hook ordering. It spans both local and forwarded traffic.

## Risks
The test is timing and resource sensitive because it uses large transfers, delayed queues, flood pings, and background listeners. Some paths skip or fail depending on SCTP, GRO offloads, `conntrack`, or helper availability. Counter expectations rely on exact hook traversal and may expose intentional kernel behavior changes.

## Test Signals
Signals include expected queue event totals, successful TCP/SCTP file comparisons, one conntrack entry for the UDP NAT race, matching queued/reinjected counters for UDP GRO, no new kernel taint, and PASS lines for stress, VRF, and queue-removal phases. Failures dump rulesets, counters, conntrack output, or file diffs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_queue.sh -->
