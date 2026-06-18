# sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_vxlan_nh.sh

## Purpose
`test_vxlan_nh.sh` validates VXLAN FDB nexthop group support. It checks that an FDB entry can point at an FDB nexthop group for basic IPv4/IPv6 transmission, that learning paths do not crash when refreshing entries involving nexthop-backed FDB state, and that proxy ARP/ND paths tolerate nexthop-backed FDB entries.

## Important APIs, Functions, and Types
The script sources `lib.sh`, defines `run_cmd` for optional verbose command execution, and uses `exit_cleanup_all` as the `EXIT` trap. `nh_stats_get` reads `ip -s -j nexthop show id 10` with `jq` to extract group packet stats. `tc_stats_get` delegates to `tc_rule_handle_stats_get`. `basic_tx_common` parameterizes address family, protocol, local/remote addresses, and prefix length. `proxy_common` parameterizes ARP/ND proxy coverage. Test functions are `basic_tx_ipv4`, `basic_tx_ipv6`, `learning`, `proxy_ipv4`, and `proxy_ipv6`.

## Control Flow
After option parsing, dependency checks, and an iproute2 nexthop-stats feature probe, the script creates one namespace per test. Basic transmit scenarios add a dummy route, attach a `tc flower` egress filter for UDP VXLAN packets, configure loopback local address, create FDB nexthop IDs `1` and group `10`, create `vx0`, add a static bridge FDB entry using `nhid 10`, inject one Ethernet frame with `mausezahn`, then busy-wait for both nexthop and `tc` packet counters to reach one. `learning` builds two local VXLAN devices and sends a packet that can trigger learning refresh against an entry using `nhid 10`. Proxy tests configure VXLAN `proxy`, a permanent neighbor entry, an FDB nexthop entry, and use `arping` or `ndisc6`.

## State and Persistence
State is per-netns kernel state: dummy links, loopback addresses, routes, nexthops, VXLAN links, bridge FDB entries, neighbor entries, and `tc` filters. No persistent files are created. Cleanup always uses `cleanup_all_ns` through the trap and between tests.

## Dependencies and Integration Points
Dependencies are root-capable networking, `mausezahn`, `arping`, `ndisc6`, `jq`, iproute2 nexthop FDB/stats support, `bridge`, `tc`, and `lib.sh` helpers. Integration points include kernel nexthop FDB objects, VXLAN static FDB resolution through `nhid`, VXLAN learning/localbypass behavior, proxy neighbor suppression, and packet injection through raw Ethernet frames.

## Risks and Test Signals
Risks include missing iproute2 support, unavailable packet tools, counter timing, and the fact that learning/proxy tests mainly assert absence of crashes rather than packet counters. Strong signals are nexthop group packets reaching one, `tc` egress packets reaching one, successful `arping`/`ndisc6`, and no kernel failure during refresh/proxy paths.
