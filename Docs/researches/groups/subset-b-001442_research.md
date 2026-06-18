# subset-b-001442 grouped research

This grouped report covers AMD Display Core HWSS initialization and hardware-sequencer files for DCN 2.0 through DCN 3.1.4. Each section is source-tree aligned and wrapped for deterministic reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn20/dcn20_init.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn20/dcn20_init.c

## Purpose
Builds the DCN 2.0 hardware sequencer vtables. `dcn20_hw_sequencer_construct()` assigns `dc->hwss` to `dcn20_funcs` and `dc->hwseq->funcs` to `dcn20_private_funcs`, selecting the generation-specific implementation for display enable, plane programming, bandwidth, writeback, DMData, VM context setup, ODM/DSC, color, and power gating.

## Important APIs, Types, and Functions
The key exported API is `dcn20_hw_sequencer_construct(struct dc *dc)`. The file defines two static dispatch tables: `struct hw_sequencer_funcs dcn20_funcs` for public DC operations and `struct hwseq_private_funcs dcn20_private_funcs` for lower-level sequencing helpers. Most entries reuse DCE110, DCN10, and DCN20 helpers such as `dcn20_program_front_end_for_ctx`, `dcn20_update_plane_addr`, `dcn20_enable_stream`, `dcn20_prepare_bandwidth`, `dcn20_enable_writeback`, `dcn20_init_sys_ctx`, `dcn20_init_vm_ctx`, `dcn20_update_odm`, and `dcn20_dsc_pg_control`.

## Control Flow
Construction is table assignment only; there is no runtime branching. Later display manager paths call through `dc->hwss` and `dc->hwseq->funcs`, so the table composition controls boot, mode set, plane update, blanking, link control, and color management behavior for DCN20 ASICs. Public hooks route user-visible operations while private hooks drive pipe reset, power gating, transfer functions, and clock initialization.

## State and Persistence Behavior
The only local state change is overwriting the function tables in `struct dc` and `struct dce_hwseq`. This persists for the lifetime of the DC instance. The functions selected by the table mutate hardware registers, pipe state, and resource-pool members elsewhere; this file has no independent memory allocation or cleanup.

## Dependencies and Integration Points
Depends on `dce110_hwseq.h`, `dcn10_hwseq.h`, and `dcn20_hwseq.h`. It integrates with the DC constructor/resource code that chooses the ASIC-specific HWSS constructor and with every caller that dereferences `dc->hwss` or `dc->hwseq->funcs`.

## Risks and Test Signals
The risk is dispatch-table mismatch: a wrong or missing hook changes hardware sequencing globally for the ASIC. Important signals are successful boot/modeset, plane flip, writeback, DMData, DSC/ODM, backlight, and clock/power tests on DCN20 hardware, plus compile coverage for all assigned function prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn20/dcn20_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn20/dcn20_init.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn20/dcn20_init.h

## Purpose
Declares the DCN 2.0 HWSS constructor used by resource/ASIC initialization code.

## Important APIs, Types, and Functions
Forward-declares `struct dc` and exports `void dcn20_hw_sequencer_construct(struct dc *dc);`.

## Control Flow
The header has no executable flow. Including code calls the constructor after allocating and initializing `struct dc` and `dc->hwseq`.

## State and Persistence Behavior
No local state. The declared function persists HWSS behavior by installing function tables into `struct dc`.

## Dependencies and Integration Points
The guarded include prevents duplicate declarations. It intentionally avoids pulling in full DC definitions by using a forward declaration.

## Risks and Test Signals
Prototype drift between the header and implementation would break compilation. Test signal is successful build of DCN20 resource code using this constructor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn20/dcn20_init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn201/dcn201_hwseq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn201/dcn201_hwseq.c

## Purpose
Implements DCN 2.0.1-specific sequencing for UMA address translation, initialization, plane disconnect/connect, cursor programming, DMData setup, pipe locking, blanking, and DP/eDP unblank.

## Important APIs, Types, and Functions
Exported functions are `dcn201_update_plane_addr`, `dcn201_init_blank`, `dcn201_init_hw`, `dcn201_plane_atomic_disconnect`, `dcn201_update_mpcc`, `dcn201_pipe_control_lock`, `dcn201_set_cursor_attribute`, `dcn201_set_dmdata_attributes`, and `dcn201_unblank_stream`. Important internal helpers are `patch_address_for_sbs_tb_stereo`, `gpu_addr_to_uma`, `plane_address_in_gpu_space_to_uma`, and `read_mmhub_vm_setup`. Core types include `struct dc`, `struct dce_hwseq`, `struct pipe_ctx`, `struct dc_plane_state`, `struct hubp`, `struct dpp`, `struct mpc`, `struct output_pixel_processor`, `struct timing_generator`, and `PHYSICAL_ADDRESS_LOC`.

## Control Flow
Plane address updates optionally patch side-by-side/top-bottom stereo secondary pipes, copy the plane address, translate GPU FB addresses into UMA offsets, program HUBP flip/address registers, and restore the patched stereo address. Initialization starts clocks and DCCG, performs BIOS golden init, derives reference clocks from BIOS, initializes link encoders, reads MMHUB VM setup if not cached, blanks active TGs with OPP display pattern generator, locks active TGs, resets DPPs and MPC, initializes OPP MPC tree state, wires temporary pipe/HUBP/DPP/OPP resources, disconnects planes, maps DWB to MCIF_WB, unlocks TGs, disables planes, initializes TG/audio/DIO, and enables clock gating. MPCC disconnect removes secondary and primary MPCC entries, marks disconnect pending, requests optimization, and disconnects HUBP. MPCC update builds blend config, fast-updates blending on non-full updates, otherwise removes existing MPCC links and inserts a plane using a fixed `mpcc_id == dpp_id` policy.

## State and Persistence Behavior
The file caches FB/UMA aperture values in `hws->fb_base`, `fb_top`, `fb_offset`, and `uma_top`. It mutates plane status requested/current addresses, HUBP `mpcc_id`, `opp_id`, `power_gated`, OPP `mpc_tree_params`, `mpcc_disconnect_pending`, `dc->optimized_required`, pipe resource pointers, and stream DMData/cursor addresses. It also touches hardware registers through MMHUB, DCFCLK, DIO, TG, MPC, HUBP, DPP, OPP, and audio functions.

## Dependencies and Integration Points
Depends on DC resource objects and HW blocks from HUBP, DCHUBBUB, TG, OPP, IPP, MPC, DCCG, CLK manager, DIO, and link encoder implementations. Integrated by `dcn201_init.c` through public/private HWSS table entries.

## Risks and Test Signals
Address translation is high risk: incorrect FB aperture math can flip to wrong UMA addresses or trigger debugger breaks for non-UMA addresses. Init order is sensitive because TG lock/unlock, MPC reset, plane disable, audio, DIO, and clock gating must match hardware expectations. Test signals include S3/S4 resume, UMA systems, stereo surfaces, cursor updates, DMData on HDMI/DP, plane enable/disable, MPC blending, writeback resource pointer setup, and sanity-check/pstate validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn201/dcn201_hwseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn201/dcn201_hwseq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn201/dcn201_hwseq.h

## Purpose
Declares the DCN 2.0.1 hardware sequencing functions used by the DCN201 dispatch tables.

## Important APIs, Types, and Functions
Includes `hw_sequencer_private.h` and declares the exported DCN201 helpers for DMData, hardware init, unblank, plane address update, atomic disconnect, MPCC update, cursor attributes, pipe control lock, and blank initialization.

## Control Flow
No executable control flow. It defines the compile-time contract between `dcn201_init.c` and `dcn201_hwseq.c`.

## State and Persistence Behavior
No direct state. Functions declared here mutate DC pipe/resource/hardware state in the implementation.

## Dependencies and Integration Points
The included private HWSS header supplies `struct dc`, `struct pipe_ctx`, `struct dc_state`, `struct timing_generator`, and related types used in prototypes.

## Risks and Test Signals
Header/implementation mismatch breaks builds or vtable assignment. Compile coverage from DCN201 initialization is the primary test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn201/dcn201_hwseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn201/dcn201_init.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn201/dcn201_init.c

## Purpose
Installs the DCN 2.0.1 HWSS dispatch tables. It mostly reuses DCN10/DCN20/DCE110 behavior but swaps in DCN201 functions for UMA-aware plane address updates, initialization, unblank, MPCC update/disconnect, pipe locking, cursor attributes, and DMData attributes.

## Important APIs, Types, and Functions
Exports `dcn201_hw_sequencer_construct(struct dc *dc)`. Static tables are `dcn201_funcs` and `dcn201_private_funcs`. Public table differences include `init_hw = dcn201_init_hw`, `power_down_on_boot = NULL`, `update_plane_addr = dcn201_update_plane_addr`, `unblank_stream = dcn201_unblank_stream`, `pipe_control_lock = dcn201_pipe_control_lock`, `set_dmdata_attributes = dcn201_set_dmdata_attributes`, and `set_cursor_attribute = dcn201_set_cursor_attribute`. Private differences include `init_pipes = NULL`, `plane_atomic_disconnect = dcn201_plane_atomic_disconnect`, `update_mpcc = dcn201_update_mpcc`, `init_blank = dcn201_init_blank`, and no DSC PG hook.

## Control Flow
Construction assigns both tables to the DC object. Runtime control is indirect through those tables. Compared with DCN20, this table disables some inherited hooks and uses a simpler post-unlock path, reflecting ASIC-specific constraints.

## State and Persistence Behavior
Persists function pointer selection in `dc->hwss` and `dc->hwseq->funcs`. No independent state is stored in this file.

## Dependencies and Integration Points
Includes DCE110, DCN10, DCN20, and DCN201 HWSEQ headers. It is selected by DCN201 resource construction and is the integration point for `dcn201_hwseq.c`.

## Risks and Test Signals
The `NULL` hooks are important risk points: callers must tolerate absent `init_pipes`, stream gating, and DSC PG behavior on this generation. Test with mode-set, boot, resume, plane update, cursor, DMData, and power-down paths on DCN201 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn201/dcn201_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn201/dcn201_init.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn201/dcn201_init.h

## Purpose
Declares the DCN201 HWSS constructor.

## Important APIs, Types, and Functions
Forward-declares `struct dc` and declares `void dcn201_hw_sequencer_construct(struct dc *dc);`.

## Control Flow
No executable flow. It allows ASIC-specific construction code to install DCN201 tables.

## State and Persistence Behavior
No local state; the implementation mutates `struct dc` function tables.

## Dependencies and Integration Points
Used by DCN201 resource/init code and protected by `__DC_DCN201_INIT_H__`.

## Risks and Test Signals
Build failures catch signature drift. Runtime coverage is through successful constructor selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn201/dcn201_init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn21/dcn21_hwseq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn21/dcn21_hwseq.c

## Purpose
Implements DCN 2.1-specific system aperture setup, power-state clock transitions, Renoir/S0i3 workarounds, HDMI/DP PLL workaround, and ABM/backlight control through DMUB or legacy DMCU.

## Important APIs, Types, and Functions
Exports `dcn21_init_sys_ctx`, `dcn21_s0i3_golden_init_wa`, `dcn21_exit_optimized_pwr_state`, `dcn21_optimize_pwr_state`, `dcn21_PLAT_58856_wa`, `dcn21_dmub_abm_set_pipe`, `dcn21_set_abm_immediate_disable`, `dcn21_set_pipe`, `dcn21_set_backlight_level`, and `dcn21_is_abm_supported`. The private `mmhub_update_page_table_config` reads VM context page-table base registers. Important types include `struct dcn_hubbub_phys_addr_config`, `struct dc_phy_addr_space_config`, `union dmub_rb_cmd`, `struct abm`, `struct panel_cntl`, and `struct set_backlight_level_params`.

## Control Flow
System-context init copies firmware/KMD aperture and GART fields, patches page-table base from VM context registers, then calls Hubbub `init_dchub_sys_ctx`. Power optimize/exit delegates to `clk_mgr->update_clocks` with optimized flag true/false. The PLAT_58856 workaround temporarily clears `dpms_off`, toggles DPMS on/off through link service, then restores `dpms_off`. ABM setup builds DMUB ABM commands when DMCU is absent; otherwise it falls back to DCE110 DMCU hooks. Backlight programming sets ABM pipe normal mode and then sends PWM/frame-ramp data either through ABM function pointers or a raw DMUB command.

## State and Persistence Behavior
Mutates Hubbub system aperture programming, clock manager state, stream `dpms_off`, panel stored backlight level, and DMUB command queue state. The ABM support predicate reads pipe topology and rejects ODM-combined streams.

## Dependencies and Integration Points
Depends on DMUB service (`dc_wake_and_execute_dmub_cmd`), `clk_mgr`, `dccg`, `hubbub`, ABM, DMCU, panel control, and link service. Integrated by `dcn21_init.c` and inherited by later DCN30/DCN31 init tables for backlight and optimized power hooks.

## Risks and Test Signals
Risks include stale page-table base register reads, DMUB command payload mismatch, backlight ramp stalls, DMCU/DMUB path divergence, and the PLAT_58856 workaround toggling DPMS in unexpected stream states. Test with Renoir S0i3, monitor-off HDMI hotplug/unplug, modern standby, ABM enable/disable, DMCU-present and DMCU-absent panels, and ODM streams where ABM should be unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn21/dcn21_hwseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn21/dcn21_hwseq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn21/dcn21_hwseq.h

## Purpose
Declares DCN 2.1 HWSS helpers for system context, power optimization, platform workaround, ABM pipe setup, backlight, and ABM support detection.

## Important APIs, Types, and Functions
Includes `hw_sequencer_private.h`, forward-declares `struct dc`, and exposes all functions implemented in `dcn21_hwseq.c`.

## Control Flow
No executable flow. The prototypes are consumed by DCN21 and later-generation init tables.

## State and Persistence Behavior
No direct state; declared functions affect Hubbub, DMUB, clock, stream, ABM, and panel state.

## Dependencies and Integration Points
Connects `dcn21_init.c`, `dcn30_init.c`, `dcn301_init.c`, `dcn31_init.c`, and `dcn314_init.c` to common DCN21 behavior.

## Risks and Test Signals
Prototype stability is critical because multiple generations reuse these hooks. Compile coverage and backlight/power-state runtime tests are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn21/dcn21_hwseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn21/dcn21_init.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn21/dcn21_init.c

## Purpose
Installs the DCN 2.1 HWSS dispatch tables. It inherits most DCN20 behavior and adds DCN21 system-context initialization, optimized power-state transitions, ABM/backlight hooks, S0i3 and platform workarounds, and ABM support detection.

## Important APIs, Types, and Functions
Exports `dcn21_hw_sequencer_construct(struct dc *dc)`. Public table entries of note are `init_sys_ctx = dcn21_init_sys_ctx`, `optimize_pwr_state = dcn21_optimize_pwr_state`, `exit_optimized_pwr_state = dcn21_exit_optimized_pwr_state`, `set_backlight_level = dcn21_set_backlight_level`, `set_abm_immediate_disable = dcn21_set_abm_immediate_disable`, `set_pipe = dcn21_set_pipe`, and `is_abm_supported = dcn21_is_abm_supported`. Private additions include `s0i3_golden_init_wa = dcn21_s0i3_golden_init_wa` and `PLAT_58856_wa = dcn21_PLAT_58856_wa`.

## Control Flow
Constructor assigns the public and private tables. Runtime calls through table pointers compose DCN20 plane/stream/writeback behavior with DCN21 power, aperture, and backlight features.

## State and Persistence Behavior
Persists vtable selection in `dc`/`hwseq`; no local state. Selected hooks later mutate clocks, DMUB, ABM, link, and stream state.

## Dependencies and Integration Points
Depends on DCE110, DCN10, DCN20, and DCN21 HWSEQ implementations. It is the base behavior inherited by several later DCN init files.

## Risks and Test Signals
Risk lies in mixing inherited DCN20 behavior with DCN21-specific power/backlight hooks. Test signals include boot, S0i3, standby/resume, ABM panel control, writeback, DSC/ODM, DPMS workaround, and mode-set stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn21/dcn21_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn21/dcn21_init.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn21/dcn21_init.h

## Purpose
Declares the DCN21 HWSS constructor.

## Important APIs, Types, and Functions
Forward-declares `struct dc` and exports `void dcn21_hw_sequencer_construct(struct dc *dc);`.

## Control Flow
No executable flow. Included by code that chooses DCN21 behavior during DC construction.

## State and Persistence Behavior
No state. The implementation writes HWSS function tables.

## Dependencies and Integration Points
Header guard is `__DC_DCN21_INIT_H__`; the closing comment references DCN20, which is cosmetic but potentially confusing.

## Risks and Test Signals
Build coverage catches declaration drift. Runtime signal is correct selection of the DCN21 constructor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn21/dcn21_init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn30/dcn30_hwseq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn30/dcn30_hwseq.c

## Purpose
Implements DCN 3.0 hardware sequencing for color programming/logging, writeback, MMHUBBUB warmup, hardware init, HDMI/DP metadata, MALL idle optimization, bandwidth preparation, hardware release, display test pattern, pending-update waits, and underflow debug snapshots.

## Important APIs, Types, and Functions
Exports `dcn30_log_color_state`, `dcn30_set_blend_lut`, `dcn30_set_input_transfer_func`, `dcn30_program_gamut_remap`, `dcn30_set_output_transfer_func`, `dcn30_update_writeback`, `dcn30_mmhubbub_warmup`, `dcn30_enable_writeback`, `dcn30_disable_writeback`, `dcn30_program_all_writeback_pipes_in_tree`, `dcn30_init_hw`, `dcn30_set_avmute`, `dcn30_update_info_frame`, `dcn30_program_dmdata_engine`, `dcn30_apply_idle_power_optimizations`, `dcn30_does_plane_fit_in_mall`, `dcn30_hardware_release`, `dcn30_set_disp_pattern_generator`, `dcn30_prepare_bandwidth`, `dcn30_wait_for_all_pending_updates`, and `dcn30_get_underflow_debug_data`. The internal `dcn30_set_mpc_shaper_3dlut` manages MPC RMU/3DLUT resources, and `dcn30_set_writeback` configures DWB mux and MCIF arbitration.

## Control Flow
Color input flow sets pre-degamma, translates distributed-point curves, programs DPP gamcor/blend/shaper/3DLUT where supported, and maps stream gamut remap through MPC on top pipes. Output color flow first tries MPC shaper/3DLUT programming and falls back to output gamma. Writeback flow derives MPCC instances for source planes, warms MCIF/VM buffers, configures DWB mux/MCIF buffer/arbitration, and enables, updates, or disables DWB/MCIF blocks. Hardware init initializes clocks/DCCG, golden init/VGA disable in non-accelerated mode, memory low-power defaults, reference clocks, link encoders/FEC state, DP blanking, plane PG, pipe init or powerdown depending on seamless boot, audio, panel/backlight/ABM, DIO memory, clock gating, watermarks, memclk bounds, pstate control, CRB, and DMUB capabilities. MALL idle optimization checks no-memory-request and single-plane eligibility, computes hysteresis timer values, optionally copies cursor through DMUB, sends MALL allow/disallow commands, and rejects unsupported formats, VM planes, PSR, multi-display, or oversized surfaces.

## State and Persistence Behavior
Mutates DPP/MPC color RAM state, RMU ownership, writeback and MCIF state, link active/FEC state, panel stored backlight, ABM state, hubbub self-refresh/pstate/CRB state, clock-manager hard limits, `dc->caps.dmub_caps`, cursor attributes if copied to MALL, and hardware register state for memory/clock gating. It reads `dc->current_state`, `context->bw_ctx`, stream writeback lists, and debug flags heavily.

## Dependencies and Integration Points
Depends on DPP, MPC, DCCG, HUBBUB, HUBP, OPP, TG, DWB, MCIF_WB, ABM, panel control, link service, DMUB service, clock manager, DIO, and DC state helpers. Integrated by `dcn30_init.c` and reused by DCN301, DCN302, DCN303, DCN31, and DCN314 tables.

## Risks and Test Signals
High-risk areas are MALL eligibility/timer math, DMUB command sequencing, RMU acquisition mismatches, writeback MPCC lookup, VM warmup rejecting p_vmid zero, seamless boot powerdown decisions, and clock/pstate handoffs. Test with color LUT/gamut, 3DLUT, writeback enable/update/disable, HDMI AV mute, DP/HDMI infoframes, dynamic metadata, MALL idle entry/exit, cursor cache, headless boot, seamless eDP boot, FEC links, underflow debug capture, and bandwidth transitions including firmware-based MCLK switching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn30/dcn30_hwseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn30/dcn30_hwseq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn30/dcn30_hwseq.h

## Purpose
Declares DCN 3.0 HWSS operations for initialization, writeback, color, metadata, MALL, bandwidth, pattern generation, pending-update waits, and underflow debug.

## Important APIs, Types, and Functions
Includes `hw_sequencer_private.h`, forward-declares `struct dc` and `struct dc_underflow_debug_data`, and exposes the functions implemented in `dcn30_hwseq.c`. Notably declares `dcn30_set_hubp_blank`, which is not implemented in the read file and may be implemented elsewhere or stale.

## Control Flow
No executable flow. It provides prototypes consumed by init tables and later-generation implementations.

## State and Persistence Behavior
No local state. Declared functions operate on DC resource pools, streams, pipes, DMUB, clocks, DWB/MCIF, and hardware registers.

## Dependencies and Integration Points
Common dependency for DCN30, DCN301, DCN302, DCN303, DCN31, and DCN314 init code. The private HWSS include supplies shared DC type definitions.

## Risks and Test Signals
Prototype drift affects many generations. The `dcn30_set_hubp_blank` declaration should be checked during build/link. Runtime tests should cover every vtable hook assigned from this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn30/dcn30_hwseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn30/dcn30_init.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn30/dcn30_init.c

## Purpose
Installs DCN 3.0 HWSS dispatch tables, adding DCN30 color, init, infoframe, AV mute, writeback, DMData, MALL, hardware release, pattern generation, bandwidth, pending-update, and underflow-debug hooks on top of DCN20/DCN21 behavior.

## Important APIs, Types, and Functions
Exports `dcn30_hw_sequencer_construct(struct dc *dc)`. Public table additions include `program_gamut_remap = dcn30_program_gamut_remap`, `init_hw = dcn30_init_hw`, `update_info_frame = dcn30_update_info_frame`, `disable_pixel_data = dcn20_disable_pixel_data`, `prepare_bandwidth = dcn30_prepare_bandwidth`, `set_avmute = dcn30_set_avmute`, writeback hooks, `program_dmdata_engine = dcn30_program_dmdata_engine`, `apply_idle_power_optimizations`, `does_plane_fit_in_mall`, `hardware_release`, `wait_for_all_pending_updates`, and `get_underflow_debug_data`. Private additions include DCN30 input/output transfer functions, `program_all_writeback_pipes_in_tree`, and `set_blend_lut`.

## Control Flow
Construction copies static tables into `dc` and `dc->hwseq`. Runtime flow comes from indirect calls through those tables.

## State and Persistence Behavior
Persists DCN30 function selection. No additional local state.

## Dependencies and Integration Points
Includes DCE110, DCN10, DCN20, DCN21, and DCN30 HWSEQ headers. It is a base constructor reused directly by DCN302 and DCN303 before they patch power-gating hooks.

## Risks and Test Signals
Risks include missing `power_down_on_boot` compared with earlier generations and broad changes to writeback, color, and MALL behavior. Test with full DCN30 boot/modeset, color, writeback, MALL, DP/HDMI metadata, and power management.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn30/dcn30_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn30/dcn30_init.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn30/dcn30_init.h

## Purpose
Declares the DCN30 HWSS constructor.

## Important APIs, Types, and Functions
Forward-declares `struct dc` and exports `void dcn30_hw_sequencer_construct(struct dc *dc);`.

## Control Flow
No executable flow. Used by ASIC init and by smaller derivative constructors.

## State and Persistence Behavior
No direct state. Constructor implementation installs function tables.

## Dependencies and Integration Points
DCN302 and DCN303 constructors include and call this constructor before applying overrides.

## Risks and Test Signals
Build and constructor selection coverage are sufficient for this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn30/dcn30_init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn301/dcn301_hwseq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn301/dcn301_hwseq.c

## Purpose
Currently a placeholder/stub implementation file for DCN 3.0.1 HWSS-specific code. It only includes shared headers and defines local register-helper macros; no functions are implemented in this source.

## Important APIs, Types, and Functions
There are no exported functions or local routines. Included headers are `core_types.h`, `dce_hwseq.h`, `dcn301_hwseq.h`, and `reg_helper.h`.

## Control Flow
No executable control flow.

## State and Persistence Behavior
No state mutation. Any DCN301 behavior is selected from inherited DCN30/DCN21/DCN20 functions through `dcn301_init.c`.

## Dependencies and Integration Points
The file exists so the DCN301 HWSS module can grow generation-specific functions without changing build structure. The empty header similarly provides an extension point.

## Risks and Test Signals
Risk is mostly dead/stale scaffolding or build-system expectations. Compile coverage should confirm the empty translation unit is accepted and no vtable points to missing DCN301-specific functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn301/dcn301_hwseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn301/dcn301_hwseq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn301/dcn301_hwseq.h

## Purpose
Placeholder header for DCN 3.0.1 HWSS-specific declarations.

## Important APIs, Types, and Functions
Includes `hw_sequencer_private.h` but declares no DCN301-specific functions.

## Control Flow
No executable flow.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Included by `dcn301_init.c` and `dcn301_hwseq.c`; it reserves a generation-specific extension point while DCN301 uses inherited behavior.

## Risks and Test Signals
Low risk. Test signal is successful compilation and absence of unresolved DCN301 symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn301/dcn301_hwseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn301/dcn301_init.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn301/dcn301_init.c

## Purpose
Installs DCN 3.0.1 HWSS tables. It is a custom table largely based on DCN30 but uses `dcn10_init_hw`, retains `dcn10_power_down_on_boot`, and keeps bandwidth hooks closer to DCN20 while importing DCN30 color/writeback/metadata helpers and DCN21 optimized power hooks.

## Important APIs, Types, and Functions
Exports `dcn301_hw_sequencer_construct(struct dc *dc)`. Public table uses `dcn30_program_gamut_remap`, `dcn30_update_info_frame`, `dcn30_set_avmute`, DCN30 writeback and DMData engine, DCN21 backlight/power hooks, and `dcn30_wait_for_all_pending_updates`. Private table uses DCN30 input/output transfer and blend LUT, plus DCN30 writeback tree programming, while using DCN20 power gating and DSC/ODM hooks.

## Control Flow
Constructor assigns static tables. No runtime branches inside this file.

## State and Persistence Behavior
Persists function table selection. No independent state.

## Dependencies and Integration Points
Depends on DCE110, DCN10, DCN20, DCN21, DCN30, and placeholder DCN301 headers. Integrates inherited generation behavior for a DCN301 ASIC variant.

## Risks and Test Signals
The mixed inheritance is the main risk: init and bandwidth come from older paths while color/writeback/metadata come from DCN30. Test with boot, power-down-on-boot, writeback, DMData, color, ABM, optimized power state, and pending-update waits on DCN301.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn301/dcn301_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn301/dcn301_init.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn301/dcn301_init.h

## Purpose
Declares the DCN301 HWSS constructor.

## Important APIs, Types, and Functions
Forward-declares `struct dc` and exports `void dcn301_hw_sequencer_construct(struct dc *dc);`.

## Control Flow
No executable flow.

## State and Persistence Behavior
No direct state.

## Dependencies and Integration Points
Used by DCN301 resource initialization. The closing comment references DCN30, which is cosmetic.

## Risks and Test Signals
Build coverage catches signature problems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn301/dcn301_init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn302/dcn302_hwseq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn302/dcn302_hwseq.c

## Purpose
Implements DCN 3.0.2-specific power-gating register control for DPP, HUBP, and DSC blocks.

## Important APIs, Types, and Functions
Exports `dcn302_dpp_pg_control`, `dcn302_hubp_pg_control`, and `dcn302_dsc_pg_control`. Each accepts `struct dce_hwseq *hws`, an instance index, and `bool power_on`. It uses register helper macros over domain PG config/status registers and `DC_IP_REQUEST_CNTL` for DSC.

## Control Flow
DPP and HUBP functions compute `power_gate` and expected `pwr_status`, honor debug disable flags, skip if the first PG config register is absent, switch over instance 0-4, update the domain power gate bit, and wait for PG FSM status. DSC additionally enables `IP_REQUEST_EN` around domain 16-20 programming and restores it afterward.

## State and Persistence Behavior
Mutates hardware PG control/status state and temporarily changes `DC_IP_REQUEST_CNTL.IP_REQUEST_EN`. No software state is retained.

## Dependencies and Integration Points
Called through private HWSS hooks patched by `dcn302_init.c` after inheriting DCN30 tables. Depends on register definitions in the DCN302 register table and debug flags `disable_dpp_power_gate`, `disable_hubp_power_gate`, and `disable_dsc_power_gate`.

## Risks and Test Signals
Risks include wrong domain-to-instance mapping, timeout waiting for PG FSM, leaving IP request enabled/disabled incorrectly, and unsupported instances breaking into debugger. Test with plane power gating on/off for all supported pipes, DSC enable/disable, debug flags, suspend/resume, and systems with missing PG registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn302/dcn302_hwseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn302/dcn302_hwseq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn302/dcn302_hwseq.h

## Purpose
Declares DCN302 power-gating overrides.

## Important APIs, Types, and Functions
Includes `hw_sequencer_private.h` and declares DPP, HUBP, and DSC PG control functions.

## Control Flow
No executable flow.

## State and Persistence Behavior
No direct state; declared functions mutate PG registers.

## Dependencies and Integration Points
Used by `dcn302_init.c` to override inherited DCN30 private HWSS hooks.

## Risks and Test Signals
Compile coverage plus runtime PG tests for all declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn302/dcn302_hwseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn302/dcn302_init.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn302/dcn302_init.c

## Purpose
Constructs DCN302 HWSS behavior by calling the DCN30 constructor and then overriding private power-gating hooks for DPP, HUBP, and DSC.

## Important APIs, Types, and Functions
Exports `dcn302_hw_sequencer_construct(struct dc *dc)`. It calls `dcn30_hw_sequencer_construct(dc)` then assigns `dc->hwseq->funcs.dpp_pg_control`, `hubp_pg_control`, and `dsc_pg_control`.

## Control Flow
Linear inheritance-and-patch pattern. The DCN30 public/private tables are installed first; only three private functions are changed.

## State and Persistence Behavior
Persists inherited DCN30 table state with DCN302 PG overrides in `dc->hwseq->funcs`.

## Dependencies and Integration Points
Includes `dcn302_hwseq.h`, `dcn30_init.h`, and `dc.h`. Integrated by ASIC resource construction for DCN302.

## Risks and Test Signals
Risk is forgetting to call the base constructor or overriding the wrong function fields. Test boot and power-gating behavior to confirm DCN302 register mappings are used while all DCN30 behavior remains intact.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn302/dcn302_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn302/dcn302_init.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn302/dcn302_init.h

## Purpose
Declares the DCN302 HWSS constructor.

## Important APIs, Types, and Functions
Forward-declares `struct dc` and exports `void dcn302_hw_sequencer_construct(struct dc *dc);`.

## Control Flow
No executable flow.

## State and Persistence Behavior
No local state.

## Dependencies and Integration Points
Used by resource code selecting DCN302 behavior.

## Risks and Test Signals
Build coverage and constructor selection tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn302/dcn302_init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn303/dcn303_hwseq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn303/dcn303_hwseq.c

## Purpose
Provides no-op DCN303 power-gating hooks because DCN303 removes the PG registers used by related generations.

## Important APIs, Types, and Functions
Exports `dcn303_dpp_pg_control`, `dcn303_hubp_pg_control`, `dcn303_dsc_pg_control`, and `dcn303_enable_power_gating_plane`. All parameters are explicitly cast to void.

## Control Flow
Each function immediately returns after void-casting arguments and documenting that PG registers are removed.

## State and Persistence Behavior
No software or hardware state is changed.

## Dependencies and Integration Points
Patched into inherited DCN30 tables by `dcn303_init.c`. This prevents generic DCN30/DCN20 PG code from touching nonexistent registers.

## Risks and Test Signals
Risk is power leakage or missing required power transitions if a future DCN303 revision reintroduces PG controls. Test signal is stable boot/modeset/suspend without register access faults when PG hooks are invoked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn303/dcn303_hwseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn303/dcn303_hwseq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn303/dcn303_hwseq.h

## Purpose
Declares DCN303 no-op power-gating functions.

## Important APIs, Types, and Functions
Includes `hw_sequencer_private.h` and declares DPP, HUBP, DSC, and plane PG-control hooks.

## Control Flow
No executable flow.

## State and Persistence Behavior
No direct state.

## Dependencies and Integration Points
Consumed by `dcn303_init.c` when patching the inherited DCN30 table.

## Risks and Test Signals
Compile coverage and runtime confirmation that PG paths do not access removed registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn303/dcn303_hwseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn303/dcn303_init.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn303/dcn303_init.c

## Purpose
Constructs DCN303 HWSS behavior by inheriting DCN30 tables and overriding all plane-related PG hooks with DCN303 no-op implementations.

## Important APIs, Types, and Functions
Exports `dcn303_hw_sequencer_construct(struct dc *dc)`. It calls `dcn30_hw_sequencer_construct(dc)` and then patches `dpp_pg_control`, `hubp_pg_control`, `dsc_pg_control`, and `enable_power_gating_plane`.

## Control Flow
Linear base-constructor call followed by hook replacement.

## State and Persistence Behavior
Persists DCN30 behavior plus DCN303 no-op PG overrides in the DC function tables.

## Dependencies and Integration Points
Includes `dcn303_hwseq.h`, `dcn30_init.h`, and `dc.h`. Selected by DCN303 resource construction.

## Risks and Test Signals
Risk is accidental inherited register access if any PG hook is missed. Test boot, suspend/resume, plane disable, and DSC paths on DCN303 to ensure no PG register programming occurs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn303/dcn303_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn303/dcn303_init.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn303/dcn303_init.h

## Purpose
Declares the DCN303 HWSS constructor.

## Important APIs, Types, and Functions
Forward-declares `struct dc` and exports `void dcn303_hw_sequencer_construct(struct dc *dc);`.

## Control Flow
No executable flow.

## State and Persistence Behavior
No local state.

## Dependencies and Integration Points
Used by DCN303 ASIC/resource init code.

## Risks and Test Signals
Build coverage catches declaration drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn303/dcn303_init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn31/dcn31_hwseq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn31/dcn31_hwseq.c

## Purpose
Implements DCN 3.1-specific initialization, memory low-power setup, DSC/HUBP power gating, DP 128b/132b infoframe routing, Z10 save/restore through DMUB, system aperture setup, backend reset, HPO control, static-screen triggers, and enhanced backlight control.

## Important APIs, Types, and Functions
Exports `dcn31_init_hw`, `dcn31_dsc_pg_control`, `dcn31_enable_power_gating_plane`, `dcn31_update_info_frame`, `dcn31_z10_save_init`, `dcn31_z10_restore`, `dcn31_hubp_pg_control`, `dcn31_init_sys_ctx`, `dcn31_reset_hw_ctx_wrap`, `dcn31_setup_hpo_hw_control`, `dcn31_set_static_screen_control`, and `dcn31_set_backlight_level`. Internal helpers include `enable_memory_low_power`, `dcn31_reset_back_end_for_pipe`, and a DMUB backlight command helper.

## Control Flow
Initialization starts clocks, runs golden init/VGA disable when not accelerated, initializes DCCG, applies memory low-power policies for DMCU/OPTC/VGA/MPC/VPG, derives reference clocks, initializes only physical endpoint link encoders, blanks DP displays, enables plane PG, optionally blanks eDP when ODM fast-boot would be unsafe, initializes pipes and self-refresh, initializes audio/panels/ABM/DIO/HPO, enables clock gating, initializes watermarks, notifies WM ranges, sets hard max memclk, releases forced pstate, optionally initializes CRB, and queries DMUB caps. Infoframe updates choose HDMI, HPO DP stream encoder for 128b/132b signals, or legacy stream encoder. Reset walks old pipes from high to low, skips top/ODM secondary pipes, resets backend when streams disappear or require reprogramming, disables DSC/CRTC/OPTC clock, handles TMDS symclk refs, DPMS/audio/resource release, and enters transient link-encoder mode when needed.

## State and Persistence Behavior
Mutates memory power registers, link active/FEC state, hubbub self-refresh/pstate/CRB state, panel/ABM state, HPO top control, DMUB idle-restore state, HUBP/DSC PG registers, GART page-table base programming, pipe stream/resource pointers, audio acquisition, link PHY symclk counters/state, `wa_state.skip_blank_stream`, and `dc->caps.dmub_caps`.

## Dependencies and Integration Points
Depends on DCCG, CLK manager, HUBBUB, TG, HUBP, OPP, MPC, MCIF, ABM, DMUB, link service/HWSS, link encoder config, VPG, I2C, DIO, DMCU, and DCE/DCN10/DCN21 helpers. Integrated by `dcn31_init.c` and inherited by DCN314 for init/reset/Z10/HPO behavior.

## Risks and Test Signals
Risk areas include ODM/eDP fast boot handling, HPO DP metadata routing, Z10 restore-needed optimization, backend reset ordering, smartmux/SPRS DSC disable conditions, dynamic audio release, GART MC-address conversion, PG domain mapping, and HPO register gating under debug flags. Test with DP2/HPO links, eDP seamless/ODM boot, Z10 idle restore, DSC, TMDS symclk, dynamic audio, backlight control including AUX mode, suspend/resume, and link encoder assignment transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn31/dcn31_hwseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn31/dcn31_hwseq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn31/dcn31_hwseq.h

## Purpose
Declares DCN31 HWSS helpers for init, power gating, infoframes, Z10, HUBP PG, system context, reset, backlight, HPO, and static-screen control.

## Important APIs, Types, and Functions
Includes `hw_sequencer_private.h`, forward-declares `struct dc`, and declares functions implemented in `dcn31_hwseq.c`. It also declares `dcn31_is_abm_supported` and `dcn31_init_pipes`, which are not implemented in the read file and may be external/stale declarations.

## Control Flow
No executable flow.

## State and Persistence Behavior
No direct state. Declared functions mutate hardware and DC pipe/resource state.

## Dependencies and Integration Points
Consumed by DCN31 and DCN314 init tables. Provides later generation access to DCN31 reset, HPO, and power functions.

## Risks and Test Signals
Prototype/link consistency matters because some declarations were not present in this source. Build/link tests plus runtime coverage of HPO, Z10, PG, reset, and backlight hooks are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn31/dcn31_hwseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn31/dcn31_init.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn31/dcn31_init.c

## Purpose
Installs DCN31 HWSS tables. It inherits broad DCN30/DCN21/DCN20 behavior but replaces init, system context, infoframes, reset, power gating, Z10, static-screen control, HPO setup, and underflow debug integration for DCN31.

## Important APIs, Types, and Functions
Exports `dcn31_hw_sequencer_construct(struct dc *dc)`. Public table key entries include `init_hw = dcn31_init_hw`, `update_info_frame = dcn31_update_info_frame`, `set_static_screen_control = dcn31_set_static_screen_control`, `init_sys_ctx = dcn31_init_sys_ctx`, `z10_restore`, `z10_save_init`, `setup_hpo_hw_control`, and `get_underflow_debug_data = dcn30_get_underflow_debug_data`. Private table key entries include `reset_hw_ctx_wrap = dcn31_reset_hw_ctx_wrap`, `enable_power_gating_plane = dcn31_enable_power_gating_plane`, `hubp_pg_control = dcn31_hubp_pg_control`, `dsc_pg_control = dcn31_dsc_pg_control`, and `setup_hpo_hw_control`.

## Control Flow
Constructor assigns static public and private tables. Runtime flow is fully indirect through the table.

## State and Persistence Behavior
Persists DCN31 table selection. No file-local state.

## Dependencies and Integration Points
Includes DCE110, DCN10, DCN20, DCN21, DCN30, DCN301, and DCN31 HWSEQ headers. Used by DCN31 ASIC initialization and as a base for DCN314 behavior.

## Risks and Test Signals
Risks come from mixing DCN31 init/reset with older DCN20 bandwidth and DCN30 color/writeback. Test mode-set, HPO/DP2, Z10, power gating, static screen, writeback, ABM/backlight, and underflow debug on DCN31.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn31/dcn31_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn31/dcn31_init.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn31/dcn31_init.h

## Purpose
Declares the DCN31 HWSS constructor.

## Important APIs, Types, and Functions
Forward-declares `struct dc` and exports `void dcn31_hw_sequencer_construct(struct dc *dc);`.

## Control Flow
No executable flow.

## State and Persistence Behavior
No local state.

## Dependencies and Integration Points
Used by DCN31 resource/init code.

## Risks and Test Signals
Build coverage and correct constructor selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn31/dcn31_init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn314/dcn314_hwseq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn314/dcn314_hwseq.c

## Purpose
Implements DCN 3.1.4-specific sequencing for ODM/DSC programming, DSC/DPP/plane power gating, pixel-rate divider calculation, FIFO/DCCG/DIO resync, DPP root-clock control, and link-output disable handling with SYMCLK workaround.

## Important APIs, Types, and Functions
Exports `dcn314_update_odm`, `dcn314_dsc_pg_control`, `dcn314_enable_power_gating_plane`, `dcn314_calculate_dccg_k1_k2_values`, `dcn314_calculate_pix_rate_divider`, `dcn314_resync_fifo_dccg_dio`, `dcn314_dpp_root_clock_control`, `dcn314_disable_link_output`, and `dcn314_dpp_pg_control`. Internal helpers are `update_dsc_on_stream`, `get_odm_config`, `dcn314_is_pipe_dig_fifo_on`, and `apply_symclk_on_tx_off_wa`.

## Control Flow
ODM update derives ODM combine factor and OPP instances, programs OPTC combine/bypass, clears MPC out rate control, enables secondary OPP pipe clocks, and reprograms/disconnects DSC as topology changes. DSC programming divides slice width across ODM pipes, programs DSC blocks and OPTC DSC mode, and disables all ODM DSC blocks when off. Pixel divider calculation chooses K1/K2 based on 128b/132b DP, HDMI/DVI, YCbCr420, two-pixels-per-container, virtual signals, and ODM combine factor. FIFO resync temporarily disables eligible DPMS-off/virtual OTGs unless DIG FIFO is already on, triggers DIO FIFO resync through DCCG, and restores CRTC/ODM. Link disable delegates to link HWSS, handles eDP backlight or DMCU PHY locking, traces DPCD sequence, then reapplies SYMCLK-on/TX-off workaround when OTG still references the PHY clock. DPP PG handles debug-disabled power gating by force-disabling cursor when powering off.

## State and Persistence Behavior
Mutates OPTC ODM/DSC state, DSC block state, MPC rate control, OPP clocks, DCCG root clocks and FIFO resync state, pipe pixel-rate divider fields, link PHY `symclk_state` and ref-count-dependent behavior, DMCU PHY lock state, eDP backlight state, DPP cursor state, and PG registers. It reads current and target pipe contexts during staged programming.

## Dependencies and Integration Points
Depends on DCCG, TG/OPTC, DSC, OPP, MPC, link service/HWSS, DMCU, DCE I2C, VPG, DCN20 OPTC, and DCN30 color/common helpers. Integrated by `dcn314_init.c` through public/private hooks, while reusing DCN31 init/reset and DCN30/DCN20 base behavior.

## Risks and Test Signals
Risks include incorrect ODM slice/DSC slice arithmetic, failure to disconnect old DSC after ODM collapse, K1/K2 divider errors affecting stream clocks, FIFO resync disrupting live or seamless-boot streams, SYMCLK workaround failing for TMDS, root-clock gating races, and cursor stuck visible when DPP PG is disabled. Test DCN314 with ODM combine/split, DSC on/off, DP2 128b/132b, HDMI/DVI/YCbCr420, virtual/DPMS-off pipes, TMDS link disable, eDP backlight control, root clock optimization, DPP PG disabled, and multi-pipe mode sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn314/dcn314_hwseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn314/dcn314_hwseq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn314/dcn314_hwseq.h

## Purpose
Declares DCN314 HWSS-specific ODM, DSC, power, clock-divider, FIFO resync, root-clock, link-disable, and DPP PG functions.

## Important APIs, Types, and Functions
Includes `hw_sequencer_private.h`, forward-declares `struct dc`, and declares all exported functions from `dcn314_hwseq.c`.

## Control Flow
No executable flow.

## State and Persistence Behavior
No local state; declared functions mutate DC pipe, link, clock, DSC/ODM, and register state.

## Dependencies and Integration Points
Consumed by `dcn314_init.c` and any shared code calling DCN314 helpers through private HWSS hooks.

## Risks and Test Signals
Compile/link coverage plus runtime coverage for every hook assigned in `dcn314_init.c`, especially pixel divider and FIFO resync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn314/dcn314_hwseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn314/dcn314_init.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn314/dcn314_init.c

## Purpose
Installs DCN314 HWSS tables. It builds on DCN31 init/reset/HPO/Z10 behavior and DCN30 color/writeback behavior, while adding DCN314 link disable, pixel-rate divider calculation, ODM, DSC/plane/DPP PG, DPP root-clock, DCCG K1/K2, and FIFO resync hooks.

## Important APIs, Types, and Functions
Exports `dcn314_hw_sequencer_construct(struct dc *dc)`. Public table additions include `disable_link_output = dcn314_disable_link_output` and `calculate_pix_rate_divider = dcn314_calculate_pix_rate_divider`; it keeps `init_hw = dcn31_init_hw`, `update_info_frame = dcn31_update_info_frame`, `init_sys_ctx = dcn31_init_sys_ctx`, Z10, HPO, DCN30 writeback/color, and DCN21 backlight/power hooks. Private table additions include `enable_power_gating_plane = dcn314_enable_power_gating_plane`, `dpp_root_clock_control`, `dpp_pg_control`, `update_odm`, `dsc_pg_control`, `calculate_dccg_k1_k2_values`, and `resync_fifo_dccg_dio`.

## Control Flow
Constructor assigns static public/private tables. Later mode-set and link paths call through these hooks to get DCN314-specific clock, DSC, ODM, PG, and link-disable handling.

## State and Persistence Behavior
Persists DCN314 function table selection. No local state.

## Dependencies and Integration Points
Includes DCE110, DCN10, DCN20, DCN21, DCN30, DCN301, DCN31, and DCN314 HWSEQ headers. It is the high-level integration point for `dcn314_hwseq.c`.

## Risks and Test Signals
The table mixes multiple generations, so missed overrides can silently use older behavior. Test DCN314-specific ODM/DSC, DP2, pixel-rate divider, FIFO resync, DPP root clock, link disable, and all inherited DCN31/DCN30 paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn314/dcn314_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn314/dcn314_init.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn314/dcn314_init.h

## Purpose
Declares the DCN314 HWSS constructor.

## Important APIs, Types, and Functions
Forward-declares `struct dc` and exports `void dcn314_hw_sequencer_construct(struct dc *dc);`.

## Control Flow
No executable flow.

## State and Persistence Behavior
No local state.

## Dependencies and Integration Points
Used by DCN314 resource/ASIC initialization.

## Risks and Test Signals
Build coverage and correct constructor selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn314/dcn314_init.h -->
