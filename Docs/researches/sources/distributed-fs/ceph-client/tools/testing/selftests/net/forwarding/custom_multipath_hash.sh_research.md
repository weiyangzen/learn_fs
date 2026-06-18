# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/custom_multipath_hash.sh

## Purpose
`custom_multipath_hash.sh` tests native IPv4 and IPv6 ECMP distribution when the kernel is configured for custom multipath hashing. It verifies that only the fields selected by `fib_multipath_hash_fields` affect path selection.

## Important APIs, Functions, and Control Flow
The script builds an eight-interface topology: H1, SW1, two parallel routed links, SW2, and H2. SW1 and SW2 each have multipath routes for the opposite host subnet. `ping_ipv4` and `ping_ipv6` establish baseline reachability. Flow generators vary exactly one field at a time: source IPv4, destination IPv4, UDP source/destination ports, source IPv6, destination IPv6, IPv6 flow label, and UDP ports.

`custom_hash_test` snapshots TX packet counters on SW1’s two path interfaces, runs a generator, computes per-path deltas, calculates percentage imbalance through `bc`, and expects it to be within plus/minus 20 percent for balanced cases or outside that range for unbalanced cases. `custom_hash_v4` sets `net.ipv4.fib_multipath_hash_policy=3`, raises IPv4 neighbor GC thresholds for high destination churn, then tests field masks `0x0001`, `0x0002`, `0x0010`, and `0x0020`. `custom_hash_v6` does the same for `net.ipv6` and additionally tests flow label mask `0x0008`.

## State, Dependencies, Integration Points, and Risks
State includes VRFs, routes, sysctls, neighbor GC thresholds, link counters, and generated traffic. Dependencies include `lib.sh`, `$MZ`, `$PING6`, `bc`, `ip vrf exec`, and sysctl save/restore helpers. The test is statistical: insufficient traffic, noisy counters, packet loss, or neighbor churn can make balance thresholds flaky. It restores sysctls after each family-specific suite.

## Test Signals
Signals are ping success plus `custom_hash_test` balance assertions and logged packet deltas. A mismatch between selected hash field and observed balanced/unbalanced distribution fails the test.
