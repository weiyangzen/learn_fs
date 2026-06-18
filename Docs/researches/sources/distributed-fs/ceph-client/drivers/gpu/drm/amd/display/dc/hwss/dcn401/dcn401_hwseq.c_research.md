# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn401/dcn401_hwseq.c

## Purpose
`dcn401_hwseq.c` is the DCN 4.01 display hardware sequencer implementation for AMDGPU DC. It owns the DCN401-specific ordering around display hardware initialization, stream timing/link programming, color management, cursor positioning, bandwidth and watermark transitions, ODM/DSC changes, MALL/CAB idle optimizations, front-end pipe programming, power gating, writeback sequencing, and block-sequence based programming helpers. It is a bridge between high-level `dc_state`/`pipe_ctx` state and low-level resource function tables for HUBP, DPP, MPC, OPP, DCCG, timing generators, DSC, DMUB, DIO, audio, panel control, and Hubbub.

## Important APIs, Types, and Functions
- Clock and boot initialization: `dcn401_initialize_min_clocks()` seeds minimum display, DCF, SOC, DRAM, DPP, DTB, and deep-sleep clocks from `clk_mgr->bw_params`; `dcn401_init_hw()` performs the full boot/resume hardware bring-up.
- Color pipeline: `dcn401_program_gamut_remap()` programs three MPCC gamut remap blocks; `dcn401_set_mcm_luts()` programs movable color management 1D LUT, shaper, and 3D LUT paths, including fast-load DMA; `dcn401_set_output_transfer_func()` uses MPC shaper/3DLUT when possible and falls back to output gamma.
- Stream timing/link: `dcn401_calculate_dccg_tmds_div_value()`, `dcn401_enable_stream_timing()`, `dcn401_enable_stream()`, `dcn401_unblank_stream()`, `dcn401_disable_link_output()`, and `dcn401_setup_hpo_hw_control()` coordinate DCCG dividers, pixel clocks, OPTC timing, DP/HDMI link encoders, HPO/128b132b paths, and PHY state.
- Cursor and offload: `dcn401_set_cursor_position()` translates stream-space cursor coordinates into per-pipe recout space with ODM/MPC split handling; `dcn401_update_cursor_offload_pipe()` copies HUBP/DPP cursor register snapshots into the DMUB cursor-offload shared buffer.
- Bandwidth and idle power: `dcn401_prepare_bandwidth()`, `dcn401_optimize_bandwidth()`, `dcn401_update_bandwidth()`, `dcn401_apply_idle_power_optimizations()`, `dcn401_fams2_update_config()`, and DMUB lock helpers manage clocks, watermarks, compbuf, P-state/FAMS2 behavior, CAB allocation, and MALL eligibility.
- Pipe and topology programming: `dcn401_detect_pipe_changes()`, `dcn401_program_pipe()`, `dcn401_program_front_end_for_ctx()`, `dcn401_post_unlock_program_front_end()`, `dcn401_reset_back_end_for_pipe()`, and `dcn401_reset_hw_ctx_wrap()` drive the main update lifecycle.
- ODM/DSC: `dcn401_update_odm()` and `dcn401_update_odm_sequence()` update OPTC ODM combine/bypass, OPP clock/extra-pixel state, and DSC connection/disconnection when slice topology changes.
- Sequence framework: `*_sequence` variants append `hwss_add_*` operations to `struct block_sequence_state` instead of touching hardware immediately. These cover pipe programming, plane enable/disable, plane power-down/disconnect, MPCC update, writeback, GSL, blanking, MALL, DCHUBP/DPP update, and recovery paths.

## Control Flow and State Behavior
`dcn401_init_hw()` starts with clock-manager initialization and DC-mode power-limit discovery, initializes DCCG, applies selected memory low-power defaults, derives reference clocks from BIOS firmware info, initializes link encoders and existing DIG/link status, blanks DP displays, optionally initializes or powers down pipes depending on accelerated mode and seamless boot, initializes audio/panel/ABM blocks, enables clock gating, enables HPO hardware control, initializes watermarks/CRB/request limits, and finally queries DMUB caps. The function mutates persistent driver state such as `dc->caps`, `res_pool->ref_clocks`, link active/FEC/symclk state, ABM backlight state, `debug.fams2_config`, and the bounding box when FAMS2 or DCHUB reference changes require it.

Normal commit programming is split across prepare, lock, program, unlock, and optimize phases. `dcn401_prepare_bandwidth()` raises clocks and programs non-optimized watermarks before the pipe update. `dcn401_program_front_end_for_ctx()` detects per-pipe changes, blanks/disconnects disabled pipes, updates ODM for blanked OTG masters, then walks each top pipe and its bottom-pipe chain to program HUBP/DPP/MPC/OPP/TG state. `dcn401_post_unlock_program_front_end()` handles post-double-buffer work: OPP reset, disable-plane cleanup, flip-pending waits, ODM slice-count transition waits, phantom pipe programming, P-state force updates, MALL pipe config, and selected workarounds. `dcn401_optimize_bandwidth()` restores optimized watermarks, compbuf, clocks, and FAMS2 after the visible update.

The sequence-based functions model the same control flow as explicit block steps, which is important for DMUB-assisted or batched hardware sequencing. Several sequence functions update software state while queuing hardware operations, for example MPCC IDs on HUBP, GSL group allocation bits in `res_pool->gsl_groups`, and pipe resource pointers during disable.

## Dependencies and Integration Points
This file depends heavily on function tables from `struct resource_pool` and `struct dce_hwseq`: DCCG (`set_pixel_rate_div`, DSC clocks, DP stream clocks), Hubbub (`program_watermarks`, DET/compbuf programming, P-state control), HUBP/DPP/MPC/OPP methods, timing generator methods, link service helpers, link HWSS, DMUB services, and cross-generation DCN helpers from DCN10/DCN20/DCN30/DCN32/DCN35. It is wired into the driver by `dcn401_init.c`, which installs these functions into `dc->hwss` and `dc->hwseq->funcs`.

## Risks and Edge Cases
- Hardware ordering is the primary risk. Power gating, DC IP request control, DSC disconnect, MPCC idle waits, FAMS2 locks, and p-state transitions must remain in the documented order to avoid hangs, underflow, stale double-buffer updates, or clocks dropping too early.
- Several paths assume instance identity, especially HUBP/DPP/MPCC instance matching. `dcn401_detect_pipe_changes()` comments that MPCC sequencing assumes MPCC instance equals pipe/HUBP index.
- 3D LUT fast-load has hardware constraints: toggling DMA and host modes is not atomic, fast load requires HUBP support, and a VREADY workaround is needed when unlocking.
- MALL/CAB idle optimization is deliberately disabled for PSR, stereo, TMZ, or over-capacity cache-way cases; tests must verify that unsupported surfaces do not enter MALL.
- Cursor placement is sensitive to stream scaling, clipped source translation, ODM slices, MPC split overlays, negative coordinates, magnification, and recout bounds.
- Some defensive checks are function-pointer based rather than hard requirements. Missing resource methods can silently skip features, so ASIC integration needs coverage for each populated function table.

## Test Signals
- Boot/resume on accelerated and non-accelerated modes, seamless eDP boot, headless boot with DIG already enabled, and S3/S4 transitions.
- Multi-monitor DP/eDP/HDMI/TMDS link enable/disable, including 128b/132b DP HPO, FEC state, symclk ref-count transitions, and eDP backlight/power sequencing.
- Plane enable/disable, MPO, ODM combine changes, DSC on/off, SubVP main/phantom, writeback enable/update/disable, ABM, test patterns, and pipe topology changes.
- Color-management tests for plane gamut remap, stream gamut remap, input/output transfer functions, MCM 1D/shaper/3D LUT host and DMA paths, and 3D LUT unlock workaround.
- Watermark/P-state/FAMS2 transitions under high bandwidth, low power, DC-mode softmax, MALL/CAB eligibility, PSR exclusion, and recovery-enabled sanity checks.
- Cursor tests across scaling, clipping, split pipes, ODM, magnification, offload, and edges outside the visible recout.
