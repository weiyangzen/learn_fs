# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_igmp.sh

## Purpose
`bridge_igmp.sh` validates bridge IGMP snooping and multicast database behavior for IGMPv2 and IGMPv3. It covers report/leave handling, IGMPv3 include and exclude filter-mode transitions, source-specific multicast forwarding, automatically added S,G entries for star-exclude ports, timeout behavior, and per-VLAN snooping interactions with STP state.

## Important APIs, Functions, and Types
The script sources forwarding `lib.sh`, uses `ip`, `bridge`, `jq`, `$MZ`, tc-enabled multicast helpers from the library (`mcast_packet_test`, `brmcast_check_sg_entries`, `brmcast_check_sg_state`, `brmcast_check_sg_fwding`), and JSON bridge MDB output. It defines raw IGMPv3 payload hex strings for IS_INCLUDE, IS_EXCLUDE, ALLOW, TO_EXCLUDE, and BLOCK records. `v3include_prepare()` and `v3exclude_prepare()` are shared setup routines that send crafted IGMPv3 reports and verify resulting MDB filter modes and source lists.

## Control Flow
The topology is a two-host bridge `br0` with multicast snooping and querier enabled. `v2reportleave_test()` uses `ip address ... autojoin` to create and remove an IGMPv2 membership and checks multicast forwarding before and after leave. IGMPv3 tests set bridge IGMP version 3, inject crafted packets with mausezahn, sleep for processing/timer windows, verify MDB JSON, and test S,G forwarding. Include-mode tests cover include-to-allow, include-to-is_include, include-to-is_exclude, include-to-to_exclude, and include-to-block transitions. Exclude-mode tests cover exclude-to-allow, exclude-to-is_include, exclude-to-is_exclude, exclude-to-to_exclude, exclude-to-block, timeout, and auto-added S,G entries. The final tests enable VLAN multicast snooping and verify IGMP query transmission starts when port or VLAN STP state enters forwarding.

## State and Persistence
State is in `br0`, `swp1`, `swp2`, host addresses, bridge MDB entries, multicast timers, STP state, VLAN multicast snooping attributes, and multicast statistics. `v3cleanup()` removes MDB entries and restores IGMP version 2. Some tests temporarily change multicast query intervals, response intervals, membership intervals, last-member intervals, VLAN filtering, and stats settings before restoring defaults.

## Dependencies and Integration Points
The file integrates with forwarding `lib.sh` and requires bridge multicast snooping, bridge MDB JSON with detailed source lists, mausezahn packet injection, jq, tc support from the harness, and per-VLAN multicast/stats support for the STP tests. It is listed as a forwarding `TEST_PROGS` script.

## Risks
The test uses handcrafted IGMP payload checksums and raw protocol bytes, so any packet-definition error invalidates the scenario. Timer-based tests are sensitive to system load and bridge timer units. Output checks assume specific JSON fields such as `source_list`, `filter_mode`, `flags`, and multicast xstats. Some functions refer to arrays named `X` and `Y` populated by prepare functions or local scopes; shell scoping mistakes could cause subtle test fragility.

## Test Signals
Signals include MDB entries appearing after reports and disappearing after leaves, expected filter modes (`include` or `exclude`), expected source lists and forwarding states, absence of stale sources after transitions, traffic forwarding only for allowed sources, `added_by_star_ex` flags on auto-created S,G entries, transition from exclude to include after timeout, and increasing IGMP query counters after STP forwarding state changes.
