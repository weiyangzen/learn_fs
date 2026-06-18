# sources/distributed-fs/ceph-client/tools/testing/selftests/net/l2_tos_ttl_inherit.sh

Purpose: Matrix test for L2 tunnel TOS and TTL inheritance or fixed-value behavior across GRE tap, VXLAN, and Geneve with IPv4 or IPv6 outer headers, IPv4/IPv6/ARP-like inner traffic, and optional VLAN.

Important commands: Uses root checks, `tcpdump`, `modprobe`, `ip netns`, veth, `gretap`, `ip6gretap`, `vxlan`, `geneve`, VLAN devices, `ping`, random TOS/TTL generation, and tcpdump BPF byte offsets.

Control flow: For each tunnel type, outer family, inner payload family, inherit/random mode, and VLAN flag, `setup` creates two namespaces, a veth underlay, tunnel endpoints with fixed or inherited TOS/TTL parameters, optional VLAN subinterfaces, and inner addresses. `verify` starts ping or ARP-generating traffic, captures exactly one matching underlay packet with tcpdump filters adjusted for tunnel type and VLAN offsets, extracts `tos`/`ttl` or IPv6 `class`/`hlim`, compares against expected values, prints a table row, and records failure. Cleanup removes namespaces after each case.

State and persistence: Temporary namespaces/devices per matrix row. Global expected values and `failed` track results.

Dependencies and integration: Requires root, tcpdump, tunnel modules, iproute2 support, and ping.

Risks: Tcpdump parsing and byte offsets are brittle across header changes. Random chosen values avoid defaults but can complicate reproduction. Non-IP inner traffic expects inheritance to fall back to default outer values.

Test signals: Final exit 0 if every table row reports `OK`; exit 1 if any captured TOS/TTL differs.
