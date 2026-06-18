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
