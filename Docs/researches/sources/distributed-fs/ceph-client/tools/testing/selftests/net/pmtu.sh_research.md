<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/pmtu.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/pmtu.sh

## Purpose

`pmtu.sh` is a large kselftest shell harness for route Path MTU discovery behavior. It validates cached PMTU exceptions, MTU propagation on link and tunnel changes, PMTU exception cleanup, route-cache list/flush behavior, route replacement cleanup, DSCP/ECN handling, multipath nexthop exceptions, and default/configured MTU behavior for VTI devices. The scenarios cover plain IPv4/IPv6 routing, VXLAN, GENEVE, FoU/GUE, IP-in-IP, VTI/VTI6, XFRM ESP and ESP-in-UDP, Linux bridge forwarding, and Open vSwitch forwarding.

## Important APIs, Types, and Functions

The script is built around `lib.sh` kselftest helpers such as `setup_ns`, `cleanup_all_ns`, `wait_local_port_listen`, `ksft_skip`, and command wrappers. Important helpers are `setup_namespaces`, `setup_routing`, `setup_routing_old`, `setup_routing_new`, `setup_policy_routing`, `setup_vxlan_or_geneve`, `setup_fou_or_gue`, `setup_ipvX_over_ipvY`, `setup_vti`, `setup_xfrm`, `setup_bridge`, `setup_ovs_bridge`, `setup_multipath`, `trace`, `cleanup`, `mtu`, `link_get_mtu`, `route_get_dst_pmtu_from_exception`, `check_pmtu_value`, `run_test`, and `run_test_nh`. External integration is through `ip`, `tc`, `ping`, `ping6`, `socat`, `tcpdump`, `taskset`, `nettest`, `ovs-vsctl`, and the local Open vSwitch datapath utility.

## Control Flow

The `tests` table maps test names to descriptions and whether the test is rerun with nexthop objects when `ip nexthop` is supported. Startup parses `-p`, `-t`, and `-v`, validates requested test names, cleans any previous topology, probes nexthop support, then iterates the table. Each test runs in a subshell with an EXIT trap so namespace, OVS, tcpdump, socat, and nettest state is cleaned even on failures. Common test patterns are: create namespaces and links, assign MTUs and routes, send oversized traffic with DF/PMTU discovery enabled, inspect `ip route get` or `ip route list cache`, mutate local or remote MTU, and compare the parsed `mtu` or `lock mtu` value with the expected result.

## State and Persistence Behavior

State is deliberately transient: network namespaces `NS_A`, `NS_B`, `NS_C`, `NS_R1`, `NS_R2`, veth pairs, bridges, tunnel devices, OVS datapaths, XFRM state/policy, route/nexthop objects, qdiscs, and route exception caches. The only durable artifacts are optional trace pcaps named from the current test/interface when tracing is enabled. Cleanup kills background captures and test daemons, removes namespaces, deletes leaked init-namespace veth/OVS devices, and removes temporary output files.

## Dependencies, Integration Points, Risks, and Test Signals

The test requires root/CAP_NET_ADMIN, kernel support for namespaces, veth, IPv6, tunnels, xfrm, PMTU exception caching, and sometimes OVS, FoU/GUE, VTI, dummy, tcpdump, taskset, nettest, and socat. It integrates directly with kernel routing, tunnel PMTU accounting, fib nexthop objects, XFRM encapsulation, bridge/OVS forwarding, route-cache flushing, and device unregister paths. Risks include environmental skips, brittle exact MTU overhead calculations, timing in cleanup checks, stale init-namespace devices after interrupted OVS tests, and tool-version differences in `ip route` output parsing. Strong signals are `[ OK ]` lines from `run_test`, expected PMTU values such as `1400`, `1500`, tunnel-overhead-adjusted MTUs, absence of exceptions where expected, cache counts of 101 before flush and zero after flush, timely veth deletion, and successful reruns through nexthop-object routes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/pmtu.sh -->
