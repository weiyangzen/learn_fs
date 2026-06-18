# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_fltr.h

## Purpose
`ice_fltr.h` declares the filter helper interface for VSI-level switch filters and promiscuous mode operations. It gives higher-level VSI/netdev code a compact API for MAC, broadcast, VLAN, ethertype, all-filter removal, and switch-rule flag updates.

## Important APIs, types, and functions
The header exports `ice_fltr_free_list`, promisc setters/clearers, list and single-entry MAC helpers, VLAN add/remove, ethertype add/remove, `ice_fltr_remove_all`, and `ice_fltr_update_flags`. It includes `ice_vlan.h` for `struct ice_vlan` used in VLAN filter APIs and relies on switch-rule types such as `enum ice_sw_fwd_act_type`.

## Control flow
Callers can either build lists with `ice_fltr_add_mac_to_list` and submit them through list APIs, or use single-filter helpers that build and free temporary lists internally. Promiscuous mode APIs directly wrap lower-level hardware state transitions.

## State and persistence behavior
The header stores no state. Its APIs mutate lower-level switch rule state through `struct ice_hw` or `struct ice_vsi` and may allocate temporary filter-list entries that callers must free with `ice_fltr_free_list` when they build lists manually.

## Dependencies and integration points
It is consumed by VSI, netdev, VLAN, and switchdev-adjacent code that needs filter management without dealing directly with `ice_fltr_info` list construction. The declared `ice_fltr_update_flags` integrates with switch-rule maintenance even though its implementation is outside `ice_fltr.c` in this source subset.

## Risks and edge cases
- Manual list-building callers must free lists on all error paths.
- APIs mix `struct ice_hw *`, `struct ice_vsi *`, software VSI handles, VLAN IDs, and forwarding actions; incorrect identifier type can program the wrong switch rule.
- `ice_fltr_update_flags` being declared here but implemented elsewhere means link-time coverage is needed when changing switch-rule modules.

## Test signals
Compile/link checks for all declarations, manual MAC-list construction/free tests, VLAN and ethertype add/remove through VSI setup paths, promisc transitions, and teardown through `ice_fltr_remove_all` are the main signals.
