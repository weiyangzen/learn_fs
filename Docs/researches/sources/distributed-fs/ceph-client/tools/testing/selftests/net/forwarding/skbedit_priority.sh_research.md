# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/skbedit_priority.sh

Purpose: verifies that `tc action skbedit priority` on ingress or egress changes skb priority before PRIO qdisc classification on `$swp2`.

Important functions are `switch_create`, `test_skbedit_priority_one`, `test_ingress`, and `test_egress`. Setup builds a VLAN-aware bridge, attaches `$swp1/$swp2`, adds clsact to both switch ports, and installs `prio bands 8 priomap 7 6 5 4 3 2 1 0` on `$swp2`. `test_skbedit_priority_one` adds a flower rule at a supplied locus, sends ten UDP packets, waits for the expected PRIO class packet counter, and checks the tc rule counter.

Control flow runs ping, then loops priority 0-7 for ingress on `$swp1` and egress on `$swp2`, expecting class `10:(8-prio)`. State is qdiscs, tc filters, bridge membership, and counters. Risks include priority-to-band mapping assumptions, timing via `HIT_TIMEOUT`, and needing clean filter deletion per iteration. Test signals are class packet count increases and skbedit rule hit counters for every priority/locus combination.
