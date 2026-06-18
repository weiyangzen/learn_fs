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
