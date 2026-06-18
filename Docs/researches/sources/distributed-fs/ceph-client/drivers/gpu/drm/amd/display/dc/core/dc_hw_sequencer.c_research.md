# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_hw_sequencer.c

## Purpose

`dc_hw_sequencer.c` is a shared AMD Display Core hardware sequencing utility file. It provides color-space helpers, visual-confirmation color selection, wait/synchronization helpers, and a generic block-sequence mechanism that lets higher-level DCN code build ordered hardware programming steps and execute them through the HWSS, HWSEQ, HUBP, DPP, MPC, OPP, DSC, DCCG, ABM, DWBC, MCIF, timing-generator, and DMUB function tables.

The file is intentionally broad. Most exported `hwss_*` functions are small adapters from `union block_sequence_params` to lower-level block-specific callbacks. The substantive logic is in default CSC/black-color mapping, visual-confirmation state derivation, fast flip sequence assembly, outstanding-update waits, DSC configuration calculation, and the consistent block-sequence add/dispatch pattern.

## Important APIs, Types, And Functions

- `enum black_color_format`, `black_color_format[]`: local mapping from output color format/range to TG black values.
- `enum dc_color_space_type`, `struct out_csc_color_matrix_type`, `output_csc_matrix[]`: local normalized color-space categories and static 3x4 output CSC coefficient tables.
- `find_color_matrix(color_space, array_size)`: returns a 12-entry default output CSC coefficient array selected by `get_color_space_type`.
- `color_space_to_black_color(dc, colorspace, black_color)`: maps DC color spaces to RGB or YUV black TG values.
- `hwss_wait_for_blank_complete(tg)`: polls `tg->funcs->is_blanked` up to 100 ms and reports failure through `dm_error`.
- Visual-confirmation helpers: `get_mpctree_visual_confirm_color`, `get_surface_visual_confirm_color`, `get_hdr_visual_confirm_color`, `get_smartmux_visual_confirm_color`, `get_vabc_visual_confirm_color`, `get_subvp_visual_confirm_color`, `get_mclk_switch_visual_confirm_color`, `get_cursor_visual_confirm_color`, `get_dcc_visual_confirm_color`, `get_surface_tile_visual_confirm_color`, `get_fams2_visual_confirm_color`, and `get_refresh_rate_confirm_color`.
- `set_p_state_switch_method(dc, context, pipe_ctx)`: classifies a pipe into `P_STATE_*` visual/debug categories using DML DRAM clock support, vactive margin, FW-based MCLK switching, SubVP pairing, and FreeSync.
- `set_drr_and_clear_adjust_pending(pipe_ctx, stream, params)`: programs DRR through the timing generator and clears `stream->adjust.timing_adjust_pending`.
- `hwss_build_fast_sequence(...)`: builds a `struct block_sequence[]` for fast updates/flips from update flags, DMUB commands, lock requirements, SubVP state, and pipe topology.
- `hwss_execute_sequence(dc, block_sequence, num_steps)`: central dispatcher from `enum block_sequence_func` values to the wrapper or direct lower-level function call that performs each step.
- `hwss_add_*` helpers: append one step to a `struct block_sequence_state` if `*num_steps < MAX_HWSS_BLOCK_SEQUENCE_SIZE`.
- `hwss_wait_for_all_blank_complete`, `hwss_wait_for_odm_update_pending_complete`, `hwss_wait_for_no_pipes_pending`, `hwss_wait_for_outstanding_hw_updates`, `hwss_process_outstanding_hw_updates`: synchronization around pending flips, ODM double-buffer updates, OPP blank updates, MPCC disconnects, and post-update programming.
- Wrapper families: DPP setup/gamut/bias/scaler/cursor/HDR, HUBP surface/config/clock/VM/viewport/blank/SubVP/MALL, MPC output CSC/blending/plane insertion/DWB mux/MPCC idle, OPP format/dynamic expansion/blank/test-pattern, DSC config/enable/disable/read-state/clock, TG/OPTC sync/GSL/DSC/manual trigger/wait, DCCG DTO/ref DSC clock, ABM, MCIF writeback, DWBC, HUBBUB p-state/self-refresh/reset, and DMUB command/SubVP address forwarding.

## Control Flow

Color helpers normalize public `enum dc_color_space` values into internal color-space categories. `find_color_matrix` uses that category to scan `output_csc_matrix`, while `color_space_to_black_color` explicitly switches over every known color space to select TG black levels.

Visual-confirmation helpers derive debug colors from runtime pipe state. Some use pipe-chain traversal: MPCTree confirmation walks to the top pipe, HDR uses the top-most desktop plane, and tile confirmation walks to the bottom-most plane. Others inspect stream transfer functions, pixel formats, Smart Mux config, backlight control type, SubVP/p-state classification, cursor enable state, DCC/mcache assignment, FAMS2 enablement, or refresh-rate range.

`hwss_build_fast_sequence` is the key sequence builder. It returns immediately if the pipe has no plane or stream. It then conditionally appends DCC meta propagation waits, SubVP pipe-control locks, DMUB hardware locks, OPTC pipe-control locks, queued DMUB commands, and per-pipe update work. For each ODM pipe and each MPC pipe in the stack, it checks plane and stream update flags and appends only the needed steps: flip-control GSL, triple buffering, SubVP surface-address save, plane address programming, input/output transfer functions, gamut remap, DPP input CSC setup, bias/scale, CM histogram, visual-confirmation update, and output CSC programming. It unlocks in reverse-style trailing steps, then appends cursor offload and manual-trigger steps for the final pipe when an address update needs a manual trigger.

`hwss_execute_sequence` is a large switch over the block function enum. It unpacks the matching `union block_sequence_params` member and either directly invokes a low-level function pointer or calls a `hwss_*` wrapper. The default branch asserts false, so adding a new enum without dispatcher support is caught in debug builds.

Most `hwss_add_*` helpers are deliberately uniform: populate one union member, set the block function enum, and increment `num_steps`. This file relies on callers and the dispatcher to keep parameter lifetimes valid until execution.

Synchronization helpers walk `MAX_PIPES` or the resource pool pipe count and skip inactive/phantom pipes. They wait for blank completion, ODM/OTG double-buffer drain, no pending flips, all pending updates on OTG masters, and MPCC disconnect idleness before allowing full updates or post-update programming to continue.

## State And Persistence Behavior

This file does not persist data outside the in-memory DC structures and hardware registers it programs. It mutates:

- `pipe_ctx->p_state_type` for debug/visual confirmation.
- `stream->adjust.timing_adjust_pending` after DRR programming.
- `pipe_ctx->visual_confirm_color` in refresh-rate confirmation.
- `hubp->power_gated` in surface config and HUBP clock-control wrappers.
- `plane_state->status.is_flip_pending` while polling flip state.
- `opp->mpcc_disconnect_pending[mpcc_inst]` after waiting for MPC idle.
- Optional caller-owned booleans such as `disallow_self_refresh_applied`, frame-count outputs, and DSC power-gate state outputs.

The durable side effects are hardware-facing: MMIO/register writes and DMUB messages performed through function tables. `hwss_build_fast_sequence` stores pointers into a caller-provided block-sequence array, so referenced objects must remain alive until `hwss_execute_sequence` completes.

## Dependencies And Integration Points

The file depends heavily on AMD DC internals:

- Core DC structures: `struct dc`, `struct dc_state`, `struct pipe_ctx`, `struct dc_stream_state`, `struct dc_plane_state`.
- Hardware abstraction function tables: `dc->hwss`, `dc->hwseq->funcs`, and block-specific `funcs` under TG, HUBP, DPP, MPC, OPP, DSC, DCCG, ABM, MCIF, DWBC, and HUBBUB.
- Resource/topology helpers: `resource_is_pipe_type`, `dc_state_get_pipe_subvp_type`, `dc_state_get_paired_subvp_stream`, `dc_state_is_fams2_in_use`.
- DMUB integration: `dc_wake_and_execute_dmub_cmd`, `dc_dmub_srv_subvp_save_surf_addr`, and `dmub_hw_lock_mgr_does_link_require_lock`.
- DML/DML2 structures for bandwidth, p-state classification, HUBP programming, mcache, and global-sync data.

It is integrated by generation-specific HWSS code that constructs block sequences during commits, fast updates, power transitions, DSC changes, writeback setup, cursor updates, and pipe topology changes. The wrapper layer allows sequence construction to be shared while the actual register programming stays ASIC-specific behind function tables.

## Risks And Edge Cases

- Bounds safety depends on every add/build path respecting `MAX_HWSS_BLOCK_SEQUENCE_SIZE`. The `hwss_add_*` helpers check capacity, but `hwss_build_fast_sequence` appends directly without local capacity checks.
- Many wrappers only null-check the block object and function pointer, not every nested pointer. Callers must pass fully populated, generation-appropriate params.
- `get_dcc_visual_confirm_color` indexes `id_colors[assigned_id]` for mcache IDs other than `0xF`; IDs outside `0..7` would be unsafe if upstream mcache programming violates expectations.
- The color-space type function contains an unreachable duplicated `COLOR_SPACE_YCBCR709` check before `COLOR_SPACE_YCBCR709_BLACK`; behavior is still correct for black because the explicit black case follows.
- Static CSC tables contain a TODO for limited YCbCr values, so color correctness depends on later validation elsewhere.
- Wait loops can block commit paths for up to 100 ms per pipe/operation; missed pending-status updates or hardware that never drains can produce asserts or boot/update stalls.
- DSC config calculation divides horizontal slices by `opp_cnt`; callers must avoid zero and ensure stream DSC config is divisible for the topology.
- Sequence params often hold raw pointers to stack or context objects from the caller. Deferring execution beyond those lifetimes would corrupt hardware programming.
- Debug visual confirmation changes output border/colors intentionally and must be gated by `dc->debug.visual_confirm`.

## Test Signals

- Kernel build coverage for AMDGPU display catches missing enum cases, function declarations, and union member mismatches.
- Unit or simulator tests should validate `find_color_matrix`, `color_space_to_black_color`, and visual-confirmation helpers for representative RGB/YUV/HDR/SubVP/DCC paths.
- Sequence tests can construct mock `dc`, `pipe_ctx`, and function tables, set update flags, run `hwss_build_fast_sequence`, and verify ordered function enums and params.
- Dispatcher tests should ensure every block function enum has a non-default `hwss_execute_sequence` case.
- Hardware or emulation tests should cover fast flips, SubVP immediate flips, FAMS2/DMUB lock paths, output CSC changes, DCC metadata propagation, cursor offload/manual trigger, DSC enable/disable/reconfigure, ODM combine/bypass changes, MPCC disconnects, writeback enable/update/disable, and p-state/self-refresh transitions.
- Runtime debug signals include `dm_error("failed to blank crtc")`, asserts in pending-flip and dispatcher paths, visual-confirm colors, link/DMUB command failures outside this file, and stalls around wait loops.
