
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_inner_v4_multipath.sh

Purpose: Tests IPv4 payload distribution over `ip6gre` when the IPv6 underlay route uses ECMP or weighted multipath. It specifically enables inner-flow hashing with `net.ipv6.fib_multipath_hash_policy=2`.

Important APIs/functions: topology helpers `h1_create`, `sw1_create`, `sw2_create`, `sw3_create`, `sw4_create`, `h2_create`; tests `ping_ipv4`, `multipath_ipv4`; core evaluator `multipath4_test`.

Control flow: creates a 10-interface chain H1-SW1-SW2-SW3-SW4-H2. SW2 and SW3 connect through VLAN 111/222 parallel paths, with tc flower counters on SW3 ingress. `multipath4_test` changes the SW2 route weights, sends many UDP flows with varied IPv4 source/destination ranges through the tunnel, computes per-VLAN deltas, and calls `multipath_eval`.

State/persistence: creates VRFs, IPv4 host routes, IPv6 underlay addresses, VLANs, `ip6gre` tunnels `g1`/`g2`, multipath IPv6 routes, tc clsact filters, and temporarily changes a sysctl.

Dependencies/integration: relies on `lib.sh` tunnel/VLAN helpers, `MZ` traffic generation, `tc_rule_stats_get`, `multipath_eval`, and `bc` ratio math.

Risks: packet distribution is statistical and can be flaky on slow machines or small samples. A typo in destroy uses `2001:Db8` but IPv6 parsing is case-insensitive. Failure can also indicate kernel hash policy ignoring inner headers.

Test signals: baseline ping to 192.0.4.2 succeeds; ECMP and weighted 2:1 and 11:45 tests produce measured VLAN counter ratios within 15 percent of expected.
