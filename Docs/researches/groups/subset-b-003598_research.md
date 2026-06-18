<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_plane.c

## Purpose
`intel_plane.c` provides the common Intel display plane implementation used by i915 atomic modesetting. It owns Intel-specific plane state allocation, duplication, destruction, user-API-to-hardware state translation, visibility and bandwidth accounting, plane update ordering, framebuffer preparation/cleanup, panic scanout support, NV12 auxiliary Y-plane linking, joiner-pipe affected-plane expansion, and final atomic plane validation.

This file is a central integration layer between DRM atomic plane helpers and generation-specific plane implementations such as i9xx, cursor, and SKL universal planes. The generation-specific hooks live in `struct intel_plane` function pointers; this file coordinates when those hooks run and how their results affect `struct intel_crtc_state`.

## Important APIs, Types, And Functions
The exported lifecycle functions are `intel_plane_alloc()`, `intel_plane_free()`, `intel_plane_destroy()`, `intel_plane_duplicate_state()`, and `intel_plane_destroy_state()`. They allocate `struct intel_plane` plus `struct intel_plane_state`, reset default scaler state, duplicate DRM atomic state, manage framebuffer references in `plane_state->hw.fb`, and assert that pinned GGTT/DPT VMAs have been unpinned before destruction.

The exported validation and accounting helpers are `intel_plane_atomic_check()`, `intel_plane_atomic_check_with_state()`, `intel_plane_check_clipping()`, `intel_plane_check_src_coordinates()`, `intel_plane_set_invisible()`, `intel_plane_pixel_rate()`, `intel_plane_data_rate()`, `intel_adjusted_rate()`, and `intel_plane_add_affected()`. These functions derive enabled/active/scaled/NV12/C8/async plane masks, per-plane data rates, minimum CDCLK requirements, clipping, scaling, sub-sampling alignment, and affected plane state coverage.

The exported commit helpers are `intel_crtc_planes_update_noarm()`, `intel_crtc_planes_update_arm()`, `intel_plane_update_noarm()`, `intel_plane_update_arm()`, `intel_plane_disable_arm()`, and `intel_plane_async_flip()`. They dispatch to per-plane hooks and tracepoints while respecting async-flip and SKL+ DDB overlap ordering.

`intel_plane_copy_uapi_to_hw_state()` and `intel_plane_copy_hw_state()` are key state-transfer helpers. They separate logical UAPI state from `hw` state, handle joiner-secondary CRTC mapping, copy color properties, and maintain framebuffer references. `intel_plane_copy_uapi_plane_damage()` merges DRM damage into `plane_state->damage` on display version 12 and newer.

Framebuffer helper hooks are installed by `intel_plane_helper_add()`. Primary planes get `get_scanout_buffer` and `panic_flush` handlers in addition to prepare/cleanup hooks; non-primary planes only get prepare/cleanup.

## Control Flow
Atomic validation begins in `intel_plane_atomic_check()`. It first expands state coverage through `intel_add_affected_planes()` so joined pipes and linked planar planes have matching state objects. Then each new plane runs `plane_atomic_check()`, which copies damage from the relevant primary/joiner plane, copies UAPI fields into Intel hardware state, and calls `intel_plane_atomic_check_with_state()`.

`intel_plane_atomic_check_with_state()` resets the plane’s contribution, exits early for fully detached old/new state, calls the generation-specific `plane->check_plane()`, sets CRTC bitmasks for enabled, active, scaled, NV12, C8, and update planes, computes data-rate arrays for RGB or NV12 Y/UV planes, and then calls `intel_plane_atomic_calc_changes()`. That final step handles SKL scaler allocation, disabled CRTC invisibility, frontbuffer bits, CxSR disable requirements, async flip eligibility, and update flags.

Commit sequencing is split into no-arm and arm phases. `intel_crtc_planes_update_noarm()` writes non-arming registers before the arm phase unless the CRTC is doing an async flip. `intel_crtc_planes_update_arm()` dispatches to a SKL+ path or an i9xx path. The SKL+ path repeatedly chooses a plane with `skl_next_plane_to_commit()` so old and new DDB allocations do not overlap with already committed planes; the older path walks planes directly. Visible planes, and SKL Y planes, arm updates; invisible planes disable.

Framebuffer preparation flows through DRM plane helper `.prepare_fb`. `intel_prepare_plane_fb()` optionally chains fences from the old framebuffer on modesets, pins the new framebuffer, runs DRM GEM prepare, promotes fence priority for display, triggers RPS vblank boost, and marks the display workload interactive. Cleanup reverses the interactive mark and unpins the old framebuffer.

## State And Persistence Behavior
`struct intel_plane_state` carries both DRM UAPI state and Intel `hw` state. The file carefully manages `hw.fb` references independently from `uapi.fb` and clears/preserves `ggtt_vma`, `dpt_vma`, flags, damage, color blobs, and linked-plane metadata across state duplication and copy operations.

CRTC state is the persistent aggregation target during atomic check. Plane visibility mutates `enabled_planes`, `active_planes`, `scaled_planes`, `nv12_planes`, `c8_planes`, `async_flip_planes`, `update_planes`, `fb_bits`, `data_rate[]`, `data_rate_y[]`, `rel_data_rate[]`, `rel_data_rate_y[]`, and `plane_min_cdclk[]`. `unlink_nv12_plane()` and `link_nv12_planes()` keep those aggregates consistent when planar YUV uses a separate hidden Y plane.

Hardware-facing state is intentionally separated from logical UAPI state. Joiner secondary planes may have a logical `uapi.crtc` pointing at the primary CRTC, while `hw.crtc` is set to the actual secondary CRTC. This distinction is critical for joined-pipe updates and for framebuffer reference lifetime.

Panic scanout support temporarily exposes current primary-plane framebuffers as `drm_scanout_buffer` objects. For fbdev framebuffers it reuses the fbdev map and cache flushes; for other framebuffers it may use Intel parent panic setup and, for DPT tiled scanout, records a tiling offset callback in the framebuffer.

## Dependencies And Integration Points
This file depends heavily on DRM atomic helpers, GEM framebuffer helpers, DMA fences/reservations, DRM damage helpers, and DRM format metadata. Within i915 it integrates with Intel framebuffer pinning, CDCLK, RPS, parent-fence priority, FBC dirty updates, PSR2 selective fetch, SKL scalers/watermarks/DDB allocation, cursor unpin work, color pipeline/colorop blobs, and frontbuffer tracking.

Generation-specific behavior enters through `struct intel_plane` hooks: `check_plane`, `min_cdclk`, `can_async_flip`, `async_flip`, `update_noarm`, `update_arm`, `disable_arm`, `disable_tiling`, and `format_mod_supported`. The common code assumes these hooks populate fields such as `ctl`, `color_ctl`, `view`, and `decrypt` consistently before commit.

## Risks And Edge Cases
State lifetime is refcount-sensitive. Missing `drm_framebuffer_get()` or `drm_framebuffer_put()` in copy/clear/destroy paths would leak or prematurely free scanout buffers. The destroy path warns if VMAs are still pinned, making framebuffer pin/unpin ordering a key risk.

Atomic aggregation is sensitive to stale bitmasks. NV12 Y-plane link/unlink paths must update active, enabled, update, and data-rate masks together, or watermarks and commit order can be computed for the wrong plane set. Joiner pipes add another risk because all joined pipes must have the same affected plane coverage.

Async flips are intentionally restricted. Semiplanar YUV and C8 are rejected, and SKL+ first async flips may be forced through sync commit so watermarks/modifiers can update. Regressions here could produce missed flip completions, wrong selective fetch damage, or unsupported hardware programming.

Clipping and source-coordinate validation are format, rotation, modifier, and display-version dependent. The DISPLAY_VER >= 20 semiplanar exceptions and Wa_16023981245 are especially easy to break by simplifying subsampling checks.

Panic scanout code has hardware-format risk: only supported tiled DPT layouts have tiling callbacks, and unsupported tiling/modifier combinations return `-EOPNOTSUPP`. Incorrect tiling offsets would corrupt panic output.

## Test Signals
Useful test signals include DRM atomic/KMS tests for plane enable/disable, scaling, rotation, clipping, C8, NV12, async flips, joined-pipe modes, and modesets with old framebuffer fences. IGT-style coverage should inspect watermark/DDB updates across multi-plane SKL+ commits, cursor unpin after vblank, damage propagation on display version 12+, and invalid subsampling coordinates.

Runtime signals include `drm_dbg_atomic()` plane visibility logs, tracepoints `trace_intel_plane_update_noarm`, `trace_intel_plane_update_arm`, `trace_intel_plane_disable_arm`, and `trace_intel_plane_async_flip`, plus warnings for stale pinned VMAs, unexpected old visibility on disabled CRTCs, and panic scanout unsupported formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_plane.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_plane.h

## Purpose
`intel_plane.h` declares the common Intel display plane API exported by `intel_plane.c` to the rest of the i915 display stack. It keeps consumers insulated from the implementation details of Intel plane state lifetime, atomic checking, update dispatch, framebuffer helper installation, and format/async capability filtering.

## Important APIs And Types
The header forward-declares DRM and Intel display types instead of including large internal headers. This makes it a low-dependency interface for `struct intel_plane`, `struct intel_plane_state`, `struct intel_crtc_state`, `struct intel_atomic_state`, `struct intel_dsb`, and related DRM objects.

The declarations group into lifecycle (`intel_plane_alloc`, `intel_plane_free`, `intel_plane_destroy`, `intel_plane_duplicate_state`, `intel_plane_destroy_state`), state copying (`intel_plane_copy_uapi_to_hw_state`, `intel_plane_copy_hw_state`), rate/accounting (`intel_adjusted_rate`, `intel_plane_pixel_rate`, `intel_plane_data_rate`), commit dispatch (`intel_plane_update_noarm`, `intel_plane_update_arm`, `intel_plane_disable_arm`, `intel_plane_async_flip`, CRTC arm/noarm helpers), validation (`intel_plane_atomic_check`, `intel_plane_atomic_check_with_state`, clipping and source coordinate checks), and utilities (`intel_crtc_get_plane`, `intel_plane_set_invisible`, `intel_plane_needs_physical`, `intel_plane_helper_add`, `intel_plane_add_affected`, async format/modifier support).

## Control Flow And Integration
Generation-specific plane files call these declarations to participate in common atomic validation and commit sequencing. Atomic modeset code calls `intel_plane_atomic_check()` and the CRTC plane update helpers; plane initialization code calls allocation/helper-install functions; platform plane check hooks call clipping/source coordinate/rate helpers.

Because only prototypes are present, the header does not own state mutations itself. Its role is contract definition: callers must pass Intel atomic/CRTC/plane state objects that are already in the DRM atomic transaction and must respect lock and refcount assumptions enforced in `intel_plane.c`.

## State, Dependencies, Risks, And Test Signals
The header has no persistent data and no direct MMIO behavior. Its main dependency is ABI consistency between declarations and `intel_plane.c`. Misdeclared argument types would usually fail at build time, but semantic mismatches are still possible: for example, callers must understand that `intel_plane_copy_uapi_to_hw_state()` grabs framebuffer references and that `intel_plane_set_invisible()` mutates CRTC aggregate masks.

Test signals are mostly compile/link coverage plus exercising external users of the API: plane init, atomic check, update arm/noarm, async flip, and cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_plane.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pmdemand.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pmdemand.c

## Purpose
`intel_pmdemand.c` implements i915 display PM Demand programming for display version 14 and newer. PM Demand packages display bandwidth, DBUF, CDCLK, DDI clock, active PHY, PLL, pipe, voltage, and scaler requirements into Punit-facing request registers. The code models those requirements as an Intel global atomic state object so atomic commits can detect changes, serialize when needed, and program higher-safe values before plane updates and settled values after plane updates.

## Important APIs, Types, And Functions
`struct pmdemand_params` is the register payload model. It tracks QGV bandwidth/index, voltage index, active pipe count, active DBUF count on pre-Xe3 platforms, active non-Type-C PHY count, PLL count, CDCLK MHz, max DDI clock MHz, and scaler count on pre-Xe3.

`struct intel_pmdemand_state` embeds `struct intel_global_state`, preserving `ddi_clocks[]`, `active_combo_phys_mask`, and the current `params`. This state is registered by `intel_pmdemand_init()` with duplicate/destroy callbacks and initialized early by `intel_pmdemand_init_early()` for the mutex and waitqueue.

The atomic-facing API is `intel_pmdemand_atomic_check()`, which decides whether the global state must be pulled into the transaction, updates parameters from bandwidth/DBUF/CDCLK/connector state, and either serializes or locks the global state depending on `allow_modeset`. `intel_pmdemand_pre_plane_update()` and `intel_pmdemand_post_plane_update()` then program registers around plane updates.

Other exported helpers update persistent input state: `intel_pmdemand_update_port_clock()` records per-pipe DDI clocks; `intel_pmdemand_update_phys_mask()` updates the active non-TC PHY mask; `intel_pmdemand_init_pmdemand_params()` reads existing hardware request values into software state; and `intel_pmdemand_program_dbuf()` programs DBUF count during display init sequencing.

## Control Flow
`intel_pmdemand_atomic_check()` is gated by `DISPLAY_VER(display) >= 14` and by `intel_pmdemand_needs_update()`. The update decision considers bandwidth PM Demand changes, DBUF changes, CDCLK changes, CRTC port-clock changes, and connector modesets that switch between non-Type-C PHY encoders.

When an update is needed, the function acquires the PM Demand global state, reads related new global states, and fills `params`: QGV peak bandwidth from `intel_bw_qgv_point_peakbw()`, active pipe/DBUF counts from DBUF state, voltage and CDCLK from CDCLK state, max DDI clock from persistent per-pipe clocks plus current CRTC states, active PHY count from connector old/new states, PLL count as active PHYs plus the CDCLK PLL, and scaler count fixed at max on pre-Xe3 because fast paths cannot safely lock all required global state.

Register programming uses `intel_pmdemand_program_params()`. It locks `display->pmdemand.lock`, verifies no previous transaction is in flight, reads both request registers, calls `intel_pmdemand_update_params()`, writes changed registers, sets `XELPDP_PMDEMAND_REQ_ENABLE`, and waits for completion either via polling on display version 20 or via the waitqueue on other platforms.

The pre-plane update passes both new and old states so each field is programmed to the maximum of old/new values. The post-plane update passes no old state so the final new values can settle. If a commit is not serialized, current register values are also considered to avoid under-programming while parallel commits may be active.

## State And Persistence Behavior
The PM Demand object is a persistent global atomic object under `display->pmdemand.obj`. It carries historical DDI clocks and non-TC PHY mask across transactions because not every CRTC or connector participates in every commit. This persistence is required to compute max DDI clock and active combo PHY count from partial atomic state.

The mutex protects MMIO register transactions and wait sequencing. The waitqueue coordinates PM Demand completion interrupts or wakeups elsewhere in the display stack. Hardware state is also read at initialization so software does not assume zeroed request parameters after firmware or BIOS programming.

## Dependencies And Integration Points
This file depends on Intel atomic global-state helpers, bandwidth state, DBUF state, CDCLK state, display register access, display workarounds, connector/encoder helpers, and platform stepping/version predicates. It programs `XELPDP_INITIATE_PMDEMAND_REQUEST(0/1)`, `GEN12_DCPR_STATUS_1`, and workaround register `XELPD_CHICKEN_DCPR_3`.

It integrates with atomic modeset validation before commit, with pre/post plane update phases during commit, and with display initialization for early DBUF programming and initial register readout.

## Risks And Edge Cases
The most important correctness risk is under-programming PM Demand during a transition. That is why pre-plane programming uses max(old,new,current) when needed. Removing that behavior could cause transient performance or power-management failures while display hardware still consumes old resources.

Concurrency is another risk. Non-modeset commits cannot serialize global state, so the code must lock the global object and consider current register values. Bugs here could race concurrent fastsets or flips.

Version-specific field packing is split between pre-Xe3 and Xe3+ paths. Active DBUF/scaler fields are not present on newer platforms, while active pipe masks use a different field. Incorrect version gating would corrupt PM Demand payloads.

Timeouts from `intel_pmdemand_check_prev_transaction()` or wait completion indicate firmware/Punit handshake issues. The initialization path zeros params on failed previous-transaction checks to avoid trusting stale state.

## Test Signals
Relevant tests include atomic modesets and fastsets that change CDCLK, bandwidth, DBUF slices, active pipes, port clocks, and connector PHY assignments on display version 14+ hardware. Stress tests should include parallel non-modeset commits to exercise current-register maxing and lock-global-state behavior.

Runtime signals include PM Demand debug logs showing request register values and error logs for timed-out Punit PM Demand responses. Workaround coverage should verify `DMD_RSP_TIMEOUT_DISABLE` programming when Wa_14016740474 applies and polling behavior for display version 20.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pmdemand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pmdemand.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pmdemand.h

## Purpose
`intel_pmdemand.h` declares the public PM Demand interface used by Intel display initialization, atomic validation, and commit code. It exposes the opaque PM Demand global-state type and the operations needed to initialize, update inputs, and program PM Demand around plane updates.

## Important APIs And Control Flow
`to_intel_pmdemand_state()` converts from `struct intel_global_state` to the PM Demand state container. `intel_pmdemand_init_early()` initializes synchronization primitives, while `intel_pmdemand_init()` allocates and registers the global atomic object.

`intel_pmdemand_atomic_check()` is called during atomic validation. If PM Demand inputs changed, it pulls the global object into the transaction and computes new parameters. `intel_pmdemand_pre_plane_update()` and `intel_pmdemand_post_plane_update()` are commit-phase hooks used before and after plane programming.

`intel_pmdemand_init_pmdemand_params()` reads initial hardware values, `intel_pmdemand_program_dbuf()` programs display-init DBUF count, and the update helpers maintain persistent DDI-clock and non-Type-C PHY inputs.

## State, Dependencies, Risks, And Test Signals
The header intentionally forward-declares most types and includes only `linux/types.h`, so it does not own state directly. Its API contract assumes callers pass a valid `struct intel_display`, `struct intel_atomic_state`, or PM Demand global state obtained through Intel atomic helpers.

The notable interface risk is argument semantics: `intel_pmdemand_update_phys_mask()` takes a boolean named `clear_bit` in the header but implemented as `set_bit` in the C file. The type is identical, so builds succeed, but readers must consult the implementation or call sites to avoid inverted meaning.

Test coverage is provided by building all PM Demand users and running atomic commit paths that call the declared check and pre/post update hooks on supported display versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pmdemand.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pps.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pps.c

## Purpose
`intel_pps.c` implements embedded DisplayPort panel power sequencing for i915. It selects and initializes panel power sequencers, manages panel VDD and panel power transitions, applies panel timing delays from BIOS/VBT/spec fallbacks, controls PPS backlight bits, handles Valleyview/Cherryview sequencer stealing and kicking, restores/reset state after suspend or power-well events, exposes panel timing debugfs, and validates legacy PPS register locking.

The code applies only to eDP for most power operations, while several Valleyview/Cherryview helpers are called on all DP ports because those platforms bind PPS ownership to active pipes and DP ports in unusual ways.

## Important APIs, Types, And Functions
`intel_pps_lock()` and `intel_pps_unlock()` are foundational. They acquire a display-core power wakeref before taking `display->pps.mutex`, avoiding the lock ordering problem described in `vlv_pps_reset_all()`. The header macro `with_intel_pps_lock()` wraps this pattern.

Sequencer selection is handled by `pps_initial_setup()`, `vlv_initial_power_sequencer_setup()`, `vlv_power_sequencer_pipe()`, `bxt_power_sequencer_idx()`, and `intel_pps_get_registers()`. These functions map an `intel_dp` to the correct `PP_CONTROL`, `PP_STATUS`, `PP_ON_DELAYS`, `PP_OFF_DELAYS`, and optional `PP_DIVISOR` registers.

Power and VDD APIs include `intel_pps_vdd_on_unlocked()`, `intel_pps_vdd_off_unlocked()`, `intel_pps_vdd_on()`, `intel_pps_vdd_off()`, `intel_pps_vdd_off_sync()`, `intel_pps_on_unlocked()`, `intel_pps_off_unlocked()`, `intel_pps_on()`, `intel_pps_off()`, `intel_pps_wait_power_cycle()`, and `intel_pps_have_panel_power_or_vdd()`.

Backlight APIs include `intel_pps_backlight_on()`, `intel_pps_backlight_off()`, and `intel_pps_backlight_power()`. Initialization and reset APIs include `intel_pps_init()`, `intel_pps_init_late()`, `intel_pps_encoder_reset()`, `intel_pps_setup()`, `vlv_pps_pipe_init()`, `vlv_pps_pipe_reset()`, `vlv_pps_port_enable_unlocked()`, `vlv_pps_port_disable()`, `vlv_pps_reset_all()`, and `bxt_pps_reset_all()`.

## Control Flow
Initialization starts with `intel_pps_setup()` choosing the MMIO base. `intel_pps_init()` marks PPS as initializing, initializes delayed VDD-off work, initializes timestamps, selects an initial sequencer, initializes delays, programs registers, and tracks BIOS-left-on VDD. `intel_pps_init_late()` reruns after VBT parsing, optionally adjusts PPS index, reinitializes delays/registers, clears the initializing flag, and schedules delayed VDD off if needed.

Delay initialization combines three sources. `pps_init_delays_bios()` reads current hardware registers, `pps_init_delays_vbt()` reads panel VBT timings and applies quirks such as increased T12 delay, and `pps_init_delays_spec()` provides eDP-spec upper-limit fallbacks. `pps_init_delays()` chooses max(BIOS,VBT) per field or spec when both are zero, converts PPS units to milliseconds for software waits, overrides hardware backlight delays to one unit because software waits manually, and rounds power-cycle delay to hardware granularity.

Register initialization writes PP_ON/PP_OFF delay registers, port-select bits on platforms that need them, and either PP_DIVISOR or the BXT/CNP+ power-cycle field in PP_CONTROL. Optional `force_disable_vdd` clears stale VDD on sequencers before they are attached to a port.

VDD-on flow cancels delayed VDD-off work, records `want_panel_vdd`, obtains AUX power-domain wakeref if VDD is not already on, waits for power-cycle if panel power is off, sets `EDP_FORCE_VDD`, and delays before AUX access when needed. VDD-off can be delayed by `edp_panel_vdd_schedule_off()` or immediate through `intel_pps_vdd_off_sync_unlocked()`, which clears `EDP_FORCE_VDD`, records power-off time when panel power is off, invalidates source OUI, and releases the AUX wakeref.

Panel power-on waits for power-cycle, optionally toggles `PANEL_POWER_RESET` for Ironlake, applies WA 22019252566 DPLS gating around the sequence on display versions 13/14, sets `PANEL_POWER_ON` and reset, waits for PP_STATUS on-idle, and records `last_power_on`. Panel power-off requires VDD ownership, clears panel power/reset/VDD/backlight bits, waits for off-idle, records `panel_power_off_time`, invalidates source OUI, and releases the AUX wakeref.

## State And Persistence Behavior
Persistent per-panel state lives in `intel_dp->pps`: selected PPS index or VLV pipe, active VLV pipe, reset flags, initialized delays, BIOS delay snapshot, software millisecond delays, timestamps, `want_panel_vdd`, `vdd_wakeref`, delayed VDD-off work, and initializing flag.

The code persists `panel_power_off_time`, `last_power_on`, and `last_backlight_off` so later power-cycle and backlight waits honor panel timing even when hardware status bits are already idle. BIOS-left-on VDD is reconciled by taking the missing power-domain reference and scheduling VDD off instead of assuming software owns nothing.

Valleyview/Cherryview state is unusually dynamic. A PPS can be stolen from another encoder, detached by clearing port-select bits, kicked by temporarily enabling the DP port, and reset globally without taking the PPS mutex. Correct use requires a display-core wakeref plus PPS mutex when reading or mutating VLV PPS ownership.

## Dependencies And Integration Points
This file depends on Intel MMIO helpers, display power domains, DP/eDP connector and encoder state, DPIO/PLL helpers for VLV/CHV sequencer kicks, LVDS/DP port-enabled readout, VBT panel data, quirks, debugfs, delayed workqueues, jiffies/ktime delay helpers, and PPS register definitions from `intel_pps_regs.h`.

It integrates with AUX transactions through `intel_pps_check_power_unlocked()`, with DP enable/disable on VLV through port enable/disable hooks, with suspend/resume or power-well reset via encoder reset and reset-all helpers, with backlight sysfs through `intel_pps_backlight_power()`, and with connector debugfs through `i915_panel_timings`.

## Risks And Edge Cases
Lock ordering is a major risk. PPS operations must use `intel_pps_lock()`/`with_intel_pps_lock()` so a power-domain reference is acquired before `pps.mutex`. Taking locks in the wrong order can deadlock with power-domain code.

VDD wakeref lifetime is another critical risk. If VDD is already on from BIOS, software must take a wakeref; if VDD/panel power is later turned off, the wakeref must be released exactly once. The code uses `fetch_and_zero()` to avoid double puts.

Panel timing regressions can cause visible flicker, failed panel wake, or AUX failures. The code manually waits for backlight timing and power-cycle timing in addition to hardware PP_STATUS polling, and VBT/spec/quirk interactions must remain conservative.

VLV/CHV PPS selection is fragile because power sequencers can be shared, stolen, or not yet locked to a port. The kick path temporarily forces PLL/PHY state and toggles DP port enable; failures here can leave VDD force ineffective.

Register layout varies by platform: VLV/CHV and PCH split use different MMIO bases; BXT/CNP+ move power-cycle delay into PP_CONTROL; multi-PPS systems need valid PPS index selection and PCH-specific second PPS IO selection checks.

## Test Signals
Useful test signals include eDP boot, suspend/resume, VBT late init, repeated AUX access with panel off, panel on/off cycles, backlight sysfs toggling, and VLV/CHV DP/eDP port enable/disable sequences. Hardware tests should watch for PP_STATUS timeouts, PPS state mismatch logs, VDD already-on/not-on warnings, and power sequencer mismatch warnings.

Debugfs `i915_panel_timings` exposes computed software delays for connected eDP panels. Runtime logs from `drm_dbg_kms()` and `drm_err()` around PP_STATUS/PP_CONTROL values are essential for diagnosing timing and register-programming failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pps.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pps.h

## Purpose
`intel_pps.h` declares the eDP panel power sequencing interface for the i915 display stack. It exposes lock helpers, VDD/panel power operations, backlight control, initialization/reset hooks, VLV/CHV pipe ownership helpers, debugfs setup, and a legacy PPS lock assertion helper.

## Important APIs And Control Flow
The most important interface is the `with_intel_pps_lock(dp)` macro, built on `intel_pps_lock()` and `intel_pps_unlock()`. Callers use it to obtain a display-core power wakeref and `display->pps.mutex` in the correct order.

Unlocked operations such as `intel_pps_vdd_on_unlocked()`, `intel_pps_vdd_off_unlocked()`, `intel_pps_on_unlocked()`, `intel_pps_off_unlocked()`, and `intel_pps_check_power_unlocked()` require the caller to hold the PPS lock. Locked wrappers such as `intel_pps_vdd_on()`, `intel_pps_vdd_off()`, `intel_pps_on()`, `intel_pps_off()`, `intel_pps_vdd_off_sync()`, `intel_pps_have_panel_power_or_vdd()`, and `intel_pps_wait_power_cycle()` acquire it internally.

Initialization APIs are split into early panel setup (`intel_pps_init()`), late VBT-aware setup (`intel_pps_init_late()`), encoder reset/reprogramming (`intel_pps_encoder_reset()`), and display MMIO-base setup (`intel_pps_setup()`). VLV/CHV-specific APIs expose pipe tracking, active-pipe reset, backlight initial-pipe selection, port enable/disable integration, and global reset of PPS state.

## State, Dependencies, Risks, And Test Signals
The header has no direct state storage, but its API controls persistent fields inside `struct intel_dp::pps` and global fields inside `struct intel_display::pps`. Correct lock choice is the main risk: using unlocked functions without the PPS lock can race delayed VDD-off work, power-domain wakeref updates, or PP_CONTROL programming.

The API is consumed by DP/eDP enable/disable, AUX, backlight, suspend/resume, and debugfs paths. Build tests plus eDP panel power/backlight and VLV/CHV port ownership tests exercise the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pps_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pps_regs.h

## Purpose
`intel_pps_regs.h` defines the MMIO register addresses and bitfields for Intel panel power sequencing. It is a pure register contract used by `intel_pps.c` and related display code to read status, control panel power/VDD/backlight, program on/off delays, and configure power-cycle delay.

## Important Registers And Fields
`PPS_BASE`, `VLV_PPS_BASE`, and `PCH_PPS_BASE` describe the possible MMIO base addresses. `_MMIO_PPS(display, pps_idx, reg)` maps a PPS register offset through `display->pps.mmio_base` and the sequencer index.

`PP_STATUS(display, pps_idx)` exposes `PP_ON`, `PP_READY`, sequence type fields, cycle-delay-active state, and detailed sequence state values such as off-idle, on-idle, power-up substates, power-down substates, and reset.

`PP_CONTROL(display, pps_idx)` exposes legacy register unlock bits, BXT/CNP+ power-cycle delay field, `EDP_FORCE_VDD`, `EDP_BLC_ENABLE`, `PANEL_POWER_RESET`, and `PANEL_POWER_ON`.

`PP_ON_DELAYS` carries panel port selection, panel power-up delay, and backlight-on delay. `PP_OFF_DELAYS` carries panel power-down and backlight-off delays. `PP_DIVISOR` carries the older reference divider and panel power-cycle delay fields.

## Control Flow And Integration
The register macros are consumed by `intel_pps_get_registers()`, `wait_panel_status()`, VDD/panel on/off functions, delay readout, and register initialization in `intel_pps.c`. Platform code chooses the correct base through `intel_pps_setup()` and the correct `pps_idx` or VLV pipe before applying these macros.

## State, Dependencies, Risks, And Test Signals
This header stores no runtime state, but it defines the bit meanings that gate PPS state machines. Incorrect masks or field definitions would produce severe panel power sequencing failures: stuck waits, wrong delay programming, VDD not forced, backlight left disabled, or locked legacy registers.

Tests should indirectly validate these definitions through eDP power-cycle tests, PP_STATUS wait behavior, delay readback/debugfs output, and platform coverage for old PP_DIVISOR versus newer PP_CONTROL power-cycle programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pps_regs.h -->
