# subset-b-006868 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_meta.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_meta.sh

## Purpose
This kselftest validates nftables `meta` matches on loopback traffic in an isolated network namespace. It checks ingress and egress interface identity, interface names, interface groups, interface types, protocol family, L4 protocol, packet mark, socket UID/GID, CPU, and time-window matches.

## Important APIs, Types, And Functions
The script uses `nft`, `ip netns`, `ping -m`, `taskset`, `date`, and shell helpers `cleanup()`, `check_one_counter()`, and `check_lo_counters()`. The central nftables API surface is `meta iif`, `iifname`, `iifgroup`, `iiftype`, `oif`, `oifname`, `oifgroup`, `oiftype`, `nfproto`, `l4proto`, `mark`, `skuid`, `skgid`, `cpu`, and `time`.

## Control Flow
It creates one namespace, brings up loopback, loads an `inet filter` table with named counters, verifies zero counters, sends a marked loopback ping, and checks expected packet counts. It then pins the shell to CPU 0, resets nft counters, sends another ping, and confirms the CPU meta counter increments.

## State, Persistence, And Dependencies
State is limited to a temporary netns, loopback address, nftables ruleset, process CPU affinity, and counters. The cleanup trap deletes the namespace. The test depends on nftables meta expression support, `iproute2`, `ping`, `taskset`, and root privileges.

## Integration Points
This is a focused nftables meta-expression regression test in the netfilter selftest suite. It exercises both input and output hook paths and validates that loopback packets produce the expected two hook observations.

## Risks
The CPU test assumes `taskset -p 01 $$` causes the packet-processing path to see CPU 0, which may be sensitive to scheduler and namespace behavior. Time matching depends on system date and nftables time parser support. The cleanup path assumes namespace creation succeeded.

## Test Signals
PASS output reports expected meta counters and CPU counter behavior. Failure signals are mismatched named counters, nft ruleset load failures, missing `nft`, and nonzero exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_meta.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_nat.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_nat.sh

## Purpose
This large kselftest exercises nftables NAT behavior across three namespaces: a router namespace and two endpoint namespaces. It covers local DNAT, DNAT with port-only rewrite, masquerade, redirect, inet-family NAT, port-shadowing mitigations, stateless address rewrite, fragmented UDP through stateless NAT, and a DNAT clash regression.

## Important APIs, Types, And Functions
The script sources `lib.sh` and uses `setup_ns`, `cleanup_all_ns`, `checktool`, and `busywait`. Local helpers include `do_config()`, `bad_counter()`, `check_counters()`, `check_ns0_counters()`, `reset_counters()`, NAT-specific test functions, `listener_ready()`, `test_port_shadow*()`, `file_cmp()`, `ping_basic()`, and `test_basic_conn()`. It drives `ip`, `nft`, `ping`, `socat`, `conntrack`, `dd`, and namespace-scoped sysctls.

## Control Flow
After tool checks, it creates a router with two veth links, assigns IPv4/IPv6 addresses, installs counter maps in all namespaces, and proves baseline connectivity. It then runs IPv4, IPv6, and conditional `inet` NAT cases. For each NAT mode it installs nft tables/chains, generates ping or `socat` traffic, checks source/destination counter changes, flushes or deletes rules, and resets counters between cases. Later phases test UDP port-shadow behavior under default masquerade and three mitigations, stateless map-based source/destination rewrites including fragmentation, and repeated UDP DNAT to catch conntrack tuple clashes.

## State, Persistence, And Dependencies
State includes netns topology, temporary input/output files, nftables rulesets, conntrack entries, sysctls enabling forwarding, and background `socat` listeners. Cleanup kills namespace processes, removes temp files, and deletes namespaces. Required dependencies include nftables NAT support, veth, `socat`, `conntrack` for port-shadow tests, and root-capable namespace operations.

## Integration Points
This script is a broad integration test for nftables NAT, conntrack, inet-family NAT hooks, counter maps, policy around service-port shadowing, and defragmentation ordering. It also validates compatibility between nftables rules and common userspace traffic generators.

## Risks
The test is timing-sensitive around listener startup and background process cleanup. Exact counter byte counts assume ping payload/header sizes and may shift if tool defaults change. Optional `inet` NAT is disabled on ruleset load failure, so downstream coverage depends on kernel support. Port-shadow behavior depends on conntrack flushing and UDP tuple timing.

## Test Signals
Strong signals are PASS lines for baseline routing and each NAT scenario, expected packet/byte counters, successful file comparisons for UDP payloads, and successful `socat` replies. Failure signals include unexpected nft counter values, ping or connection failures, missing return payloads, failed ruleset deletion, and nonzero final `ret`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_nat.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_nat_zones.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_nat_zones.sh

## Purpose
This test validates connection tracking zones combined with NAT source port reallocation when many clients share the same IP address and source port. The gateway must isolate identical tuples by ingress interface/zone and still NAT all connections to a common server.

## Important APIs, Types, And Functions
The script uses `lib.sh` helpers, `nft`, `ip -batch`, `conntrack`, `socat`, `ping`, namespace sysctls, and `ss`. The key helper is `listener_ready()`. The nftables rules use maps from interface name to mark and conntrack zone, dynamic sets for ICMP/TCP flow accounting, `ct original zone set`, `ct mark`, policy routing marks, and `masquerade`.

## Control Flow
It creates gateway and server namespaces plus up to `maxclients` client namespaces, with all clients using the same client IPs. Batched `ip` commands configure per-client veths, duplicate gateway-side addresses, policy routing tables, and fwmark rules. The gateway nft rules assign zones and marks by input interface, record flow tuples in dynamic sets, and masquerade toward the server. The script first runs parallel pings and validates dynamic ICMP set counters, then runs TCP `socat` connections from all clients using source port 10000 and verifies dynamic TCP flow entries.

## State, Persistence, And Dependencies
State includes many netns, veth devices, policy routing tables, neighbor-cache sysctl changes, nft dynamic sets/maps, conntrack zones, and a server `socat` process. Cleanup restores neighbor GC thresholds and removes namespaces. `KSFT_MACHINE_SLOW=yes` reduces client count.

## Integration Points
This is an end-to-end stress/regression test for nf_conntrack zone isolation, NAT port reallocation, dynamic nft sets, mark-reflect sysctls, and policy routing. It complements simpler NAT tests by forcing tuple collisions at scale.

## Risks
The test is resource-heavy and can be slow on debug/KASAN kernels. It assumes per-interface duplicate addressing and large dynamic sets are supported. Failures may arise from neighbor table limits, missing `socat`, or timing on listener readiness.

## Test Signals
PASS conditions are successful ping from all clients, exact ICMP counter totals per client and server-facing interface, successful TCP connections from all clients, and expected TCP flow entries in gateway nft sets. Failures print missing set elements, conntrack stats, or connection errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_nat_zones.sh -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_synproxy.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_synproxy.sh

## Purpose
This script verifies nftables `synproxy` can establish a TCP connection through a router when direct SYN forwarding is otherwise blocked. It uses `iperf3` to prove application data can pass after SYN proxy negotiation.

## Important APIs, Types, And Functions
The script uses `lib.sh`, `nft`, `ip`, `iperf3`, `modprobe nf_conntrack`, veth devices, and namespace-scoped sysctls. The nft rules combine raw-priority `notrack` for incoming SYNs, `ct state new,established accept`, `synproxy mss 1460 sack-perm timestamp`, invalid drops, and a final SYN drop.

## Control Flow
It creates router, client, and server namespaces; configures two subnets; enables IPv4 forwarding and strict TCP conntrack mode; validates bidirectional ping; starts an `iperf3` server; installs the synproxy ruleset; then runs a bounded `iperf3` client transfer from client to server.

## State, Persistence, And Dependencies
State includes the three namespaces, veth links, forwarding/sysctl settings, conntrack module state, an nft ruleset in the router, and a background `iperf3` server. Cleanup kills endpoint namespace processes and removes namespaces.

## Integration Points
This test covers nftables synproxy integration with conntrack strictness, raw-hook notrack behavior, forward-hook policy, and real TCP data transfer. It is part of netfilter selftest coverage for TCP handshake proxying.

## Risks
It depends on `iperf3`, nft synproxy support, conntrack, and root network namespace operations. A one-second server startup sleep is a simple readiness mechanism and can be fragile on slow hosts. The test is IPv4-only despite using an `inet` table.

## Test Signals
PASS is a successful 1 MiB `iperf3` transfer through the synproxy rules. Failure signals are ping failures, inability to load the nft synproxy ruleset, `iperf3` client failure, and dumped router ruleset on transfer failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_synproxy.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_tproxy_tcp.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_tproxy_tcp.sh

## Purpose
This kselftest validates nftables transparent proxy (`tproxy`) handling for TCP in IPv4 and IPv6, for both forwarded traffic and locally originated router traffic. It confirms only traffic to the selected destination is intercepted and that unrelated destinations still reach their real servers.

## Important APIs, Types, And Functions
The script uses `lib.sh`, `nft`, `ip rule`, local route tables, `socat` with `ip-transparent`, and helper functions `test_ping()`, `test_ping_router()`, `listener_ready()`, `test_tproxy()`, and protocol/origin wrappers. The nft rules use prerouting `tproxy $ip_proto to :12345 meta mark set 1` and, for local-origin cases, route-output marking.

## Control Flow
It builds a router connected to three endpoint namespaces with IPv4 and IPv6 addressing and forwarding. `test_tproxy()` derives protocol-specific addresses and rules, installs fwmark policy routing to local delivery, starts a transparent echo proxy on the router plus normal TCP servers in ns2/ns3, then sends four requests: ns1 to ns2, ns1 to ns3, router to ns2, and router to ns3. Expected replies distinguish proxied echo from real `PONG_NS*` servers.

## State, Persistence, And Dependencies
State includes four namespaces, veth topology, policy-routing table 100, fwmark rules, nft rulesets, and background `socat` listeners. Cleanup kills namespace processes and removes namespaces; each test case deletes its policy route state.

## Integration Points
This test ties nftables tproxy expressions to Linux policy routing, transparent sockets, IPv4/IPv6 forwarding, and local output marking. It validates both route and filter hook participation.

## Risks
The test depends on `socat` transparent socket support and has comments for a known socat 1.8.0 family-binding bug. Listener timing and policy route cleanup are important; stale table 100 routes could affect later cases. It assumes tproxy support in the kernel and nft.

## Test Signals
PASS lines compare each returned string with expected proxy or real-server output. Failures are wrong replies, missing connectivity before tproxy, nft ruleset/policy route errors, or nonzero final status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_tproxy_tcp.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_tproxy_udp.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_tproxy_udp.sh

## Purpose
This script validates nftables transparent proxy behavior for UDP forwarding over IPv4 and IPv6. It ensures UDP traffic to ns2 can be intercepted and relayed by a transparent proxy while traffic to ns3 and router-originated traffic remain unproxied.

## Important APIs, Types, And Functions
The script uses `lib.sh`, `nft`, `ip rule`, local route table 100, `socat` UDP listeners with `ip-transparent`, and helpers `test_ping()`, `test_ping_router()`, `listener_ready()`, and `test_tproxy_udp_forward()`. The nft rule is a prerouting `udp dport 8080 tproxy ... meta mark set 1` match.

## Control Flow
It creates the same four-namespace, three-subnet router topology as the TCP tproxy test. For each address family, it adds fwmark routing for ns2's address, installs a tproxy rule, starts a UDP transparent relay on the router and normal UDP servers in ns2/ns3, then sends packets from ns1 and nsrouter to ns2/ns3. ns1-to-ns2 should echo through the proxy; other paths should return real server strings.

## State, Persistence, And Dependencies
State includes namespace topology, forwarding sysctls, policy routing, nft rules, and background UDP `socat` listeners. The UDP timeout is longer than TCP because datagram relay startup and response timing are slower. Cleanup removes namespace processes and all namespaces.

## Integration Points
This is the UDP companion to TCP tproxy coverage and validates nftables tproxy with datagram transparent sockets and policy routing. It also checks that local router-originated traffic is not captured in the forward-only UDP scenario.

## Risks
UDP tests are timing-sensitive and depend on `socat` behavior with `shut-none`, `reuseport`, and transparent bind options. The script only tests forwarded tproxy, not local-output UDP interception. Stale fwmark routes would affect later protocol cases if cleanup failed.

## Test Signals
PASS output is based on exact returned strings for ns1/nsrouter to ns2/ns3. Wrong strings, timeouts, missing listeners, or baseline ping failures set `ret=1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_tproxy_udp.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_zones_many.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_zones_many.sh

## Purpose
This test measures and validates insertion of many conntrack entries that share identical addresses and ports but live in distinct conntrack zones. It covers both packet-path insertion through nftables and optional ctnetlink insertion through the `conntrack` tool.

## Important APIs, Types, And Functions
The script uses `lib.sh`, `nft`, `socat`, optional `conntrack`, `date +%s%3N`, and helpers `test_zones()` and `test_conntrack_tool()`. The nft rules use a `numgen inc mod` expression mapped to `ct zone set`, and the ctnetlink path uses `conntrack -I --zone`.

## Control Flow
It creates one namespace, installs nft rules that assign outgoing UDP packets to zones, populates the zone map, sends batches of 1000 UDP packets with identical endpoint tuples, and optionally checks `conntrack -C` for at least the requested count. If `conntrack` is available, it flushes state and inserts the same number of TCP entries directly via ctnetlink, reporting per-1000 timings and final counts.

## State, Persistence, And Dependencies
State is confined to one namespace, nft rules/maps, UDP conntrack timeout, and conntrack table entries. Cleanup removes namespaces. `KSFT_MACHINE_SLOW=yes` lowers the zone count from 2000 to 500.

## Integration Points
This is a performance/regression probe for conntrack zone hash behavior and nftables zone assignment. It complements `nft_nat_zones.sh` by focusing on insertion volume rather than NAT routing correctness.

## Risks
Runtime and reliability depend on host speed, conntrack table capacity, and `socat` throughput. The packet-path count check only runs when `conntrack` exists. The nft map uses `numgen` and may expose parser or modulo behavior changes.

## Test Signals
PASS lines report per-batch insertion durations and final conntrack counts. Failures are packet send errors, final count below expected, ctnetlink insertion errors, or nonzero final `ret`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_zones_many.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/packetdrill/common.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/packetdrill/common.sh

## Purpose
This common shell fragment normalizes network stack settings for netfilter packetdrill tests. It reduces timing variance, enables conntrack, and configures TCP defaults expected by packetdrill scenarios.

## Important APIs, Types, And Functions
It directly invokes `modprobe nf_conntrack`, `sysctl`, `ip tcp_metrics flush`, `tc qdisc`, and `$xtables`. It expects the caller to define `xtables` as the iptables command to use.

## Control Flow
The file runs commands at source time: loads conntrack, enables invalid logging, flushes TCP metrics, adjusts TCP rmem/wmem, sets cubic congestion control, disables slow start after idle and ECN, sets `tcp_notsent_lowat`, replaces the `tun0` qdisc with `pfifo`, and appends an INPUT conntrack match rule for TCP SYNs.

## State, Persistence, And Dependencies
This fragment mutates global or namespace sysctls, qdisc state on `tun0`, TCP metrics, module state, and iptables rules. There is no cleanup in this file; callers must run it in disposable namespaces or restore state.

## Integration Points
It is shared setup for packetdrill-based netfilter tests and links packetdrill traffic to conntrack/iptables visibility. The `$xtables` hook allows callers to choose legacy or nft-backed iptables tooling.

## Risks
Because it executes immediately and has no guards around all commands, missing `tun0`, missing `$xtables`, or permission problems can break callers. Sysctl changes may leak when not run inside a test namespace. The qdisc replacement is intentionally chosen to avoid FQ pacing but assumes packetdrill timing needs.

## Test Signals
The file itself emits no PASS/FAIL output. Downstream signals are reduced packetdrill timing flakes and conntrack-enabled packet traces; setup errors surface as command failures in the caller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/packetdrill/common.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/rpath.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/rpath.sh

## Purpose
This test validates reverse-path filtering matches in iptables/ip6tables and nftables. It checks that martian traffic fails rpfilter/fib reverse-path matches while regular traffic passes, both before and after putting an interface into a VRF.

## Important APIs, Types, And Functions
The script uses `lib.sh`, `iptables` or `iptables-legacy`, `ip6tables` or legacy, `nft`, `ip netns`, `ping`, veth/dummy/VRF devices, and helpers `die()`, `ipt_zero_rule()`, `ipt_zero_reverse_rule()`, `nft_zero_rule()`, `netns_ping()`, `clear_counters()`, and `testrun()`. nft coverage uses `fib saddr . iif oif exists`.

## Control Flow
It chooses available firewall tools, creates two namespaces, configures normal veth-connected addresses and martian addresses where ns2 routes return traffic via a dummy device, installs rpfilter/inverted rules, and adds static IPv6 neighbors. `testrun()` clears counters, sends martian pings that should fail, verifies only inverted rpfilter rules match, then sends regular pings and verifies normal rules match. It repeats after enslaving veth to a VRF in ns2.

## State, Persistence, And Dependencies
State includes namespaces, veth/dummy/VRF devices, IPv4/IPv6 addresses, static neighbors, raw-table iptables rules, and nft rules. Cleanup removes namespaces. The test can run with any of iptables, ip6tables, or nft present, but full coverage requires all.

## Integration Points
It bridges legacy xtables `rpfilter` behavior and nftables FIB expression behavior, including VRF routing semantics. It is a regression test for source validation in netfilter prerouting.

## Risks
Tool availability changes coverage. Counter parsing depends on iptables `-vS` and nft chain output formats. VRF support may be unavailable, and static neighbor setup assumes predictable veth MAC parsing.

## Test Signals
Success prints `PASS: netfilter reverse path match works as intended`. Failures identify whether martian or regular traffic matched incorrectly for iptables, ip6tables, or nft, and exit immediately.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/rpath.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/sctp_collision.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/sctp_collision.c

## Purpose
This helper program creates an SCTP one-to-one collision scenario between a server and client using `SOCK_SEQPACKET`. It coordinates delayed connects and message exchange to reproduce SCTP conntrack or association collision behavior used by surrounding netfilter tests.

## Important APIs, Types, And Functions
The single `main()` uses `socket(AF_INET, SOCK_SEQPACKET, IPPROTO_SCTP)`, `bind()`, `listen()`, `setsockopt(SO_RCVTIMEO)`, `connect()`, `sendto()`, `recvfrom()`, `sleep()`, `usleep()`, `inet_addr()`, `htons()`, and `close()`.

## Control Flow
The program expects `server|client LOCAL_IP LOCAL_PORT REMOTE_IP REMOTE_PORT`. Both roles bind and listen on their local address and configure a receive timeout. The server sleeps to allow the client INIT, connects to the peer, receives a message, and echoes it. The client waits briefly for listening, connects, sleeps to delay data until after the server's INIT_ACK timing, sends `hello`, and waits for the echoed response.

## State, Persistence, And Dependencies
State is one SCTP socket and stack SCTP address structures. There is no filesystem persistence. It depends on kernel SCTP support and the test harness to create addresses, routes, and concurrent server/client processes.

## Integration Points
The helper is intended for netfilter/SCTP collision tests that need deterministic bidirectional SCTP setup and controlled timing. Its output strings are simple harness-readable milestones.

## Risks
Timing uses fixed sleeps, which can be fragile on slow or heavily loaded systems. Error handling prints generic messages without `errno`, making diagnostics limited. `inet_addr()` supports only IPv4 dotted decimal and cannot report all parse errors distinctly.

## Test Signals
Successful server output is `Server: sent!` and successful client output is `Client: rcvd!`, with return code 0. Any socket, bind, listen, connect, send, receive, or timeout failure returns nonzero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/sctp_collision.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/udpclash.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/udpclash.c

## Purpose
This helper emits many concurrent UDP datagrams from one socket to the same remote tuple to exercise conntrack clash-resolution races. It mimics resolver libraries that send parallel requests sharing source and destination tuples.

## Important APIs, Types, And Functions
Core pieces are `struct thread_args`, global `wait`, `thread_main()`, `run_test()`, and `main()`. It uses pthreads, a nonblocking `SOCK_DGRAM|SOCK_CLOEXEC` socket, `sendto()`, `recvfrom()`, `bind()`, `inet_ntop()`, `inet_addr()`, and `usleep()`.

## Control Flow
`main()` parses destination IP/port, creates and binds an unconnected UDP socket to an ephemeral local port, and calls `run_test()`. `run_test()` creates 128 threads that spin on a shared flag, releases them simultaneously, joins all sends, then polls the socket until it receives 128 replies or times out. It validates reply source address and port against the requested remote.

## State, Persistence, And Dependencies
State is process-local: one UDP socket, thread IDs, a shared wait flag, and receive counters. It has no persistent files. The surrounding test must provide an echo server and any netfilter/conntrack rules under test.

## Integration Points
This binary is a targeted stress generator for nf_conntrack insertion clash logic. It pairs with netfilter tests that inspect whether racing UDP packets create correct state and receive all replies.

## Risks
The busy-wait flag is `volatile int`, not a formal synchronization primitive, although thread creation/join timing is sufficient for this test style. A send failure exits the whole process from a worker thread. Nonblocking receive loops use a fixed 5 second aggregate timeout and may be flaky under severe load.

## Test Signals
Success prints `got 128 of 128 replies` and returns 0. Fewer replies, wrong source warnings, socket/bind errors, allocation failure, or pthread failures indicate regressions or environment problems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/udpclash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/vxlan_mtu_frag.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/vxlan_mtu_frag.sh

## Purpose
This test checks that large packets through a VLAN-aware bridge with an external VXLAN device and br_netfilter do not panic when VXLAN MTU forces fragmentation. Packet delivery is expected to fail; absence of kernel crash is the pass condition.

## Important APIs, Types, And Functions
The script uses `lib.sh`, `modprobe br_netfilter`, `ip`, `bridge`, `ping`, and helpers `create_topology()`, `setup_host()`, `setup_vtep()`, `setup_router()`, `setup()`, `test_large_mtu_untagged_traffic()`, `test_large_mtu_tagged_traffic()`, and `do_test()`.

## Control Flow
It checks for `br_netfilter`, creates host/vtep/router namespaces, links them with veth pairs, configures host VLAN subinterfaces, builds a VLAN-filtering bridge in the VTEP namespace, adds an external VXLAN device with VLAN-to-VNI mappings, and brings links up. Tests set VXLAN MTU to 1000 and send 2000-byte pings for VLAN-tagged and untagged traffic toward static neighbor entries.

## State, Persistence, And Dependencies
State includes namespaces, veths, VLAN subinterfaces, a bridge, VXLAN device, bridge VLAN/VNI mappings, static neighbors, and loaded br_netfilter module state. Cleanup removes namespaces. It requires bridge/VXLAN/VLAN kernel support and root privileges.

## Integration Points
This test is a netfilter/bridge/VXLAN integration regression focused on fragmentation paths with br_netfilter enabled. It exercises bridge VLAN tunnel metadata, external VXLAN mode, and oversized ICMP frames.

## Risks
Because ping failure is expected, the script can only detect command/setup errors or crashes indirectly. It does not inspect dmesg, so kernel warnings without panic may be missed. The `modprobe -n` feature check may differ from actual load behavior.

## Test Signals
Success prints the test banner and `PASS!` after traffic generation returns. Setup command failures or module absence lead to SKIP/failure; a kernel panic or hang is the primary regression signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/vxlan_mtu_frag.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/xt_string.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/xt_string.sh

## Purpose
This test validates the xtables `string` match offset semantics for Boyer-Moore and KMP algorithms, including payload before/inside/outside `--from` and `--to` bounds and patterns spanning fragmentation boundaries.

## Important APIs, Types, And Functions
It uses `lib.sh`, `iptables`, `socat`, `ip netns`, dummy devices, and helpers `add_rule()`, `showrules()`, `zerorules()`, `countrule()`, and `send()`. The tested API is `iptables -m string --string ... --algo bm|kmp --from --to`.

## Control Flow
The script creates a namespace with a dummy interface and four OUTPUT rules: bm/kmp over ranges 1000-1500 and 1400-1600. `send()` creates UDP payloads with the pattern at specified absolute packet offsets. Each phase zeroes counters, sends one or more packets, counts rules with expected packet counters, and decrements `rc` on mismatch.

## State, Persistence, And Dependencies
State includes one namespace, dummy link, iptables OUTPUT rules/counters, and a temporary payload file. Cleanup deletes the namespace and temp file. It depends on iptables string match support and `socat`.

## Integration Points
This is legacy xtables coverage rather than nftables coverage. It is useful for regression testing text-search behavior in netfilter, especially boundary handling when payload spans fragments.

## Risks
The test assumes IPv4+UDP header length of 28 bytes and depends on generated packet sizes creating the intended offsets/fragments. Counter parsing relies on iptables `-v -S` including `-c` counters. It uses negative return count values for failures, which are shell-exit-code wrapped.

## Test Signals
Success prints `PASS: string match tests`. Failures name the offset/range scenario and dump matching rules with counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/xt_string.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netlink-dumps.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netlink-dumps.c

## Purpose
This kselftest harness validates robustness of netlink dump error handling, extended ACK parsing, and socket close behavior while generic-netlink dumps are in progress or referenced by mqueue notification state.

## Important APIs, Types, And Functions
Key pieces are `struct ext_ack`, `enum get_ea_ret`, `nl_get_extack()`, static malformed request blobs `dump_neigh_bad` and `dump_policies`, and tests `dump_extack`, `test_sanity`, `close_in_progress`, and `close_with_ref`. It uses `NETLINK_ROUTE`, `NETLINK_GENERIC`, `SOL_NETLINK` options `NETLINK_CAP_ACK`, `NETLINK_EXT_ACK`, `NETLINK_GET_STRICT_CHK`, generic netlink control commands, POSIX mqueue syscalls, and `kselftest_harness.h`.

## Control Flow
`dump_extack` opens a route netlink socket with strict/extack options, sends many invalid neighbor dump requests to overflow receive buffers, observes `ENOBUFS`, then parses subsequent messages to ensure extack data reports `EINVAL` and the expected bad attribute offset. `test_sanity` proves the policy dump spans more than one message. `close_in_progress` closes a socket after starting a generic-netlink policy dump. `close_with_ref` adds a message-queue notification reference to the netlink socket before closing it.

## State, Persistence, And Dependencies
State is limited to sockets, receive buffers, and a POSIX message queue named `sed` created via syscall. There is no explicit unlink in this file. The test depends on netlink strict validation, generic netlink controller policy dumps, YNL attribute helpers, and mqueue support.

## Integration Points
It exercises kernel netlink dump lifecycle and extack reporting from userspace selftests. It integrates low-level raw netlink messages with the kselftest C harness and YNL parsing helpers.

## Risks
The exact extack offset and error sequence are tied to kernel validation behavior. The mqueue object name may persist outside the process if not cleaned by system policy. Buffer-overflow timing around ENOBUFS/EBUSY can vary, though the test tolerates early receive exhaustion after at least 10 replies.

## Test Signals
Assertions validate socket creation, send sizes, ENOBUFS observation, extack presence, `EINVAL`, bad attribute offset, multi-message dumps, and no crash on close paths. Any assertion failure is a kselftest failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netlink-dumps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netns-name.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netns-name.sh

## Purpose
This shell test verifies network device name, ifindex, and alternate-name semantics when devices are created in or moved between network namespaces. It specifically uses netdevsim for notifier-sensitive move coverage.

## Important APIs, Types, And Functions
It sources `lib.sh` and uses `setup_ns`, `create_netdevsim`, `cleanup_netdevsim`, `cleanup_ns`, `ip link set ... netns`, `ip link property add ... altname`, and dummy devices. Local helpers are `cleanup()` and `fail()`.

## Control Flow
The script creates two namespaces, moves a netdevsim device without rename, tests a move rejected due to name conflict, tests conflict resolution by renaming during move, tests alternate-name duplication rejection, tests that an alternate name moves namespace visibility correctly, and validates that identical name/ifindex pairs can exist in separate namespaces.

## State, Persistence, And Dependencies
State includes two namespaces, netdevsim device instance address 2025, dummy devices, alternate names, and selected ifindex values. Cleanup removes netdevsim and namespaces. It depends on netdevsim support and recent iproute2 alternate-name functionality.

## Integration Points
This is net core namespace/name management coverage and exercises notifier paths through netdevsim. It complements netns sysctl and netdev generic-netlink tests by validating namespace isolation at the rtnetlink/iproute2 level.

## Risks
The script relies on helper cleanup even if intermediate device deletion fails. The fixed netdevsim address can collide if parallel tests reuse it. It uses `set -o pipefail` but accumulates failures in `RET_CODE`, so later cleanup/test actions still run.

## Test Signals
The final line prints the script basename with `[  OK  ]` or `[ FAIL ]`. Each failure reports the specific invalid move, missing device, or alternate-name visibility problem.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netns-name.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netns-sysctl.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/netns-sysctl.sh

## Purpose
This test verifies selected network core buffer sysctls are visible in network namespaces, reflect the init namespace value, and are read-only from inside non-init netns.

## Important APIs, Types, And Functions
It uses `lib.sh`, `setup_ns`, `cleanup_ns`, `sysctl`, `/proc/sys/net/core`, `ip netns exec`, and local `cleanup()`/`fail()` helpers. The sysctls under test are `rmem_default`, `rmem_max`, `wmem_default`, and `wmem_max`.

## Control Flow
The script creates one test namespace. For each sysctl, it checks write permission in the init namespace, writes value `300000`, checks that the test namespace reads the same value, and verifies the file is not writable from inside the test namespace.

## State, Persistence, And Dependencies
State includes one namespace and host-level sysctl values modified to `300000`; the script does not save/restore original values. It depends on procfs sysctl exposure, namespace execution, and root privileges.

## Integration Points
This is a net namespace/sysctl regression test for shared read-only core memory settings. It validates the expected relationship between init-net writable knobs and per-netns read visibility.

## Risks
The lack of restoration can affect later tests that assume default socket buffer sysctl values. The `-e` shell mode exits immediately on unexpected command failure, so diagnostics may be limited outside explicit `fail()` calls.

## Test Signals
Success prints `Test passed OK`. Failures identify missing init-net write permission, failed write, namespace value mismatch, or unexpected writeability inside the namespace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/netns-sysctl.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/nettest.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/nettest.c

## Purpose
`nettest` is a general-purpose networking selftest utility that can run as client, server, or combined forked client/server. It exercises TCP, UDP, raw sockets, multicast, device binding, address expectations, network namespace switching, TCP MD5 signatures, DS fields, freebind, control-message device selection, XFRM UDP encapsulation, and interactive or repeated message loops.

## Important APIs, Types, And Functions
The core type is `struct sock_args`, which carries addresses, ports, socket type/protocol, namespace names, device binding, expected addresses/devices, multicast group, MD5 credentials, XFRM flags, and mode bits. Major functions include logging helpers, `switch_ns()`, `tcp_md5sig()`, `tcp_md5_remote()`, device helpers, socket-option helpers, `convert_addr()`, `validate_addresses()`, `send_msg*()`, `socket_read_*()`, `msg_loop()`, multicast socket setup, listener/client socket setup, `config_xfrm_policy()`, `do_server()`, `do_client()`, IPC helpers, and `main()` option parsing.

## Control Flow
`main()` parses a broad CLI, validates required address/port/mode combinations, resolves protocols, and chooses server, client, or both mode. Both mode forks a server child, waits for readiness over a pipe, then runs the client. Server mode can bind/listen/read datagrams or accept streams; client mode creates and optionally connects a socket, validates local/remote addresses, sends messages, and reads replies. Message loops support fixed iterations, random payloads, stdin/stdout interactive mode, cmsg packet info, and expected interface/address checks.

## State, Persistence, And Dependencies
State is process-local plus optional namespace membership changed by `setns()`. It opens sockets, may fork, and may configure per-socket TCP MD5, freebind, reuse, DS field, multicast, pktinfo, recverr, SO_BINDTODEVICE, SO_DONTROUTE, and XFRM policy options. It depends on Linux networking headers/features and root privileges for namespace and some socket options.

## Integration Points
Many shell selftests use `nettest` as a flexible endpoint generator and verifier. It integrates socket API behavior with namespaces, device routing, multicast membership, TCP authentication, and IPsec/XFRM policy plumbing.

## Risks
The CLI surface is large, so invalid combinations can produce confusing outcomes. Some functions assume address family consistency after parse. `SO_BINDTODEVICE`, TCP MD5, raw sockets, and XFRM require capabilities. The combined mode kills the child after the client finishes, which is appropriate for tests but not graceful server shutdown.

## Test Signals
Signals are exit codes plus timestamped client/server logs showing binds, peers, expected address/device matches, send/receive success, timeouts, and socket-option failures. In quiet mode, only the exit status remains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/nettest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/nk_qlease.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/nk_qlease.py

## Purpose
This Python kselftest exercises the netdev generic-netlink queue leasing API with netkit virtual devices and netdevsim physical devices. It validates successful leases, rejection paths, cleanup on device or namespace removal, channel resizing interactions, cross-namespace references, and lease persistence across link state and namespace movement.

## Important APIs, Types, And Functions
Helpers include `wait_until()`, `create_netkit()`, and `create_netkit_single()`. The test matrix uses `NetNS`, `NetNSEnter`, `NetdevFamily.queue_create()`, `queue_get()`, `bind_rx()`, `EthtoolFamily.channels_set()`, `RtnlFamily.newlink()`, `NetdevSimDev`, `cmd()`, `defer()`, `ip()`, and kselftest assertions/errors from `lib.py`. `main()` runs 45 named test functions.

## Control Flow
Each test creates isolated netdevsim and/or netkit devices, often moves the netkit guest into a test namespace, brings devices up or down, performs queue lease operations from the relevant namespace, and validates returned queue IDs or expected `NlError` errno values. The matrix covers duplicate leases, invalid lessors/lessees, queue range/type errors, physical and virtual deletion order, link flaps, multiple leases, l3/single netkit modes, netns ID validation, guest/physical namespace moves, channel shrink/grow cases, bind-rx rejection on leased queues, and capacity exhaustion.

## State, Persistence, And Dependencies
State includes temporary network namespaces, netkit pairs, netdevsim devices, NAPI/queue state, queue lease relationships, ethtool channel counts, netns IDs, and deferred cleanup callbacks. It depends on the Python netlink helpers in `lib.py`, kernel netdev-genl queue APIs, netkit, netdevsim, ethtool netlink, and sufficient privileges.

## Integration Points
This is deep integration coverage for queue leasing across generic netlink, rtnetlink-created netkit devices, simulated physical NIC queues, ethtool channel management, and netns lifetime rules. It also validates what lease information is visible from the physical side versus virtual side.

## Risks
The file is broad and newer-kernel dependent; missing netkit, netdevsim, or netdev-genl features will cause skips/failures outside the logic being tested. Many tests depend on ifindex values captured before netns moves, so kernel semantics around ifindex preservation matter. Deferred cleanup order is important for devices moved between namespaces.

## Test Signals
`ksft_run()` reports each function result. Strong signals are exact returned queue IDs, presence or absence of `lease` in `queue_get()`, expected errno values such as `EINVAL`, `EBUSY`, `EOPNOTSUPP`, `ERANGE`, and successful cleanup after deleting devices or namespaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/nk_qlease.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/nl_netdev.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/nl_netdev.py

## Purpose
This Python kselftest validates the `netdev` generic-netlink family for device queries, NAPI listing and threaded mode control, queue reset behavior, and page-pool reporting/orphaning.

## Important APIs, Types, And Functions
It uses `NetdevFamily`, `NetdevSimDev`, `NlError`, `ip()`, `ksft_run()`, `ksft_exit()`, `ksft_eq/ge/ne`, `ksft_raises`, and `ksft_busy_wait`. Test functions are `empty_check()`, `lo_check()`, `dev_dump_reject_attr()`, `napi_list_check()`, `napi_set_threaded()`, `dev_set_threaded()`, `nsim_rxq_reset_down()`, and `page_pool_check()`.

## Control Flow
The tests instantiate `NetdevFamily`, run a basic device dump, validate loopback XDP feature fields, assert that dump requests reject unexpected attributes with extack details, create netdevsim devices with controlled queue counts, inspect NAPI IDs, toggle threaded mode through both netdev-genl and sysfs, reset queues while up/down, and exercise page-pool visibility as a netdevsim device is brought up/down and holds/releases pages.

## State, Persistence, And Dependencies
State includes temporary netdevsim devices, sysfs threaded flags, netdev-genl NAPI state, page-pool references, and debugfs-like netdevsim controls (`queue_reset`, `pp_hold`). Context managers clean up devices. It depends on Python YNL/lib helpers and kernel support for netdev family operations.

## Integration Points
This test connects netdev generic-netlink reporting/control to netdevsim behavior, sysfs threaded NAPI controls, and page-pool lifetime accounting. It also validates strict policy/extack behavior for netdev dump commands.

## Risks
Threaded NAPI and page-pool fields are kernel-version sensitive. Page-pool freeing is asynchronous and uses a busy wait, so slow cleanup can be flaky. Tests rely on netdevsim debug controls and loopback ifindex 1.

## Test Signals
Signals are kselftest assertion results: device dump nonempty, expected loopback feature arrays empty, exact extack message/bad attribute, NAPI counts and threaded PID presence/absence, successful queue reset while down, and expected page-pool inflight/detach behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/nl_netdev.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/nl_nlctrl.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/nl_nlctrl.py

## Purpose
This Python kselftest validates the `nlctrl` generic-netlink controller family, especially family discovery and policy dump reporting for split-op and full-op families.

## Important APIs, Types, And Functions
It uses `NlctrlFamily`, `NetdevFamily`, `EthtoolFamily`, `ksft_run()`, `ksft_exit()`, and assertion helpers. Test functions are `getfamily_do()`, `getfamily_dump()`, `getpolicy_dump()`, and `getpolicy_by_op()`.

## Control Flow
The script queries the `netdev` family by name, rekeys its op list by command ID, and checks capability flags and notification-only exclusions. It dumps all families and confirms `nlctrl` and `netdev` are present. It then uses family helpers to retrieve operation policies for netdev split ops and ethtool full ops, checking that do/dump policies exist or are absent as expected and that attribute names are resolved.

## State, Persistence, And Dependencies
There is no persistent state; all work is generic-netlink querying. It depends on the Python netlink helper library, `netdev` and `ethtool` generic-netlink families, and kernel support for controller policy dumps.

## Integration Points
This file verifies the metadata layer consumed by other YNL-based tests. It ensures generic-netlink family operation flags and policy resolution are visible and correctly decoded for netdev and ethtool.

## Risks
It hard-codes command IDs such as netdev `dev-get` 1, `qstats-get` 12, and `napi-set` 14, so legitimate UAPI renumbering would require updates. Family availability is kernel-configuration dependent.

## Test Signals
Kselftest assertions check family names/IDs, op capability flags, dump contents, policy dictionaries, absence of notification-only ops, and no unresolved `attr-N` names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/nl_nlctrl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/openvswitch/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/openvswitch/Makefile

## Purpose
This Makefile wires the Open vSwitch network selftest directory into the kernel kselftest build system. It declares the shell test program, supporting Python file, compiler flags, and cleanup target for generated artifacts.

## Important APIs, Types, And Functions
It sets `top_srcdir`, appends to `CFLAGS`, declares `TEST_PROGS := openvswitch.sh`, `TEST_FILES := ovs-dpctl.py`, `EXTRA_CLEAN := test_netlink_checks`, and includes `../../lib.mk`.

## Control Flow
There is no runtime control flow. During kselftest build/install, `lib.mk` interprets `TEST_PROGS` as executable tests to run/install, `TEST_FILES` as support files to stage, `CFLAGS` for local compilations, and `EXTRA_CLEAN` for cleanup.

## State, Persistence, And Dependencies
Build state is limited to generated test binaries or helper artifacts in the openvswitch selftest directory. The flags depend on kernel UAPI headers under `$(top_srcdir)/usr/include` and any `KHDR_INCLUDES` supplied by the parent build.

## Integration Points
This file integrates Open vSwitch selftests with the broader `tools/testing/selftests/net` kselftest infrastructure. It ensures `openvswitch.sh` can find `ovs-dpctl.py` when staged.

## Risks
Incorrect `top_srcdir` depth or missing `lib.mk` would break builds. `-Wl,--no-as-needed` affects linker behavior for local binaries and should remain aligned with helper requirements. `EXTRA_CLEAN` must match generated artifact names.

## Test Signals
Signals are build-system level: `make -C tools/testing/selftests/net/openvswitch` should stage `openvswitch.sh` and `ovs-dpctl.py`, and `make clean` should remove `test_netlink_checks` if generated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/openvswitch/Makefile -->
