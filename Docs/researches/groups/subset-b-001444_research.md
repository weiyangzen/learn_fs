# Research: subset-b-001444

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn401/dcn401_hwseq.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn401/dcn401_hwseq.c

### Purpose
`dcn401_hwseq.c` is the DCN 4.01 display hardware sequencer implementation for AMDGPU DC. It owns the DCN401-specific ordering around display hardware initialization, stream timing/link programming, color management, cursor positioning, bandwidth and watermark transitions, ODM/DSC changes, MALL/CAB idle optimizations, front-end pipe programming, power gating, writeback sequencing, and block-sequence based programming helpers. It is a bridge between high-level `dc_state`/`pipe_ctx` state and low-level resource function tables for HUBP, DPP, MPC, OPP, DCCG, timing generators, DSC, DMUB, DIO, audio, panel control, and Hubbub.

### Important APIs, Types, and Functions
- Clock and boot initialization: `dcn401_initialize_min_clocks()` seeds minimum display, DCF, SOC, DRAM, DPP, DTB, and deep-sleep clocks from `clk_mgr->bw_params`; `dcn401_init_hw()` performs the full boot/resume hardware bring-up.
- Color pipeline: `dcn401_program_gamut_remap()` programs three MPCC gamut remap blocks; `dcn401_set_mcm_luts()` programs movable color management 1D LUT, shaper, and 3D LUT paths, including fast-load DMA; `dcn401_set_output_transfer_func()` uses MPC shaper/3DLUT when possible and falls back to output gamma.
- Stream timing/link: `dcn401_calculate_dccg_tmds_div_value()`, `dcn401_enable_stream_timing()`, `dcn401_enable_stream()`, `dcn401_unblank_stream()`, `dcn401_disable_link_output()`, and `dcn401_setup_hpo_hw_control()` coordinate DCCG dividers, pixel clocks, OPTC timing, DP/HDMI link encoders, HPO/128b132b paths, and PHY state.
- Cursor and offload: `dcn401_set_cursor_position()` translates stream-space cursor coordinates into per-pipe recout space with ODM/MPC split handling; `dcn401_update_cursor_offload_pipe()` copies HUBP/DPP cursor register snapshots into the DMUB cursor-offload shared buffer.
- Bandwidth and idle power: `dcn401_prepare_bandwidth()`, `dcn401_optimize_bandwidth()`, `dcn401_update_bandwidth()`, `dcn401_apply_idle_power_optimizations()`, `dcn401_fams2_update_config()`, and DMUB lock helpers manage clocks, watermarks, compbuf, P-state/FAMS2 behavior, CAB allocation, and MALL eligibility.
- Pipe and topology programming: `dcn401_detect_pipe_changes()`, `dcn401_program_pipe()`, `dcn401_program_front_end_for_ctx()`, `dcn401_post_unlock_program_front_end()`, `dcn401_reset_back_end_for_pipe()`, and `dcn401_reset_hw_ctx_wrap()` drive the main update lifecycle.
- ODM/DSC: `dcn401_update_odm()` and `dcn401_update_odm_sequence()` update OPTC ODM combine/bypass, OPP clock/extra-pixel state, and DSC connection/disconnection when slice topology changes.
- Sequence framework: `*_sequence` variants append `hwss_add_*` operations to `struct block_sequence_state` instead of touching hardware immediately. These cover pipe programming, plane enable/disable, MPCC update, writeback, GSL, blanking, MALL, DCHUBP/DPP update, and recovery paths.

### Control Flow and State Behavior
`dcn401_init_hw()` starts with clock-manager initialization and DC-mode power-limit discovery, initializes DCCG, applies selected memory low-power defaults, derives reference clocks from BIOS firmware info, initializes link encoders and existing DIG/link status, blanks DP displays, optionally initializes or powers down pipes depending on accelerated mode and seamless boot, initializes audio/panel/ABM blocks, enables clock gating, enables HPO hardware control, initializes watermarks/CRB/request limits, and finally queries DMUB caps. The function mutates persistent driver state such as `dc->caps`, `res_pool->ref_clocks`, link active/FEC/symclk state, ABM backlight state, `debug.fams2_config`, and the bounding box when FAMS2 or DCHUB reference changes require it.

Normal commit programming is split across prepare, lock, program, unlock, and optimize phases. `dcn401_prepare_bandwidth()` raises clocks and programs non-optimized watermarks before the pipe update. `dcn401_program_front_end_for_ctx()` detects per-pipe changes, blanks/disconnects disabled pipes, updates ODM for blanked OTG masters, then walks each top pipe and its bottom-pipe chain to program HUBP/DPP/MPC/OPP/TG state. `dcn401_post_unlock_program_front_end()` handles post-double-buffer work: OPP reset, disable-plane cleanup, flip-pending waits, ODM slice-count transition waits, phantom pipe programming, P-state force updates, MALL pipe config, and selected workarounds. `dcn401_optimize_bandwidth()` restores optimized watermarks, compbuf, clocks, and FAMS2 after the visible update.

The sequence-based functions model the same control flow as explicit block steps, which is important for DMUB-assisted or batched hardware sequencing. Several sequence functions update software state while queuing hardware operations, for example MPCC IDs on HUBP, GSL group allocation bits in `res_pool->gsl_groups`, and pipe resource pointers during disable.

### Dependencies and Integration Points
This file depends heavily on function tables from `struct resource_pool` and `struct dce_hwseq`: DCCG (`set_pixel_rate_div`, DSC clocks, DP stream clocks), Hubbub (`program_watermarks`, DET/compbuf programming, P-state control), HUBP/DPP/MPC/OPP methods, timing generator methods, link service helpers, link HWSS, DMUB services, and cross-generation DCN helpers from DCN10/DCN20/DCN30/DCN32/DCN35. It is wired into the driver by `dcn401_init.c`, which installs these functions into `dc->hwss` and `dc->hwseq->funcs`.

### Risks and Edge Cases
- Hardware ordering is the primary risk. Power gating, DC IP request control, DSC disconnect, MPCC idle waits, FAMS2 locks, and p-state transitions must remain in the documented order to avoid hangs, underflow, stale double-buffer updates, or clocks dropping too early.
- Several paths assume instance identity, especially HUBP/DPP/MPCC instance matching. `dcn401_detect_pipe_changes()` comments that MPCC sequencing assumes MPCC instance equals pipe/HUBP index.
- 3D LUT fast-load has hardware constraints: toggling DMA and host modes is not atomic, fast load requires HUBP support, and a VREADY workaround is needed when unlocking.
- MALL/CAB idle optimization is deliberately disabled for PSR, stereo, TMZ, or over-capacity cache-way cases; tests must verify that unsupported surfaces do not enter MALL.
- Cursor placement is sensitive to stream scaling, clipped source translation, ODM slices, MPC split overlays, negative coordinates, magnification, and recout bounds.
- Some defensive checks are function-pointer based rather than hard requirements. Missing resource methods can silently skip features, so ASIC integration needs coverage for each populated function table.

### Test Signals
- Boot/resume on accelerated and non-accelerated modes, seamless eDP boot, headless boot with DIG already enabled, and S3/S4 transitions.
- Multi-monitor DP/eDP/HDMI/TMDS link enable/disable, including 128b/132b DP HPO, FEC state, symclk ref-count transitions, and eDP backlight/power sequencing.
- Plane enable/disable, MPO, ODM combine changes, DSC on/off, SubVP main/phantom, writeback enable/update/disable, ABM, test patterns, and pipe topology changes.
- Color-management tests for plane gamut remap, stream gamut remap, input/output transfer functions, MCM 1D/shaper/3D LUT host and DMA paths, and 3D LUT unlock workaround.
- Watermark/P-state/FAMS2 transitions under high bandwidth, low power, DC-mode softmax, MALL/CAB eligibility, PSR exclusion, and recovery-enabled sanity checks.
- Cursor tests across scaling, clipping, split pipes, ODM, magnification, offload, and edges outside the visible recout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn401/dcn401_hwseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn401/dcn401_hwseq.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn401/dcn401_hwseq.h

### Purpose
`dcn401_hwseq.h` declares the DCN401 hardware sequencer surface consumed by DCN401 initialization and reused by later DCN generations such as DCN42. It exposes direct hardware programming functions and sequence-builder variants for the display core commit path.

### Important APIs and Types
- `enum ips_ono_state` and `struct ips_ono_region_state` describe ON/OFF/in-progress power-gating state for IPS/ONO-style regions, though the header only defines the types.
- Public hardware entry points include initialization, stream timing, stream enable/unblank, link disable, cursor position, bandwidth prepare/optimize/update, idle power optimization, ODM update, front-end programming, pipe reset, pipe change detection, and hardware release.
- Color and LUT APIs include `dcn401_program_gamut_remap()`, `dcn401_set_mcm_luts()`, `dcn401_set_output_transfer_func()`, `dcn401_populate_mcm_luts()`, and `dcn401_trigger_3dlut_dma_load()`.
- Sequence APIs mirror critical immediate operations: pipe programming, plane enable/disable, plane power-down/disconnect, blanking, writeback, GSL locking, MPCC updates, vupdate interrupt setup, HDR multiplier, MALL pipe config, p-state verification, and recovery.

### Control Flow and State Behavior
The header itself stores no state, but its signatures show the state model: most operations take `struct dc *`, `struct dc_state *`, `struct pipe_ctx *`, or `struct block_sequence_state *`. Immediate functions mutate hardware and software state directly; sequence functions append work into a `block_sequence_state` while sometimes updating software-visible fields such as pipe resource ownership.

### Dependencies and Integration Points
It includes DC core types, stream types, private and public sequencer declarations, and DCN401 DCCG definitions. It is included by `dcn401_init.c`, `dcn42_init.c`, and DCN42 hardware sequencing code, making DCN401 a base implementation layer for later ASICs.

### Risks and Test Signals
The main risk is API drift: the init dispatch tables rely on these prototypes matching function-pointer contracts in `hw_sequencer_funcs` and `hwseq_private_funcs`. Header-level validation comes from successful compilation across DCN401 and DCN42 configs, plus runtime coverage of both immediate and sequence paths where a declared helper is installed into a function table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn401/dcn401_hwseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn401/dcn401_init.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn401/dcn401_init.c

### Purpose
`dcn401_init.c` installs the DCN401 hardware sequencer vtables. It maps the generic DC hardware sequencing contract to a mix of DCN401-specific functions and inherited helpers from DCE110, DCN10, DCN20, DCN21, DCN30, DCN31, DCN32, and DCN35.

### Important APIs and Tables
- `static const struct hw_sequencer_funcs dcn401_funcs` is the public sequencer dispatch table stored into `dc->hwss`.
- `static const struct hwseq_private_funcs dcn401_private_funcs` is the private sequencer dispatch table stored into `dc->hwseq->funcs`.
- `dcn401_hw_sequencer_init_functions(struct dc *dc)` performs the assignment.

The table selects DCN401 implementations for hardware init, gamut remap, front-end programming, post-unlock programming, stream enable/unblank, bandwidth prepare/optimize/update, cursor position/offload pipe update, idle power optimization, link disable, DCC metadata wait, DMUB hardware locks, FAMS2, pipe change detection, plane/MPCC/writeback sequence helpers, ODM sequence helpers, MALL sequence, and recovery hooks. It reuses mature earlier-generation helpers for context application, plane address update, DCHUB update, infoframes, audio, DRR, status, eDP controls, writeback immediate functions, VM/system context, GSL flip control, phantom streams, DCS power gating, and several workarounds.

### Control Flow and State Behavior
The file has no runtime control flow beyond initialization. Its state effect is decisive: after `dcn401_hw_sequencer_init_functions()` runs, every later commit path invokes the selected function pointers. `NULL` entries are also meaningful; for example `apply_ctx_for_surface`, `does_plane_fit_in_mall`, `calculate_dccg_k1_k2_values`, and private `populate_mcm_luts` are intentionally absent.

### Dependencies and Integration Points
This file integrates DCN401 with the generic Display Core by including the headers for all reused generation helpers. It is typically called during DC resource construction for the ASIC. Because it mixes generations, behavioral changes in inherited helpers can affect DCN401 even when this file is unchanged.

### Risks and Test Signals
Risks center on vtable mismatches and stale inherited behavior. A wrong function pointer can cause subtle ordering regressions, especially between immediate and sequence variants. Build coverage validates signatures; runtime test signals include full display bring-up, modesets, suspend/resume, multi-plane commits, link enable/disable, cursor offload, FAMS2/idle power, and sequence-enabled paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn401/dcn401_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn401/dcn401_init.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn401/dcn401_init.h

### Purpose
`dcn401_init.h` is a small public declaration header for DCN401 hardware sequencer initialization. It forwards `struct dc` and declares `dcn401_hw_sequencer_init_functions()`.

### Important API
- `void dcn401_hw_sequencer_init_functions(struct dc *dc);` installs DCN401 public and private hardware sequencer function tables.

### Control Flow, State, and Integration
The header has no persistent state and no implementation logic. Its only role is to let the DCN401 resource construction path call the vtable initializer without importing implementation internals.

### Risks and Test Signals
Risk is limited to declaration/definition mismatch or include-guard mistakes. Compile coverage is the primary signal; runtime confidence comes indirectly from successful DCN401 device initialization using the installed vtables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn401/dcn401_init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn42/dcn42_hwseq.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn42/dcn42_hwseq.c

### Purpose
`dcn42_hwseq.c` implements the DCN 4.2 hardware sequencer deltas on top of DCN401. It provides DCN42-specific hardware initialization, MPCC blending, RMCM color programming, bandwidth wrappers with driver power gating, root-clock and block power control, stereo setup, DMUB hardware locking policy, and boot power-down handling.

### Important APIs and Functions
- `dcn42_init_hw()` is the DCN42 boot/resume hardware initializer. It closely follows DCN401 init but differs in clock-gating programming, request-limit channel source, missing `dcn401_initialize_min_clocks()` call in the accelerated-mode block, extra null checks on link encoders, and PG status initialization/debug logging.
- `dcn42_update_mpcc()` programs MPCC blending for DCN42, using 12-bit-looking alpha/gain defaults (`0xfff`) and direct MPC insert/remove/update operations.
- `dcn42_program_cm_hist()` forwards plane color histogram controls to DPP.
- `dcn42_set_mcm_luts()` calls `dcn401_set_mcm_luts()` for MCM and optionally adds RMCM fast-load programming through `dcn42_program_rmcm_luts()`.
- `dcn42_prepare_bandwidth()` and `dcn42_optimize_bandwidth()` wrap DCN401 bandwidth transitions with block ungate/gate and root-clock sequencing.
- `dcn42_calc_blocks_to_gate()` and `dcn42_calc_blocks_to_ungate()` compute `struct pg_block_update` masks for DIO, HPO, HUBP, DPP, MPCC, DSC, OPP, OPTC, DPSTREAM, PHYSYMCLK, DCCG/DCIO/DCHUBBUB/DCHVM/DCOH, based on current and target resource state.
- `dcn42_hw_block_power_up()`, `dcn42_hw_block_power_down()`, and `dcn42_root_clock_control()` execute PG controller and root-clock operations in DCN42-specific order.
- `dcn42_dmub_hw_control_lock()` extends lock requirements beyond FAMS2/cursor offload by consulting `dmub_hw_lock_mgr_does_context_require_lock()`.
- `dcn42_power_down_on_boot()` powers down BIOS-left-enabled display hardware and asks the clock manager for low-power state.

### Control Flow and State Behavior
DCN42 init mutates the same broad state as DCN401 init: clock capabilities, reference clocks, link active/FEC/symclk state, panel and ABM state, DMUB caps, FAMS2 enable compatibility, and bandwidth bounding boxes. It additionally initializes `pg_cntl` status and prints optional PG status debug logs.

The bandwidth path is the main DCN42 behavioral difference. Before DCN401 prepare-bandwidth work, DCN42 calculates blocks that must be powered/root-clocked on for the target context and powers them up. After DCN401 optimize-bandwidth work, it calculates unused blocks and powers/root-clocks them down. The gate/ungate calculations persist only in the local `pg_block_update` mask, but the called PG functions update hardware power state and PG controller state.

RMCM programming is conditional on a stream-level RMCM 3D LUT allocation. It requires MPC RMCM shaper/3DLUT functions and HUBP fast-load support. It programs shaper LUT data, configures fast-load 3DLUT parameters, programs HUBP DMA config/address, and power-cycles the RMCM shaper/3DLUT block around configuration.

### Dependencies and Integration Points
DCN42 reuses many DCN401 functions through `dcn42_init.c`, so this file is intentionally a delta layer. It depends on `pg_cntl` callbacks for driver power gating, `dccg` callbacks for DSC/root clocks, DCN35 root-clock helpers, DMUB hardware lock manager helpers, DC stream private helpers for RMCM LUT lookup, and resource/pipe topology state from `dc_state`.

### Risks and Edge Cases
- Power-gating mask correctness is critical. A missed ungate can cause programming a powered-down block; a missed gate wastes power or conflicts with IPS.
- `dcn42_calc_blocks_to_gate()` has a local `hpo_frl_stream_enc_acquired` initialized false and never set in this file, so HPO gating currently depends only on HPO DP acquisition.
- Gate/ungate arrays use resource instance indices from pipe resources; resource remapping bugs can target the wrong hardware block.
- RMCM LUT programming currently uses `lut_bank_a = true` with a TODO to read from hardware, so bank conflicts are a risk during dynamic updates.
- `dcn42_program_rmcm_luts()` does not propagate its return value through `dcn42_set_mcm_luts()`; the MCM result is returned even if RMCM fails.
- Header/footer comments indicate no sequential ONO order for DCN42, but hardware PG ordering still matters for DIO/HPO/DSC/HUBP/DPP/plane/OTG domains.

### Test Signals
- Boot/resume and headless boot with BIOS-enabled DIG, including `power_down_on_boot()` and low-power clock assertion.
- Driver PG tests while adding/removing streams, planes, HPO DP, DSC, DIO encoders, disconnected links, and active streams.
- RMCM and MCM color tests with shaper enabled, DMA 3D LUT enabled, unsupported HUBP/MPC callbacks, missing stream RMCM allocation, and repeated LUT updates.
- MPO blending/global alpha/per-pixel alpha format tests for `dcn42_update_mpcc()`.
- PSR/Replay/FAMS2/cursor-offload scenarios that require or skip DMUB hardware locks.
- Stereo programming on timing generator and OPP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn42/dcn42_hwseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn42/dcn42_hwseq.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn42/dcn42_hwseq.h

### Purpose
`dcn42_hwseq.h` declares the DCN42-specific hardware sequencer deltas that are installed by `dcn42_init.c`. It keeps the DCN42 public surface small because most behavior is inherited from DCN401 and earlier generations.

### Important APIs
The header declares DCN42 init, MPCC update, color histogram programming, MCM/RMCM LUT programming, hardware release, bandwidth prepare/optimize, power-gating mask calculation, block power up/down, root-clock control, DMUB hardware lock helpers, stereo setup, and boot power-down.

### Control Flow and State Behavior
The declarations show the DCN42 state model: functions operate on `struct dc`, `struct dc_state`, `struct pipe_ctx`, `struct dc_plane_state`, `struct dc_plane_cm`, `struct hubp`, `struct mpc`, and `struct pg_block_update`. PG helpers split calculation from execution, allowing prepare/optimize code to compute a power transition mask and then apply root-clock and block power operations.

### Dependencies and Integration Points
It includes `dc.h` and `hw_sequencer_private.h`, so it is tied to the DC core and private sequencer contracts. Its functions are consumed by `dcn42_init.c` and may be invoked through generic `dc->hwss` or `dc->hwseq->funcs` pointers.

### Risks and Test Signals
API risk is mostly around keeping declarations synchronized with the function tables and implementation. Compile coverage validates signatures. Runtime coverage should exercise DCN42-specific PG, RMCM, MPCC, stereo, DMUB lock, and boot power-down paths rather than only inherited DCN401 behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn42/dcn42_hwseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn42/dcn42_init.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn42/dcn42_init.c

### Purpose
`dcn42_init.c` installs the DCN42 hardware sequencer vtables. It composes DCN42-specific functions with inherited DCN401, DCN35, DCN32, DCN31, DCN30, DCN21, DCN20, DCN10, DCE110, and DCN314 helpers.

### Important APIs and Tables
- `static const struct hw_sequencer_funcs dcn42_funcs` is installed into `dc->hwss`.
- `static const struct hwseq_private_funcs dcn42_private_funcs` is installed into `dc->hwseq->funcs`.
- `dcn42_hw_sequencer_init_functions(struct dc *dc)` performs both assignments.

DCN42 uses its own `init_hw`, `power_down_on_boot`, MPCC update, color histogram, bandwidth prepare/optimize, hardware release, setup stereo, DMUB locks, and driver PG hooks. It reuses many DCN401 implementations for gamut remap, front-end programming, stream enable/unblank, output transfer, link disable, cursor position/offload, DCC propagation wait, FAMS2 update, outstanding updates, pipe change detection, and backend reset. It selects DCN35 implementations for plane enable/disable, DRR, static screen control, idle power optimization, cursor offload management, and root-clock private helpers.

### Control Flow and State Behavior
Like the DCN401 init file, runtime behavior is function-pointer installation. The table contents define which hardware paths are active for the ASIC. Driver PG is exposed through public `hwss` entries (`hw_block_power_up`, `hw_block_power_down`, `root_clock_control`, `calc_blocks_to_gate`, `calc_blocks_to_ungate`) while root-clock primitive helpers are installed in the private table.

### Dependencies and Integration Points
The file integrates DCN42 with the generic DC commit code and with inherited generation implementations. It includes DCN314 specifically for `dcn314_resync_fifo_dccg_dio`, DCN35 for root-clock and power behavior, and DCN401 for most DCN4 base sequencing.

### Risks and Test Signals
The risk profile is vtable composition. A stale inherited function can miss a DCN42 hardware requirement, and a DCN42 override can accidentally bypass sequence variants available in DCN401. Build tests catch type mismatches; runtime tests should verify DCN42 boot, normal modesets, power-down-on-boot, driver PG, root-clock control, PSR/Replay locks, RMCM, stereo, cursor offload, and inherited DCN401 front-end programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn42/dcn42_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn42/dcn42_init.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn42/dcn42_init.h

### Purpose
`dcn42_init.h` declares the DCN42 hardware sequencer vtable initializer and forwards `struct dc`.

### Important API
- `void dcn42_hw_sequencer_init_functions(struct dc *dc);` installs DCN42 public and private sequencer function tables.

### Control Flow, State, and Integration
The header contains no executable logic or persistent state. It is the include point for code that constructs a DCN42 display core and needs to install DCN42 sequencing behavior.

### Risks and Test Signals
The include guard closing comment names `__DC_DCN401_INIT_H__` even though the guard is `__DC_DCN42_INIT_H__`; this is harmless for compilation but can confuse maintenance. Functional validation is compile-time declaration matching plus runtime initialization of DCN42 hardware sequencer tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn42/dcn42_init.h -->
