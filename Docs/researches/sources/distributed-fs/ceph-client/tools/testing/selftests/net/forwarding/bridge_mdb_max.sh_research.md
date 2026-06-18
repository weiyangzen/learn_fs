# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_mdb_max.sh

## Purpose
`bridge_mdb_max.sh` validates bridge multicast group accounting and `mcast_max_groups` limit enforcement. It runs the same logical checks across 802.1d bridges, VLAN-filtering 802.1q bridges, and VLAN-filtering bridges with `mcast_vlan_snooping 1`, and across both explicit configuration (`bridge mdb`) and packet-driven control paths (IGMPv3/MLDv2 reports).

## Important APIs, Functions, and Control Flow
The top-level tests are `test_8021d`, `test_8021q`, `test_8021qvs`, and `test_mdb_count_warning`. Setup creates two hosts with VLAN subinterfaces, then each top-level test creates and destroys the bridge mode it needs. `switch_create_8021d`, `switch_create_8021q`, and `switch_create_8021qvs` configure snooping, VLANs, fastleave, and per-VLAN MLD/IGMP versions.

Entry creation is abstracted. `cfg4_entries_add/del` and `cfg6_entries_add/del` program MDB include entries with source lists via `bridge mdb`. `ctl4_entries_add/del` and `ctl6_entries_add/del` send IGMPv3/MLDv2 reports and leaves/done packets through mausezahn, then verify the number of created MDB lines. `bridge_port_ngroups_get`, `bridge_port_maxgroups_get`, `bridge_port_vlan_ngroups_get`, and `bridge_port_vlan_maxgroups_get` parse `bridge -j -d link/vlan` output through `jq`. Matching setters use `bridge link set ... mcast_max_groups` and `bridge vlan set ... mcast_max_groups`.

The test matrix is built from reusable suites: `test_ngroups_reporting` checks counters increment and decrement; `test_ngroups_cross_vlan` checks per-VLAN counters are isolated; `test_maxgroups_zero` verifies zero means unlimited; `test_maxgroups_zero_cross_vlan` verifies port and per-VLAN maximums are independent; `test_maxgroups_too_low` checks setting a max below current count rejects further additions without blocking additions after count drops; `test_maxgroups_too_many_entries` checks failed over-limit operations leave counters unchanged; `test_maxgroups_too_many_cross_vlan` combines aggregate port and per-VLAN limits. `test_vlan_attributes` verifies per-VLAN attributes only exist when VLAN snooping is active. `test_toggle_vlan_snooping` checks counters and maximums survive toggling `mcast_vlan_snooping`.

## State, Dependencies, Integration Points, and Risks
State spans bridge MDB entries, per-port and per-VLAN multicast accounting, bridge snooping flags, timer-driven control-packet state, and dmesg. The script uses `lib.sh`, `tc_common.sh`, `bridge`, `ip`, `jq`, mausezahn, multicast packet builder helpers, and kernel support advertised by `bridge link help` for `mcast_max_groups`. It reads `dmesg` to ensure no `br_multicast_port_ngroups_dec` warning appears, so prior warnings in the ring buffer can contaminate results. Control-path tests can partially add entries before hitting a limit, so cleanup explicitly deletes possible committed entries.

## Test Signals
Signals are JSON bridge counter comparisons, explicit return-code checks, error-message matching for `mcast_max_groups`, tc/mausezahn-driven MDB creation counts, and dmesg warning absence. The script skips when iproute2 lacks `mcast_max_groups` support.
