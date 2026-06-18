# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_switch.c

## Purpose

`ice_switch.c` implements the Intel ICE driver's software switch programming layer. It translates higher-level VSI, MAC, VLAN, promiscuous, default-port, RDMA, and advanced/classifier filter requests into firmware AdminQ commands for switch rules, recipes, VSI lists, profile associations, and resource counters.

The file owns most switch-side software bookkeeping for:

- VSI contexts cached in `hw->vsi_ctx[]`.
- Per-recipe filter lists in `hw->switch_info->recp_list[]`.
- VSI-list resource mappings in `hw->switch_info->vsi_list_map_head`.
- Advanced recipe creation, reuse, subscription, and profile association.
- Replay lists used after reset recovery.
- Dummy packet templates used to program advanced switch rules.

## Important APIs, Types, And Data

The implementation includes `ice_lib.h`, `ice_switch.h`, and `ice_trace.h`, and depends on AdminQ helpers from common code (`ice_aq_send_cmd`, `ice_fill_dflt_direct_cmd_desc`, `ice_aq_alloc_free_res`, `ice_acquire_change_lock`, `ice_release_change_lock`), package/profile helpers (`ice_get_sw_fv_bitmap`, `ice_get_sw_fv_list`, `ice_init_prof_result_bm`, `ice_find_prot_off`), tunnel-port helpers (`ice_get_open_tunnel_port`), and kernel list/bitmap/mutex/devm allocation APIs.

Local packet-template structures are:

- `struct ice_dummy_pkt_offsets`: maps an `enum ice_protocol_type` to a byte offset in a dummy packet.
- `struct ice_dummy_pkt_profile`: bundles offsets, packet bytes, a match bitmask, length, and offset count.

The file declares static dummy packet templates for VLAN/QinQ, TCP/UDP IPv4 and IPv6, UDP tunnels, NVGRE, GTP-C/GTP-U with IPv4/IPv6 inner traffic, PFCP, PPPoE, and L2TPv3. `ice_dummy_pkt_profiles[]` orders these from more specific to less specific so `ice_find_dummy_packet()` can select the first profile whose flags cover the requested lookup/tunnel combination.

Global static bitmaps:

- `recipe_to_profile[ICE_MAX_NUM_RECIPES]`: profiles associated with each recipe.
- `profile_to_recipe[ICE_MAX_NUM_PROFILES]`: recipes associated with each profile.

Major exported functions include:

- VSI context and AdminQ operations: `ice_add_vsi()`, `ice_free_vsi()`, `ice_update_vsi()`, `ice_is_vsi_valid()`, `ice_get_hw_vsi_num()`, `ice_get_vsi_ctx()`, `ice_clear_all_vsi_ctx()`, `ice_cfg_rdma_fltr()`.
- Initial switch and default setup: `ice_init_def_sw_recp()`, `ice_get_initial_sw_cfg()`, `ice_init_chk_recipe_reuse_support()`.
- Basic filter operations: `ice_add_mac()`, `ice_remove_mac()`, `ice_add_vlan()`, `ice_remove_vlan()`, `ice_add_eth_mac()`, `ice_remove_eth_mac()`, `ice_vlan_fltr_exist()`, `ice_remove_vsi_fltr()`.
- Promiscuous/default behavior: `ice_cfg_dflt_vsi()`, `ice_check_if_dflt_vsi()`, `ice_set_vsi_promisc()`, `ice_clear_vsi_promisc()`, `ice_set_vlan_vsi_promisc()`.
- AdminQ/resource wrappers: `ice_aq_sw_rules()`, `ice_aq_add_recipe()`, `ice_aq_get_recipe()`, `ice_aq_get_recipe_to_profile()`, `ice_aq_map_recipe_to_profile()`, `ice_update_recipe_lkup_idx()`, `ice_alloc_recipe()`, `ice_alloc_res_cntr()`, `ice_free_res_cntr()`, `ice_share_res()`.
- Advanced rule operations: `ice_add_adv_rule()`, `ice_rem_adv_rule_by_id()`, metadata helpers `ice_rule_add_tunnel_metadata()`, `ice_rule_add_direction_metadata()`, `ice_rule_add_vlan_metadata()`, `ice_rule_add_src_vsi_metadata()`, and DVM protocol update `ice_change_proto_id_to_dvm()`.
- Reset replay cleanup: `ice_replay_vsi_all_fltr()`, `ice_rm_all_sw_replay_rule_info()`.

## Control Flow

### Initialization

`ice_init_def_sw_recp()` allocates the recipe table with `devm_kcalloc()`, sets each recipe's `root_rid` to its index, initializes `filt_rules` and `filt_replay_rules`, and initializes each recipe mutex. It stores the table in `hw->switch_info->recp_list`.

`ice_get_initial_sw_cfg()` repeatedly calls `ice_aq_get_sw_cfg()` until firmware returns `req_desc == 0`. It parses each switch configuration element, ignores firmware VSI elements, and initializes physical port data through `ice_init_port_info()`.

`ice_init_chk_recipe_reuse_support()` sets `hw->recp_reuse` from NVM version, enabling newer firmware behavior where recipes can be subscribed to and reused.

### VSI Context Operations

`ice_add_vsi()` validates the software VSI handle, calls `ice_aq_add_vsi()`, and then creates or updates `hw->vsi_ctx[vsi_handle]`. If local context allocation fails after firmware allocation, it calls `ice_aq_free_vsi()` to roll back the hardware allocation.

`ice_free_vsi()` validates the cached handle, fills the caller's context with the hardware VSI number, calls `ice_aq_free_vsi()`, and only clears the local context on success. `ice_update_vsi()` similarly validates the handle, sets `vsi_ctx->vsi_num`, and sends an update AdminQ command.

`ice_cfg_rdma_fltr()` builds a small temporary VSI context that preserves cached queue option fields, toggles `ICE_AQ_VSI_Q_OPT_PE_FLTR_EN`, calls `ice_update_vsi()`, and updates the cached context on success.

### Switch Rule Creation

Basic rules flow through `ice_add_rule_internal()`:

1. Validate the target VSI and translate `vsi_handle` to hardware VSI ID.
2. Derive source from port for RX or hardware VSI for TX.
3. Lock the recipe's `filt_rule_lock`.
4. Search existing rules with `ice_find_rule_entry()`.
5. If no matching rule exists, unlock and create a new firmware rule with `ice_create_pkt_fwd_rule()`.
6. If a matching rule exists, update it to include the new VSI using `ice_add_update_vsi_list()`.

`ice_create_pkt_fwd_rule()` allocates a switch rule buffer and a management entry, calls `ice_fill_sw_rule()` to encode the dummy Ethernet header and action, sends `ice_aq_sw_rules(... add_sw_rules ...)`, captures the returned firmware rule ID, and appends an `ice_fltr_mgmt_list_entry` to the recipe's filter list.

`ice_fill_sw_rule()` is the central encoder for basic rules. It populates:

- Rule type (`LKUP_RX` or `LKUP_TX`) from `ICE_FLTR_RX`/`ICE_FLTR_TX`.
- Recipe ID from lookup type.
- Source port/VSI.
- Action bits for forward-to-VSI, forward-to-VSI-list, queue, queue group, or drop.
- Loopback and LAN enable bits via `ice_fill_sw_info()`.
- Header bytes for MAC, VLAN, MAC+VLAN, ethertype, ethertype+MAC, promiscuous, and promiscuous+VLAN lookups.

`ice_fill_sw_info()` sets `lb_en` and `lan_en` based on TX/RX direction, forwarding action, lookup type, VEB/VEPA mode, and `ICE_FLTR_TX_ONLY`. This controls whether the programmed action loops packets back internally or permits LAN forwarding.

### VSI List Management

When a second VSI subscribes to an existing filter, `ice_add_update_vsi_list()` either:

- Allocates a VSI-list firmware resource and adds both old/new VSIs, updates the existing rule from single-VSI forwarding to VSI-list forwarding, and creates a local `ice_vsi_list_map_info`; or
- Updates an existing VSI list with the new VSI and sets the local bitmap bit.

`ice_rem_update_vsi_list()` removes one VSI from a basic-rule VSI list, updates firmware first, then local state. If one non-VLAN VSI remains, it converts the rule back to `ICE_FWD_TO_VSI` and frees the VSI-list resource. VLAN pruning differs: VLAN rules always use VSI lists, and the list is freed when VLAN `vsi_count` reaches zero.

VLAN creation in `ice_add_vlan_internal()` has additional sharing logic. VLAN pruning rules use `ICE_AQC_RES_TYPE_VSI_LIST_PRUNE`; the function attempts to reuse one-VSI VLAN lists across rules by `ref_cnt`, and when a shared list must diverge, it creates a new list and decrements the old list refcount.

### Removal And Cleanup

`ice_remove_rule_internal()` validates the VSI, finds the rule, and either:

- Removes the whole firmware lookup rule, then deletes the list entry; or
- For VSI-list rules, updates/removes only the VSI membership first, deleting the rule only if no subscribers remain.

`ice_remove_vsi_fltr()` removes every supported lookup family for one VSI by collecting matching rules into temporary filter-list copies and dispatching to the relevant remove API.

`ice_rem_sw_rule_info()` and `ice_rem_adv_rule_info()` only free software bookkeeping lists; they are used for replay-list cleanup, not firmware rule teardown.

### Promiscuous And Default Rules

`ice_cfg_dflt_vsi()` programs or removes default VSI rules with `ICE_SW_LKUP_DFLT`, using port source for RX and VSI source plus `ICE_FLTR_TX_ONLY` for TX.

`ice_set_vsi_promisc()` decomposes a promiscuous mask into separate unicast/multicast/broadcast and RX/TX rules. It chooses `ICE_SW_LKUP_PROMISC` or `ICE_SW_LKUP_PROMISC_VLAN`, sets a representative destination MAC in the dummy header, and calls `ice_add_rule_internal()` per bit. `ice_clear_vsi_promisc()` searches existing promisc rules used by the VSI and removes only those fully covered by the requested mask.

`ice_set_vlan_vsi_promisc()` derives the VLANs currently used by a VSI from VLAN filter bookkeeping and sets or clears VLAN-promiscuous rules per VLAN, with a DVM-specific skip for duplicated VLAN zero handling.

### Recipe And Advanced Rule Creation

Advanced rules start in `ice_add_adv_rule()`:

1. Initialize profile-result bitmaps if needed.
2. Count masked lookup words and reject empty or oversized requests.
3. Pick a dummy packet profile with `ice_find_dummy_packet()`.
4. Validate action and target VSI.
5. Translate software VSI handles to hardware VSI/source IDs.
6. Call `ice_add_adv_recipe()` to find or create a recipe.
7. If the same rule already exists, update its VSI list.
8. Otherwise build a lookup RX/TX rule with the selected dummy packet and action, send `add_sw_rules`, and store an `ice_adv_fltr_mgmt_list_entry`.

`ice_add_adv_recipe()` converts lookup masks into protocol/offset words through `ice_fill_valid_words()`, finds compatible field vectors, fills recipe field-vector indices, searches for an equivalent recipe with `ice_find_recp()`, and either subscribes to an existing recipe or creates a new chained recipe through `ice_add_sw_recipe()`.

`ice_add_sw_recipe()` calculates how many recipe entries are needed, allocates recipe IDs, assigns result indexes for chained non-root recipes, builds a root recipe containing remaining lookup words plus intermediate results, sends `ice_aq_add_recipe()` under the change lock, and books local recipe metadata. It also associates the recipe bitmap with all compatible profiles through `ice_aq_map_recipe_to_profile()`.

`ice_find_recp()` compares word counts, protocol IDs, offsets, masks, tunnel type, pass-L2 bits, and priority. When recipe reuse is supported, it first refreshes local recipe data from firmware with `ice_get_recp_frm_fw()`.

Advanced dummy packet generation has three phases:

- `ice_find_dummy_packet()` derives a bitmask from lookup types and tunnel type; it may allocate a VLAN-augmented copy with `ice_dummy_packet_add_vlan()`.
- `ice_fill_adv_dummy_packet()` copies the selected template and overlays only masked lookup words.
- `ice_fill_adv_packet_tun()` inserts current VXLAN/Geneve UDP tunnel destination ports when needed.
- `ice_fill_adv_packet_vlan()` writes VLAN TPID for DVM mode when a VLAN type is supplied.

### Advanced Rule Removal

`ice_rem_adv_rule_by_id()` locates the management entry by recipe ID and firmware rule ID, injects the requested VSI handle into a copied `ice_adv_rule_info`, and calls `ice_rem_adv_rule()`.

`ice_rem_adv_rule()` reconstructs lookup extension words, finds the recipe, finds the matching advanced rule entry, and either removes a VSI from the rule's VSI list or deletes the firmware rule. If a recipe becomes empty and recipe reuse is enabled, it releases recipe resources with `ice_release_recipe_res()`, which also disassociates the recipe bitmap from profile maps.

### Reset Replay

`ice_replay_vsi_all_fltr()` iterates all recipes and replays entries from `filt_replay_rules`, using basic replay for normal recipes and advanced replay for advanced rules. Replay updates source/hardware VSI IDs before re-adding rules. `ice_rm_all_sw_replay_rule_info()` frees replay rule entries after reset handling.

## State And Persistence Behavior

The state is runtime-only kernel driver state. Firmware stores active switch rules, VSI lists, recipes, resource counters, and profile associations. The driver mirrors enough of that state to support deduplication, incremental updates, removals, and reset replay.

Local persistent-for-device-lifetime state includes:

- `hw->vsi_ctx[]`: cached VSI context pointers allocated with `devm_` APIs.
- `hw->switch_info->recp_list[]`: recipe metadata and rule lists.
- Per-recipe `filt_rules`: active software mirrors of firmware rules.
- Per-recipe `filt_replay_rules`: reset-replay inputs.
- `hw->switch_info->vsi_list_map_head`: local mapping from firmware VSI-list IDs to software VSI-handle bitmaps.
- `recipe_to_profile[]` and `profile_to_recipe[]`: cached profile association matrices.
- `hw->switch_info->rule_cnt` and `recp_cnt`: counters updated around AdminQ add/remove resource operations.
- `hw->recp_reuse`: feature gate determined from NVM.

Synchronization is mostly per-recipe through `filt_rule_lock`. AdminQ changes usually occur before local bookkeeping is updated. This ordering favors consistency after failed firmware operations, but not every multi-step path has complete rollback. For example, recipe allocation or VSI-list creation can succeed before later profile/rule updates fail.

## Dependencies And Integration Points

Primary callers are elsewhere in the ICE driver:

- `ice_fltr.c` calls MAC, VLAN, and promiscuous helpers.
- `ice_lib.c` and `ice_eswitch.c` configure default VSI behavior.
- `ice_tc_lib.c`, `ice_eswitch_br.c`, and `ice_main.c` add/remove advanced switch rules for traffic control and switchdev paths.
- `ice_idc.c` toggles RDMA filtering.
- `ice_common.c` uses replay and cleanup helpers during reset/rebuild.

The file integrates with:

- Firmware AdminQ opcodes: switch config, add/update/free VSI, add/update/remove switch rules, add/get recipe, recipe-to-profile, resource allocation/free/share.
- Package parser/profile state through field vectors and profile-result bitmaps.
- Tunnel configuration state for open VXLAN/Geneve ports.
- DVM/SVM VLAN mode via `ice_change_proto_id_to_dvm()`, `ice_is_dvm_ena()`, and VLAN TPID handling.
- Kernel memory management, list operations, bitmaps, lock primitives, endian helpers, and Ethernet address helpers.

## Risks And Edge Cases

- Multi-step firmware transactions can partially complete. Recipe creation allocates multiple recipe resources before profile association; failures can leave resources that rely on later cleanup, especially when `hw->recp_reuse` gates cleanup behavior.
- Locking is per recipe list, but some helpers inspect or update shared VSI-list mappings and recipe/profile bitmaps. Cross-recipe shared VLAN-list refcounts require careful sequencing.
- Several advanced-rule paths call `ice_find_adv_rule_entry()` before taking the recipe lock, then lock for mutation. Concurrent callers could race unless higher layers serialize operations.
- `ice_add_rule_internal()` unlocks before `ice_create_pkt_fwd_rule()` after not finding an existing rule. Concurrent insertion of the same rule could create duplicates if callers are not externally serialized.
- VLAN lookup and DVM behavior depends on `tpid`, `tpid_valid`, and VLAN zero handling. Incorrect caller initialization may create duplicate or unremovable filters.
- `ice_find_rule_entry()` compares the entire `l_data` union with `memcmp`; callers must zero unused union bytes as required by the header comments.
- Advanced dummy packet selection depends on profile ordering and match flags. Missing a new protocol/tunnel in templates, offsets, `ice_prot_ext[]`, or `ice_prot_id_tbl[]` can break recipe programming for that protocol.
- `ice_dummy_packet_add_vlan()` allocates a synthetic profile and marks it with `ICE_PKT_KMALLOC`; callers must free only those profiles, which `ice_add_adv_rule()` does.
- Hardware VSI IDs are cached but can change after reset. Replay paths refresh IDs, but stale rule entries outside replay could be wrong if used after rebuild without refresh.
- `ice_aq_sw_rules()` updates `rule_cnt` based on requested rule count, assuming firmware command success maps directly to all rule mutations.

## Test Signals

Useful validation should cover:

- Add/remove MAC filters for unicast, multicast, broadcast, and duplicate MAC subscriptions across multiple VSIs.
- VLAN pruning rules with one VSI, multiple VSIs, shared one-VSI list reuse, removal back to zero, DVM enabled, VLAN zero, and non-default TPID.
- Promiscuous RX/TX unicast, multicast, broadcast, VLAN-promiscuous set/clear, and mask combinations where only a subset should be removed.
- Default VSI set/clear for RX and TX.
- Bridge-mode changes from VEB to VEPA and back, verifying TX unicast rule action bits are updated.
- RDMA filter enable/disable preserving unrelated VSI queue option fields.
- Advanced rules for non-tunnel, VXLAN, Geneve, NVGRE, GTP-C/GTP-U, PFCP, PPPoE, L2TPv3, IPv4/IPv6, VLAN/QinQ, queue, queue-group, drop, mirror, and NOP actions.
- Recipe reuse across equivalent advanced rules and correct recipe release when the last rule is removed.
- Reset replay where hardware VSI IDs differ after reset.
- Error injection for AdminQ allocation, switch-rule update, recipe programming, and profile mapping failures to inspect rollback behavior and local bookkeeping consistency.
