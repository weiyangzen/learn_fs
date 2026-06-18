# Research: subset-b-003588

Grouped source research for subset B work item `subset-b-003588`. Each delimited section preserves the source path and can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_regs.h

## Purpose
This header is the common display-engine MMIO register map for the i915/Xe display code paths represented by this tree. It defines register addresses and bitfields for legacy GMCH display, PCH display, modern DDI/DP transcoders, power wells, CDCLK/DPLL/PLL programming, hotplug, interrupts, pipe timing, scalers, watermarks, Type-C/FIA status, display workarounds, and memory/QGV discovery.

## Important APIs, Types, and Functions
There are no functions, but the macros are the API. Important register families include `DPLL()`, `DPLL_MD()`, `FP0()/FP1()`, `TRANSCONF()`, `TRANS_*` timing registers, `PIPEDSL()`, `PIPESTAT()`, `PIPE_MISC()`, `GEN8_DE_PIPE_*`, `GEN11_DE_HPD_*`, `PICAINTERRUPT_*`, `SDE*`, `PORT_HOTPLUG_*`, `SHOTPLUG_CTL_*`, `DP_*`, `DP_TP_CTL()`, `TRANS_DDI_FUNC_CTL()`, `DDI_BUF_CTL()`, `DDI_BUF_TRANS_*`, `HSW_TVIDEO_DIP_*`, `ICL_VIDEO_DIP_PPS_*`, `HSW_PWR_WELL_CTL*`, `ICL_PWR_WELL_CTL_AUX*`, `ICL_PWR_WELL_CTL_DDI*`, `CDCLK_CTL`, `CDCLK_SQUASH_CTL`, `ICL_DPLL_*`, `TGL_DPLL_*`, `BXT_DE_PLL_*`, `DC_STATE_EN`, `WM_LINETIME()`, `ICL_PHY_MISC()`, `PORT_TX_DFLEX*`, `TCSS_DDI_STATUS()`, and `MTL_MEM_SS_INFO_*`. Helper macros use `_MMIO*`, `_PICK*`, `REG_BIT`, `REG_GENMASK`, and `REG_FIELD_PREP`.

## Control Flow
The file has no executable control flow. Runtime display code chooses these macros by platform, pipe, transcoder, port, PHY, TC port, or PLL ID and then calls lower-level MMIO helpers to program hardware. Atomic modeset, interrupt, hotplug, power domain, clock, DDI, DP, watermark, and workaround code all rely on these definitions to encode control words and decode live status.

## State and Persistence Behavior
The header stores no state, but it defines persistent hardware state fields. Many registers survive until display reset, power-well loss, suspend/resume, or firmware takeover. Examples include pipe enable/timing state, DDI/DP link state, PLL configuration, CDCLK state, interrupt masks, power-well request/status bits, hotplug pulse/status fields, BIOS scratch registers, fuse straps, and memory system information. Some fields are write-one-to-clear or status latches, while others are request/status pairs requiring polling.

## Dependencies and Integration Points
The header depends on `intel_display_reg_defs.h` and display enums from nearby headers via the consumers. It is integrated with `intel_de` MMIO accessors, interrupt handlers, hotplug code, power domains, CDCLK/shared-DPLL code, DP/HDMI/DDI encoders, PPS/PSR/DSC/infoframe programming, watermark and DBUF code, display workarounds, and Type-C mode detection. It also encodes platform differences from gen2 through Xe3-era display versions.

## Risks
The main risk is register semantic drift: a bit reused across platforms can have a different meaning, and many macros have platform-specific names or comments. Wrong pipe/transcoder/port selector helpers can program the wrong MMIO offset. Interrupt enable/status masks must not be confused, hotplug status bits may be sticky, and power-well request/status bits are paired. PLL/CDCLK/DDI values are hardware-critical and can cause blank displays, link training failures, hangs, or underruns. Register fields using raw shifts instead of `REG_FIELD_PREP` are especially easy to misuse.

## Test Signals
Useful signals include successful build with all display objects, modeset bring-up on representative legacy and modern platforms, clean hotplug/AUX interrupts, DP/HDMI/eDP link training, no FIFO underruns, stable CDCLK and DPLL lock polling, correct power-well refcount transitions, valid infoframes/DSC/PSR behavior, accurate memory/QGV parsing on MTL+, and no unclaimed MMIO or display error interrupts during suspend/resume and reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_reset.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_reset.c

## Purpose
This file coordinates display state preservation and restoration around GPU/display reset. It provides the modeset-side reset hooks that stop active CRTCs safely, keep a duplicated atomic state for restoration, reinitialize display hardware when needed, and release the modeset locks acquired during reset preparation.

## Important APIs, Types, and Functions
`intel_display_reset_test()` returns `display->params.force_reset_modeset_test` for test-only reset behavior. `intel_display_reset_prepare()` is the main prepare hook and takes a `modeset_stuck_fn` callback for wedging a stuck modeset. `intel_display_reset_finish()` resumes from the duplicated state, either by committing it directly for test-only reset or by reinitializing display hardware and invoking the full display resume path. It uses `display->restore.reset_ctx`, `display->restore.modeset_state`, and `display->restore.pending_fb_pin`.

## Control Flow
Preparation exits early when `HAS_DISPLAY()` is false. If a framebuffer pin is pending, it calls the supplied stuck callback. It then locks `mode_config.mutex`, initializes a modeset acquire context, repeatedly locks all modeset locks with deadlock backoff, duplicates DRM atomic state, disables all CRTCs, and stores the duplicated state. Finish fetches and clears the saved state, unlocks directly if none exists, commits duplicated state for test-only reset, or runs the full hardware reinit sequence: PPS register unlock workaround, display hardware init, clock-gating init, CX0 PLL power-save workaround, HPD init, display driver resume, and HPD polling disable.

## State and Persistence Behavior
The saved atomic state persists between prepare and finish through `display->restore.modeset_state`; `fetch_and_zero()` prevents double restoration. The modeset acquire context persists across the reset window and must be finalized exactly once. Hardware state is intentionally disabled before reset and either restored directly or reconstructed through hardware reinitialization.

## Dependencies and Integration Points
The code depends on DRM atomic helpers, modeset locking, `intel_display_driver`, `intel_clock_gating`, `intel_cx0_phy`, `intel_hotplug`, `intel_pps`, `intel_display_utils`, and `intel_display_types`. It is called by higher-level reset paths that decide whether display hardware was actually reset.

## Risks
Error paths after lock acquisition still require `intel_display_reset_finish()` to release locks, so callers must honor the boolean return contract. Failed state duplication or disable leaves the reset lane with locks held but no saved state. Deadlock handling depends on the DRM modeset acquire context. Reinitializing hardware in the non-test path must happen before resume, or restored state may program stale power/clock/HPD state.

## Test Signals
Test signals include forced reset modeset tests, GPU reset with active displays, reset with pending framebuffer pin, suspend/resume adjacent to reset, no modeset lock leaks or `-EDEADLK` warnings, successful state restore, working hotplug after reset, and no persistent blank display after display-engine reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_reset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_reset.h

## Purpose
This header declares the display reset prepare/finish API used by the wider driver reset path. It also defines the callback type used when reset preparation detects a potentially stuck modeset.

## Important APIs, Types, and Functions
The exported type is `typedef void modeset_stuck_fn(void *context)`. The public functions are `intel_display_reset_test(struct intel_display *display)`, `intel_display_reset_prepare(struct intel_display *display, modeset_stuck_fn modeset_stuck, void *context)`, and `intel_display_reset_finish(struct intel_display *display, bool test_only)`.

## Control Flow
The header has no executable logic. It documents the call pairing implicitly: reset code calls `intel_display_reset_prepare()` before the reset and, when it returns true, calls `intel_display_reset_finish()` afterward with the test-only decision from the reset owner.

## State and Persistence Behavior
No state is stored in this header. The API manages state in `struct intel_display`, especially the reset acquire context and saved modeset state.

## Dependencies and Integration Points
It forward-declares `struct intel_display` and includes `<linux/types.h>` for `bool`. Integration points are higher-level GT/GPU reset code, display reset implementation, and any test path that forces modeset reset coverage.

## Risks
The boolean return from `intel_display_reset_prepare()` is a cleanup contract. A caller that ignores it can either leak locks or call finish unnecessarily. The callback must be safe in reset context because it is used to break a possibly stuck modeset before locks are acquired.

## Test Signals
Build coverage should catch signature drift. Runtime signals include reset paths pairing prepare/finish correctly, forced test-only reset restoring modesets, and no lockdep reports around reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_rpm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_rpm.c

## Purpose
This file is a thin display-side adapter for runtime power management. It forwards display RPM get/put/assert operations through the parent display interface so common display code can be shared between i915 and Xe parent implementations.

## Important APIs, Types, and Functions
The exported wrappers are `intel_display_rpm_get_raw()`, `intel_display_rpm_put_raw()`, `intel_display_rpm_get()`, `intel_display_rpm_get_if_in_use()`, `intel_display_rpm_get_noresume()`, `intel_display_rpm_put()`, `intel_display_rpm_put_unchecked()`, `intel_display_rpm_suspended()`, `assert_display_rpm_held()`, `intel_display_rpm_assert_block()`, and `intel_display_rpm_assert_unblock()`. All use `display->parent->rpm` callbacks and pass `display->drm`.

## Control Flow
There is no local branching other than the parent callback call chain. Each function delegates to the matching parent RPM operation, so all wake reference creation, ref tracking, noresume behavior, and assertion semantics are owned by the parent implementation.

## State and Persistence Behavior
This file does not own RPM state. It moves `struct ref_tracker *` wake references between caller and parent runtime PM code. Correct pairing of `get` and `put` calls controls whether display MMIO/power domains can autosuspend.

## Dependencies and Integration Points
It includes `drm/intel/display_parent_interface.h`, `intel_display_core.h`, and its public header. It integrates with display code that needs a runtime PM wakeref before MMIO access, power-domain logic, and parent driver implementations for i915/Xe.

## Risks
Because the wrappers are direct callbacks, a missing or mismatched parent `rpm` method will crash or corrupt wakeref accounting. `put_unchecked()` and raw/noresume variants are special-case APIs and can hide unbalanced references if used casually. Callers must hold a wakeref around MMIO paths that may run while runtime suspended.

## Test Signals
Signals include runtime PM selftests, suspend/autosuspend cycles, ref-tracker leak reports, `assert_display_rpm_held()` coverage around MMIO, and display operation success under aggressive runtime PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_rpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_rpm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_rpm.h

## Purpose
This header exposes display runtime PM helpers and a scoped helper macro for holding a display RPM wakeref. It keeps display code independent of parent-driver runtime PM details.

## Important APIs, Types, and Functions
Public functions mirror the implementation wrappers: normal `get/put`, raw `get_raw/put_raw`, `get_if_in_use`, `get_noresume`, `put_unchecked`, `intel_display_rpm_suspended()`, and assertion block/unblock helpers. `with_intel_display_rpm(display)` expands to a `for` loop that gets a wakeref, runs a scoped block, and puts the wakeref exactly once.

## Control Flow
The header only defines declarations and macros. The scoped macro uses `__UNIQUE_ID(wakeref)` to avoid local variable collisions and uses the loop increment expression to release the wakeref.

## State and Persistence Behavior
No state lives here. The API exposes `struct ref_tracker *` ownership to callers and creates a scope-based lifetime for wakerefs.

## Dependencies and Integration Points
It forward-declares `struct intel_display` and `struct ref_tracker`, and includes Linux types. It is consumed throughout display code before MMIO or parent operations that require runtime resume.

## Risks
The scoped macro is only safe when used as a block-like construct; control flow that exits abnormally must still respect C cleanup behavior. Raw, noresume, and unchecked helpers should remain restricted to display power implementation or carefully audited paths.

## Test Signals
Build coverage confirms prototypes. Runtime PM leak detection, lockdep, and suspend/resume tests are the meaningful validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_rpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_rps.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_rps.c

## Purpose
This file connects display activity to render power-state/RPS behavior. It can request an RPS boost after the next vblank when a fence is still not started, mark atomic commits as interactive, and wire Ironlake-era display PCU events into the parent RPS handler.

## Important APIs, Types, and Functions
`struct wait_rps_boost` stores a vblank wait entry, target CRTC, and fence. `intel_display_rps_boost_after_vblank()` registers a waitqueue callback for the CRTC vblank. `do_rps_boost()` performs the actual boost through `intel_parent_rps_boost_if_not_started()`, releases fence/vblank references, removes the wait entry, and frees it. `intel_display_rps_mark_interactive()` forwards interactivity changes to the parent. `ilk_display_rps_enable()`, `ilk_display_rps_disable()`, and `ilk_display_rps_irq_handler()` manage `DE_PCU_EVENT`.

## Control Flow
Boost registration first checks parent RPS availability, display generation, and vblank reference acquisition. If allocation succeeds it holds a fence reference and queues a wait entry on the CRTC vblank waitqueue. At vblank, the callback boosts only if the request has not started, then tears down all references. Interactive marking avoids duplicate parent calls by comparing `state->rps_interactive`.

## State and Persistence Behavior
Transient state is held in the allocated `wait_rps_boost` until the next vblank callback. The atomic state records whether the current commit has already marked RPS interactive. IRQ enable/disable state is in display interrupt masks guarded by `display->irq.lock`.

## Dependencies and Integration Points
Dependencies include DMA fences, DRM vblank, display IRQ helpers, `intel_parent` RPS callbacks, `intel_display_regs.h`, and display atomic state. Integration points are page-flip/commit code, vblank waitqueues, and ILK display interrupt setup.

## Risks
The callback must always drop the fence and vblank references or it leaks resources. If vblank is disabled or unavailable, boosting is skipped. Races around fence start/completion are intentionally handled by the parent `boost_if_not_started` predicate. IRQ enable/disable must hold `display->irq.lock` to avoid corrupting display interrupt state.

## Test Signals
Signals include interactive workload latency, fence boost behavior across missed vblanks, no vblank ref leaks, no waitqueue use-after-free, correct ILK PCU event handling, and power/performance tests showing RPS transitions during display-driven work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_rps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_rps.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_rps.h

## Purpose
This header declares the display-to-RPS integration API for vblank-delayed boosting, interactive commit marking, and Ironlake display RPS interrupt control.

## Important APIs, Types, and Functions
The declared APIs are `intel_display_rps_boost_after_vblank(struct drm_crtc *, struct dma_fence *)`, `intel_display_rps_mark_interactive(struct intel_display *, struct intel_atomic_state *, bool)`, `ilk_display_rps_enable()`, `ilk_display_rps_disable()`, and `ilk_display_rps_irq_handler()`.

## Control Flow
The header has no control flow. It defines the contract that callers can ask display RPS code to defer boost decisions until vblank and to reflect commit interactivity into parent RPS state.

## State and Persistence Behavior
No state is stored here. Callers pass the atomic state that records interactivity and, for boost, the fence whose lifetime is managed by the implementation.

## Dependencies and Integration Points
It forward-declares `struct dma_fence`, `struct drm_crtc`, `struct intel_atomic_state`, and `struct intel_display`, allowing display commit and IRQ code to include it with minimal dependencies.

## Risks
The API implies the fence pointer must remain valid for `dma_fence_get()`, and callers must only use the ILK IRQ helpers on hardware paths that expose `DE_PCU_EVENT`.

## Test Signals
Build integration across display commit and IRQ code, plus runtime validation of RPS boosting and ILK PCU interrupt handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_rps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_snapshot.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_snapshot.c

## Purpose
This file captures, prints, and frees display diagnostic snapshots. It packages display device info, runtime info, module/display parameters, DMC state, and display IRQ state for later error reporting without requiring live hardware reads for every field.

## Important APIs, Types, and Functions
`struct intel_display_snapshot` stores the `intel_display` pointer, `intel_display_device_info`, `intel_display_runtime_info`, `intel_display_params`, `intel_dmc_snapshot *`, and `intel_display_irq_snapshot *`. `intel_display_snapshot_capture()` allocates and fills the snapshot with `GFP_ATOMIC`. `intel_display_snapshot_print()` emits the stored data through a `drm_printer`. `intel_display_snapshot_free()` releases copied params and child snapshots.

## Control Flow
Capture allocates zeroed memory, stores the display pointer, copies static/runtime display info, copies current display parameters, then captures IRQ and DMC snapshots. Print returns immediately for null snapshots and otherwise prints device info, parameters, IRQ snapshot, and DMC snapshot. Free tolerates null, frees nested param allocations, then frees IRQ, DMC, and the snapshot object.

## State and Persistence Behavior
The snapshot is persistent diagnostic state after capture. The info/runtime/params fields are copies, while DMC and IRQ snapshots are separate allocated objects owned by the snapshot. The original display pointer is kept for driver-name access during printing, so it is not a fully standalone object.

## Dependencies and Integration Points
Dependencies include display device info, display params, display IRQ snapshot, DMC snapshot, overlay include context, slab allocation, and DRM printer/driver metadata. It likely integrates with error capture, debug dumps, and crash/reset diagnostics.

## Risks
`GFP_ATOMIC` allocation can fail, producing a null snapshot that callers and printers must tolerate. Child snapshot capture failures are not fatal but produce partial dumps. The stored display pointer must outlive printing. `intel_display_snapshot_free()` assumes child snapshots can be freed with `kfree()`, matching their capture APIs.

## Test Signals
Signals include forced error-state capture, snapshot printing from debug paths, allocation-failure tolerance, KASAN/lockdep clean free paths, and dumps showing device info, params, IRQ, and DMC sections without live MMIO faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_snapshot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_snapshot.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_snapshot.h

## Purpose
This header declares the opaque display snapshot diagnostic API.

## Important APIs, Types, and Functions
It forward-declares `struct intel_display_snapshot`, `struct intel_display`, and `struct drm_printer`, then declares `intel_display_snapshot_capture()`, `intel_display_snapshot_print()`, and `intel_display_snapshot_free()`.

## Control Flow
The header has no logic. The API lifecycle is capture, optional print, then free. All functions are expected to tolerate null where implemented for print/free.

## State and Persistence Behavior
The snapshot type is opaque to callers, preserving ownership and layout in the C file. Callers own the returned pointer and must free it.

## Dependencies and Integration Points
The header is consumed by diagnostic and error capture code that should not depend on the detailed snapshot layout.

## Risks
Because the object is opaque, misuse is mainly lifecycle related: leaking snapshots, printing after display teardown, or failing to handle capture returning null.

## Test Signals
Build coverage, error-state dump tests, and memory leak checking around capture/free are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_snapshot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_trace.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_trace.c

## Purpose
This file instantiates the display tracepoints declared in `intel_display_trace.h`. It is the single translation unit that defines `CREATE_TRACE_POINTS` for the display trace event system.

## Important APIs, Types, and Functions
There are no functions. When `__CHECKER__` is not defined, it defines `CREATE_TRACE_POINTS` and includes `intel_display_trace.h`, causing the Linux tracepoint machinery to emit tracepoint definitions rather than only declarations.

## Control Flow
The only control flow is preprocessor-controlled. Static analysis with `__CHECKER__` avoids creating tracepoints, while normal kernel builds instantiate them.

## State and Persistence Behavior
Tracepoint registration/static key state is generated by the tracing subsystem as a build artifact of this file. The file itself stores no runtime state.

## Dependencies and Integration Points
It depends entirely on `intel_display_trace.h` and Linux tracepoint infrastructure. Build systems must compile exactly one such instantiation unit, or tracepoint symbols would be missing or duplicated.

## Risks
Removing or duplicating `CREATE_TRACE_POINTS` would break trace event linkage. Including the trace header from the wrong path or with wrong `TRACE_SYSTEM` definitions would produce incorrect trace namespaces for i915 versus Xe.

## Test Signals
Build/link success, presence of display events under tracing debugfs, and successful enable/disable of display tracepoints are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_trace.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_trace.h

## Purpose
This header defines display trace events for pipe enable/disable, flips, CRCs, FIFO underruns, memory self-refresh/watermarks, plane/scaler updates, FBC transitions, vblank work, pipe update timing, and frontbuffer invalidate/flush. It supports both i915 and Xe trace namespaces by selecting `TRACE_SYSTEM` at preprocessing time.

## Important APIs, Types, and Functions
The exported tracepoints are `intel_pipe_enable`, `intel_pipe_disable`, `intel_crtc_flip_done`, `intel_pipe_crc`, `intel_cpu_fifo_underrun`, `intel_pch_fifo_underrun`, `intel_memory_cxsr`, `g4x_wm`, `vlv_wm`, `vlv_fifo_size`, `intel_plane_async_flip`, `intel_plane_update_noarm`, `intel_plane_update_arm`, `intel_plane_disable_arm`, `intel_plane_scaler_update_arm`, `intel_pipe_scaler_update_arm`, `intel_scaler_disable_arm`, `intel_fbc_activate`, `intel_fbc_deactivate`, `intel_fbc_nuke`, `intel_crtc_vblank_work_start`, `intel_crtc_vblank_work_end`, `intel_pipe_update_start`, `intel_pipe_update_vblank_evaded`, `intel_pipe_update_end`, `intel_frontbuffer_invalidate`, and `intel_frontbuffer_flush`. Helper macros include device-name extraction and fixed pipe frame/scanline formatting with static assertions for pipe numbering.

## Control Flow
Each tracepoint uses trace event fast-assign code to sample current frame and scanline counters, pipe names, rectangles, formats, watermark fields, or frontbuffer bits at the call site. The header finishes by setting `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` and including `<trace/define_trace.h>` outside the include guard, as required by Linux tracepoint generation.

## State and Persistence Behavior
Trace events do not own driver state. They snapshot selected fields into trace buffers when enabled. Several events sample live CRTC vblank counters and scanlines, so the recorded values are time-sensitive diagnostics rather than persistent driver state.

## Dependencies and Integration Points
It depends on Linux tracepoints, string helpers, `intel_crtc`, display core/limits/types, and vblank helpers. It integrates with display modeset, plane update, watermark, FBC, frontbuffer, underrun, and debugging paths. The i915/Xe `TRACE_SYSTEM` selection controls where events appear in tracing.

## Risks
Tracepoint fast paths must avoid expensive or unsafe operations when enabled in timing-sensitive display paths. Constant pipe formatting assumes `I915_MAX_PIPES` and pipe enum values remain aligned with the static assertions. Tracepoint field layouts are user-visible through tracing format files, so renaming fields or changing types can break tools. Some tracepoints dereference plane/framebuffer state and require valid call-site invariants.

## Test Signals
Signals include successful tracepoint compilation, visible events in ftrace/perf, enabling each event during modesets and flips, no crashes with tracing enabled, expected frame/scanline values, and trace output matching watermarks, scaler rectangles, FBC transitions, and frontbuffer bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_types.h

## Purpose
This is the central display object and atomic-state type contract for i915/Xe display code. It extends DRM framebuffer, connector, encoder, CRTC, plane, DP, HDMI, panel, PSR, PPS, watermark, and atomic state objects with Intel-specific hardware state, cached capability data, function hooks, and typed conversion helpers.

## Important APIs, Types, and Functions
Core types include `intel_fb_view`, `intel_framebuffer`, `intel_encoder`, `intel_panel_bl_funcs`, `intel_pps_delays`, `intel_vbt_panel_data`, `intel_panel`, `intel_hdcp`, `intel_connector`, `intel_digital_connector_state`, `intel_atomic_state`, `intel_plane_state`, `intel_initial_plane_config`, `intel_crtc_scaler_state`, watermark structs for ILK/SKL/VLV/G4X, `intel_crtc_state`, `intel_pipe_crc`, `intel_flipq`, `intel_crtc`, `intel_plane`, `intel_hdmi`, `intel_dp_compliance`, `intel_pps`, `intel_psr`, `intel_dp`, `intel_lspcon`, `intel_digital_port`, `intel_dp_mst_encoder`, and `intel_colorop`. Inline helpers convert DRM base objects to Intel objects, fetch old/new atomic states, identify DP/HDMI/MST encoders, obtain attached DP/HDMI/digital-port structures, and convert many object pointer types to `struct intel_display *`.

## Control Flow
The file is mostly data definitions, but the inline helpers contain small control decisions. Encoder helpers branch on `enum intel_output_type` to determine DP, HDMI, DDI, or MST shape. Atomic helpers call DRM atomic accessors and cast returned states. CRTC helpers map state flags to modeset, fastset, and color-update decisions. The `_Generic` `to_intel_display()` macro selects the correct conversion by pointer type.

## State and Persistence Behavior
These structures hold nearly all display state. Atomic state persists across check/commit/cleanup and includes wakerefs, global objects, DPLL state, watermark flags, and RPS interactivity. CRTC and plane states separate userspace-facing DRM state from actual hardware state for verification and readout. Connectors cache EDID, DPCD/DSC/PSR/panel replay data, HDCP state, and hotplug retry state. DP state stores link rates, lane counts, MST topology, AUX, link-training history, tunneling, compliance, PPS, PSR, ALPM, and quirks. CRTC and plane objects hold runtime hardware resources, events, IRQ flags, watermark state, callbacks, and debug counters.

## Dependencies and Integration Points
The header pulls together DRM atomic/KMS types, DP/HDMI/DSC/HDCP concepts, display limits/enums, power domains, frontbuffer, DPLL, DSB, FBC, TC ports, VBT, panel, PSR, PPS, and PXP-related plane state. It is included by most display subsystems and is a high-coupling contract between modeset checking, hardware programming, state verification, suspend/resume, hotplug, link training, watermarks, color management, and debugfs.

## Risks
This header has a large blast radius. Adding fields to permanent objects can change memory layout and lifetime expectations; adding state to the wrong object can break atomic rollback or hardware verification. State duplication rules matter because many fields use DRM property blob references, VMA pointers, wakerefs, delayed work, and nested locks. Inline type conversions assume exact object embedding. DP/MST/HDCP/PSR fields have subtle synchronization requirements, and watermark/plane state affects underrun risk.

## Test Signals
Signals include all display build targets, atomic modeset and fastset tests, state readout/verification, suspend/resume, hotplug, DP/HDMI/eDP/MST link training, PSR/panel replay/DSC/FEC/VRR/ALPM coverage, HDCP tests, plane format/rotation/scaler tests, watermark underrun tests, and memory/leak checking for property blobs, wakerefs, work items, and VMA references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_utils.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_utils.c

## Purpose
This file provides small environment-detection helpers for display code, currently focused on virtualization and IOMMU/VT-d assumptions.

## Important APIs, Types, and Functions
`intel_display_run_as_guest()` returns whether the system is running under a non-native x86 hypervisor when `CONFIG_X86` is enabled, and false otherwise. `intel_display_vtd_active()` returns true if the display device is IOMMU-mapped or, as a fallback, if it is running as a guest.

## Control Flow
The guest check is compile-time gated by `IS_ENABLED(CONFIG_X86)`. VT-d detection first calls `device_iommu_mapped(display->drm->dev)`. If that is false, it assumes host-enforced VT-d for virtualized guests by calling `intel_display_run_as_guest()`.

## State and Persistence Behavior
No state is stored. Results are derived from current kernel device/IOMMU and hypervisor state.

## Dependencies and Integration Points
Dependencies include Linux device APIs, DRM device, optional x86 hypervisor APIs, `intel_display_core.h`, and the public utils header. These helpers can influence display paths sensitive to DMA remapping, guard pages, or guest behavior.

## Risks
The guest fallback is intentionally conservative and may report VT-d active even without direct guest visibility into host remapping. Non-x86 always returns not guest, so architectures without implementation may miss equivalent virtualization handling. Callers must treat these as policy helpers, not proof of a specific IOMMU configuration.

## Test Signals
Signals include builds with and without `CONFIG_X86`, bare-metal versus VM behavior, IOMMU-on/off boot tests, and display memory/DMA paths that branch on VT-d activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_utils.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_utils.h

## Purpose
This header exposes small display utility macros and environment helper declarations used across display code.

## Important APIs, Types, and Functions
`MISSING_CASE(x)` emits a warning for unhandled enum/switch values. `fetch_and_zero(ptr)` atomically at C-expression level reads a value, stores zero back to the pointed object, and returns the old value. `KHz(x)` and `MHz(x)` are unit-conversion macros. It declares `intel_display_run_as_guest()` and `intel_display_vtd_active()`.

## Control Flow
The macros expand inline at call sites. `fetch_and_zero()` uses a GNU statement expression and `typeof` to preserve the pointed type.

## State and Persistence Behavior
The only state mutation is from `fetch_and_zero()`, which clears the caller-provided object. It is not an atomic CPU operation and relies on caller synchronization.

## Dependencies and Integration Points
It includes Linux bug/types headers and forward-declares `struct intel_display`. It is used by reset code and general display code for warnings, unit conversions, clear-on-fetch ownership transfers, and environment queries.

## Risks
`fetch_and_zero()` can be mistaken for atomic synchronization; it is only safe when the caller controls concurrent access. `KHz`/`MHz` are simple multiplication macros and can overflow if used with large values or side-effect expressions. `MISSING_CASE` warns but does not enforce recovery.

## Test Signals
Build coverage, warning paths for unexpected enum values, reset cleanup paths using `fetch_and_zero()`, and unit-sensitive clock calculations are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_wa.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_wa.c

## Purpose
This file applies and queries display hardware workarounds. It programs a small set of platform-specific workaround registers during display init and provides a central predicate for workaround IDs used throughout display code.

## Important APIs, Types, and Functions
Static apply helpers include `gen11_display_wa_apply()`, `xe_d_display_wa_apply()`, `adlp_display_wa_apply()`, and `xe3plpd_display_wa_apply()`. The public `intel_display_wa_apply()` dispatches by display version/platform. `intel_display_needs_wa_16025573575()` gates a GPIO bitbashing workaround for Xe3-derived versions. `__intel_display_wa()` maps each `enum intel_display_wa` value to platform, display version, stepping, or PCH predicates and emits a warning for missing cases.

## Control Flow
At init, `intel_display_wa_apply()` applies register writes with `intel_de_rmw()` for display versions 35, 12, 11, and Alder Lake-P. Runtime predicate flow is a switch over sorted workaround lineage IDs. Cases test `DISPLAY_VER`, `DISPLAY_VERx100`, `IS_DISPLAY_VER`, `IS_DISPLAY_STEP`, platform flags, PCH type, and one external helper for WA 16023588340.

## State and Persistence Behavior
Apply helpers mutate display MMIO registers such as `GEN8_CHICKEN_DCPR_1`, `CLKREQ_POLICY`, `GEN9_CLKGATE_DIS_5`, and `GEN9_CLKGATE_DIS_0`. Predicate helpers store no state; they encode static platform policy.

## Dependencies and Integration Points
Dependencies include DRM warnings, `intel_de`, display core/platform data, `intel_display_regs.h`, `intel_display_wa.h`, and stepping helpers. Integration points include init sequences and any code guarded by `intel_display_wa(display, WA_ID)`.

## Risks
The enum and switch must stay in sync. A missing case warns and returns false, which can silently skip a needed workaround. Register writes are platform-specific; applying them too broadly can disable useful clock gating or change power/latency behavior. Stepping bounds must match hardware documentation exactly.

## Test Signals
Signals include boot logs free of missing-WA warnings, register readback for applied workarounds, platform/stepping-specific CI coverage, absence of regressions in GPIO bitbanging, scaler/fatal error masking, clock gating, memory-up policy, DP/MST/FEC/PSR behavior, and power measurements after workaround changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_wa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_wa.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_wa.h

## Purpose
This header defines the display workaround ID namespace and exposes helpers to apply or query workaround policy.

## Important APIs, Types, and Functions
It declares `intel_display_wa_apply()`, `__intel_display_wa()`, and the user-facing macro `intel_display_wa(display, wa)`, which passes the enum value and stringified name. `enum intel_display_wa` lists sorted workaround IDs such as `INTEL_DISPLAY_WA_1409120013`, `INTEL_DISPLAY_WA_16025573575`, and `INTEL_DISPLAY_WA_22021048059`. `intel_display_needs_wa_16023588340()` is provided as an inline false stub for i915 builds and an external declaration otherwise.

## Control Flow
The header has no runtime logic beyond the macro and i915 conditional stub. The enum comment establishes the maintenance contract that each enum entry must have a matching switch case in `__intel_display_wa()`.

## State and Persistence Behavior
No state is stored here. The enum values are stable identifiers used as predicates across the driver.

## Dependencies and Integration Points
It includes Linux types and forward-declares `struct intel_display`. It integrates with display feature paths that need platform-specific workaround checks and with init code that applies global workaround registers.

## Risks
Adding an enum without updating the implementation produces runtime warnings and false predicates. Renumbering is less visible because callers use names, but ordering by lineage helps audits. The i915 versus Xe difference for WA 16023588340 must remain intentional.

## Test Signals
Build coverage for i915 and non-i915 configurations, no missing-WA warnings, and targeted platform stepping tests for each workaround predicate are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_wa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dkl_phy.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dkl_phy.c

## Purpose
This file implements serialized access to Dekel PHY registers. Dekel registers require selecting a HIP index/bank before accessing the actual MMIO register, so the code wraps reads, writes, read-modify-writes, and posting reads with a display-global PHY spinlock.

## Important APIs, Types, and Functions
`intel_dkl_phy_init()` initializes `display->dkl.phy_lock`. `dkl_phy_set_hip_idx()` selects the HIP index for a `struct intel_dkl_phy_reg`. `intel_dkl_phy_read()`, `intel_dkl_phy_write()`, `intel_dkl_phy_rmw()`, and `intel_dkl_phy_posting_read()` perform the corresponding `intel_de` MMIO operation after setting the index.

## Control Flow
Each public accessor acquires `display->dkl.phy_lock`, calls `dkl_phy_set_hip_idx()`, accesses `DKL_REG_MMIO(reg)`, and releases the lock. The HIP selector validates that the decoded TC port is in range and warns/returns early when invalid. RMW delegates the masked update to `intel_de_rmw()`.

## State and Persistence Behavior
The persistent local state is the spinlock in `display->dkl`. Hardware state is the selected HIP index and the target PHY registers. The lock ensures that index selection and data access are an indivisible sequence with respect to other Dekel PHY accesses.

## Dependencies and Integration Points
Dependencies include DRM device/print helpers, `intel_de`, display core, `intel_dkl_phy_regs.h`, and Dekel register encoding helpers such as `DKL_REG_TC_PORT`, `HIP_INDEX_REG`, `HIP_INDEX_VAL`, and `DKL_REG_MMIO`. It integrates with Type-C/PHY programming, PLL/link setup, and low-level display bring-up paths.

## Risks
Without the lock, concurrent PHY accesses could select one bank and read or write another caller's target register. Invalid TC port decoding only warns and returns from HIP selection, so the following access still uses the encoded MMIO register under the lock; callers must pass valid `intel_dkl_phy_reg` values. Accessors assume runtime power and MMIO readiness are handled by the caller.

## Test Signals
Signals include link training on Dekel PHY platforms, no HIP-index race symptoms under concurrent hotplug/modeset, correct PHY register readback, lockdep clean spinlock usage, and no invalid TC port warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dkl_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dkl_phy.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dkl_phy.h

## Purpose
This header declares the Dekel PHY register access API for display code.

## Important APIs, Types, and Functions
It includes `intel_dkl_phy_regs.h` for `struct intel_dkl_phy_reg` and declares `intel_dkl_phy_init()`, `intel_dkl_phy_read()`, `intel_dkl_phy_write()`, `intel_dkl_phy_rmw()`, and `intel_dkl_phy_posting_read()`.

## Control Flow
The header has no logic. The API contract is that callers initialize the PHY lock before performing serialized register accesses through the C implementation.

## State and Persistence Behavior
No state is defined here. Accessors operate on lock and hardware state owned by `struct intel_display` and Dekel PHY registers.

## Dependencies and Integration Points
It forward-declares `struct intel_display` and depends on Dekel register descriptors. It is consumed by PHY, DDI, PLL, and Type-C display code needing banked PHY MMIO access.

## Risks
Callers must not bypass these helpers for banked Dekel registers unless they can prove serialization and HIP index correctness. The API also assumes the caller has satisfied runtime power requirements.

## Test Signals
Build coverage, Dekel PHY link bring-up, register read/write validation, and absence of HIP index races are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dkl_phy.h -->
