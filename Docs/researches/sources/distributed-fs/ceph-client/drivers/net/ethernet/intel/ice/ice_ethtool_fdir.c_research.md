# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ethtool_fdir.c

## Purpose

`ice_ethtool_fdir.c` is the ethtool ntuple/classifier translation and orchestration layer for ICE Flow Director sideband filters. It converts `struct ethtool_rxnfc` and `struct ethtool_rx_flow_spec` requests into `struct ice_fdir_fltr` objects, validates ethtool masks against hardware-supported extraction profiles, programs or removes Flow Director flow profiles, writes filter add/delete training packets, maintains the in-memory filter list, and exposes filter read/list operations back to ethtool.

This file sits between `ice_ethtool.c` and lower-level Flow Director helpers in `ice_fdir.c` and `ice_flow.c`. Its main exported functions are `ice_get_ethtool_fdir_entry()`, `ice_get_fdir_fltr_ids()`, `ice_fdir_rem_adq_chnl()`, `ice_fdir_release_flows()`, `ice_fdir_replay_flows()`, `ice_fdir_num_avail_fltr()`, `ice_fdir_replay_fltrs()`, `ice_fdir_create_dflt_rules()`, `ice_fdir_del_all_fltrs()`, `ice_vsi_manage_fdir()`, `ice_del_fdir_ethtool()`, and `ice_add_fdir_ethtool()`.

## Important APIs, Types, and Functions

Flow type translation is handled by `ice_fltr_to_ethtool_flow()` and `ice_ethtool_flow_to_fltr()`. These map common ethtool flow types such as `TCP_V4_FLOW`, `UDP_V6_FLOW`, `IPV4_USER_FLOW`, `IPV6_USER_FLOW`, and `ETHER_FLOW` to ICE `enum ice_fltr_ptype` values. Unsupported types become `ICE_FLTR_PTYPE_NONF_NONE` or ethtool flow `0`.

Filter retrieval uses `ice_get_ethtool_fdir_entry()` to fill an ethtool flow spec from an existing `ice_fdir_fltr` selected by location. `ice_get_fdir_fltr_ids()` walks `hw->fdir_list_head` under `hw->fdir_fltr_lock` and returns active filter IDs.

Hardware profile management uses `struct ice_fd_hw_prof` entries stored in `hw->fdir_prof[flow]`. `ice_fdir_alloc_flow_prof()` allocates the table, `ice_fdir_set_hw_fltr_rule()` creates ICE flow profiles and entries for main VSI, control VSI, and ADQ channel VSIs, `ice_fdir_rem_flow()` releases a flow profile, and `ice_fdir_replay_flows()` rebuilds hardware flow profiles after reset. `ice_fdir_rem_adq_chnl()` removes ADQ channel VSI entries from existing profiles.

Input-set validation is split by protocol. `ice_set_fdir_ip4_seg()`, `ice_set_fdir_ip4_usr_seg()`, `ice_set_fdir_ip6_seg()`, `ice_set_fdir_ip6_usr_seg()`, `ice_set_ether_flow_seg()`, and `ice_set_fdir_vlan_seg()` build `struct ice_flow_seg_info` masks. They accept only full masks or zero masks for supported fields, reject empty rules, and return `-EOPNOTSUPP` for partially masked or unsupported fields such as TOS/TC/protocol in several paths. `ice_parse_rx_flow_user_data()` handles `FLOW_EXT` user-defined 16-bit flex-word filters and validates the encoded offset/mask.

Filter write operations go through `ice_fdir_write_fltr()` and `ice_fdir_write_all_fltr()`. These allocate raw packet buffers, call `ice_fdir_get_prgm_desc()` and `ice_fdir_get_gen_prgm_pkt()` from `ice_fdir.c`, submit the packet to the control VSI via `ice_prgm_fdir_fltr()`, and repeat for fragment templates when supported. `ice_fdir_write_all_fltr()` writes both non-tunnel and tunnel variants when a tunnel port is open.

`ice_add_fdir_ethtool()` and `ice_del_fdir_ethtool()` are the ethtool entry points called from `ice_ethtool.c`. They enforce feature enablement, reset/flush constraints, capacity limits, duplicate detection, profile compatibility, list updates, and hardware programming.

## Control Flow

Adding a filter starts in `ice_add_fdir_ethtool()`. The function validates VSI and `ICE_FLAG_FD_ENA`, rejects reset state, parses optional user-defined flex data, rejects `FLOW_MAC_EXT`, configures the extraction sequence through `ice_cfg_fdir_xtrct_seq()`, checks the requested location against total Flow Director capacity, checks remaining guaranteed/shared filter availability, allocates `struct ice_fdir_fltr`, converts the ethtool flow spec into ICE filter data with `ice_set_fdir_input_set()`, then takes `hw->fdir_fltr_lock`.

Under the lock, it rejects duplicates with `ice_fdir_is_dup_fltr()`, copies flex filter details, sets descriptor status/counter/reporting fields, updates or inserts the software list entry through `ice_fdir_update_list_entry()`, and writes all hardware variants. If hardware programming fails after list insertion, it rolls back counters, per-channel sideband counts, and the list node before freeing the input.

Deleting a filter starts in `ice_del_fdir_ethtool()`. It validates Flow Director enablement and reset/flush state, locks `hw->fdir_fltr_lock`, then calls `ice_fdir_update_list_entry()` with `input == NULL`. That removes hardware filter programming, decrements counters, updates ADQ per-queue filter count, deletes the list node, frees it, and if the deleted filter was the last one for the flow type, removes or restores the corresponding hardware profile.

Profile configuration flows from ethtool masks to `ice_flow_seg_info` and then to `ice_flow_add_prof()`/`ice_flow_add_entry()`. A key invariant is that all filters for a given flow type on a port must share the same input set. If a new request asks for a different input set while filters exist, the request fails. If no filters exist, the old profile can be removed and replaced unless aRFS is using the perfect flow.

Default rules are created by `ice_fdir_create_dflt_rules()` for IPv4 TCP/UDP and IPv6 TCP/UDP. `ice_vsi_manage_fdir()` enables these defaults when turning Flow Director on and deletes all filters/profiles when disabling.

## State and Persistence Behavior

The core persistent runtime state is in `hw->fdir_prof`, `hw->fdir_list_head`, `hw->fdir_fltr_lock`, `hw->fdir_active_fltr`, `hw->fdir_fltr_cnt[]`, `hw->fdir_perfect_fltr`, PF flag `ICE_FLAG_FD_ENA`, PF state bit `ICE_FD_FLUSH_REQ`, VSI guaranteed filter allocation `vsi->num_gfltr`, and ADQ channel per-ring sideband filter counters.

Filter list entries are allocated with devm memory and sorted by `fltr_id`. They persist across ordinary operations and are replayed after reset by `ice_fdir_replay_fltrs()`. Hardware flow profile entries and filter entries are not permanent across reset, so `ice_fdir_release_flows()`, `ice_fdir_replay_flows()`, and `ice_fdir_replay_fltrs()` rebuild them from driver state.

Counter persistence is split between software counters (`hw->fdir_active_fltr`, `hw->fdir_fltr_cnt[]`) and hardware usage counters read from `VSIQF_FD_CNT` and `GLQF_FD_CNT` in `ice_fdir_num_avail_fltr()`. E810 and E830 use different field definitions.

## Dependencies and Integration Points

This file depends on `ice.h`, `ice_lib.h`, `ice_fdir.h`, `ice_flow.h`, Linux ethtool flow-spec structures, netdev VLAN helpers, tunnel-port state, ADQ channel structures, and ICE flow profile APIs. It calls `ice_fdir_get_prgm_desc()`, `ice_fdir_get_gen_prgm_pkt()`, `ice_fdir_has_frag()`, `ice_fdir_find_fltr_by_idx()`, `ice_fdir_list_add_fltr()`, `ice_fdir_update_cntrs()`, and `ice_fdir_is_dup_fltr()` from `ice_fdir.c`.

It integrates with `ice_ethtool.c` through RX NFC callbacks and with reset/replay paths elsewhere in the driver. It also coordinates with ADQ (`ice_is_adq_active()`, channel VSI lists), aRFS (`ice_is_arfs_using_perfect_flow()`), control VSI programming (`ice_get_ctrl_vsi()`), main VSI selection, and tunnel configuration.

## Risks and Edge Cases

Input-set compatibility is the main correctness risk. Flow Director hardware profiles are shared per flow type, so accepting incompatible masks while active filters exist would break existing matches. Partial mask handling is intentionally restrictive; relaxing it requires matching hardware extraction support.

Concurrency risks center on `hw->fdir_fltr_lock`, reset state, and flush state. Add/delete must not race reset replay or filter flush. Rollback paths are important because a software list entry may be inserted before hardware programming fails.

Capacity accounting is subtle because a single logical ethtool filter may need both tunnel and non-tunnel hardware filters. ADQ remapping changes the destination VSI and relative queue index, so tests must cover filters targeting channel queues. Duplicate detection is delegated to `ice_fdir.c` and does not compare every advanced flow type equally; newly added flow types need duplicate comparison support.

## Test Signals

Use `ethtool -N` to add and delete TCP/UDP/SCTP IPv4 and IPv6 rules, user IPv4/IPv6 rules, ether rules, VLAN-qualified ether rules, drop rules, and flex-word rules. Verify `ethtool -n` single-rule and list output, duplicate rejection, partial mask rejection, max-location and capacity errors, tunnel-port open/closed behavior, ADQ queue remapping, reset replay, Flow Director disable cleanup, and per-channel sideband filter counts.
