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
