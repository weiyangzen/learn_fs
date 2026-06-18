# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_switch.h

## Purpose

`ice_switch.h` is the public/private driver contract for the ICE software switch layer. It defines the data structures that describe switch lookup filters, advanced classifier rules, recipe bookkeeping, VSI-list mappings, and VSI contexts, plus prototypes for the switch operations implemented in `ice_switch.c` and consumed by the rest of the driver.

The header is not a standalone userspace ABI. It is an internal kernel-driver interface layered on `ice_common.h`, AdminQ structures, protocol-header unions, package field-vector types, and switch action enums defined elsewhere in the ICE driver.

## Important APIs, Types, And Constants

Constants:

- `ICE_SW_CFG_MAX_BUF_LEN`: switch configuration AdminQ response buffer size.
- `ICE_FLTR_RX`, `ICE_FLTR_TX`, `ICE_FLTR_TX_ONLY`: direction and TX-only flags used by filter descriptions.
- `ICE_DFLT_VSI_INVAL`, `ICE_VSI_INVAL_ID`, `ICE_INVAL_Q_HANDLE`: invalid sentinel values.
- `ICE_PROFID_*`: profile IDs for GTP and PFCP switch-rule profiles.
- `ICE_SW_RULE_*_SIZE()` macros: type-safe flexible-array sizing for AdminQ switch rule structures.
- `DUMMY_ETH_HDR_LEN`: dummy Ethernet header length used for basic switch-rule programming.
- `ICE_INVAL_LG_ACT_INDEX`, `ICE_INVAL_SW_MARKER_ID`, `ICE_INVAL_COUNTER_ID`: management-entry sentinels.

Core structures:

- `struct ice_vsi_ctx`: cached VSI state used for add/get/update/free operations. It stores firmware VSI number, allocation counters, flags, AdminQ VSI properties, scheduler info, VF/pool metadata, and per-TC LAN/RDMA queue context arrays.
- `enum ice_sw_lkup_type`: hardware-specific recipe IDs for default/basic lookup types: ethertype, MAC, MAC+VLAN, promiscuous, VLAN, default VSI, ethertype+MAC, promiscuous+VLAN.
- `enum ice_src_id`: identifies whether a filter source is a VSI, queue, logical port, or unknown.
- `struct ice_fltr_info`: basic filter descriptor. It combines lookup type, action, firmware rule ID, direction/source, lookup payload union, forwarding destination union, software VSI handle, queue-group size, and computed `lb_en`/`lan_en` action hints.
- `struct ice_update_recipe_lkup_idx_params`: arguments for read-modify-write updates of a default recipe lookup index and mask.
- `struct ice_adv_lkup_elem`: advanced rule match element. It names a protocol type and carries header values plus masks via `union ice_prot_hdr`, with raw 16-bit array views for iteration.
- `struct ice_sw_act_ctrl`: action/source object embedded in advanced rules.
- `struct ice_rule_query_data`: compact recipe/rule/VSI tuple returned from add and consumed by remove-by-ID.
- `struct ice_adv_rule_flags_info`: optional action-bit override for advanced rules.
- `struct ice_adv_rule_info`: advanced rule descriptor containing tunnel type, VLAN type, firmware rule ID, priority, pass-L2 flags, source VSI, switch action, and optional action flags.
- `struct ice_sw_recipe`: software recipe bookkeeping. It stores root recipe ID, creation flags, extraction words/masks/FV indices, recipe bitmaps, tunnel type, filter lists, replay lists, rule lock, compatible field vectors, associated profiles, result indices, priority, pass-L2 flags, and lookup extensions.
- `struct ice_vsi_list_map_info`: maps a firmware VSI-list ID to a bitmap of software VSI handles plus a reference count.
- `struct ice_fltr_list_entry`: caller-facing list entry for basic filter add/remove batches, including per-entry status.
- `struct ice_fltr_mgmt_list_entry`: internal active-rule bookkeeping for basic filters, including VSI-list pointer, subscriber count, large action marker/counter metadata, and `ice_fltr_info`.
- `struct ice_adv_fltr_mgmt_list_entry`: internal active-rule bookkeeping for advanced filters, including copied lookups, rule info, lookup count, VSI-list pointer, and subscriber count.
- `enum ice_promisc_flags`: bitmask for RX/TX unicast, multicast, broadcast, and VLAN promiscuous behavior.

Declared operations:

- VSI management: `ice_add_vsi()`, `ice_free_vsi()`, `ice_update_vsi()`, `ice_is_vsi_valid()`, `ice_get_vsi_ctx()`, `ice_get_hw_vsi_num()`, `ice_clear_all_vsi_ctx()`.
- Switch configuration and AdminQ wrappers: `ice_get_initial_sw_cfg()`, `ice_aq_sw_rules()`, recipe add/get/map/get-map functions, `ice_update_recipe_lkup_idx()`, resource counter allocation/free, `ice_share_res()`.
- Basic switch filters: MAC, VLAN, ethertype/MAC, RDMA, all-filters-for-VSI removal, and VLAN-existence query.
- Default/promiscuous filters: `ice_cfg_dflt_vsi()`, `ice_check_if_dflt_vsi()`, `ice_set_vsi_promisc()`, `ice_clear_vsi_promisc()`, `ice_set_vlan_vsi_promisc()`.
- Advanced rules: metadata helper functions, `ice_add_adv_rule()`, `ice_rem_adv_rule_by_id()`.
- Recipe and replay helpers: `ice_init_def_sw_recp()`, `ice_init_chk_recipe_reuse_support()`, `ice_alloc_recipe()`, `ice_find_vsi_list_entry()`, `ice_replay_vsi_all_fltr()`, `ice_rm_all_sw_replay_rule_info()`, `ice_change_proto_id_to_dvm()`, `ice_fill_eth_hdr()`.

## Control Flow Implied By The Interface

The header expresses two main programming models.

For basic filters, callers allocate one or more `struct ice_fltr_list_entry` objects, initialize `fltr_info` with lookup type, source identity, lookup data, forwarding action, and VSI handle, then call a typed batch function such as `ice_add_mac()`, `ice_add_vlan()`, `ice_add_eth_mac()`, or the corresponding remove helper. Each list entry has a `status` field so batch functions can report the failing entry.

For advanced rules, callers build an array of `struct ice_adv_lkup_elem` values, filling protocol-specific header values and masks, then pass that with `struct ice_adv_rule_info` to `ice_add_adv_rule()`. On success, `struct ice_rule_query_data` records the recipe ID, firmware rule ID, and VSI handle required for `ice_rem_adv_rule_by_id()`.

The VSI context APIs imply a lifecycle where the driver first initializes recipe bookkeeping and switch configuration, then adds VSIs, then programs filters against valid VSI handles. Many switch APIs require valid cached VSI handles because they translate software VSI handles to hardware VSI numbers before issuing AdminQ commands.

## State And Persistence Behavior

The header's structures define the switch layer's in-memory persistence model:

- `ice_vsi_ctx` entries live in `hw->vsi_ctx[]` and cache firmware VSI identity plus queue configuration.
- `ice_sw_recipe` entries live in `hw->switch_info->recp_list[]` and persist recipe metadata, active filter lists, replay lists, profile associations, result-index use, and matching criteria.
- `ice_fltr_mgmt_list_entry` and `ice_adv_fltr_mgmt_list_entry` mirror firmware switch rules so add/remove operations can deduplicate, update VSI-list membership, and replay after resets.
- `ice_vsi_list_map_info` bridges firmware-assigned VSI-list IDs and software VSI-handle bitmaps.

These structures are volatile driver state, not disk-persistent state. Firmware keeps the authoritative hardware rule/programming state while the driver mirrors it for orchestration and recovery.

## Dependencies And Integration Points

The header depends directly on `ice_common.h`, which supplies AdminQ command structures, hardware constants, protocol unions, switch action types, profile/field-vector types, `struct ice_hw`, `struct ice_port_info`, and other core definitions.

The interface is consumed by:

- Filter setup paths (`ice_fltr.c`) for MAC/VLAN/promisc filters.
- VSI/default-VSI setup paths (`ice_lib.c`, eswitch code).
- Traffic-control and representor/switchdev paths (`ice_tc_lib.c`, `ice_eswitch_br.c`) for advanced rules.
- Reset/rebuild code (`ice_common.c`) for replay.
- RDMA peer-device integration (`ice_idc.c`) for RDMA filter toggles.

## Risks And Edge Cases

- `struct ice_fltr_info::l_data` explicitly requires callers to zero unused union fields. Since rule matching can compare the whole union, uninitialized padding or stale union data can create duplicate, unremovable, or mismatched filters.
- Several fields use bitfields with hardware-sized limits (`q_id:11`, `hw_vsi_id:10`, `vsi_list_id:10`). Callers must pass values already validated against hardware limits.
- The `flag` field is shared across RX/TX/TX-only semantics; invalid combinations may produce incorrect source/action encoding.
- `struct ice_sw_recipe` exposes many internal mutable fields. Callers outside the switch layer should avoid direct mutation because recipe/profile bitmaps and firmware state must stay synchronized.
- `struct ice_vsi_list_map_info::ref_cnt` and `vsi_count` in management entries are separate concepts. Misinterpreting one as the other can leak VSI-list resources or remove lists still shared by other rules.
- `ice_rule_query_data` removal depends on the exact tuple returned at add time. Losing it forces callers to reconstruct lookup/rule information or accept `-ENOENT`.
- Advanced metadata helper functions mutate caller-provided lookup elements and set `type = ICE_HW_METADATA`; callers need sufficient array space and should avoid overwriting real protocol lookups.

## Test Signals

Header-level contract tests should focus on integration compile coverage and caller behavior:

- Build coverage for all prototypes and structures across `ice_fltr.c`, `ice_lib.c`, `ice_tc_lib.c`, `ice_eswitch*.c`, `ice_idc.c`, and reset code.
- Static analysis or KUnit-style checks that filter descriptors are zero-initialized before union fields are populated.
- Tests that batch add/remove functions populate per-entry `status` on the first failing item.
- Tests that advanced rule add returns a usable `ice_rule_query_data` and remove-by-ID succeeds with that tuple.
- Tests for invalid VSI handles, invalid VLAN IDs, unsupported lookup types, and out-of-range queue/VSI-list IDs.
- Reset replay tests that verify `filt_replay_rules` structures contain enough data to reconstruct basic and advanced filters after hardware state is rebuilt.
