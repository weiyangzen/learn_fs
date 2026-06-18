# sources/distributed-fs/ceph-client/tools/testing/selftests/net/traceroute.sh

Purpose: Bash kselftest for IPv4 and IPv6 traceroute behavior across namespace topologies, VRF devices, and ICMP RFC 5837 extension reporting. It validates that ICMP error source address selection uses the correct ingress or forwarding interface address rather than a bridge, wrong subnet, or VRF master address.

Important APIs/functions: sources `lib.sh` for `setup_ns`, `cleanup_ns`, `cleanup_all_ns`, `check_err`, `check_fail`, `log_test`, `log_test_skip`, and `require_command`. `run_cmd()` wraps `ip netns exec` and optional verbose logging. `create_ns()` applies loopback addresses, unreachable default routes, forwarding, ICMP ratelimit, and IPv6 DAD/forwarding sysctls. `connect_ns()` creates veth pairs and assigns IPv4/IPv6 addresses. Version helpers require traceroute/traceroute6 2.1.5 for extension tests.

Control flow: the main path parses `-p`/`-v`, requires `traceroute6`, `traceroute`, and `jq`, then calls `run_tests()`. The test suite builds six independent topologies: IPv6 traceroute, IPv6 traceroute with router interfaces enslaved to VRF, IPv6 ICMP extension reporting, IPv4 traceroute source address selection with `icmp_errors_use_inbound_ifaddr`, IPv4 VRF traceroute, and IPv4 ICMP extension reporting. Each setup starts from cleanup, creates namespaces/veth/bridge/VRF state, primes neighbor state with ping, runs traceroute plus grep expectations, logs, and cleans up.

State and persistence: all state is ephemeral kernel networking state in netns, veths, bridge `br0`/`br100`, VRF `vrf100`, routes, and sysctls such as `net.ipv[46].icmp*_errors_extension_mask`. No files are persisted. The global `RET`/`EXIT_STATUS` behavior comes from `lib.sh`; cleanup is explicit after each scenario.

Dependencies and integration: depends on iproute2 VRF/bridge/netns support, traceroute utilities, `jq` for JSON link ifindex extraction, ping/ping6, root privileges, and `lib.sh`. It integrates with kselftest by returning `EXIT_STATUS`.

Risks: version parsing assumes a three-component traceroute version; extension string greps are coupled to traceroute output formatting. Namespace sysctl changes require sufficient privilege and kernel support. ICMP extension tests depend on interface names/MTUs and on `jq`; neighbor priming can hide timing issues but reduces flakiness. Some commands use `eval` inside `run_cmd`, so caller-provided command strings must remain controlled.

Test signals: PASS means expected hop/source/extension strings appeared and unsupported sysctl values were rejected. SKIP is used for too-old traceroute extension support. Failures isolate source address selection regressions, VRF source leaks, RFC 5837 extension toggling, and malformed incoming-interface metadata.
