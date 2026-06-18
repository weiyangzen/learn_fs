# sources/distributed-fs/ceph-client/tools/testing/selftests/net/fib_nexthop_multiprefix.sh

Purpose: this script validates cached route exceptions when one nexthop object is shared by multiple IPv4 and IPv6 prefixes. It ensures path-MTU exceptions for different remote hosts remain distinct instead of being incorrectly shared through the common `fib_nh` / `fib6_nh`.

Important APIs and functions: it uses `setup_ns`, veth links, namespace sysctls for forwarding, `ip nexthop add`, routes using `nhid`, `taskset` to generate per-CPU cached routes, `ping`/`ping6`, MTU changes, and route lookup checks with `ip route get` / `ip -6 route get`. Key functions are `create_ns`, `setup`, `change_mtu`, `validate_v4_exception`, and `validate_v6_exception`.

Control flow: setup creates host namespaces h0..h3 and router r1, connects each host to r1, assigns IPv4/IPv6 subnets, adds nexthop ids 4 and 6 in h0 via r1, and routes h1-h3 prefixes through those shared nexthops. Main code pings each destination from each CPU to populate cached routes, then changes MTUs on h1, h2, and h3 links to 1300, 1350, and 1400. For each host it sends oversized pings to trigger PMTU exceptions and validates `route get` output contains the expected mtu. It then revalidates without more pings and deletes selected routes/nexthops to exercise cleanup paths.

State and persistence: state consists of namespaces, links, routes, nexthop objects, route cache exceptions, and MTU changes. Cleanup removes all namespaces. No files are written.

Dependencies and integration points: requires nexthop object support, IPv6, route exception reporting in `ip route get`, multiple CPUs or compatible `/sys/devices/system/cpu/online` parsing, and ping utilities.

Risks and test signals: parsing CPU ranges with `seq ${cpus/-/ }` handles simple ranges but not comma-separated CPU lists. Grep patterns depend on iproute2 route-get output format. Strong signals are successful initial pings and route-get output showing the distinct expected MTU for each destination in both families.
