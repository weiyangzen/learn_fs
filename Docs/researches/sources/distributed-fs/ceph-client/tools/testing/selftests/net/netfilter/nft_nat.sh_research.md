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
