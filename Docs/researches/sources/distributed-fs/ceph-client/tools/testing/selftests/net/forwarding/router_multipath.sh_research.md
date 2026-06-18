# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_multipath.sh

Purpose: baseline ECMP/weighted multipath routing test using classic route nexthop syntax instead of nexthop objects. It covers IPv4 and IPv6 distribution over two router-to-router links.

Important functions are `router1_create`, `router2_create`, `multipath4_test`, `multipath6_test`, and `multipath_test`. R1 and R2 VRFs each install routes with two `nexthop via ... dev ...` clauses. Tests replace those routes with weighted nexthops, generate UDP flows through `$MZ`, compare `$rp12` and `$rp13` TX packet deltas, and call `multipath_eval`.

Control flow creates H1/H2/R1/R2 VRFs, assigns IPv4 and IPv6 addresses including link-local IPv6 nexthop networks, enables forwarding, runs pings, and validates ECMP and two weighted ratios for both address families. State is routes, VRFs, addresses, sysctls `fib_multipath_hash_policy`, and link counters. Risks include enough flow entropy, mausezahn availability, counter timing, and hash-policy restoration. Test signals are ping reachability plus packet-count ratios for 1:1, 2:1, and 11:45 distributions.
