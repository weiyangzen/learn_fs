# sources/distributed-fs/ceph-client/tools/testing/selftests/net/vrf_route_leaking.sh

Purpose: Comprehensive VRF route-leaking test for ICMP error route lookup, traceroute, fragmentation errors, and local TCP/UDP/ICMP connections in symmetric and asymmetric topologies across IPv4 and IPv6.

Important APIs/functions: uses namespace setup helpers, `create_vrf`, `setup_sym`, `setup_asym`, `check_connectivity`, `run_cmd_grep`, and `nettest`. Symmetric topology has h1-r1-h2 with blue/red VRFs and bidirectional route leaks; asymmetric topology uses h1/h2 bridges plus r1/r2 where return traffic uses r2 and red lacks a route back to n1.

Control flow: parses `-4`, `-6`, `-t`, `-p`, `-v`; expands named test groups; then dispatches each selected test through a `case`. Tests rebuild topology per scenario, validate base connectivity, and check traceroute hop, TTL exceeded messages, fragmentation/packet-too-big messages, local VRF ping, and local TCP/UDP via `nettest`.

State and persistence: namespaces h1/h2/r1/r2, bridges, veths, VRFs, routes, MTUs, forwarding sysctls, and background nettest servers are ephemeral. `cleanup` deletes namespaces after all tests and each setup begins with cleanup.

Dependencies and integration: requires root, VRF/veth/bridge/netns, ping or ping6, optional traceroute/traceroute6 for traceroute tests, generated `nettest`, and `lib.sh`.

Risks: grep patterns depend on ping/traceroute output text. Asymmetric topology intentionally lacks a red return leak; only TTL/traceroute style tests are suitable there. Missing traceroute prints SKIP-like text but returns from that individual test.

Test signals: pass/fail counters report each scenario. Grep success on ICMP/traceroute output and nettest exit status are the main correctness signals.
