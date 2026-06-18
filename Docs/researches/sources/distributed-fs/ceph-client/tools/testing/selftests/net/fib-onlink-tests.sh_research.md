# sources/distributed-fs/ceph-client/tools/testing/selftests/net/fib-onlink-tests.sh

Purpose: this script validates IPv4 and IPv6 `onlink` route handling for valid and invalid nexthops across default table, VRF table, policy-routing table, and multipath routes.

Important APIs and functions: it uses `setup_ns`, `ip route add ... onlink`, `ip -6 route add ... onlink`, VRF creation (`ip link add type vrf table`), veth pairs, link-local lookup, and helper functions `run_ip`, `run_ip_mpath`, `run_ip6`, `run_ip6_mpath`, `valid_onlink_ipv4`, `invalid_onlink_ipv4`, `valid_onlink_ipv6`, and `invalid_onlink_ipv6`.

Control flow: `setup` creates two namespaces, a VRF `lisa` with table 1101, four veth pairs with odd ends in ns1 and even ends in ns2, enslaves selected ns1 interfaces to the VRF, assigns IPv4/IPv6 addresses, and installs IPv6 defaults. The IPv4 valid suite adds host routes via connected and recursive unicast gateways, including device mismatch and multipath combinations. IPv4 invalid cases expect iproute2 exit code 2 for local unicast gateways, multicast gateways, and missing nexthop device. IPv6 valid cases add unicast, recursive, v4-mapped, device mismatch, and multipath onlink routes. IPv6 invalid cases include local unicast, local link-local, multicast, VRF equivalents, and missing device.

State and persistence: all state is namespace-local routes, VRF, veths, and addresses. Cleanup removes the namespaces at the end. No files are written.

Dependencies and integration points: requires root, VRF, veth, IPv6, and iproute2 with onlink route syntax. It directly targets FIB nexthop validation paths.

Risks and test signals: expected failure code 2 is iproute2-specific and could change with tool behavior. `run_ip_mpath` contains an unused `dev` variable check, but the caller supplies device strings inside nexthop arguments so the tests still form intended commands. Strong signals are exact command return codes for every valid and invalid route addition.
