# subset-b-004470 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_flex_pipe.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_flex_pipe.c

## Purpose
`ice_flex_pipe.c` is the Intel ice driver's flexible-pipeline programming layer. It translates DDP package sections and flow/profile requests into hardware table updates for parser boost TCAM, XLT1 packet type groups, XLT2 VSI groups, profile TCAM, profile redirection, extraction sequences, RSS masks, and Flow Director swap/inset registers. It also owns the software mirrors of those tables under `hw->blk[]`, plus tunnel and double-VLAN parser boost updates.

## Important APIs, types, and functions
- Package/table initialization: `ice_init_hw_tbls`, `ice_fill_blk_tbls`, `ice_clear_hw_tbls`, `ice_free_hw_tbls`, `ice_free_seg`, `ice_init_pkg`, `ice_copy_and_init_pkg`, `ice_pkg_buf_alloc_single_section`, `ice_pkg_buf`, `ice_pkg_buf_free`, `ice_aq_upload_section`.
- Change serialization: `ice_acquire_change_lock` and `ice_release_change_lock` wrap the AdminQ resource lock for package/profile changes.
- Parser boost updates: `ice_udp_tunnel_set_port`, `ice_udp_tunnel_unset_port`, `ice_create_tunnel`, `ice_destroy_tunnel`, `ice_get_open_tunnel_port`, `ice_set_dvm_boost_entries`.
- Profile plumbing: `ice_add_prof`, `ice_rem_prof`, `ice_search_prof_id`, `ice_add_prof_id_flow`, `ice_rem_prof_id_flow`, `ice_flow_assoc_fdir_prof`, `ice_find_prot_off`, `ice_get_sw_fv_bitmap`, `ice_get_sw_fv_list`.
- Internal data structures come from `ice_flex_type.h`: `ice_xlt1`, `ice_xlt2`, `ice_prof_tcam`, `ice_es`, `ice_prof_map`, `ice_vsig_prof`, `ice_chs_chg`, and mask/resource state.

## Control flow
Initialization allocates per-block software mirrors using the fixed `blk_sizes[]` capabilities, initializes locks/lists, assigns section IDs from `ice_blk_sids`, allocates XLT/PTG/VSIG/TCAM/redirection/extraction arrays, and initializes RSS/FD mask registers. `ice_fill_blk_tbls` enumerates DDP package sections with `ice_pkg_enum_section`, copies section payloads into those mirrors, and reconstructs PTG and VSIG linked-list state via `ice_init_sw_db`.

Profile creation starts in `ice_add_prof`: it either reuses an existing extraction sequence/profile ID or allocates a profile ID, optionally rewrites FD swap/inset behavior, programs profile masks, writes the extraction sequence into the software table, and records the PTG/attribute list in `es.prof_map`. The profile is not necessarily written to hardware until a VSI is associated.

VSI association flows through `ice_add_prof_id_flow`. The code looks up or creates a VSIG whose ordered profile-property list exactly matches the requested profile set. It may move a VSI to an existing VSIG, add a profile to a one-VSI VSIG, or create a fresh VSIG with copied profile properties. Hardware writes are accumulated as `ice_chs_chg` records and committed by `ice_upd_prof_hw`, which builds a package buffer in ES, TCAM, XLT1, XLT2 order and calls `ice_update_pkg`.

Removal mirrors addition: profile removal scans all VSIGs for the profile, releases TCAM entries by writing never-match keys, possibly frees VSIGs and moves VSIs to default, then decrements profile reference counts and frees profile IDs/masks when the last reference disappears.

## State and persistence behavior
The persistent driver state is in `struct ice_hw`: `hw->blk[]` mirrors advanced feature tables; `hw->tnl` stores parser boost tunnel slots and active UDP ports; `hw->dvm_upd` stores double-VLAN boost entries; `hw->fl_profs[]` stores flow profiles owned by `ice_flow.c`; and `hw->rss_list_head` is freed here on teardown. Hardware persistence is via package update AdminQ commands and direct register writes (`wr32`) for FD/RSS mask/symmetry/inset/swap registers. The code uses `devm_k*` allocations tied to the device lifetime and explicit list cleanup during reset/unload.

## Dependencies and integration points
This file integrates tightly with `ice_common.h` AdminQ/package helpers, `ice_flow.c` flow profile lifecycle, `ice_ddp.h` section layouts, Linux UDP tunnel offload callbacks, `net_device` tunnel port APIs, and hardware resource allocation helpers (`ice_alloc_hw_res`, `ice_free_hw_res`). It depends on `ice_flex_type.h` for table layouts and on `ice_flow.h` for PTYPE limits and flow profile removal.

## Risks and edge cases
- Hardware and software state can diverge if `ice_upd_prof_hw` fails after software lists/TCAM ownership were already mutated; callers often free change records but do not fully roll back all software-side moves.
- TCAM/profile/mask resource exhaustion returns `-ENOSPC` or `-EIO`; paths that allocate multiple TCAM entries need careful cleanup because partial allocations can be left in in-memory structures until higher-level teardown.
- `ice_get_prof` marks `es.written[prof_id] = true` before the package update succeeds, so a failed first association may suppress later ES writes unless reset/cleanup restores state.
- FD swap handling assumes field vectors are populated right-to-left and source/destination fields appear in complete pairs; new FD extraction layouts must preserve that invariant.
- Tunnel index conversion assumes the UDP tunnel NIC stack's linear index still maps to the driver's sparse valid table; unexpected invalid index paths WARN and fall back to entry 0.

## Test signals
Useful validation signals include successful driver probe with DDP package load, reset/reload without leaked VSIG/profile state, UDP tunnel add/remove via VXLAN/GENEVE offloads, double-VLAN mode enablement, RSS profile add/remove/replay through ethtool or VF requests, Flow Director profile association for both main and control VSI, resource exhaustion injection for TCAM/profile IDs, and debug traces from `ICE_DBG_PKG`, `ICE_DBG_INIT`, and `ICE_DBG_FLOW`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_flex_pipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_flex_pipe.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_flex_pipe.h

## Purpose
`ice_flex_pipe.h` declares the flexible-pipeline programming interface consumed by the rest of the ice driver. It exposes DDP package initialization, hardware table allocation/fill/free, parser tunnel updates, profile add/remove, flow-to-profile association, extraction-sequence lookup, and package-buffer helpers.

## Important APIs, types, and functions
- Locking and package transport: `ice_acquire_change_lock`, `ice_release_change_lock`, `ice_aq_upload_section`.
- Parser and tunnel control: `ice_hw_ptype_ena`, `ice_get_open_tunnel_port`, `ice_udp_tunnel_set_port`, `ice_udp_tunnel_unset_port`, `ice_set_dvm_boost_entries`.
- Flow/profile programming: `ice_add_prof`, `ice_search_prof_id`, `ice_add_prof_id_flow`, `ice_rem_prof_id_flow`, `ice_flow_assoc_fdir_prof`, `ice_rem_prof`.
- Table lifecycle: `ice_init_pkg`, `ice_copy_and_init_pkg`, `ice_is_init_pkg_successful`, `ice_init_hw_tbls`, `ice_fill_blk_tbls`, `ice_clear_hw_tbls`, `ice_free_hw_tbls`, `ice_free_seg`.
- Package-buffer helpers: `ice_pkg_buf_alloc_single_section`, `ice_pkg_buf`, `ice_pkg_buf_free`.

## Control flow
The header splits responsibilities cleanly: callers initialize package/table state during probe, call `ice_add_prof` to register a hardware profile, call `ice_add_prof_id_flow` or `ice_flow_assoc_fdir_prof` to bind that profile to hardware VSI numbers, and call the matching remove/free APIs during flow removal, VSI teardown, reset, or driver unload. UDP tunnel callbacks are exported with Linux `net_device` callback signatures.

## State and persistence behavior
The declarations imply stateful operations on `struct ice_hw`; no state is stored in the header itself. Many APIs mutate hardware tables, firmware package sections, or software mirrors and therefore require lock discipline through the implementation. Package initialization and table fill APIs persist the DDP-derived state in `hw->seg` and `hw->blk[]`.

## Dependencies and integration points
The header includes `ice_type.h`, which supplies `struct ice_hw`, block enums, DDP state enums, AdminQ descriptor types, and shared driver types. It is included by flow, parser, VSI, and offload code that needs to program or query flexible pipeline state.

## Risks and edge cases
- `ice_add_prof` takes raw bitmaps, attribute arrays, extraction sequences, masks, and mode booleans; incorrect caller-provided lengths or block choices can corrupt intended hardware profile semantics even if C type checks pass.
- Several APIs use hardware VSI numbers while others use software VSI handles; call sites must distinguish them.
- Tunnel callbacks return Linux errno values but wrap lower-level ice status paths; tests should verify error translation remains stable.

## Test signals
Compilation is the first signal because this header is a cross-module contract. Runtime signals include successful package init, tunnel callback registration, RSS/FD profile add/remove, and reset teardown paths that call all table lifecycle functions without leaks or WARNs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_flex_pipe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_flex_type.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_flex_type.h

## Purpose
`ice_flex_type.h` defines the data model for ice flexible-pipeline programming. It names key hardware PTYPEs, tunnel types, GTP PTYPE attributes, parser boost tunnel tables, XLT1/PTG state, XLT2/VSIG state, profile TCAM entries, extraction sequences, mask pools, change records, profile categories, and metadata initialization section formats.

## Important APIs, types, and functions
This header is primarily type and constant definitions:
- PTYPE and tunnel constants: `ICE_PTYPE_*`, `ICE_MAC_*`, `enum ice_tunnel_type`, `struct ice_tunnel_table`, `struct ice_dvm_table`.
- Attribute model: `enum ice_ptype_attrib_type`, `struct ice_ptype_attrib_info`, `struct ice_ptype_attributes`, and GTP flag/mask constants.
- Table mirrors: `struct ice_xlt1`, `struct ice_xlt2`, `struct ice_prof_tcam`, `struct ice_prof_redir`, `struct ice_es`, `struct ice_blk_info`.
- Profile and VSIG mapping: `struct ice_prof_map`, `struct ice_vsig_prof`, `struct ice_vsig_entry`, `struct ice_vsig_vsi`, `struct ice_tcam_inf`.
- Resource/mask tracking: `struct ice_prof_id`, `struct ice_masks`, `struct ice_mask`.
- Change tracking: `enum ice_chg_type`, `struct ice_chs_chg`.
- Metadata init: `ICE_META_*`, `struct ice_meta_init_entry`, `struct ice_meta_init_section`.

## Control flow
There is no executable control flow, but the type relationships drive `ice_flex_pipe.c`: XLT1 maps PTYPE to PTG, profile TCAM maps PTG plus VSIG and flags to profile ID, extraction sequence maps profile ID to field vectors, and XLT2 maps VSI to VSIG. Change records describe atomic update batches sent to firmware.

## State and persistence behavior
Most structs are software mirrors of firmware or hardware package tables. `ice_blk_info` is the central per-block persisted state in `struct ice_hw`. Lists and reference counts persist dynamic profile associations across flow add/remove until reset/unload. Tunnel and DVM tables preserve parser boost update addresses and active port/enable state.

## Dependencies and integration points
The header includes `ice_ddp.h` for DDP package section layouts and uses kernel list, bitmap, endian, and mutex types via surrounding ice headers. It is consumed by `ice_flex_pipe.c`, `ice_flow.c`, parser/raw profile code, RSS code, and tunnel offload setup.

## Risks and edge cases
- Fixed limits such as `ICE_MAX_TCAM_PER_PROFILE`, `ICE_MAX_PTG_PER_PROFILE`, `ICE_MAX_PTG_ATTRS`, `ICE_TUNNEL_MAX_ENTRIES`, and `ICE_XLT2_CNT` are hard hardware limits; additions of new PTYPE groups or attributes must check these limits.
- `ICE_VSIG_VALUE` embeds PF number bits into VSIG values; code must mask with `ICE_VSIG_IDX_M` before indexing arrays.
- `struct ice_chs_chg` is a broad union-like record without a union; only fields meaningful for the selected `type` are valid.
- Metadata bit constants use global bit offsets into packed package entries; changes to DDP layout would break VLAN mode detection if not updated consistently.

## Test signals
Compile-time struct layout compatibility, DDP package load, adding profiles with GTP attributes, stress of tunnel table capacity, and profile add/remove under multiple PFs are the strongest signals. Static checks should watch enum expansion near `ICE_FLOW_FIELD_IDX_MAX <= 64` in the dependent flow header and any hardware table count mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_flex_type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_flow.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_flow.c

## Purpose
`ice_flow.c` turns logical flow descriptions into flexible-pipeline profiles. It maps protocol headers and hash fields to PTYPE bitmaps, field-vector extraction sequences, masks, GTP attributes, RSS symmetry registers, flow profile lists, flow entries, and RSS configuration replay records. It is the bridge between user/VF/RSS/FD requests and the low-level profile programming in `ice_flex_pipe.c`.

## Important APIs, types, and functions
- Field metadata and PTYPE maps: `ice_flds_info[]`, many `ice_ptypes_*` bitmaps, and GTP attribute tables.
- Profile build path: `ice_flow_add_prof`, `ice_flow_add_prof_sync`, `ice_flow_proc_seg_hdrs`, `ice_flow_create_xtrct_seq`, `ice_flow_xtract_fld`, `ice_flow_xtract_raws`, `ice_flow_set_parser_prof`.
- Entry/profile lifecycle: `ice_flow_add_entry`, `ice_flow_rem_entry`, `ice_flow_rem_prof`, `ice_flow_rem_vsi_prof`, `ice_flow_find_prof_conds`.
- Caller helpers: `ice_flow_set_fld`, `ice_flow_add_fld_raw`.
- RSS management: `ice_add_rss_cfg`, `ice_rem_rss_cfg`, `ice_add_avf_rss_cfg`, `ice_rem_vsi_rss_cfg`, `ice_rem_vsi_rss_list`, `ice_replay_rss_cfg`, `ice_get_rss_cfg`, `ice_set_rss_cfg_symm`, `ice_rss_update_raw_symm`.

## Control flow
For general profiles, callers populate `struct ice_flow_seg_info` with headers and matched fields. `ice_flow_add_prof` validates segment count and mutually exclusive L3/L4 headers, allocates a profile ID, derives matching PTYPEs with `ice_flow_proc_seg_hdrs`, creates extraction sequences with `ice_flow_xtract_fld` and raw extraction helpers, then calls `ice_add_prof` to register the hardware profile. Association to a VSI happens later via `ice_flow_add_entry` and `ice_flow_assoc_prof`.

For RSS, `ice_add_rss_cfg` converts `ice_rss_hash_cfg` into one or two segment descriptors. It first tries to find an exact profile already associated with the VSI. If the same VSI has a profile with matching headers but different fields, it disassociates/removes that old state. It then reuses a compatible existing profile or creates a new one, configures symmetric hashing registers if requested, associates the VSI, and records the config in `hw->rss_list_head` for replay.

For AVF RSS, `ice_add_avf_rss_cfg` validates VF-provided pctype bits, expands L4 requests to include corresponding L3 hashes, converts each pctype group to ICE hash fields, and calls the normal RSS add path. For raw parser profiles, `ice_flow_set_parser_prof` uses parser-supplied FV entries and PTYPEs directly, sets GTP attributes from flags, registers the profile, and associates both destination and FDIR programming VSIs.

## State and persistence behavior
Flow profiles live in `hw->fl_profs[blk]`, protected by `hw->fl_profs_locks[blk]`. Each `ice_flow_prof` stores segment descriptors, matched fields, associated VSI bitmap, entries list, direction, and symmetric RSS flag. RSS replay state lives in `hw->rss_list_head` under `hw->rss_locks`, with each `ice_rss_cfg` holding the hash configuration and VSI bitmap. Actual hardware persistence is delegated to `ice_add_prof`, `ice_add_prof_id_flow`, and direct `GLQF_HSYMM` writes.

## Dependencies and integration points
This file depends on `ice_flex_pipe.c` for hardware profile registration and VSIG/TCAM updates, `ice_parser.h` for raw parser profiles, Linux GRE definitions for field offsets, `libie/pctype.h` for AVF RSS pctype bits, and `ice_common.h` for hardware/VSI helpers. It integrates with ethtool RSS controls, virtchnl/VF RSS requests, Flow Director profile setup, and reset replay.

## Risks and edge cases
- Field extraction relies on hard-coded protocol IDs, offsets, masks, and PTYPE bitmaps; new protocols or DDP layout changes need synchronized updates across `ice_flow.h`, `ice_flex_type.h`, and the bitmap tables.
- `ice_flow_xtract_fld` shares extraction words for sibling fields such as TTL/protocol and ICMP type/code; mask mistakes can silently hash or match unintended bits.
- RSS list locking nests calls into flow-profile operations; deadlock risk should be considered when changing lock order with `fl_profs_locks` or `prof_map_lock`.
- Symmetric raw RSS only verifies the first destination FV entry before programming a multi-word pair; profiles with partial IPv6 address pairs could still configure symmetry using indexes that do not represent a complete pair.
- `ice_flow_rem_entry` removes the entry object but does not disassociate the VSI from the profile; higher-level RSS/FD removal paths must call the profile/VSI disassociation APIs when they intend to change hardware association.

## Test signals
Signals include adding/removing RSS hash fields through ethtool, toggling symmetric RSS, VF RSS capability/config requests, reset replay via `ice_replay_rss_cfg`, raw parser profile setup for Flow Director, GTP-U up/down/extension-header RSS profiles, IPv4/IPv6/TCP/UDP/SCTP hash combinations, and negative tests for invalid header combinations, unsupported AVF pctype bits, extraction sequence exhaustion, and VSI teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_flow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_flow.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_flow.h

## Purpose
`ice_flow.h` declares the public flow-profile and RSS configuration contract for the ice driver. It defines hash-field macros, supported protocol segment bits, flow field indices, flow segment/profile/entry structures, RSS configuration structures, and APIs for adding/removing profiles, entries, RSS configs, and parser profiles.

## Important APIs, types, and functions
- Hash macros: `ICE_FLOW_HASH_*`, `ICE_HASH_*`, GTP/PFCP/L2TP/ESP/AH/NAT-T/L2TPv2 hash combinations, and `ICE_DEFAULT_RSS_HASHCFG`.
- Header model: `enum ice_flow_seg_hdr`, `ICE_FLOW_SEG_HDR_GTPU`, `ICE_FLOW_SEG_HDR_PFCP`, `enum ice_flow_field`, and field-offset constants.
- Flow state: `struct ice_flow_seg_xtrct`, `struct ice_flow_fld_info`, `struct ice_flow_seg_info`, `struct ice_flow_entry`, `struct ice_flow_prof`.
- RSS state: `enum ice_rss_cfg_hdr_type`, `struct ice_rss_hash_cfg`, `struct ice_rss_raw_cfg`, `struct ice_rss_cfg`.
- APIs: `ice_flow_add_prof`, `ice_flow_rem_prof`, `ice_flow_set_parser_prof`, `ice_flow_add_entry`, `ice_flow_rem_entry`, `ice_flow_set_fld`, `ice_flow_add_fld_raw`, `ice_flow_rem_vsi_prof`, `ice_add_rss_cfg`, `ice_rem_rss_cfg`, `ice_add_avf_rss_cfg`, `ice_replay_rss_cfg`, `ice_set_rss_cfg_symm`, `ice_get_rss_cfg`.

## Control flow
The header supports a staged call pattern: describe headers and fields in `ice_flow_seg_info`, register a profile with `ice_flow_add_prof`, associate entries or RSS configs with VSIs, and later remove entries/profiles or replay RSS after reset. RSS callers usually use `ice_rss_hash_cfg`, while Flow Director/raw parser paths may use `ice_flow_set_parser_prof`.

## State and persistence behavior
Structures declared here are embedded in driver-owned lists in `struct ice_hw`. `ICE_FLOW_ENTRY_HNDL` converts an entry pointer to an opaque handle, making handle validity dependent on the lifetime of the allocated `ice_flow_entry`. RSS configs persist in the driver's replay list until explicitly removed or the VSI is cleaned up.

## Dependencies and integration points
The header includes `ice_flex_type.h`, `ice_parser.h`, and Intel libie pctype definitions. It is consumed by RSS, virtchnl/VF, Flow Director, parser, and VSI teardown code. Its field enum must stay below 64 because many APIs represent field sets as a `u64`.

## Risks and edge cases
- Adding a field beyond 64 breaks the `u64` bitmap model; the `static_assert` guards this at compile time.
- Hash macros combine field-index bits and are easy to misuse with header bits; callers must pass them to the correct `hash_flds` field.
- `ICE_FLOW_ENTRY_HNDL` exposes pointer-derived handles, so stale handles after removal are unsafe.
- Header type semantics distinguish outer, inner, and inner-with-outer-IP RSS cases; wrong `hdr_type` can create profiles that hash a different packet layer than intended.

## Test signals
Compile-time coverage for enum limits, RSS add/remove/replay for each advertised hash macro, VF pctype capability mapping, Flow Director raw parser profile setup, and stale-VSI cleanup are the primary signals. Tests should also verify `ICE_DEFAULT_RSS_HASHCFG` stays aligned with virtchnl-advertised capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_flow.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_fltr.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_fltr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_fltr.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_fltr.h -->
