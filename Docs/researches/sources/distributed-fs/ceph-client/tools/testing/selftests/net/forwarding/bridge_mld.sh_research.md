# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_mld.sh

## Purpose
`bridge_mld.sh` is a packet-driven MLDv2 bridge snooping state-machine test. It feeds fixed MLDv2 report packets into a bridge and validates `(*,G)` source-list state, `(S,G)` forwarding entries, include/exclude transitions, blocked-source behavior, timeout behavior, automatic star-exclude entries, and per-VLAN snooping interaction with STP state.

## Important APIs, Functions, and Control Flow
The script defines fixed hexadecimal packet payloads for MLDv2 MODE_IS_INCLUDE, MODE_IS_EXCLUDE, CHANGE_TO_EXCLUDE, ALLOW_NEW_SOURCES, and BLOCK_OLD_SOURCES reports against group `ff02::cc`. `switch_create` configures `br0` with multicast snooping, a querier, MLDv2, shortened query response/startup intervals, and two bridge ports. `mldv2include_prepare` sends an include report, then checks JSON MDB output for a source-list `(*,G)` entry in include mode and calls `brmcast_check_sg_entries`. `mldv2exclude_prepare` builds from include state to exclude state and validates source states.

Individual tests cover transitions: include plus ALLOW, include plus IS_IN, include plus IS_EX, include to exclude, exclude plus ALLOW, exclude plus IS_IN, exclude plus IS_EX, exclude to exclude, include/exclude plus BLOCK, and exclude timeout back to include. Forwarding checks use `brmcast_check_sg_fwding` for allowed and blocked source sets. `mldv2star_ex_auto_add_test` verifies that a later `(S,G)` learned on another port also creates an `added_by_star_ex` entry for the existing `(*,G)` exclude port. `mldv2per_vlan_snooping_stp_test` enables VLAN filtering and `mcast_vlan_snooping`, changes port or VLAN STP state from disabled/blocking to forwarding, and checks multicast xstats for transmitted MLDv2 queries.

## State, Dependencies, Integration Points, and Risks
State lives in bridge MDB source lists, per-source timers, per-source forwarding/block flags, bridge multicast timers, per-VLAN global multicast settings, STP state, and multicast xstats. Dependencies include `lib.sh`, `jq`, `ip -j stats`, `bridge -j -d -s mdb`, mausezahn, and helper functions such as `brmcast_check_sg_entries`, `brmcast_check_sg_state`, and `brmcast_check_sg_fwding`. Timing is central: tests sleep after report injection and deliberately shorten last-member and membership intervals. Risks include brittle fixed packet payloads, environment-specific multicast timer jitter, and xstats availability differences.

## Test Signals
Signals are JSON MDB predicates over `grp`, `source_list`, `filter_mode`, `src`, `port`, and `flags`, forwarding helper results for allowed/blocked sources, xstats deltas for MLD query transmission, and normal kselftest `RET`/`EXIT_STATUS` aggregation.
