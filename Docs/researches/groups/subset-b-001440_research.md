# Research: subset-b-001440

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce110/dce110_hwseq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce110/dce110_hwseq.c

Purpose: DCE 11.0 hardware sequencer implementation for the AMD display core. It is the base HWSS for several DCE generations: it owns mode-set sequencing, stream/audio/link enable and disable, eDP panel power sequencing, front-end plane programming, display watermark programming, FBC enablement, cursor programming, and the function-table construction that wires these operations into `dc->hwss` and `dc->hwseq->funcs`.

Important APIs, types, and functions: public entry points include `dce110_hw_sequencer_construct()`, `dce110_apply_ctx_to_hw()`, `dce110_apply_single_controller_ctx_to_hw()`, `dce110_enable_stream()`, `dce110_disable_stream()`, `dce110_unblank_stream()`, `dce110_blank_stream()`, `dce110_enable_audio_stream()`, `dce110_disable_audio_stream()`, `dce110_update_info_frame()`, `dce110_enable_accelerated_mode()`, `dce110_prepare_bandwidth()`, `dce110_optimize_bandwidth()`, `dce110_set_safe_displaymarks()`, link output helpers, and eDP/backlight helpers. Key private helpers include `dce110_init_pte()`, `dce110_enable_display_power_gating()`, transfer-function programming, `dce110_enable_stream_timing()`, `dce110_reset_hw_ctx_wrap()`, `dce110_setup_audio_dto()`, `dce110_program_front_end_for_pipe()`, and FBC predicates. It programs objects from `struct dc`, `dc_state`, `pipe_ctx`, `dc_link`, `dc_stream_state`, `timing_generator`, `mem_input`, `transform`, `stream_encoder`, `link_encoder`, `dccg`, `abm`, `panel_cntl`, `audio`, and `dc_bios`.

Control flow: construction installs `dce110_funcs` into `dc->hwss` and private hooks into `dc->hwseq->funcs`. `dce110_apply_ctx_to_hw()` first resets removed or reprogrammed pipes, powers ungated controllers for new streams, disables FBC, programs shared audio DTO state, updates HPO control when acquired state changes, then iterates root pipes and applies each controller through `dce110_apply_single_controller_ctx_to_hw()`. The single-controller path disables stream gating if present, configures audio output and AZ endpoint, programs OPP format and dynamic expansion, optionally enables stream timing before or after DP HPO stream enable depending on workaround state, sets DRR/static-screen controls, connects DIG to OTG, enables DSC in selected eDP smartmux paths, and calls link-service DPMS on when needed. Surface commits use `dce110_apply_ctx_for_surface()`: allocate MI, program color/scaler/tiling/PTE/gamma front-end state, update the flip address, and set blender/CRTC blanking based on plane visibility. Shutdown paths blank streams, disable audio and stream encoders, reset symbol clocks, disable link PHY, free MI, power down unused clocks, and power-gate front ends.

State and persistence: most state is hardware register state reached through component function tables and direct `dm_read_reg()`/`dm_write_reg()` calls. Software state updates include `plane_state->status.requested_address/current_address/is_flip_pending`, `audio->enabled`, link `phy_state.symclk_state` and reference counts, `link_status.link_active`, `cur_link_settings`, FEC state, panel/backlight stored levels, PSR/Replay feature flags, and eDP power timestamps kept by link service. No filesystem persistence exists. Boot and resume flows also set VBIOS scratch critical/accelerated-mode bits and may preserve eDP VDD/backlight state for fast boot, seamless boot, or mux-switch paths.

Dependencies and integration points: this file is deeply integrated with the DC resource pool, link service, BIOS parser/command tables, DMCU/DMUB mediated panel controls, DCCG/clock manager, DSC, ABM/FBC, mem-input and transform blocks, OPP/IPP color pipelines, timing generators, stream/link encoders, and DCE register headers (`dce_11_0_*`). Generation-specific sequencers for DCE60, DCE80, DCE112, and DCE120 reuse this constructor and override selected hooks. External integration is via the Linux DRM AMD DC commit path and link-training/link-management code.

Risks and test signals: ordering is the main risk. The code relies on blank-before-disable, CRTC power-gating/PTE initialization, eDP T7/T9/T12 delays, VBIOS command side effects, DP HPO sequencing, and audio DTO selection. Mistakes show up as blank screens, hung CRTC counters, panel flashes during mux switching, broken DP/HDMI info packets, audio lag, incorrect cursor or color/gamma output, FBC corruption, or watermark underruns. Test signals include multi-monitor mode sets, hotplug/remove, DP MST and DP 2.0/HPO paths, eDP suspend/resume and fast boot, HDMI and DP audio, DSC cleanup after boot firmware, FBC on single eDP tiled surfaces, DRR/static-screen behavior, and visual-confirm/color pipeline validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce110/dce110_hwseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce110/dce110_hwseq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce110/dce110_hwseq.h

Purpose: public header for the DCE110 hardware sequencer implementation. It exposes the base DCE HWSS constructor and the subset of stream, audio, panel, bandwidth, backlight, link-output, and FBC helpers that other DCE generation files or adjacent display modules reuse.

Important APIs, types, and functions: declarations cover `dce110_hw_sequencer_construct()`, context application helpers, stream enable/disable/blank/unblank, audio stream enable/disable, info-frame updates, AV mute, accelerated-mode and power-down hooks, safe/display bandwidth hooks, eDP power/backlight/HPD helpers, backlight level and ABM helpers, link-output enable/disable helpers for LVDS/TMDS/DP, `build_audio_output()`, `translate_to_dto_source()`, `populate_audio_dp_link_info()`, and `enable_fbc()`. It forward-declares `struct dc`, `struct dc_state`, and `struct dm_pp_display_configuration`, and includes core DC and private HW sequencer types.

Control flow: the header itself has no executable flow, but it defines the reusable interface consumed by constructors in DCE60, DCE80, DCE112, DCE120, and link/display sequencing code. The primary construction flow is to call `dce110_hw_sequencer_construct(dc)` and then optionally override fields in `dc->hwss` or `dc->hwseq->funcs`.

State and persistence: no state is stored in the header. Its function signatures expose stateful objects, especially `dc`, `dc_state`, `pipe_ctx`, `dc_link`, `link_resource`, `dc_link_settings`, and `audio_output`, whose state is mutated by the implementation.

Dependencies and integration points: depends on `core_types.h` and `hw_sequencer_private.h`. It is the cross-generation contract for legacy DCE HWSS code and lets smaller generation shims reuse DCE110 behavior without duplicating the large sequencer implementation.

Risks and test signals: because it is a shared interface, signature drift or missing prototypes can break generation-specific builds or cause inconsistent hook wiring. Compile coverage across DCE60/DCE80/DCE110/DCE112/DCE120 configurations is the key test signal, followed by runtime smoke tests for any exported helper reused outside `dce110_hwseq.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce110/dce110_hwseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce112/dce112_hwseq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce112/dce112_hwseq.c

Purpose: DCE 11.2 hardware sequencer shim. It reuses the DCE110 sequencer almost entirely but overrides display power-gating to use DCE11.2 register offsets and PTE initialization behavior.

Important APIs, types, and functions: `dce112_hw_sequencer_construct()` is the only exported function. Private support includes `struct dce112_hw_seq_reg_offsets`, `reg_offsets[]`, `HW_REG_CRTC()`, `dce112_init_pte()`, and `dce112_enable_display_power_gating()`. The PTE helper reads and updates `mmDVMM_PTE_REQ` fields for maximum PTE requests and horizontal-flip request chunking. The power-gating helper maps `PIPE_GATING_CONTROL_*` to BIOS `ASIC_PIPE_*` actions, calls `dc_bios->funcs->enable_disp_power_gating()`, clears `CRTC_MASTER_UPDATE_MODE`, and reinitializes PTE settings when not enabling power gating.

Control flow: construction calls `dce110_hw_sequencer_construct(dc)` first, inheriting the base DCE110 `dc->hwss` and private hook tables. It then replaces `dc->hwseq->funcs.enable_display_power_gating` with the DCE112 version. Runtime callers therefore follow the DCE110 mode-set flow but land in DCE112-specific power-gating/PTE code whenever a pipe is initialized, ungated, or gated.

State and persistence: persistent state is hardware register state and BIOS-controlled pipe power state. The helper deliberately repairs `CRTC_MASTER_UPDATE_MODE` after BIOS command-table calls because BIOS sets it to a non-driver default. No software state is stored beyond the inherited `dc`/pipe/link state.

Dependencies and integration points: depends on DCE110 HWSS, `dc_bios` command tables, `dm_read_reg()`/`dm_write_reg()`, DCE11.2 register definitions, and the private HW sequencer function table. It is selected by the DCE11.2 resource path to provide generation-correct power gating while preserving base behavior.

Risks and test signals: the risk is register-offset mismatch or BIOS side effects during pipe gating. Broken PTE chunk programming may appear as scanout/f flip corruption. Test signals include DCE11.2 boot, mode set, suspend/resume, pipe power-gating transitions, and confirming `CRTC_MASTER_UPDATE_MODE` is restored after BIOS calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce112/dce112_hwseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce112/dce112_hwseq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce112/dce112_hwseq.h

Purpose: minimal public header for the DCE11.2 hardware sequencer shim. It exposes only the constructor needed by DCE11.2 display resource initialization.

Important APIs, types, and functions: declares `dce112_hw_sequencer_construct(struct dc *dc)`. It includes `core_types.h` and `hw_sequencer_private.h`, and forward-declares `struct dc`.

Control flow: no executable flow exists in the header. Users include it and call the constructor, which installs the DCE110 base table and then overrides display power-gating behavior.

State and persistence: no direct state. The constructor signature passes the global display core object whose HWSS function tables will be mutated by the implementation.

Dependencies and integration points: integrated with DCE11.2 resource construction and indirectly with the DCE110 HWSS contract. The include guard isolates this generation-specific interface.

Risks and test signals: risk is limited to build integration and selecting the correct constructor for DCE11.2 ASIC paths. Test signals are successful compilation and runtime confirmation that `enable_display_power_gating` resolves to the DCE112 override.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce112/dce112_hwseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce120/dce120_hwseq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce120/dce120_hwseq.c

Purpose: DCE 12.0 hardware sequencer shim for Vega-era display. It inherits DCE110 sequencing, disables the older BIOS display power-gating path for bringup, provides DCHUB framebuffer/AGP initialization, exposes an xGMI detection helper, and reuses DCE100 surface DCC/tiling reset behavior.

Important APIs, types, and functions: exported functions are `dce120_hw_sequencer_construct()` and `dce121_xgmi_enabled()`. Private `dce120_enable_display_power_gating()` is currently a disabled stub returning false, with the previous BIOS/PTE flow preserved under `#if 0`. `dce120_update_dchub()` programs `DCHUB_FB_LOCATION`, `DCHUB_AGP_BASE`, `DCHUB_AGP_BOT`, and `DCHUB_AGP_TOP` based on `struct dchub_init_data` framebuffer mode. `dce121_xgmi_enabled()` reads `MC_VM_XGMI_LFB_CNTL.PF_MAX_REGION`.

Control flow: construction calls `dce110_hw_sequencer_construct(dc)`, then overrides `dc->hwseq->funcs.enable_display_power_gating`, `dc->hwss.update_dchub`, and `dc->hwss.clear_surface_dcc_and_tiling`. DCHUB update handles three modes: ZFB-only inverts FB base/top and programs AGP aperture, mixed ZFB/local leaves FB location to VBIOS and programs AGP aperture, and local-only clears AGP to an invalid/disabled range. It marks `dchub_initialzied` true and invalidates the consumed info.

State and persistence: hardware state is held in DCHUB and MC VM registers. The DCHUB input state is consumed by toggling `dh_data->dchub_initialzied` and `dh_data->dchub_info_valid`. Power-gating state is intentionally not changed by the stub. No file or firmware persistence is introduced, though VBIOS-owned FB location is deliberately preserved for local and mixed modes.

Dependencies and integration points: depends on DCE110 and DCE100 HWSS code, SOC15/Vega10 register headers, `reg_helper` macros, DCHUB init data, and memory-controller xGMI registers. It integrates with the common DC init path through `dc->hwss.update_dchub` and with any code that needs to know whether xGMI is active.

Risks and test signals: the power-gating stub means callers expecting true pipe gating must tolerate false or skip the feature on DCE12. Incorrect DCHUB aperture programming can break zero-frame-buffer or mixed memory scanout. The misspelled `dchub_initialzied` field must match the existing structure. Test signals include DCE12 boot in local, ZFB-only, and mixed-ZFB configurations, display scanout after DCHUB init, xGMI-enabled platform detection, and ensuring no caller treats the disabled power-gating return as fatal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce120/dce120_hwseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce120/dce120_hwseq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce120/dce120_hwseq.h

Purpose: public header for the DCE12.0 hardware sequencer shim. It exposes the DCE120 constructor and the DCE12.1 xGMI state helper.

Important APIs, types, and functions: declares `bool dce121_xgmi_enabled(struct dce_hwseq *hws)` and `void dce120_hw_sequencer_construct(struct dc *dc)`. It includes core DC and private HW sequencer definitions and forward-declares `struct dc`.

Control flow: no executable flow exists. Including code can construct the DCE120 HWSS table or query xGMI state through the implementation.

State and persistence: no state is stored here. The function prototypes expose `dc` and `dce_hwseq`, which give the implementation access to register helpers and HWSS function-table mutation.

Dependencies and integration points: used by DCE12 resource construction and code paths that need xGMI awareness. It depends on the DCE private HW sequencer type for the xGMI helper signature.

Risks and test signals: build risk comes from the xGMI helper requiring `struct dce_hwseq` visibility via included headers. The include guard comment names DCE112, which is cosmetic but can confuse maintenance. Test signals are successful DCE120 builds and constructor selection on DCE12 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce120/dce120_hwseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce60/dce60_hwseq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce60/dce60_hwseq.c

Purpose: DCE6 hardware sequencer adaptation. It inherits most DCE110 behavior but replaces surface/front-end handling and selected hooks for older display hardware that lacks later bottom-pipe/blender capabilities, while reusing DCE100 power/bandwidth/DCC helpers.

Important APIs, types, and functions: exported `dce60_hw_sequencer_construct()` installs the DCE60 overrides. Private helpers include `dce60_should_enable_fbc()`, `dce60_enable_fbc()`, `dce60_set_default_colors()`, `dce60_program_surface_visibility()`, `dce60_get_surface_visual_confirm_color()`, `dce60_program_scaler()`, `dce60_program_front_end_for_pipe()`, and `dce60_apply_ctx_for_surface()`. These operate on `dc`, `dc_state`, `pipe_ctx`, `mem_input`, `transform`, `compressor`, and plane/stream color and scaling state.

Control flow: construction first calls `dce110_hw_sequencer_construct(dc)` and then overrides power gating with `dce100_enable_display_power_gating`, surface commit with `dce60_apply_ctx_for_surface`, cursor and pipe locks with `dce60_pipe_control_lock`, bandwidth hooks with DCE100 versions, and DCC/tiling clear with DCE100 reset. Surface application disables FBC, iterates pipes for the target stream, allocates MI, programs front-end color/scaler/tiling/PTE/gamma state, updates plane addresses through common HWSS, then sets CRTC blanking directly from plane visibility. It re-enables FBC afterward when eligible.

State and persistence: state changes are hardware register programming through component function tables and FBC compressor state. Plane flip status is delegated to inherited DCE110 address update logic. The DCE6 FBC predicate requires allocated `fbc_gpu_addr`, single display, eDP, no PSR, present plane, and non-linear tiling. No persistent storage is used.

Dependencies and integration points: depends on DCE110 base functions, DCE100 power/bandwidth/reset helpers, DCE6 register headers, and older pipe-control locking. It integrates with the normal DC HWSS table but narrows surface visibility semantics because DCE6 has no later blender/bottom-pipe model.

Risks and test signals: key risk is assuming no DCE110-style blender. Visibility programming blanks/unblanks the CRTC directly, so multi-plane or underlay behavior must stay within DCE6 limitations. FBC eligibility lacks the DCE110 Replay exclusion, matching older feature support. Test signals include DCE6 single eDP FBC, plane visibility toggles, cursor updates under DCE60 locks, GPU VM PTE programming, color/gamma changes, and bandwidth updates through the DCE100 hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce60/dce60_hwseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce60/dce60_hwseq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce60/dce60_hwseq.h

Purpose: public header for the DCE6 hardware sequencer adaptation. It exposes the constructor used to install DCE6-specific HWSS overrides.

Important APIs, types, and functions: declares `dce60_hw_sequencer_construct(struct dc *dc)`, includes `core_types.h` and `hw_sequencer_private.h`, and forward-declares `struct dc`.

Control flow: no executable flow exists in this header. Resource construction calls the constructor, which first installs DCE110 defaults and then replaces hooks that differ on DCE6.

State and persistence: no direct state. The implementation mutates the `dc` object's HWSS/private function tables and later programs hardware state through those hooks.

Dependencies and integration points: integrated with DCE6 display resource initialization and with the DCE110/DCE100 shared HWSS interfaces. The header keeps the older generation entry point isolated from newer generation files.

Risks and test signals: risk is incorrect constructor selection or missing prototype coverage in DCE6 builds. Test signals are compile coverage and runtime confirmation that the DCE6 surface and locking overrides are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce60/dce60_hwseq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce80/dce80_hwseq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce80/dce80_hwseq.c

Purpose: DCE8 hardware sequencer shim. It reuses the DCE110 base sequencer but overrides a small set of hooks to match DCE8/DCE100-era power gating, bandwidth, pipe locking, and surface DCC/tiling behavior.

Important APIs, types, and functions: exported `dce80_hw_sequencer_construct()` is the only implementation function. It calls `dce110_hw_sequencer_construct()` and then assigns `dce100_enable_display_power_gating`, `dce_pipe_control_lock`, `dce100_prepare_bandwidth`, `dce100_optimize_bandwidth`, and `dce100_reset_surface_dcc_and_tiling` into the relevant private/public HWSS slots.

Control flow: all normal mode-set, stream, audio, eDP, link, and front-end flows continue through DCE110 handlers unless one of the overridden hooks is invoked. DCE80 does not define additional runtime sequencing of its own.

State and persistence: no local state is maintained. State effects come from the inherited DCE110 logic and the DCE100 helper hooks that program hardware power, clock, bandwidth, DCC, and tiling state.

Dependencies and integration points: depends on DCE110 HWSS, DCE100 HWSS helpers, DCE common pipe-control locking, and DCE8 register headers. It integrates with DCE8 resource construction as a compatibility layer over the DCE110 function table.

Risks and test signals: the main risk is relying on the DCE110 default table for behavior that may differ subtly on DCE8. Test signals include DCE8 boot/mode-set, pipe power transitions, bandwidth changes, DCC/tiling reset paths, and lock behavior around updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce80/dce80_hwseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce80/dce80_hwseq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce80/dce80_hwseq.h

Purpose: public header for the DCE8 hardware sequencer shim. It exposes the single constructor needed by DCE8 display initialization.

Important APIs, types, and functions: declares `dce80_hw_sequencer_construct(struct dc *dc)`, includes `core_types.h` and `hw_sequencer_private.h`, and forward-declares `struct dc`.

Control flow: no executable flow exists. Callers use the constructor to install DCE110 base functions plus DCE8-specific overrides.

State and persistence: no state is held in the header. The implementation mutates HWSS function tables and later inherited/overridden hooks program hardware state.

Dependencies and integration points: tied to DCE8 resource construction and the shared DCE110/DCE100 HWSS contracts.

Risks and test signals: risk is limited to build integration and constructor selection. Test signals are successful DCE8 compile coverage and runtime hook-table verification through mode-set and bandwidth paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce80/dce80_hwseq.h -->
