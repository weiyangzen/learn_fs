# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_vlan_mcast.sh

## Purpose
`bridge_vlan_mcast.sh` validates per-VLAN multicast snooping controls and statistics on a VLAN-aware bridge. It checks global VLAN multicast option visibility/defaults, per-VLAN snooping enable/disable, querier behavior, IGMP/MLD version selection, timer knobs, router-port behavior, membership expiration, and automatic disablement when VLAN filtering is turned off.

## Important APIs, Functions, and Control Flow
Setup creates VLAN subinterfaces on both hosts, a VLAN-filtering bridge with multicast snooping and querier enabled, installs `clsact` on bridge ports, adds VLANs 10 and 11 to both ports, then enables `mcast_vlan_snooping`. `vlmc_v2join_test` adds an IPv4 multicast `autojoin` address on `$h2.10`, waits, and checks for a VID 10 MDB entry, with an `expect` flag for positive and negative cases. `vlmc_control_test` checks `bridge -j vlan global show` default `mcast_snooping`, disables it on VID 10, and verifies joins no longer create MDB entries.

`vlmc_query_cnt_setup`, `vlmc_query_cnt_xstats`, and `vlmc_check_query` use tc egress filters plus bridge multicast xstats to count tagged IGMP or MLD general queries. The querier/version/startup/query interval tests set per-VLAN global options and validate query counts. Other timer tests validate default and mutable values for last-member, membership, querier, query, and query-response intervals. `vlmc_router_port_test` checks per-port VLAN `mcast_router`, sets one port as router and the other non-router, sends unknown multicast from `br0`, and verifies flooding only to the router port. `vlmc_filtering_test` disables bridge VLAN filtering and expects `mcast_vlan_snooping` to be disabled.

## State, Dependencies, Integration Points, and Risks
State includes per-VLAN global multicast attributes, per-port VLAN router flags, MDB entries with `vid`, host `autojoin` memberships, tc filter counters, bridge xstats, and bridge link info. Dependencies include `lib.sh`, `tc_rule_stats_get`, `jq`, `bridge vlan global`, `ip -j link xstats`, mausezahn, and per-VLAN multicast support in kernel/iproute2. Timer/count tests use sleeps from 1 to 5 seconds and can be sensitive to scheduler latency. Some tests create a temporary `br1` and reparent `$h1`, so cleanup must restore host addressing.

## Test Signals
Pass/fail signals are JSON predicates over `bridge vlan global show`, `bridge -j -d vlan show`, `bridge -j mdb show`, tc filter packet counts, xstats deltas, and link-info checks for `mcast_vlan_snooping`.
