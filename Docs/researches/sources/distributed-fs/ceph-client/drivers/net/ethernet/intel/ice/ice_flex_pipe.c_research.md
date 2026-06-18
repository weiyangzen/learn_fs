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
