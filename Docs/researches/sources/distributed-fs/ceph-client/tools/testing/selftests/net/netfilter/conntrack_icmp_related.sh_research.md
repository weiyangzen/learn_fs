## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_icmp_related.sh

Purpose: verifies that ICMP/ICMPv6 PMTU errors and redirect messages are classified as `ct state related`, including across NAT masquerade for ICMP echo traffic.

Important APIs and tools: uses namespace helpers, nftables inet/ip/ip6 tables, counters, IPv4/IPv6 forwarding sysctls, `ping`/`ping6`, route manipulation, and NAT masquerade rules.

Control flow: creates client1 -> router1 -> router2 -> client2 topology with the router2-client2 link at MTU 1280. It installs forward/input nft rules with counters for `unknown`, `related`, `new`, and redirects; router1 also masquerades ICMP/ICMPv6 toward router2. Baseline pings assert routing and no unknown drops. Oversized IPv4 and IPv6 pings with DF/PMTU behavior are expected to fail while causing related counters on router1 and client1, not router2 forward. Later, it adds bad routes on client1 to provoke IPv4/IPv6 redirects and checks redirect counters.

State and persistence: all netns/rules/routes are temporary. Dependencies include nft, ICMP conntrack, NAT core, IPv6, and deterministic packet sizes/counter bytes. Risks include byte-count dependence on kernel packet formatting, route/redirect suppression differences, and PMTU timing. Test signals are PASS/ERROR lines and counter comparisons.
