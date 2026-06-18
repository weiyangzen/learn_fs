# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_fdb_local_vlan_0.sh

## Purpose
`bridge_fdb_local_vlan_0.sh` tests the bridge `fdb_local_vlan_0` option, which controls whether local FDB entries are shared through VLAN 0. It validates both FDB table representation and end-to-end forwarding for bridge and port MAC addresses across 802.1d and 802.1q bridge modes, including runtime toggling and MAC address changes.

## Important APIs, Functions, and Types
The script sources forwarding `lib.sh` and uses ADF helpers, `bridge`, `ip`, `tc`, `jq`, and `$MZ`. `setup_prepare()` creates three hosts / switch-side links, enables forwarding, and installs routes between two IPv4/IPv6 subnets through a bridge gateway. `adf_bridge_create()` creates `br` with requested bridge attributes and restores its MAC after VLAN configuration. `check_mac_presence()` inspects JSON FDB output for a device MAC and VLAN. `do_end_to_end_test()` injects UDP traffic and checks tc flower counters on the expected receiving device.

## Control Flow
Default tests cover no-sharing and sharing cases for both non-VLAN-filtering and VLAN-filtering bridges, plus `test_addr_set`. The bridge is configured with VLANs 1, 2, and 3 on the bridge and on `swp1` / `swp2`. `do_test_no_sharing()` creates a bridge without sharing, verifies MAC entries per VLAN, changes port and bridge MACs, then toggles `fdb_local_vlan_0=1` and expects shared behavior. `do_test_sharing()` starts with sharing enabled, checks FDB sharing and forwarding, verifies flooding for nonexistent FDBs, checks that misleading nonlocal VLAN 0 entries do not affect VLAN-aware lookup, changes MACs, then toggles sharing off. `test_addr_set()` specifically covers bridge MAC assignment through `NET_ADDR_SET`.

## State and Persistence
The test creates bridge `br`, VLAN membership, VRF host state, tc ingress counters on `h2` and `h3`, and deferred cleanup actions through the harness. It temporarily changes MAC addresses on `swp1` and `br`, adds and deletes FDB records, and relies on per-test defer scopes for cleanup.

## Dependencies and Integration Points
It depends on the ADF forwarding library, bridge VLAN filtering, the `fdb_local_vlan_0` bridge attribute, JSON FDB output, tc flower counters, and mausezahn packet injection. It is integrated into the forwarding Makefile as a runnable test.

## Risks
The semantics under test differ between 802.1d and 802.1q modes; a mistake in expected flooding counts can mask a data-plane regression. End-to-end checks use exact packet counter deltas of 10, so background traffic on the same test devices would be problematic. The support probe uses `adf_ip_link_add XXbr ...` and must be cleaned by the library's defer scope. The test is sensitive to bridge FDB JSON schema and to MAC restoration after address changes.

## Test Signals
Pass signals include expected presence or absence of local MAC FDB entries on VLAN 0 and VLANs 1-3, exact tc counter increments for packets addressed to shared local MACs, flooding to `h2` for nonexistent or ignored entries, no flooding when VLAN 0 lookup is valid, and behavior changes after toggling `fdb_local_vlan_0`.
