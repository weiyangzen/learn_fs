# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/ip6_forward_instats_vrf.sh

## Purpose
`ip6_forward_instats_vrf.sh` verifies that IPv6 forwarding error statistics are charged to the incoming router interface when forwarding occurs inside a VRF. It checks normal IPv6 forwarding plus four specific `Ip6In*` counters.

## Important APIs, Functions, and Control Flow
Setup creates H1, a router VRF with ingress `$rtr1` and egress `$rtr2`, and H2. H2 and `$rtr2` MTUs are set to 1280. `require_command $TROUTE6` enforces traceroute6 availability. `ipv6_ping` verifies baseline H1-to-H2 reachability. `ipv6_in_too_big_err` snapshots `Ip6InTooBigErrors` on `$rtr1`, sends a ping larger than the egress MTU, and expects the counter to increase. `ipv6_in_hdr_err` uses traceroute6 to send hop-limit-constrained traffic and checks `Ip6InHdrErrors`. `ipv6_in_addr_err` temporarily disables global IPv6 forwarding while sending a packet and expects `Ip6InAddrErrors`. `ipv6_in_discard` installs a forwarding XFRM block policy, sends a ping, removes the policy, and expects `Ip6InDiscards`.

## State, Dependencies, Integration Points, and Risks
State includes VRFs, IPv6 routes, MTU overrides, global IPv6 forwarding sysctl, and transient XFRM policy. Dependencies include `lib.sh`, `ipv6_stats_get`, `master_name_get`, `$PING6`, traceroute6, and XFRM support. The test temporarily writes `net.ipv6.conf.all.forwarding` directly rather than through `sysctl_set`, so interruption during `ipv6_in_addr_err` could leave forwarding disabled until cleanup or external repair.

## Test Signals
Each counter test compares pre/post `ipv6_stats_get` values and requires a non-zero delta. Baseline ping uses `ping6_test`.
