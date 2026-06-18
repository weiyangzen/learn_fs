# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_nh.sh

Purpose: sanity test for simple `ip nexthop` objects used by both IPv4 and IPv6 routes. It creates AF_INET6 nexthop objects bound to router ports and uses them for connected network routes.

Important functions are `router_create`, `routing_nh_obj`, `ping_ipv4`, and `ping_ipv6`. The router has two interfaces with clsact on `$rp2`; `routing_nh_obj` creates nexthop IDs 101 and 102 as IPv6-family device nexthops, then replaces routes for both IPv4 and IPv6 prefixes with `nhid` references.

Control flow creates H1/H2 VRFs and static host routes through router addresses, creates router interfaces and addresses, enables forwarding, installs nexthop objects, and runs dual-stack pings. State is kernel nexthop table, routes, clsact qdisc, VRFs, and forwarding. Risks include kernels without nexthop object support, AF_INET6 nexthop behavior for IPv4 route references, and cleanup not explicitly deleting nexthop IDs in this script. Test signals are only successful IPv4 and IPv6 pings through the `nhid` routes.
