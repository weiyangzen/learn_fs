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
