# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/gre_inner_v4_multipath.sh

## Purpose
`gre_inner_v4_multipath.sh` tests IPv4-over-GRE-over-IPv4 weighted ECMP. It validates that underlay multipath selection can hash on inner IPv4 traffic when `fib_multipath_hash_policy=2`.

## Important APIs, Functions, and Control Flow
The topology places H1 and H2 behind GRE endpoints SW1 and SW4, with SW2/SW3 forming two underlay paths distinguished by VLAN 111 and 222. `sw1_create` and `sw4_create` create GRE tunnel devices and route host subnets through them. `sw2_create` installs the ECMP route toward the remote GRE endpoint; `sw3_create` installs return routes and tc ingress filters on `$ul32` to count traffic per VLAN path.

`multipath4_test` sets `net.ipv4.fib_multipath_hash_policy=2`, replaces SW2’s route to the remote tunnel endpoint with weights supplied by the caller, sends mausezahn UDP traffic with varying inner IPv4 source/destination ranges, reads tc counters, and calls `multipath_eval`. `multipath_ipv4` runs ECMP, 2:1, and 11:45 weight cases. `ping_ipv4` confirms tunnel reachability first.

## State, Dependencies, Integration Points, and Risks
State includes four VRFs, GRE tunnels, underlay routes, VLAN subinterfaces, tc filters, and IPv4 hash policy sysctl. Dependencies include `lib.sh`, tunnel helpers, `tc_rule_stats_get`, `multipath_eval`, `$MZ`, and weighted multipath route support. Risks are statistical variance in distribution and cleanup sensitivity because static tunnel names `g1/g2` and VLAN IDs are reused.

## Test Signals
Signals are IPv4 ping success and `multipath_eval` comparing observed VLAN path packet deltas against requested weights.
