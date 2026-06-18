# Research: subset-b-003593

Grouped source research for subset B work item `subset-b-003593`. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpll_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpll_mgr.h

## Purpose
This header defines the shared display PLL management contract for the i915 display driver. It names all platform DPLL identifiers, captures generation-specific PLL register state layouts, describes tracked shared-PLL state, and declares the atomic compute/reserve/enable/disable/readout/verification APIs used by encoder and CRTC mode-setting code.

## Important APIs, Types, and Functions
Important identifiers include `enum intel_dpll_id`, `I915_NUM_PLLS`, `enum icl_port_dpll_id`, `struct intel_dpll_hw_state`, `struct intel_dpll_state`, `struct dpll_info`, and `struct intel_dpll`. Hardware-state unions cover i9xx, HSW/BDW, SKL, BXT, ICL/TGL, MPLLB, C10/C20/CX0, and LT PHY PLL formats.

The public API is centered on `intel_dpll_compute()`, `intel_dpll_reserve()`, `intel_dpll_release()`, `intel_dpll_enable()`, `intel_dpll_disable()`, `intel_dpll_swap_state()`, `intel_dpll_init()`, `intel_dpll_readout_hw_state()`, `intel_dpll_sanitize_state()`, `intel_dpll_update_ref_clks()`, `intel_dpll_state_verify()`, and `intel_dpll_verify_disabled()`. Helpers such as `intel_get_dpll_by_id()`, `intel_dpll_get_freq()`, `intel_dpll_get_hw_state()`, `intel_dpll_compare_hw_state()`, `icl_tc_port_to_pll_id()`, `mtl_port_to_pll_id()`, and `intel_dpll_is_combophy()` expose lookup, frequency, and platform mapping services.

## Control Flow
The file itself has no executable flow, but it defines the atomic mode-set lifecycle. Encoders compute the requested PLL hardware state into `intel_crtc_state`, reserve a compatible shared PLL in the atomic state, swap committed state into `display->dpll`, enable PLLs before active scanout, disable/release them after use, and verify readout against expected state. `pipe_mask`, `active_mask`, `on`, and `wakeref` let the implementation distinguish logical users, active pipes, hardware enable state, and runtime power-management requirements.

## State and Persistence Behavior
`struct intel_dpll` is persistent per-display-driver state initialized at probe. `struct intel_dpll_state` exists both in live shared PLLs and in atomic transactions, carrying user pipe masks and exact hardware programming. The hardware-state union must remain stable with platform-specific implementations because equality and sharing decisions depend on byte-level fields such as PLL divider, spread-spectrum, C10/C20 lane, and Thunderbolt mode state.

## Dependencies and Integration Points
This header integrates with atomic CRTC/encoder state, display power domains, platform PLL backends in the DPLL manager implementation, TC/Thunderbolt and combo PHY port code, readout/sanitization paths, and state verification. Consumers depend on `intel_display_power_domain`, `enum port`, `enum tc_port`, `struct ref_tracker`, and MMIO programming hidden behind platform-specific `intel_dpll_funcs`.

## Risks
PLL IDs intentionally alias across platforms, so using an ID without the platform-specific DPLL table can select the wrong PLL. Sharing decisions are only as correct as `intel_dpll_compare_hw_state()` and the populated hardware-state fields. Power-domain and wakeref mistakes can leave PLLs inaccessible or prevent runtime power savings. C10/C20/LT PHY state carries lane-count, SSC, and TBT mode details, so partial initialization can produce link-training failures that look like encoder problems.

## Test Signals
Useful signals include successful i915 builds across display generations, atomic modeset tests covering shared PLL reuse and release, boot/readout without DPLL state mismatch warnings, hotplug and suspend/resume stability, DP/HDMI/eDP link training on combo and TC ports, runtime PM transitions with active/inactive PLLs, and debug dumps showing expected frequency and hardware-state equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpll_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpt.c

## Purpose
This file manages display page table configuration for framebuffers scanned out through GGTT-to-DPT mappings. It toggles the platform DPT enable/disable hardware knobs and preserves DPT-backed framebuffer mappings across system suspend and resume.

## Important APIs, Types, and Functions
The exported functions are `intel_dpt_configure()`, `intel_dpt_suspend()`, and `intel_dpt_resume()`. `intel_dpt_configure()` writes `PLANE_CHICKEN_DISABLE_DPT` per non-cursor plane on display version 14 and `CHICKEN_MISC_DISABLE_DPT` on display version 13, based on `display->params.enable_dpt`. Suspend/resume functions walk all registered DRM framebuffers under `mode_config.fb_lock` and call parent DPT callbacks for framebuffers with `fb->dpt`.

## Control Flow
Configuration is called per CRTC and branches by display generation. On version 14 it iterates planes on the CRTC and skips the cursor; on version 13 it uses a global display chicken register. Suspend first returns on no-display platforms, then locks framebuffer enumeration and suspends each DPT. Resume mirrors that flow and restores DPT PTEs after GGTT mappings have been restored.

## State and Persistence Behavior
The file does not allocate DPTs. It operates on persistent `struct intel_framebuffer` DPT pointers created by the framebuffer layer. During S4 and some S3RST-to-S4 flows, DPT page table contents are not stored in the hibernation image, so `intel_dpt_resume()` is responsible for reprogramming mappings rather than assuming the table memory remained valid.

## Dependencies and Integration Points
It depends on display MMIO helpers, `intel_display_types`, `intel_parent_dpt_suspend()`, `intel_parent_dpt_resume()`, and plane register definitions. It is coupled with `intel_fb.c` and `intel_fb_pin.c`, which decide when a framebuffer uses DPT, create DPT objects, and pin DPT VMAs for scanout.

## Risks
Calling suspend/resume in the wrong order relative to GGTT suspend/resume can leave hardware page tables pointing at stale or missing mappings. A mismatch between `enable_dpt` and the chicken-register setting changes how non-linear framebuffers are addressed. Framebuffer enumeration must stay under `fb_lock` because DPT-backed framebuffers can be added or destroyed by userspace.

## Test Signals
Signals include suspend/resume with tiled or compressed framebuffers, no blank scanout after hibernation/resume, correct behavior with `enable_dpt` toggled, no cursor-plane DPT side effects on display version 14, and framebuffer lifetime tests that create/destroy DPT-backed framebuffers around suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpt.h

## Purpose
This small header declares the display page table helper API used by the i915 display suspend/resume and CRTC configuration paths.

## Important APIs, Types, and Functions
The header forward declares `struct intel_crtc` and `struct intel_display`, then exposes `intel_dpt_configure()`, `intel_dpt_suspend()`, and `intel_dpt_resume()`. It intentionally does not expose the DPT object internals; those live behind the parent interface and framebuffer structures.

## Control Flow
There is no executable control flow. Callers use this header to invoke DPT configuration during display setup and to bracket system suspend/resume around GGTT state save and restore.

## State and Persistence Behavior
No state is stored here. The API implies that DPT mappings are persistent framebuffer state, but the helper functions must rebuild volatile hardware/PTE programming after low-power transitions.

## Dependencies and Integration Points
The header is included by display power-management and plane/CRTC paths needing DPT configuration. It bridges framebuffer DPT ownership in `intel_fb.c` with system suspend/resume sequencing in the display driver.

## Risks
Because only opaque forward declarations are exposed, callers cannot validate DPT state directly. Misordering these calls relative to GGTT suspend/resume is the primary integration risk.

## Test Signals
Compile coverage of display suspend/resume paths, DPT-enabled framebuffer scanout before and after resume, and no unresolved symbols when DPT support is built with the display driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dram.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dram.c

## Purpose
This file detects memory subsystem characteristics needed by display code: DRAM type, FSB and memory frequency on older platforms, channel count, QGV/PSF points, symmetry, 16Gb DIMM presence, and newer GDDR/ECC display-bandwidth effects. The results are cached in `display->dram.info`.

## Important APIs, Types, and Functions
Public functions include `intel_dram_type_str()`, `intel_mem_freq()`, `intel_fsb_freq()`, `intel_dram_detect()`, and `intel_dram_info()`. Internal helpers are grouped by generation: Pineview/i9xx/ILK frequency readers, SKL/ICL DIMM size/width/rank decoders, BXT DUNIT decoders, `icl_pcode_read_mem_global_info()`, `gen11_get_dram_info()`, `gen12_get_dram_info()`, and `xelpdp_get_dram_info()`.

Internal `struct dram_dimm_info` and `struct dram_channel_info` normalize DIMM dimensions before filling public `struct dram_info`. `intel_dram_type_str()` maps the enum values to readable debug strings and guards array size with `BUILD_BUG_ON`.

## Control Flow
`intel_dram_detect()` exits early for DG2 and no-display devices, allocates managed `dram_info`, then dispatches by display version and platform: Xe_LPD+ via `MTL_MEM_SS_INFO_GLOBAL`, Gen12 via pcode global memory info, Gen11 via SKL channel parsing plus pcode, BXT/GLK via DUNIT registers, Gen9 via SKL MCHBAR registers, and older platforms via strap/register frequency reads. Detection failures are logged but intentionally not probe-fatal.

## State and Persistence Behavior
The detected `dram_info` is device-managed memory with probe lifetime. It is a snapshot of platform memory topology and firmware-reported capabilities, not a dynamic telemetry stream. Older FSB/memory frequencies are strap-derived and may not reflect all BIOS-configured behavior. On Xe3p_LPD and later `ecc_impacting_de_bw` records whether ECC affects display engine bandwidth.

## Dependencies and Integration Points
The file depends on uncore MMIO, MCHBAR register definitions, pcode reads through `intel_parent_pcode_read()`, Valleyview IOSF sideband access, DRM managed allocation, and display platform/version helpers. Watermark, bandwidth, and display power-management code consumes `intel_dram_info()` to size memory-related limits.

## Risks
Register decoding is heavily platform-specific. Wrong display-version dispatch or field masks can misreport channel count or memory type, leading to incorrect watermark or bandwidth policy. SKL/ICL DIMM encoding differs by size units, and BXT values are per-device Gb rather than total DIMM Gb. Detection is non-fatal, so consumers must tolerate unknown or partially populated data. `intel_dram_info()` can return NULL on platforms that do not allocate DRAM info.

## Test Signals
Signals include boot logs showing expected DRAM type/channel counts on each generation, valid QGV/PSF counts from pcode, no MISSING_CASE warnings on supported hardware, watermark/bandwidth tests across memory configurations, suspend/resume without stale DRAM assumptions, and explicit coverage for NULL `intel_dram_info()` on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dram.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dram.h

## Purpose
This header exposes the display driver's normalized DRAM information structure and DRAM detection/query helpers.

## Important APIs, Types, and Functions
`struct dram_info` contains `enum intel_dram_type`, `fsb_freq`, `mem_freq`, `num_channels`, `num_qgv_points`, `num_psf_gv_points`, `ecc_impacting_de_bw`, `symmetric_memory`, and `has_16gb_dimms`. Exported helpers are `intel_dram_detect()`, `intel_fsb_freq()`, `intel_mem_freq()`, `intel_dram_info()`, and `intel_dram_type_str()`.

## Control Flow
There is no executable flow in the header. The shape of `struct dram_info` drives downstream branches in display bandwidth and watermark code after `intel_dram_detect()` populates `display->dram.info`.

## State and Persistence Behavior
The header defines persistent probe-time state rather than runtime counters. Comments clarify that `ecc_impacting_de_bw` is only valid from Xe3p_LPD onward, so consumers must gate usage by platform capability.

## Dependencies and Integration Points
It forward declares `struct intel_display` and uses Linux fixed-width types. It integrates with `intel_dram.c`, display bandwidth code, and debug logging.

## Risks
Consumers can overinterpret fields on unsupported platforms. `intel_dram_info()` may be NULL, and some fields are only populated for selected generations. Adding enum values requires updating `intel_dram_type_str()`.

## Test Signals
Compile checks for all users, enum/string array size assertions, NULL-safe consumers, and platform-specific tests that verify the valid subset of fields per generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_drrs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_drrs.c

## Purpose
This file implements Display Refresh Rate Switching for internal panels. DRRS saves power by switching from high to low refresh after frontbuffer activity becomes idle, then returning to high refresh on rendering, flips, or manual debugfs control.

## Important APIs, Types, and Functions
Public APIs are `intel_drrs_type_str()`, `intel_cpu_transcoder_has_drrs()`, `intel_drrs_is_active()`, `intel_drrs_activate()`, `intel_drrs_deactivate()`, `intel_drrs_invalidate()`, `intel_drrs_flush()`, `intel_drrs_crtc_init()`, `intel_drrs_crtc_debugfs_add()`, and `intel_drrs_connector_debugfs_add()`.

Key internal helpers are `intel_drrs_set_refresh_rate_pipeconf()`, `intel_drrs_set_refresh_rate_m_n()`, `intel_drrs_set_state()`, `intel_drrs_schedule_work()`, `intel_drrs_frontbuffer_bits()`, `intel_drrs_downclock_work()`, and `intel_drrs_frontbuffer_update()`.

## Control Flow
Activation checks `has_drrs`, active hardware state, and joiner secondary status, then stores the CPU transcoder, DP M/N pairs, relevant frontbuffer bits, clears busy bits, and schedules a one-second delayed downclock. Invalidation/flush calls intersect frontbuffer bits with each active CRTC. Any activity forces high refresh; flush clears busy bits and schedules low-refresh work only when all tracked frontbuffers are idle. Deactivation forces high refresh, clears active state, and cancels delayed work.

## State and Persistence Behavior
Per-CRTC DRRS state is protected by `crtc->drrs.mutex` and includes `cpu_transcoder`, current refresh-rate state, M/N values, tracked frontbuffer masks, busy frontbuffer masks, and delayed work. `cpu_transcoder == INVALID_TRANSCODER` marks inactive DRRS. State is runtime-only and is rebuilt on modesets/activation.

## Dependencies and Integration Points
The implementation depends on frontbuffer tracking, DP M/N programming, transcoder PIPECONF bits, panel VBT/EDID DRRS type, CRTC atomic state, joiner-pipe masks, display workqueues, and debugfs. It integrates with `intel_panel_drrs_type()` for connector reporting.

## Risks
DRRS is sensitive to frontbuffer bit accounting: missing an invalidate can leave the panel at low refresh during visible activity, while missing a flush can prevent power savings. Joiner configurations require tracking all joined pipe frontbuffers from the primary. Switching via PIPECONF versus M/N depends on transcoder capabilities. Debugfs manual activation waits for commit `hw_done`, but races around modeset state still require careful locking.

## Test Signals
Signals include debugfs `i915_drrs_status` transitions, frontbuffer invalidate/flush tests showing high/low refresh changes, internal panel EDID/VBT modes with multiple refresh rates, joiner-pipe DRRS behavior, suspend/resume and modeset deactivation returning to high refresh, and no delayed work after CRTC teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_drrs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_drrs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_drrs.h

## Purpose
This header declares the DRRS control, frontbuffer notification, initialization, and debugfs APIs for the i915 display driver.

## Important APIs, Types, and Functions
The exported declarations cover capability checks, string conversion, activation/deactivation, frontbuffer invalidate/flush handling, CRTC initialization, and CRTC/connector debugfs registration. It forward declares `enum drrs_type`, `enum transcoder`, and the Intel display/connector/CRTC state types.

## Control Flow
There is no local control flow. The API shape reflects the runtime flow: initialize per CRTC, activate on a suitable committed state, update from frontbuffer tracking, deactivate on modeset/disable, and expose status through debugfs.

## State and Persistence Behavior
No state is stored in the header. The functions operate on per-CRTC DRRS state embedded in display types.

## Dependencies and Integration Points
It is included by panel, frontbuffer, atomic modeset, and debugfs code that need to coordinate DRRS. Keeping forward declarations minimal reduces compile coupling with full display type definitions.

## Risks
Callers must pass the correct CRTC state and frontbuffer masks; the header cannot enforce joiner or active-state checks. Debugfs helpers should only be registered for initialized connectors/CRTCs.

## Test Signals
Compile coverage, debugfs node presence for DRRS-capable panels, and frontbuffer notification paths linking successfully against the DRRS implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_drrs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsb.c

## Purpose
This file implements Display State Buffer support. A DSB is a display DMA engine that executes a memory buffer of display MMIO write and wait instructions, reducing CPU programming cost and helping atomic commits fit timing windows.

## Important APIs, Types, and Functions
`struct intel_dsb` tracks the DSB id, backing buffer, target CRTC, buffer size/free position, previous instruction for indexed-write coalescing, chicken register value, and dewake scanline. Public functions include buffer sizing/address helpers, `intel_dsb_prepare()`, `intel_dsb_finish()`, `intel_dsb_gosub_finish()`, `intel_dsb_cleanup()`, write emitters, wait emitters, polling, GOSUB, chaining, vblank evasion, commit/wait, execution-time estimates, and `intel_dsb_irq_handler()`.

Internal helpers wrap the parent DSB buffer interface, encode DSB opcodes, compute scanline/vblank/VRR wait windows, set platform chicken bits, align cachelines, determine error interrupt masks, and dump timed-out command buffers.

## Control Flow
`intel_dsb_prepare()` checks hardware and module enablement, takes a runtime PM reference, allocates a cacheline-aligned command buffer, stores timing state, and falls back to MMIO on failure. Callers emit instructions with write/wait/poll helpers, then finalize with cacheline alignment and map flush. `intel_dsb_commit()` programs DSB control, chicken, interrupt, PM, head, and tail registers if the engine is idle. `intel_dsb_wait()` polls for idle, halts and dumps on timeout, resets software instruction state, disables the engine, and clears interrupts.

Chaining writes another DSB engine's registers from a running DSB and optionally holds DEwake through a vblank wait. GOSUB emits subroutine calls with 64-byte address conversion and NOP cacheline workarounds. IRQ handling acknowledges status, sends pending vblank events on program-complete interrupts, and logs ATS/GTT/timeout/poll/GOSUB errors.

## State and Persistence Behavior
DSB contexts are transient per atomic operation and freed by `intel_dsb_cleanup()`. The backing DSB buffer is parent-managed and GGTT-addressed. Hardware registers retain engine state until reset in `intel_dsb_wait()`. `crtc->dsb_event` persists across execution until IRQ completion sends it under `event_lock`.

## Dependencies and Integration Points
The implementation depends on the display parent DSB buffer interface, MMIO register definitions, runtime PM, atomic CRTC state, PSR, VRR, vblank helpers, watermark latency, and plane/commit code that chooses DSB versus MMIO. It integrates with interrupt handling through DSB interrupt status bits and with event delivery through DRM vblank events.

## Risks
DSB is timing-sensitive. Incorrect scanline-window calculations can miss vblank evasion or wait forever. Buffer overflow, unaligned tail, stale map contents, or wrong GGTT addresses can hang the DSB engine. Masked writes use byte enables, so sub-byte fields are not independently protected. Error status bits differ by display version; clearing nonexistent status bits would create false errors. GOSUB placement has explicit cacheline workarounds.

## Test Signals
Signals include successful atomic commits with DSB enabled, fallback to MMIO when prepare fails, no DSB busy timeouts, correct vblank event delivery, interrupt logs free of ATS/GTT/poll/timeout/GOSUB errors, PSR and VRR commits with correct vblank evasion, chained DSB execution, and debug dumps only on induced failure tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsb.h

## Purpose
This header exposes the DSB command-buffer API to display commit code while keeping `struct intel_dsb` opaque.

## Important APIs, Types, and Functions
It defines `enum intel_dsb_id` with three engines and `I915_MAX_DSBS`. The declared API covers preparing/finishing/cleaning contexts, size/head queries, register writes, indexed writes, masked writes, NOPs, non-posted sections, interrupts, microsecond/vblank/scanline waits, delayed-vblank waits, vblank evasion, polling, GOSUB, chaining, commit/wait, and IRQ handling.

## Control Flow
There is no implementation flow here, but the API encodes the lifecycle: prepare, emit commands, finish or GOSUB-finish, commit, wait, and cleanup. The IRQ handler declaration connects hardware completion to display interrupt dispatch.

## State and Persistence Behavior
The opaque context carries transient command-buffer state. Callers receive and pass the pointer without knowing buffer layout, which protects the instruction encoding from broad coupling.

## Dependencies and Integration Points
The header depends on `i915_reg_defs.h` for `i915_reg_t` and forward declares display atomic/CRTC types. It is used by plane, watermark, PSR/VRR, and atomic commit code that emits display programming sequences.

## Risks
Callers must honor the lifecycle and must not emit after finish or cleanup. Scanline/wait helpers require matching atomic state and CRTC. Since masked writes are byte-enable based, callers need masks aligned to byte granularity.

## Test Signals
Compile coverage for all DSB users, atomic commit tests with each DSB id, chained/GOSUB command tests, and IRQ dispatch coverage for all pipes and DSB ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsb_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsb_regs.h

## Purpose
This header defines the MMIO register map and bitfields for per-pipe DSB engines.

## Important APIs, Types, and Functions
The central macros are `DSBSL_INSTANCE(pipe, id)` and registers such as `DSB_HEAD`, `DSB_TAIL`, `DSB_CTRL`, `DSB_MMIOCTRL`, `DSB_POLLFUNC`, `DSB_POLLMASK`, `DSB_STATUS`, `DSB_INTERRUPT`, `DSB_CURRENT_HEAD`, `DSB_RM_TIMEOUT`, `DSB_PMCTRL`, `DSB_PMCTRL_2`, `DSB_PF_LN_LOWER`, `DSB_PF_LN_UPPER`, `DSB_BUFRPT_CNT`, and `DSB_CHICKEN`.

Bitfields cover enable/halt/busy control, wait-for-vblank/line-in modes, non-posted writes, poll timing/count, internal state-machine status, program and error interrupts, ATS/GTT/poll/timeout/GOSUB faults, DEwake scanlines, force-dewake, DC-state overrides, and DSB chicken workarounds.

## Control Flow
There is no control flow. `intel_dsb.c` writes these registers to arm command buffers, configure polling, manage power/dewake, acknowledge interrupts, and decode errors.

## State and Persistence Behavior
The macros describe hardware-visible state. DSB head/tail/current-head hold GGTT command-buffer pointers; control and interrupt registers retain state until the driver writes them. PMCTRL and PMCTRL_2 influence display power/dewake behavior during execution.

## Dependencies and Integration Points
The header depends on `intel_display_reg_defs.h` register helpers and is consumed by DSB execution and interrupt code. It must match the platform hardware spec for display versions that expose DSB.

## Risks
Register bit typos can have wide impact. Two macros appear suspicious by name, `DSB_MMIO_DEAD_CLOCKS_COUNT()` using `DSB_MMIO_DEAD_CLOCK_COUNT_MASK` and `DSB_RM_READY_TIMEOUT_VALUE()` using itself instead of the mask, so compile-time coverage or existing definitions must catch any mismatch. Version-specific bits must not be cleared or enabled on unsupported platforms.

## Test Signals
Signals include successful compile of all macros, DSB command execution, correct interrupt acknowledgement, register dumps matching hardware docs, and targeted tests that enable newer ATS/GOSUB bits only on supported display versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsb_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi.c

## Purpose
This file provides common MIPI DSI helpers for panel power-cycle timing, bitrate/TLPX calculation, mode validation, host/device allocation, and panel orientation selection.

## Important APIs, Types, and Functions
Exported functions are `intel_dsi_wait_panel_power_cycle()`, `intel_dsi_shutdown()`, `intel_dsi_bitrate()`, `intel_dsi_tlpx_ns()`, `intel_dsi_get_modes()`, `intel_dsi_mode_valid()`, `intel_dsi_host_init()`, and `intel_dsi_get_panel_orientation()`.

## Control Flow
Power-cycle handling compares boottime against `panel_power_off_time` and sleeps until `panel_pwr_cycle_delay` is satisfied. Bitrate computes pixel clock times bits-per-pixel divided by lane count, with a fallback for invalid format. Mode validation checks panel mode validity, fixed-mode dotclock against max CDCLK dotclock, and maximum plane size. Host initialization manually allocates a `mipi_dsi_host` and `mipi_dsi_device` because the driver uses the DRM MIPI DSI framework as a library rather than registering normal device-model hosts.

## State and Persistence Behavior
The helper updates no persistent state except allocated DSI host/device objects returned to caller-owned `intel_dsi`. Panel timing state comes from `intel_dsi` fields populated by VBT parsing. Orientation is selected from panel VBT DSI orientation, then global VBT orientation, then normal.

## Dependencies and Integration Points
It integrates with DRM MIPI DSI helpers, `intel_panel` mode helpers, CDCLK limits, display max-plane-size validation, DSI shutdown hooks, and VBT-derived `struct intel_dsi` state.

## Risks
Incorrect lane count, pixel format, or pclk produces bad bitrate calculations and PHY programming downstream. The manually allocated DSI device bypasses normal driver-model initialization, so callers must manage lifetime carefully. Power-cycle delay is only as good as `panel_power_off_time` updates elsewhere.

## Test Signals
Signals include DSI panel modes enumerating correctly, invalid high-clock modes rejected, panel shutdown/resume respecting power-cycle delay, bitrate/TLPX values matching VBT expectations, orientation property matching VBT, and leak checks for host/device allocation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi.h

## Purpose
This header defines the i915 MIPI DSI encoder state structure, DSI host wrapper, DSI mode/dual-link constants, iteration helpers, and common DSI function declarations.

## Important APIs, Types, and Functions
`struct intel_dsi` embeds `struct intel_encoder` and stores DSI hosts, IO wakerefs, optional GPIOs, attached connector, port/PHY mask, virtual channel, operation mode, lane count, I2C bus, pixel format, video mode, packet/clock flags, escape clock, dual-link layout, timing registers, pixel clock, burst ratio, and panel/backlight delays. `struct intel_dsi_host` wraps `mipi_dsi_host`, back-points to `intel_dsi`, stores a port, and holds the manually allocated `mipi_dsi_device`.

Inline helpers include `to_intel_dsi_host()`, `for_each_dsi_port()`, `for_each_dsi_phy()`, `enc_to_intel_dsi()`, `is_vid_mode()`, `is_cmd_mode()`, and `intel_dsi_encoder_ports()`.

## Control Flow
There is no executable flow beyond inline casts and mode predicates. The state layout is populated by VBT parsing, platform DSI init code, and panel power/backlight paths, then consumed by encoder enable/disable and MIPI sequence execution.

## State and Persistence Behavior
`struct intel_dsi` is persistent encoder state. Several fields are VBT-derived policy, while `panel_power_off_time` records runtime timing for power-cycle enforcement. The union of `ports` and `phys` reflects platform split between VLV-style ports and ICL-style PHYs.

## Dependencies and Integration Points
The header depends on DRM CRTC/MIPI DSI definitions and `intel_display_types.h`. It integrates with VBT parsing, DCS backlight, panel mode helpers, platform DSI encoders, shutdown, and MIPI command execution.

## Risks
Misinterpreting `ports` versus `phys` can target the wrong link. Many timing fields are in byte clocks or milliseconds depending on origin; unit confusion affects panel bring-up. The manual DSI host/device approach requires consistent lifetime management outside standard driver registration.

## Test Signals
Signals include DSI encoder initialization on single and dual-link panels, correct per-port sequence execution, video and command mode bring-up, GPIO/backlight timing, and compile coverage for all inline helpers across VLV and ICL paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_dcs_backlight.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_dcs_backlight.c

## Purpose
This file implements panel backlight control through MIPI DCS commands for DSI panels whose VBT requests `INTEL_BACKLIGHT_DSI_DCS`.

## Important APIs, Types, and Functions
The public entry point is `intel_dsi_dcs_init_backlight_funcs()`, which installs `dcs_bl_funcs`. Internal callbacks are `dcs_setup_backlight()`, `dcs_enable_backlight()`, `dcs_disable_backlight()`, `dcs_set_backlight()`, and `dcs_get_backlight()`. It uses DCS commands `GET/SET_DISPLAY_BRIGHTNESS`, `GET/WRITE_CONTROL_DISPLAY`, and `WRITE_POWER_SAVE`.

## Control Flow
Initialization rejects non-DCS backlight types and non-DSI encoders, then assigns panel backlight callbacks. Setup derives max brightness from VBT precision bits or 8-bit default and initializes the level to max. Set/get iterate the configured backlight ports. Enable sets display-control bits, enables CABC power-save mode on CABC ports, then writes brightness. Disable writes brightness zero, disables CABC, reads display-control, clears backlight/display-dimming/brightness-control bits, and writes it back.

## State and Persistence Behavior
The callback table is persistent in `panel->backlight.funcs`; current brightness lives in generic panel backlight state. DCS writes mutate panel-internal state over the DSI link. `dcs_set_backlight()` temporarily clears `MIPI_DSI_MODE_LPM` and restores original mode flags.

## Dependencies and Integration Points
The file depends on DRM MIPI DSI helpers, MIPI DCS command definitions, `intel_panel` backlight infrastructure, VBT-selected backlight/CABC port masks, and the attached DSI encoder/device objects.

## Risks
Byte order differs between get and set paths for 16-bit brightness and should be validated against panel expectations. DCS command failures are not deeply propagated in callbacks. Port masks must match initialized hosts. Clearing LPM changes transaction mode temporarily, so restoration must remain exception-safe.

## Test Signals
Signals include DCS backlight setup on VBT-marked panels, brightness read/write at 8-bit and wider precision, enable/disable sequencing on dual-link panels, CABC command behavior, no warnings for non-DSI encoders, and visible backlight changes without panel command errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_dcs_backlight.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_dcs_backlight.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_dcs_backlight.h

## Purpose
This header exposes the DSI DCS backlight initialization hook.

## Important APIs, Types, and Functions
It forward declares `struct intel_connector` and declares `intel_dsi_dcs_init_backlight_funcs()`.

## Control Flow
There is no local flow. Panel/backlight initialization calls this helper to install DCS callbacks when VBT selects the DSI DCS backlight type.

## State and Persistence Behavior
No state is stored here. The implementation persists its effect by setting `panel->backlight.funcs`.

## Dependencies and Integration Points
It is included by panel/DSI setup code that needs to try DCS backlight support without depending on implementation details.

## Risks
The function can return `-ENODEV` or `-EINVAL`; callers must continue to other backlight methods or fail appropriately.

## Test Signals
Compile coverage and panel initialization paths that either install DCS callbacks or cleanly fall back to other backlight implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_dcs_backlight.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_vbt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_vbt.c

## Purpose
This file translates VBT MIPI panel data into runtime DSI encoder parameters, executes BIOS-defined MIPI panel sequences, and handles platform-specific GPIO/I2C/PMIC side effects needed for panel power and backlight control.

## Important APIs, Types, and Functions
Public functions are `intel_dsi_vbt_init()`, `intel_dsi_vbt_gpio_init()`, `intel_dsi_vbt_exec_sequence()`, and `intel_dsi_log_params()`. Internal sequence executors handle send-packet, delay, GPIO, I2C, SPI skip, and PMIC elements through `exec_elem[]`. GPIO helpers cover SoC GPIO lookup, opaque VLV/CHV lookup tables, BXT GPIOs, and ICL native GPIO registers. ACPI I2C helpers map VBT target addresses to Linux I2C adapters when available.

## Control Flow
`intel_dsi_vbt_init()` copies fields from `mipi_config` and PPS data into `intel_dsi`, converts VBT pixel format, adjusts pixel clock for dual-link and burst mode, validates target burst frequency, converts delays from 100us units to milliseconds, initializes I2C bus selection, and attaches the manually allocated DSI devices.

`intel_dsi_vbt_exec_sequence()` wraps a sequence with optional GPIO panel/backlight toggles and calls `intel_dsi_vbt_exec()`. The executor skips the sequence id and optional size, then loops through elements until `MIPI_SEQ_ELEM_END`, dispatching each operation and verifying the consumed size for sequence versions with explicit lengths.

## State and Persistence Behavior
VBT-derived DSI fields persist in `struct intel_dsi`. Sequence data itself is stored in `connector->panel.vbt.dsi.sequence`. GPIO descriptor caching includes a static SoC GPIO table and per-encoder `gpio_panel`/`gpio_backlight` handles. `intel_dsi->i2c_bus_num` starts at `-1` and is lazily resolved on first I2C sequence operation.

## Dependencies and Integration Points
The implementation depends on VBT panel data, DRM MIPI DSI packet helpers, GPIO descriptor lookup tables, pinctrl mappings, ACPI I2C resource parsing, PMIC opregion support, VLV/CHV sideband behavior, ICL display GPIO registers, PPS registers, and platform DSI FIFO helpers. It integrates tightly with `intel_dsi.h` state and panel initialization.

## Risks
VBT sequence formats vary by version; unsupported operations without a size cannot be skipped safely. Unaligned casts from byte streams make endianness and alignment assumptions, although PMIC paths use explicit unaligned helpers. GPIO numbering differs by platform and sequence version, and some paths are marked as hacks or unclear. Missing `CONFIG_PMIC_OPREGION` can make required hardware sequences fail. Burst-mode clock validation can reject panels with bad VBT data.

## Test Signals
Signals include successful DSI panel power-on/off sequences, debug logs for expected MIPI operations, correct dual-link and burst pclk calculation, GPIO toggles on VLV/CHV/BXT/ICL panels, ACPI I2C adapter resolution, PMIC sequence execution when required, and no inconsistent operation-size errors on supported VBT sequence versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_vbt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_vbt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_vbt.h

## Purpose
This header declares the DSI VBT initialization, GPIO setup, sequence execution, and parameter logging APIs.

## Important APIs, Types, and Functions
It forward declares `enum mipi_seq` and `struct intel_dsi`, then exposes `intel_dsi_vbt_init()`, `intel_dsi_vbt_gpio_init()`, `intel_dsi_vbt_exec_sequence()`, and `intel_dsi_log_params()`.

## Control Flow
There is no local implementation flow. Callers use it during DSI encoder setup to initialize VBT-derived fields, set up panel GPIO ownership, execute panel power/backlight sequences, and log resolved parameters.

## State and Persistence Behavior
No state is defined here. The implementation mutates `struct intel_dsi` and connector panel VBT-derived state.

## Dependencies and Integration Points
The header bridges platform DSI encoder code with VBT parsing and sequence execution. It keeps MIPI sequence details behind the implementation while allowing callers to name sequence IDs.

## Risks
Callers must only execute sequences after VBT data and DSI hosts are initialized. Passing the wrong `panel_id` or executing sequences out of power order can leave panels unresponsive.

## Test Signals
Compile coverage, DSI init paths calling `intel_dsi_vbt_init()` before sequence execution, and panel bring-up logs from `intel_dsi_log_params()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_vbt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_vbt_defs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_vbt_defs.h

## Purpose
This header defines the packed VBT data structures and constants for MIPI DSI panel configuration, PPS delays, and sequence blocks.

## Important APIs, Types, and Functions
Core definitions are `enum mipi_seq`, `enum mipi_seq_element`, `MIPI_DSI_UNDEFINED_PANEL_ID`, `MIPI_DSI_GENERIC_PANEL_ID`, `struct mipi_config`, and `struct mipi_pps_data`. `struct mipi_config` includes panel id, general panel flags, command/video mode, transfer mode, CABC/PWM control, pixel format, rotation, dual-link layout, lane count, DCS port masks, controller usage, burst/reference clocks, LP byte-clock selector, DPHY flags, timeout/timer values, DPHY timing fields, and GPIO indexes.

## Control Flow
There is no control flow. The values guide `intel_dsi_vbt.c` parsing and sequence execution, including handling of renamed assert/deassert reset sequence IDs to correct VBT spec wording confusion.

## State and Persistence Behavior
The packed structs mirror BIOS/VBT binary data and must preserve field order, bit widths, and packing. PPS delays are stored in 100us units and converted by consumers. Sequence and element enum values are persistent VBT ABI values.

## Dependencies and Integration Points
The header depends only on Linux integer types. It integrates with BIOS VBT parsing, DSI VBT initialization, panel power sequencing, and MIPI command execution.

## Risks
Changing packed bitfields or enum ordering would break VBT decoding. Some fields are only valid for specific VBT BDB versions, so consumers must gate behavior. Rotation, dual-link, DCS port, and byte-clock constants are small numeric ABI values and should not be conflated with DRM/MIPI runtime enums without conversion.

## Test Signals
Signals include binary VBT parsing tests, structure-size/offset checks where available, DSI panel init on multiple VBT versions, correct delay conversion, and sequence ID logs matching BIOS-defined panel sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dsi_vbt_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dvo.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dvo.c

## Purpose
This file implements support for legacy external DVO transmitter chips attached to older Intel display hardware. It probes known I2C devices, wraps chip-specific operations in DRM encoder/connector callbacks, and programs the DVO port registers for scanout.

## Important APIs, Types, and Functions
The public entry point is `intel_dvo_init()`. Internal state is `struct intel_dvo`, embedding an `intel_encoder`, a copied `intel_dvo_device`, and the attached connector. The known device table covers sil164, ch7xxx, ivch, tfp410, ch7017, and ns2501 variants with addresses and default ports.

Important callbacks include `intel_dvo_get_hw_state()`, `intel_dvo_connector_get_hw_state()`, `intel_dvo_get_config()`, `intel_disable_dvo()`, `intel_enable_dvo()`, `intel_dvo_mode_valid()`, `intel_dvo_compute_config()`, `intel_dvo_pre_enable()`, `intel_dvo_detect()`, `intel_dvo_get_modes()`, `intel_dvo_enc_destroy()`, `intel_dvo_init_dev()`, and `intel_dvo_probe()`.

## Control Flow
Initialization allocates encoder and connector objects, assigns callbacks, probes the device table over GMBUS, initializes DRM encoder/connector objects on success, and sets up LVDS fixed-panel data if needed. Device probing selects a GMBUS pin, forces bit-banging for unstable NAK handling, temporarily enables DVO 2x clock on all pipes for ns2501-style devices, calls chip `init()`, restores DPLL state, and releases bit-banging mode.

Enable flow programs source dimensions and DVO control bits in pre-enable, calls chip `mode_set()`, enables the DVO register, then calls chip DPMS on. Disable calls chip DPMS off, clears `DVO_ENABLE`, and posts the write.

## State and Persistence Behavior
`struct intel_dvo` and its copied device descriptor persist for the encoder lifetime. The chip private state is owned by chip-specific `dev_ops`. Hardware state is split between i915 DVO MMIO registers and external transmitter registers accessed over I2C.

## Dependencies and Integration Points
The file depends on DRM connector/encoder helpers, GMBUS/I2C, chip-specific DVO drivers declared in `intel_dvo_dev.h`, panel fixed-mode helpers, display access checks, DPLL registers for temporary DVO clock enablement, and `intel_dvo_regs.h`.

## Risks
The probe table has overlapping I2C addresses, so probe order matters. Temporarily modifying DPLL DVO 2x mode must always restore original state. DVO type mapping drives connector/encoder type and cloneability. Access checks during suspend or runtime PM must avoid I2C/MMIO access when display hardware is unavailable.

## Test Signals
Signals include detection logs for supported chips, successful DDC or panel mode enumeration, mode validation through chip-specific callbacks, enable/disable DPMS sequencing, LVDS fixed-mode setup, hotplug polling for TMDS devices, and no DPLL state regression after failed probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dvo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dvo.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dvo.h

## Purpose
This header declares the legacy DVO initialization hook and provides a no-op stub when the i915 build symbol is not enabled.

## Important APIs, Types, and Functions
It forward declares `struct intel_display` and exposes `intel_dvo_init()` under `#ifdef I915`; otherwise an inline stub does nothing.

## Control Flow
There is no local runtime flow except the build-time selection of real initialization versus no-op.

## State and Persistence Behavior
No state is stored here. The implementation allocates encoder/connector state only when built in and when a DVO device probes successfully.

## Dependencies and Integration Points
It is included by display probe code that wants to call DVO init unconditionally while allowing build configurations without i915 DVO support.

## Risks
The stub can hide missing DVO support in non-i915 builds by design. Real callers should not expect an encoder to appear unless probing succeeds.

## Test Signals
Compile coverage with and without `I915`, and display probe logs showing DVO init attempts only in supported builds/platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dvo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dvo_dev.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dvo_dev.h

## Purpose
This header defines the device descriptor and operation table for external DVO transmitter chip drivers.

## Important APIs, Types, and Functions
`struct intel_dvo_device` records chip name, type, DVO port, GPIO/I2C bus selection, target address, ops pointer, chip private data, and I2C adapter. `struct intel_dvo_dev_ops` provides chip hooks for `init`, `dpms`, `mode_valid`, `mode_set`, `detect`, `get_hw_state`, `destroy`, and optional `dump_regs`. Extern declarations expose ops for sil164, ch7xxx, ivch, tfp410, ch7017, and ns2501.

## Control Flow
There is no implementation flow. `intel_dvo.c` uses the ops table to probe chips, validate modes, program modes, detect connectors, and clean up private state.

## State and Persistence Behavior
The descriptor is copied into `struct intel_dvo`; `dev_priv` and `i2c_bus` are mutable chip-driver state. The ops contract assumes `mode_set()` runs while output is disabled and `dpms()` handles the final on/off transition.

## Dependencies and Integration Points
It depends on register definitions for `enum port`, display limits, DRM mode status, display modes, and Linux I2C adapters. It is the ABI between generic DVO glue and chip-specific transmitter modules.

## Risks
Incorrect ops implementation can leave external transmitters powered or misprogrammed. `init()` comments mention returning NULL although the signature is `bool`, so implementers must follow actual return semantics. Chip hooks should only reject output-specific mode constraints in `mode_valid()`, leaving CRTC limits to generic code.

## Test Signals
Signals include successful probe/destroy for each chip driver, mode validation against chip limits, I2C transaction traces, DPMS on/off behavior, register dumps for debug builds, and hardware state readout matching generic DVO register state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dvo_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dvo_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dvo_regs.h

## Purpose
This header defines the DVO port and source-dimension MMIO registers and bitfields for legacy DVO outputs.

## Important APIs, Types, and Functions
Key macros are `_DVOA`, `_DVOB`, `_DVOC`, `DVO(port)`, `_DVOA_SRCDIM`, `_DVOB_SRCDIM`, `_DVOC_SRCDIM`, and `DVO_SRCDIM(port)`. Bitfields cover enable, pipe select, pipe stall modes, interrupt selection, preserve bits, VGA sync use, data ordering, sync disable/tristate, border, active data order, sync polarity, blank polarity, output C-state/source-size behavior, and source horizontal/vertical dimensions.

## Control Flow
There is no local flow. `intel_dvo.c` reads `DVO(port)` for hardware state and writes `DVO_SRCDIM()` plus `DVO()` during pre-enable/enable/disable.

## State and Persistence Behavior
The macros map persistent hardware registers. Some bits are preserved across programming because the driver does not know the correct active data ordering for all hardware.

## Dependencies and Integration Points
The header depends on `intel_display_reg_defs.h` and is consumed by legacy DVO encoder code. It must match older display hardware register layouts.

## Risks
Pipe select is a single bit and only suitable for the hardware generations this DVO code targets. Incorrect preserve masks or data-order bits can produce swapped colors or broken sync. Source dimensions must match adjusted mode programming.

## Test Signals
Signals include correct MMIO programming in DVO pre-enable, readout returning the selected pipe, visible sync polarity correctness, and register dump comparisons on supported legacy systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dvo_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_encoder.c

## Purpose
This file contains generic encoder helper utilities for delayed link checks, HPD blocking, suspend/shutdown fan-out, and digital port allocation.

## Important APIs, Types, and Functions
Public functions are `intel_encoder_link_check_init()`, `intel_encoder_link_check_queue_work()`, `intel_encoder_link_check_flush_work()`, `intel_encoder_block_all_hpds()`, `intel_encoder_unblock_all_hpds()`, `intel_encoder_suspend_all()`, `intel_encoder_shutdown_all()`, and `intel_dig_port_alloc()`. The internal work item callback invokes the encoder's `link_check` function.

## Control Flow
Link-check initialization stores a delayed work item and callback. Queueing schedules it on `display->wq.unordered`; flushing cancels synchronously. HPD block/unblock iterates all encoders if the platform has display. Suspend and shutdown take global modeset locks, call optional per-encoder `suspend` or `shutdown`, unlock, then call optional completion hooks. Digital port allocation zeroes state, initializes invalid MMIO/AUX defaults, sets `max_lanes` to 4, and initializes the HDCP mutex.

## State and Persistence Behavior
Delayed work is stored in each encoder and persists until canceled. Digital port allocation creates persistent encoder-private state initialized to safe invalid values. Suspend/shutdown do not persist additional state but fan out to encoder-specific callbacks.

## Dependencies and Integration Points
The file depends on display workqueues, hotplug helpers, modeset locking, encoder callback fields, and HDCP mutex state in `struct intel_digital_port`. It is used by DP/HDMI and other encoder implementations that need link checks and lifecycle fan-out.

## Risks
Delayed work must be flushed before encoder destruction to avoid use-after-free. Suspend/shutdown callbacks run under global modeset locks, so callback implementations must avoid lock inversions. HPD block/unblock should be paired around operations that cannot tolerate hotplug interrupts.

## Test Signals
Signals include link-check work firing and canceling cleanly, suspend/shutdown callback ordering, HPD interrupt masking during block windows, and default digital-port fields preventing accidental MMIO/AUX access before initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_encoder.h

## Purpose
This header declares generic i915 encoder helper APIs shared by output-specific encoder implementations.

## Important APIs, Types, and Functions
It forward declares `struct intel_digital_port`, `struct intel_display`, and `struct intel_encoder`. Declarations cover link-check work management, suspend/shutdown fan-out, HPD block/unblock fan-out, and digital port allocation.

## Control Flow
There is no implementation flow. The header defines the call surface for encoder lifecycle and workqueue helpers.

## State and Persistence Behavior
No state is stored here; the functions operate on persistent encoder and digital-port structures.

## Dependencies and Integration Points
It is included by DP/HDMI, hotplug, suspend, and display probe code that needs generic encoder helpers without pulling in implementation details.

## Risks
Callers must flush delayed work before freeing encoders. Allocation callers must complete port-specific initialization after `intel_dig_port_alloc()` sets only generic defaults.

## Test Signals
Compile coverage and lifecycle tests that exercise helper declarations from multiple encoder implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fb.c

## Purpose
This file is the i915 display framebuffer validation and view-construction layer. It maps DRM format modifiers to Intel tiling/compression capabilities, validates framebuffer layout against object and plane constraints, derives normal/rotated/remapped GTT views, creates DPT mappings when required, and wires framebuffer lifetime/dirty handling into frontbuffer tracking.

## Important APIs, Types, and Functions
Important tables include modifier-specific format overrides for SKL CCS, Gen12 CCS, Gen12 CCS with clear color, flat CCS clear color, and `intel_modifiers[]`. `struct intel_modifier_desc` records modifier, display-version range, format overrides, plane capability bits, and CCS auxiliary/clear-color plane masks.

Major public helpers include modifier predicates, `intel_fb_plane_get_modifiers()`, `intel_fb_plane_supports_modifier()`, `intel_fb_get_format_info()`, CCS plane mapping helpers, tile dimension/row/alignment helpers, DPT predicates, subsampling helpers, offset alignment helpers, remap/rotation size helpers, `intel_fill_fb_info()`, `intel_fb_fill_view()`, `intel_plane_compute_gtt()`, `intel_framebuffer_init()`, `intel_user_framebuffer_create()`, `intel_framebuffer_create()`, and `intel_fb_bo()`.

## Control Flow
Framebuffer creation looks up the GEM object, initializes frontbuffer state before BO framebuffer setup to avoid tiling races, validates format/modifier support, stride limits, zero plane-0 offset, shared handles across planes, per-plane stride alignment, Gen12 CCS auxiliary stride, and total object size. It then fills derived `intel_framebuffer` view information, optionally creates a DPT, and registers DRM framebuffer callbacks.

View construction converts framebuffer plane offsets to x/y positions, checks CCS intra-tile x/y compatibility with main planes, computes aligned tile offsets, builds normal views, optionally builds rotated views for supported Y/Yf tiling, and optionally builds remapped views for DPT power-of-two stride requirements. Plane GTT computation selects remapping when visible planes exceed hardware stride limits, otherwise copies the precomputed framebuffer view and rotates source coordinates for 90/270-degree scanout.

## State and Persistence Behavior
`struct intel_framebuffer` persists DRM framebuffer state, frontbuffer tracking, panic buffer, min alignment, VT-d guard, optional DPT object, and precomputed GTT views. Dirty handling ties DMA reservation fences to deferred frontbuffer flushes, invalidating first and flushing when the fence signals. Destroy tears down the DRM framebuffer, optional DPT, BO framebuffer state, frontbuffer reference, panic allocation, and the framebuffer object.

## Dependencies and Integration Points
The file depends on DRM GEM/framebuffer helpers, DMA fences/reservations, Intel BO hooks, frontbuffer tracking, display platform/version helpers, parent DPT/frontbuffer/panic interfaces, plane capability callbacks, rotation/remapped GTT view structures, and modifier definitions. It is directly coupled with `intel_fb_pin.c`, plane atomic checks, and DPT suspend/resume.

## Risks
This is a high-risk validation boundary exposed to userspace `ADDFB`. Modifier descriptors, CCS plane masks, tile dimensions, and stride rules must match hardware exactly. Remapping cannot be used with CCS hash modes and has cursor/pre-gen restrictions. Offset arithmetic and object-size checks must avoid overflow and permit only layouts the hardware can scan out. DPT creation error cleanup must destroy the DPT without leaking frontbuffer or BO state. Dirty fence callbacks must handle already-signaled fences and allocation failures.

## Test Signals
Signals include IGT framebuffer modifier tests, invalid stride/offset/handle rejection, CCS auxiliary stride validation, object-too-small rejection, 90/270 rotation tests on supported modifiers, DPT/remapped-view scanout on ADL-P/display version 14+, dirtyfb/frontbuffer flush behavior with pending fences, suspend/resume of DPT-backed framebuffers, and leak/error-path tests for framebuffer creation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fb.h

## Purpose
This header exposes Intel framebuffer modifier, tiling, CCS, GTT-view, DPT, validation, and creation APIs used by display plane and framebuffer code.

## Important APIs, Types, and Functions
It defines plane capability bits for CCS render compression, render compression with clear color, media compression, X/Y/Yf/4 tiling, and 64K physical placement. Declarations cover modifier predicates, CCS plane mapping, modifier-list generation, format overrides, semiplanar YUV checks, surface linearity, tile sizing, plane subsampling, offset alignment, DPT use, fence use, rotation support, view size helpers, framebuffer info filling, view selection, VT-d guard computation, GTT computation, x/y offset conversion, framebuffer initialization/allocation/creation, user framebuffer creation, modifier-to-tiling conversion, and BO lookup.

## Control Flow
There is no implementation flow. The API is used during ADDFB validation, plane atomic checks, GTT pinning, scanout programming, and framebuffer destruction.

## State and Persistence Behavior
The header does not define the full framebuffer structs, but it exposes operations that mutate persistent `struct intel_framebuffer` and `struct intel_plane_state` view state. Capability bits are stable contracts between plane initialization and modifier filtering.

## Dependencies and Integration Points
It depends on Linux bits/types and forward declarations of DRM and Intel display structures. It integrates with plane initialization, DRM framebuffer creation, BO pinning, DPT, frontbuffer, and modifier advertisement.

## Risks
Mismatched declarations and implementation changes can break userspace-visible framebuffer behavior. Capability-bit changes must be coordinated with `intel_modifiers[]` in `intel_fb.c` and per-plane capabilities. Callers must pass valid framebuffer/plane state and respect that some helpers return derived offsets in-place.

## Test Signals
Compile coverage across plane and framebuffer code, modifier advertisement tests per plane, ADDFB validation tests, and scanout tests using helper-computed views.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fb_pin.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fb_pin.c

## Purpose
This file pins framebuffer BOs into the address space needed for display scanout. It supports traditional GGTT pinning, DPT-backed pinning, fence installation for tiled scanout/FBC, physical alignment for legacy planes, VT-d guard space, and surface address calculation for plane state.

## Important APIs, Types, and Functions
Public functions are `intel_fb_pin_to_ggtt()`, `intel_fb_unpin_vma()`, `intel_plane_pin_fb()`, `intel_plane_unpin_fb()`, and `intel_fb_get_map()`. Internal helper `intel_fb_pin_to_dpt()` binds framebuffer objects into the DPT VM. Alignment helpers derive min display alignment, physical alignment, and VT-d guard requirements from framebuffer and plane state.

## Control Flow
GGTT pinning validates framebuffer BO state and power-of-two alignment, takes a runtime PM reference, increments restore pending pin count, locks the object with WW retries, attaches physical memory if needed or migrates to LMEM, pins pages, pins a display VMA with requested view/alignment/guard, optionally pins a fence, gets a VMA reference, unpins object pages, drops locks and RPM, and returns the VMA.

DPT pinning rejects async-bind VMs, ensures framebuffer BOs, locks/migrates/cache-levels the object, creates or reuses a VMA in the DPT address space, unbinds misplaced VMAs, pins globally, flushes for display, and returns a referenced VMA. `intel_plane_pin_fb()` chooses GGTT or DPT flow, pins the DPT page table itself into GGTT when needed, and computes `plane_state->surf` from either a physical DMA address or GGTT offset plus plane-specific surface offset. Unpin reverses the relevant VMA and DPT pins.

## State and Persistence Behavior
Pinning persists VMA pins, optional fence pins, `plane_state->ggtt_vma`, `plane_state->dpt_vma`, `plane_state->flags`, and `plane_state->surf` for the lifetime of the committed plane state. `display->restore.pending_fb_pin` tracks in-flight pins for restore sequencing. Unpin must clear plane-state VMA pointers and drop all references.

## Dependencies and Integration Points
The file depends on GEM object locking/migration/cache-level APIs, i915 VMA pinning, DPT VM helpers, runtime PM, framebuffer view computation from `intel_fb.c`, plane callbacks for physical needs and surface offsets, and display restore tracking. It is called from atomic plane commit paths.

## Risks
Pinning is deadlock-prone without correct WW retry handling. Failing to unpin pages, fences, DPT GGTT mappings, or VMA references leaks memory/address space. DPT VMs must not bind asynchronously because the display path does not synchronize with binding. LMEM migration for clear-color CCS must keep CPU-readable memory on small-BAR systems. Fence failure is fatal on pre-gen4 but tolerated later, affecting power-saving features.

## Test Signals
Signals include successful plane pin/unpin on GGTT and DPT framebuffers, WW deadlock retry tests, LMEM migration behavior, fence pinning on tiled pre-gen4/FBC planes, physical-alignment scanout, VT-d guard validation, restore pending-pin counters returning to zero, and no VMA/DPT leaks after failed pin paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fb_pin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fb_pin.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fb_pin.h

## Purpose
This header declares framebuffer pinning and unpinning helpers for display scanout.

## Important APIs, Types, and Functions
It declares `intel_fb_pin_to_ggtt()`, `intel_fb_unpin_vma()`, `intel_plane_pin_fb()`, `intel_plane_unpin_fb()`, and `intel_fb_get_map()`. Parameters expose framebuffer, GTT view, alignment, physical alignment, VT-d guard, fence use, flags, and plane state.

## Control Flow
There is no local flow. The lifecycle implied by the API is pin framebuffer for a new plane state, program scanout using returned state, then unpin the old plane state's framebuffer when no longer used.

## State and Persistence Behavior
No state is stored here. Implementations mutate plane-state VMA pointers and flags and manage VMA references.

## Dependencies and Integration Points
The header forward declares DRM framebuffer, i915 VMA/GTT view, Intel plane state, and `iosys_map`. It is used by plane atomic commit and display memory mapping code.

## Risks
Callers must pair pin and unpin calls and pass the same flags to `intel_fb_unpin_vma()`. Incorrect alignment or guard arguments can create hardware-visible scanout faults.

## Test Signals
Compile coverage, atomic plane pin/unpin tests, framebuffer map access through `intel_fb_get_map()`, and leak detection for pin failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fb_pin.h -->
