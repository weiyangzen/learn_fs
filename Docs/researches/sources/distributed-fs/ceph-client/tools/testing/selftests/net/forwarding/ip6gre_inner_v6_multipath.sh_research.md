
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6gre_inner_v6_multipath.sh

Purpose: IPv6 payload counterpart of the inner-flow multipath GRE-over-IPv6 test. It verifies ECMP and weighted multipath distribution when the GRE payload is IPv6.

Important APIs/functions: same topology roles as the IPv4 version; `multipath6_test` sends ranged IPv6 UDP traffic and evaluates counters; `ping_ipv6` and `multipath_ipv6` are the exported tests.

Control flow: builds H1/SW1/SW2/SW3/SW4/H2 topology, adds `ip6gre` tunnels over IPv6 underlay, installs two VLAN underlay paths between SW2 and SW3, and attaches ingress counters for VLAN 111/222. Each multipath case sets hash policy 2, replaces route weights, sends 50 UDP flows across IPv6 source/destination ranges, and checks ratio.

State/persistence: mutates VRFs, IPv6 addresses and routes, VLANs, `ip6gre` tunnel devices, tc qdiscs/filters, and `net.ipv6.fib_multipath_hash_policy`.

Dependencies/integration: uses `lib.sh` helpers, `MZ -6`, tc JSON counter helpers, and `multipath_eval`.

Risks: distribution tolerance is sample-size sensitive. Systems without inner IPv6 hash support for GRE or with different offload behavior can collapse traffic to one path. Cleanup route/address ordering is important.

Test signals: ping6 to 2001:db8:2::2 succeeds; ECMP and weighted 2:1 and 11:45 cases pass measured-versus-expected ratio checks.
