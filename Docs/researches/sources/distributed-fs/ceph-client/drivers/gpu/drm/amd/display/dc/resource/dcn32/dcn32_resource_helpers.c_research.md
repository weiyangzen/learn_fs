# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource_helpers.c

## Purpose
This file implements DCN32 policy helpers for SubVP, MALL allocation, DET override, pipe cleanup, MPO/rotation checks, and firmware-assisted MCLK switching through vblank stretch. These routines are consumed by DCN32/DCN321 resource function tables and DML/DML2 callback configuration to turn a proposed `dc_state` into hardware allocation and power-management decisions.

## Important APIs, Types, And Functions
- `dcn32_helper_calculate_mall_bytes_for_cursor` computes cursor MALL bytes from HUBP cursor attributes and stream cursor format, rounding up to DCN3.2 MALL block size and adding an alignment block.
- `dcn32_helper_calculate_num_ways_for_subvp` converts DML-computed SubVP MALL bytes into cache ways, honoring `dc->debug.force_subvp_num_ways`.
- `dcn32_merge_pipes_for_subvp` tears down ODM and pipe-split topology not supported for SubVP, releasing DSC when needed and clearing plane/stream resources.
- State predicates include `dcn32_all_pipes_have_stream_and_plane`, `dcn32_subvp_in_use`, `dcn32_mpo_in_use`, `dcn32_any_surfaces_rotated`, `dcn32_is_center_timing`, and `dcn32_is_psr_capable`.
- DET policy lives in `dcn32_determine_det_override`, `dcn32_set_det_allocations`, and the private `override_det_for_subvp`.
- FPO support is evaluated by `dcn32_can_support_mclk_switch_using_fw_based_vblank_stretch`, with private refresh-rate helpers.
- Admission helpers `dcn32_subvp_drr_admissable` and `dcn32_subvp_vblank_admissable` reject unsafe active-plus-blank combinations and PSR/Freesync conflicts.
- `dcn32_update_dml_pipes_odm_policy_based_on_context` mirrors existing ODM slice topology into DML pipes, while `dcn32_override_min_req_dcfclk` raises DCFCLK for SubVP.

## Control Flow
Most helpers iterate `dc->res_pool->pipe_count` over `context->res_ctx.pipe_ctx`. DET allocation first counts non-phantom streams, divides 18 DET segments per stream, then divides per plane and per split pipe before applying a special two-display high-refresh FHD override. Single-pipe non-linear, non-dual-plane cases prefer unbounded requesting with smaller DET unless disabled by debug flags. FPO evaluation rejects null contexts, disabled debug/cap flags, existing shutdown requests, more than two streams, no-plane candidates, EDID panel disable flags, low refresh, unsupported vblank stretch range, non-Freesync streams, and gaming VRR combinations blocked by policy. SubVP DRR/Vblank admission counts one SubVP main and one non-SubVP pipe, rejects 1080p active-plus-blank cases, screens PSR/Freesync state, checks refresh below 120 Hz, and for Vblank requires DML to report `dm_dram_clock_change_vblank_w_mall_sub_vp`.

## State And Persistence
The functions mutate only caller-owned transient state: pipe links/resources during SubVP merge, `display_e2e_pipe_params_st` fields for DET and ODM policy, and `context->bw_ctx.bw.dcn.clk.dcfclk_khz` when SubVP needs a minimum clock. They read persistent policy from `dc->debug`, capability flags from `dc->caps`, and DML results from `context->bw_ctx`.

## Dependencies And Integration Points
This file depends on DC state private helpers, stream internals, DML FPU helpers, display mode VBA utilities, resource topology helpers, and DCN20 DSC release. It integrates with validation paths that populate DML pipes, DML2 SubVP callbacks, hardware sequencing that later programs DET/ODM values, and policy gates for PSR, Freesync, MALL, and firmware-assisted MCLK switching.

## Risks And Edge Cases
Pipe-topology mutation is delicate: stale `top_pipe`, `bottom_pipe`, ODM links, DSC pointers, or resource structs could leak resources or corrupt later programming. DET division uses integer truncation and assumes an 18-segment policy, so unusual stream/plane splits can under-allocate unless DML catches it. Cursor MALL sizing assumes cursor attributes are initialized when enabled. FPO math depends on pixel-clock and timing totals and has several zero/null guards, but policy mistakes can cause flicker or unsupported memory-clock switching. SubVP DRR/Vblank admission relies on pipe type checks and stream flags that must match Display Core semantics.

## Test Signals
Exercise single-pipe non-linear surfaces, dual-plane video, pipe split, ODM split/merge, SubVP phantom streams, two-display SubVP plus DRR/Vblank, 1080p60 active-plus-blank rejection, PSR-capable secondary displays, Freesync/VRR gaming policy, FPO one- and two-display cases, cursor formats and large cursor sizes, rotated surfaces, center timing, and DML pipe DET/ODM field output.
