# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_fltr.c

## Purpose
`ice_fltr.c` is a convenience wrapper layer for switch filter operations. It builds temporary `ice_fltr_list_entry` lists for MAC, broadcast, VLAN, and ethertype filters, dispatches them to lower-level switch-rule APIs, wraps promiscuous mode calls with consistent error logging, and removes all filters for a VSI during teardown.

## Important APIs, types, and functions
- List management: `ice_fltr_free_list`, `ice_fltr_add_entry_to_list`.
- Promiscuous mode wrappers: `ice_fltr_set_vlan_vsi_promisc`, `ice_fltr_clear_vlan_vsi_promisc`, `ice_fltr_set_vsi_promisc`, `ice_fltr_clear_vsi_promisc`.
- Batch dispatch wrappers: `ice_fltr_add_mac_list`, `ice_fltr_remove_mac_list`, static VLAN and ethertype list variants.
- Entry builders: `ice_fltr_add_mac_to_list`, `ice_fltr_add_vlan_to_list`, `ice_fltr_add_eth_to_list`.
- Single-operation helpers: `ice_fltr_add_mac`, `ice_fltr_add_mac_and_broadcast`, `ice_fltr_remove_mac`, `ice_fltr_add_vlan`, `ice_fltr_remove_vlan`, `ice_fltr_add_eth`, `ice_fltr_remove_eth`, `ice_fltr_remove_all`.

## Control flow
Single filter operations allocate a stack `LIST_HEAD`, populate one or more `ice_fltr_info` records, call the relevant lower-level list operation, and then free the temporary list. MAC-and-broadcast adds two entries before dispatch. VLAN filters fill VLAN ID, TPID, and TPID-valid fields. Ethertype filters choose `ICE_SRC_ID_VSI` for TX filters and `ICE_SRC_ID_LPORT` for RX filters. Promiscuous wrappers call the lower-level switch API and log any error except `-EEXIST`.

## State and persistence behavior
This file does not own long-lived filter state. Temporary list entries are `devm_kzalloc` allocations that are explicitly freed immediately after dispatch. Persistent state is in hardware switch rules and lower-level switch-rule bookkeeping owned by `ice_switch`/common code. `ice_fltr_remove_all` removes all switch filters for a VSI and unsyncs netdev unicast/multicast lists when a netdev exists.

## Dependencies and integration points
The file includes `ice.h`, `ice_fltr.h`, and through them switch-rule and VLAN definitions. It integrates with VSI setup/teardown, netdev address synchronization, VLAN configuration, promiscuous mode transitions, and lower-level APIs such as `ice_add_mac`, `ice_remove_mac`, `ice_add_vlan`, `ice_remove_vlan`, `ice_add_eth_mac`, `ice_remove_eth_mac`, `ice_set_vsi_promisc`, and `ice_remove_vsi_fltr`.

## Risks and edge cases
- `ice_fltr_add_entry_to_list` uses `GFP_ATOMIC`; repeated batch construction under memory pressure can fail and callers must handle `-ENOMEM`.
- Temporary list allocation is freed after dispatch, so lower-level APIs must copy entries rather than retain pointers.
- MAC-and-broadcast operations are not transactional at this layer; lower-level partial add/remove failures may leave only one of the two filters changed.
- Error logging suppresses `-EEXIST`; this is intentional for idempotent promisc state but can hide unexpected duplicate-rule behavior if callers rely only on logs.

## Test signals
Signals include netdev address sync/unsync, adding/removing unicast and broadcast filters, VLAN add/remove with TPID correctness, ethertype RX/TX filters with correct source ID, promisc set/clear with VLAN and non-VLAN variants, VSI teardown calling `ice_fltr_remove_all`, and fault injection of list allocation failures.
