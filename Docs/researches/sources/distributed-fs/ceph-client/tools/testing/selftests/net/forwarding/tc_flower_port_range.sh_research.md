# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_flower_port_range.sh

Purpose: tests flower source/destination port range matching for IPv4/IPv6 and UDP/TCP on ingress and egress, plus a drop case for IPv4 UDP.

Important functions are `__test_port_range`, `test_port_range_ipv4_udp`, `test_port_range_ipv4_tcp`, `test_port_range_ipv6_udp`, `test_port_range_ipv6_tcp`, and `test_port_range_ipv4_udp_drop`. Setup creates a two-port bridge with clsact on both switch ports and simple dual-stack hosts.

Control flow installs matching filters for `src_port 100-200` and `dst_port 300-400`, sends packets at min/mid/max and out-of-range values with `$MZ`, and checks counters remain at exactly three for matches. The drop test installs an ingress drop filter for source ports 2000-3000 and checks that only in-range packets hit. State is bridge, clsact qdiscs, and tc filters. Risks include protocol naming (`ipv4`/`ipv6` and `udp`/`tcp`), exact counter checks, and out-of-range traffic still traversing other state. Test signals are tc packet counters for ingress and egress filters and `log_test` per protocol family.
