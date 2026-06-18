# subset-b-003596 i915 display hotplug, link, PHY, LVDS, and helper research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hotplug.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hotplug.c

Purpose: implements the platform-independent i915 display hotplug core. It converts decoded HPD pin interrupts into DisplayPort pulse handling, connector detection work, userspace hotplug uevents, polling fallback, storm mitigation, HPD block/unblock semantics, and debugfs controls.

Important APIs/types/functions: `intel_hpd_pin_default()` maps DDI ports to default HPD pins. `intel_hpd_irq_handler()` is the generic IRQ entry called by platform decoders. `intel_encoder_hotplug()` and `intel_hotplug_detect_connector()` run connector detection. Work functions `i915_digport_work_func()`, `i915_hotplug_work_func()`, `i915_hpd_poll_init_work()`, and `intel_hpd_irq_storm_reenable_work()` are the deferred processing paths. Lifecycle APIs include `intel_hpd_init_early()`, `intel_hpd_init()`, `intel_hpd_cancel_work()`, `intel_hpd_poll_enable()`, `intel_hpd_poll_disable()`, and `intel_hpd_poll_fini()`. Blocking APIs are `intel_hpd_block()`, `intel_hpd_unblock()`, and `intel_hpd_clear_and_unblock()`. Debugfs registration is `intel_hpd_debugfs_register()`.

Control flow: platform IRQ code passes `pin_mask` and `long_mask` into `intel_hpd_irq_handler()`. The handler classifies pins with digital `hpd_pulse` callbacks as short or long DP pulses, stores pending masks under `display->irq.lock`, runs storm accounting, disables storming pins through `intel_hpd_irq_setup()`, and queues either the DP workqueue or generic detection work. DP work drains long/short pulse masks, skips blocked pins, calls each digital port `hpd_pulse()` hook, and falls back to generic hotplug when the DP hook returns `IRQ_NONE`. Generic hotplug work drains event/retry bits, switches storm-disabled HPD connectors to polling, locks `mode_config.mutex`, calls encoder hotplug callbacks, emits connector-specific or device-wide uevents, and requeues retry bits after `HPD_RETRY_DELAY`.

State and persistence behavior: runtime state lives in `display->hotplug`: per-pin `stats` with count, last jiffies, state, and blocked count; pending `long_hpd_pin_mask`, `short_hpd_pin_mask`, `event_bits`, and `retry_bits`; storm threshold and short-storm enable flags; polling/detection booleans; work items. No filesystem persistence exists. Debugfs writes mutate the in-memory storm threshold and short-storm detection state.

Dependencies and integration points: depends on DRM connector detection helpers, DRM hotplug event helpers, i915 display power/runtime PM, DP MST/short-pulse hooks, HDCP and connector retry work cancellation, interrupt locking, and unordered/display DP workqueues. It integrates with `intel_hotplug_irq.c` for platform enable/ack paths and with connector/encoder hooks for actual detect logic.

Risks: lock ordering is critical because IRQ paths use `display->irq.lock`, detection takes `mode_config.mutex`, and work cancellation must not deadlock with display queues. HPD storm detection deliberately ignores short pulses on MST-capable systems, so regressions can either mask real storms or break MST sideband traffic. Shared HPD pins mean blocking or storm-disabling one encoder affects all encoders on that pin. Poll enable/disable is asynchronous to avoid modeset lock recursion, so missed events are recovered by explicit detect work. Debugfs threshold changes flush delayed reenable work and can alter live behavior.

Test signals: HPD long/short pulse tests for DP, MST, HDMI fallback, repeated storming interrupt suppression, polling fallback and reenable after `HPD_STORM_REENABLE_DELAY`, connector-specific uevents for one connector, device-wide uevents for multiple connectors, retry callback behavior, runtime suspend poll enable/disable, HPD block/unblock with pending events, and debugfs `i915_hpd_storm_ctl`, `i915_hpd_short_storm_ctl`, and `i915_ignore_long_hpd` coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hotplug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hotplug.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hotplug.h

Purpose: declares the hotplug core interface used by i915 display initialization, interrupt handling, polling, encoder code, and debugfs setup.

Important APIs/types/functions: exposes HPD lifecycle (`intel_hpd_init_early()`, `intel_hpd_init()`, `intel_hpd_cancel_work()`), polling control (`intel_hpd_poll_enable()`, `intel_hpd_poll_disable()`, `intel_hpd_poll_fini()`), event entry points (`intel_hpd_irq_handler()`, `intel_hpd_trigger_irq()`, `intel_encoder_hotplug()`), pin mapping (`intel_hpd_pin_default()`), block/unblock APIs, detection work enable/disable/schedule, and `intel_hpd_debugfs_register()`.

Control flow: callers initialize work structures early, enable IRQ-backed HPD after interrupt hardware is ready, route decoded IRQ masks into `intel_hpd_irq_handler()`, and use polling or blocking helpers around runtime PM, Type-C mode changes, and sensitive AUX transactions.

State and persistence behavior: the header owns no state, but its APIs operate on `struct intel_display`, `struct intel_encoder`, `struct intel_connector`, and `struct intel_digital_port` hotplug fields.

Dependencies and integration points: provides the contract between `intel_hotplug.c`, `intel_hotplug_irq.c`, display bringup/teardown, DP/Type-C code, connector probing, and debugfs.

Risks: API callers must pair `intel_hpd_block()` with an unblock variant and must not assume `intel_hpd_schedule_detection()` succeeds when detection work is disabled. Incorrect initialization order can leave work items uninitialized or IRQs enabled before the generic state is ready.

Test signals: build coverage for all prototypes, driver load/unload, suspend/resume HPD polling, manual HPD trigger through DP helpers, and block/unblock paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hotplug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hotplug_irq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hotplug_irq.c

Purpose: implements platform-specific HPD interrupt register decoding and enable programming. It maps GMCH, PCH split, ICP/SPT, Gen11, XeLPDP/PICA, DG1/DG2, BXT/GLK, and newer PCH HPD status bits into the generic pin masks consumed by `intel_hpd_irq_handler()`.

Important APIs/types/functions: `intel_hotplug_irq_init()` selects HPD pin tables and platform `intel_hotplug_funcs`. `intel_hpd_init_pins()` assigns CPU and PCH HPD bit tables. IRQ handlers include `i9xx_hpd_irq_ack()`, `i9xx_hpd_irq_handler()`, `ibx_hpd_irq_handler()`, `ilk_hpd_irq_handler()`, `bxt_hpd_irq_handler()`, `gen11_hpd_irq_handler()`, `xelpdp_pica_irq_handler()`, `icp_irq_handler()`, and `spt_irq_handler()`. Enable APIs are `intel_hpd_irq_setup()` and `intel_hpd_enable_detection()`. Register helpers include `i915_hotplug_interrupt_update_locked()` and `i915_hotplug_interrupt_update()`.

Control flow: initialization chooses HPD status arrays for north display and PCH display based on display version and PCH type, then binds a platform function table. At interrupt time, each platform handler reads or RMW-acks the relevant hotplug control/status register, calls `intel_get_hpd_pins()` with the correct long-pulse detector, accumulates `pin_mask` and `long_mask`, then calls the generic hotplug core. AUX and GMBUS interrupts are forwarded to their own handlers when sharing the same interrupt register. Setup functions compute all present encoder HPD bits and the subset still enabled after storm suppression, then program display interrupt masks and per-platform hotplug detection registers.

State and persistence behavior: this file persists selected HPD register tables in `display->hotplug.hpd` and `display->hotplug.pch_hpd`, and stores the selected function table in `display->funcs.hotplug`. Hardware state is held in MMIO interrupt masks, hotplug control registers, and platform-specific inversion/filter settings. It does not write durable storage.

Dependencies and integration points: depends on `intel_de` MMIO access, display IRQ helpers (`bdw_update_port_irq()`, `ilk_update_display_irq()`, `ibx_display_interrupt_update()`), DP AUX/GMBUS IRQ handlers, BIOS HPD inversion data, PCH/platform feature predicates, and register definitions from display register headers. It is the hardware-facing half of `intel_hotplug.c`.

Risks: register semantics vary widely by generation. Some handlers must touch registers even with zero trigger bits to satisfy PCH ack behavior, while i9xx must clear all pending status bits repeatedly to restore edge detection. Long-pulse detection must match the correct control register or DP short pulses can be misclassified. HPD polarity inversion on DG1/MTP/BXT depends on board data and platform workarounds. Storm-disabled pins are filtered through generic state, so enable-mask computation must stay aligned with encoder HPD pin assignment.

Test signals: platform boot smoke tests across GMCH, PCH split, Gen11 TC/TBT, XeLPDP PICA, DG1/DG2, BXT/GLK, and MTP/LNL; interrupt ack stuck-bit warnings; AUX/GMBUS interrupt forwarding; HPD inversion validation from VBT; SPT/CNP filter count and chicken-bit workarounds; storm-disabled pin masks reflected in MMIO interrupt masks; and HPD long/short pulse classification logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hotplug_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hotplug_irq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hotplug_irq.h

Purpose: declares the hardware-facing HPD IRQ API used by display interrupt dispatchers and the generic hotplug core.

Important APIs/types/functions: exposes per-platform IRQ decoders, i9xx ack, hotplug interrupt enable updates, per-encoder HPD detection enable, global HPD IRQ setup, and `intel_hotplug_irq_init()`.

Control flow: display IRQ code calls the relevant handler with raw IIR/status values. Hotplug core calls `intel_hpd_irq_setup()` when storm state changes. Encoder setup or Type-C code can call `intel_hpd_enable_detection()` for a single encoder.

State and persistence behavior: no direct state is defined in the header; implementations update `struct intel_display` and HPD MMIO state.

Dependencies and integration points: bridges display IRQ dispatch code, `intel_hotplug.c`, encoder setup, and platform display initialization.

Risks: adding a platform requires both a handler prototype and dispatch integration. Wrong use of locked versus unlocked interrupt update helpers can race HPD enable RMW sequences.

Test signals: compile coverage by platform configs, interrupt dispatch tests, storm reprogramming through `intel_hpd_irq_setup()`, and HPD enable calls for newly initialized encoders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hotplug_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hti.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hti.c

Purpose: captures Hardware Test Interface display resource reservations so i915 does not use display PHYs or DPLLs already claimed by HTI firmware/hardware state.

Important APIs/types/functions: `intel_hti_init()` reads `HDPORT_STATE` when the platform advertises HTI. `intel_hti_uses_phy()` reports whether HTI enabled a given PHY. `intel_hti_dpll_mask()` returns the DPLL mask encoded in the HTI state.

Control flow: display initialization calls `intel_hti_init()` before output creation. Later output and DPLL setup can query the cached state to skip reserved resources.

State and persistence behavior: a single MMIO snapshot is stored in `display->hti.state`. This runtime cache persists until driver teardown or reinitialization and is not refreshed dynamically.

Dependencies and integration points: depends on `DISPLAY_INFO(display)->has_hti`, `intel_de_read()`, `HDPORT_STATE` bits from `intel_hti_regs.h`, PHY enum values, and DPLL allocation logic elsewhere in i915.

Risks: the DPLL mask comment notes that bit values must match platform DPLL numbering. A stale or incorrectly decoded HTI state can hide usable resources or allow conflicts with HTI-owned ports. `intel_hti_uses_phy()` warns on `PHY_NONE`, so callers need valid PHY mapping.

Test signals: platform boots with and without HTI support, logs/resource availability when HTI reserves a DDI, DPLL mask correctness for each platform, and warnings for invalid PHY callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hti.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hti.h

Purpose: exposes the small HTI reservation query interface.

Important APIs/types/functions: declares `intel_hti_init()`, `intel_hti_uses_phy()`, and `intel_hti_dpll_mask()`.

Control flow: init snapshots HTI state, and display resource discovery queries the cached PHY/DPLL reservations.

State and persistence behavior: the header has no state; APIs operate on `display->hti.state`.

Dependencies and integration points: integrates HTI register decoding with encoder/PHY/DPLL allocation code through `struct intel_display` and `enum phy`.

Risks: the API assumes HTI state was initialized before resource decisions.

Test signals: build coverage and resource filtering tests on HTI-capable platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hti.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hti_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hti_regs.h

Purpose: defines the HTI `HDPORT_STATE` register and bitfields used to identify firmware-owned display resources.

Important APIs/types/functions: `HDPORT_STATE` is the MMIO address. `HDPORT_ENABLED` gates interpretation. `HDPORT_DDI_USED(phy)` encodes per-PHY reservation bits. `HDPORT_DPLL_USED_MASK` extracts reserved DPLLs.

Control flow: `intel_hti.c` reads `HDPORT_STATE` and tests these bitfields during display initialization and resource queries.

State and persistence behavior: register definitions only; hardware supplies the state.

Dependencies and integration points: depends on i915 register macros from `intel_display_reg_defs.h` and the platform PHY numbering contract.

Risks: PHY-indexed bit arithmetic must remain aligned with hardware documentation. DPLL mask values must match the platform DPLL enum/allocator.

Test signals: register decode tests against known HTI state values and platform bringup with reserved DDI/DPLL resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hti_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_initial_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_initial_plane.c

Purpose: reconstructs BIOS or firmware-programmed primary plane framebuffer state during driver takeover so i915 can preserve boot display contents when possible and avoid inconsistent active planes without framebuffers.

Important APIs/types/functions: `intel_initial_plane_config()` is the main entry. `intel_initial_plane_vblank_wait()` delegates vblank waits to the display parent interface. `intel_find_initial_plane_obj()` chooses or constructs the framebuffer object and plane state. `intel_alloc_initial_plane_obj()` validates supported modifiers and asks the parent `initial_plane` implementation to allocate backing storage. `intel_reuse_initial_plane_obj()` reuses an already reconstructed plane object when multiple active heads share the same surface base. `plane_config_fini()` releases temporary config resources.

Control flow: for each active CRTC, the display hook `get_initial_plane_config()` populates an `intel_initial_plane_config`. The code attempts to allocate a GEM object for supported linear/X/Y/4-tiled modifiers, otherwise searches active CRTCs for a matching base address. On success it fills plane rotation, framebuffer view, source/destination rectangles, framebuffer reference, CRTC association, hardware state, and frontbuffer bits. If setup fails, it disables the primary plane non-atomically to prevent later code from seeing a visible plane with no framebuffer. Platform hook `fixup_initial_plane_config()` can request a vblank wait before cleanup.

State and persistence behavior: persistent runtime state is the primary plane's DRM and i915 plane state, framebuffer references, GGTT VMA, and frontbuffer tracking. Temporary `intel_initial_plane_config` objects are finalized after each CRTC. No durable storage is used.

Dependencies and integration points: depends on display parent initial-plane callbacks (`alloc_obj`, `setup`, `config_fini`, `vblank_wait`), platform display hooks (`get_initial_plane_config`, `fixup_initial_plane_config`), framebuffer helpers, frontbuffer tracking, plane state conversion, and CRTC readout state.

Risks: unsupported modifiers or allocation failures disable inherited planes, causing visible boot transition changes. Shared framebuffer detection is based on base address, so unusual BIOS layouts can be missed. Comments call out unhandled failures when initial config readout fails and non-page-aligned surface bases. Reference handling must distinguish full framebuffers from stubs.

Test signals: fastboot/smooth boot tests, multi-head shared BIOS framebuffer takeover, unsupported modifier fallback, primary plane disabled on reconstruction failure, frontbuffer bit correctness, and vblank wait when platform fixups adjust live plane state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_initial_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_initial_plane.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_initial_plane.h

Purpose: declares initial plane takeover helpers.

Important APIs/types/functions: `intel_initial_plane_config()` reconstructs active primary plane state, and `intel_initial_plane_vblank_wait()` waits for a vblank through the display parent interface.

Control flow: display initialization calls `intel_initial_plane_config()` after CRTC/plane hardware readout is available.

State and persistence behavior: no state in the header; implementation mutates CRTC primary plane state and framebuffer references.

Dependencies and integration points: connects display initialization to platform-specific initial-plane callbacks and `struct intel_crtc`.

Risks: callers must only invoke this after display objects and platform hooks are initialized.

Test signals: build coverage and driver takeover with BIOS primary planes active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_initial_plane.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_link_bw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_link_bw.c

Purpose: coordinates shared display link bandwidth fallback during atomic check and exposes a connector debugfs control to force link bits-per-pixel. It lets DP MST, DP tunnel, FDI, and similar shared links ask for lower bpp or DSC-based recomputation without embedding the fallback loop in each encoder.

Important APIs/types/functions: `intel_link_bw_init_limits()` initializes `struct intel_link_bw_limits` from duplicated atomic state and connector force values. `intel_link_bw_reduce_bpp()` and `__intel_link_bw_reduce_bpp()` choose the pipe with the highest current link bpp and lower its maximum. `intel_link_bw_compute_pipe_bpp()` clamps simple encoder pipe bpp to max link bpp. `intel_link_bw_set_bpp_limit_for_pipe()` pins a known-good limit after compute failure. `intel_link_bw_atomic_check()` calls `intel_dp_mst_atomic_check_link()`, `intel_dp_tunnel_atomic_check_link()`, and `intel_fdi_atomic_check_link()`. Debugfs helpers parse fixed-point Q4 bpp strings and implement `intel_link_bw_connector_debugfs_add()`.

Control flow: atomic check initializes limits, computes CRTC states, then shared-link checks may update limits and return `-EAGAIN`. The caller recomputes affected pipes with lower `max_bpp_x16` or newly enabled DSC limits. Bpp reduction first respects per-connector forced bpp, then, if no fallback remains, can reduce below a forced value. The debugfs write path validates the requested bpp against DSC or minimum pipe bpp and maximum pipe bpp under `connection_mutex`.

State and persistence behavior: per-atomic-check bandwidth state is transient in `intel_link_bw_limits`. Forced bpp persists at runtime in `connector->link.force_bpp_x16` until changed or connector teardown. There is no filesystem persistence beyond debugfs control visibility.

Dependencies and integration points: integrates with Intel atomic state, connector state iteration, DP MST bandwidth allocation, DP tunnel allocation, FDI bandwidth checks, DSC capability helpers, fixed-point DRM helpers, and connector debugfs.

Risks: limits must only become stricter; `assert_link_limit_change_valid()` warns if DSC is removed or bpp increases during fallback. YUV420 is noted as a TODO because MST bandwidth currently uses pipe bpp, not actual half-rate link bpp. Forced bpp parsing uses Q4 fixed-point with overflow checks, and debugfs accepts zero as reset. Fallback can loop or fail if affected pipes are not correctly marked for modeset recomputation.

Test signals: MST over-allocation fallback, DP tunnel bandwidth pressure, FDI fallback, forced bpp debugfs read/write including fractional values and reset to zero, DSC and non-DSC min/max validation, `-EAGAIN` recompute loops, and warnings on invalid limit changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_link_bw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_link_bw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_link_bw.h

Purpose: defines the shared-link bandwidth limit structure and exported helpers used by atomic mode computation and connector debugfs.

Important APIs/types/functions: `struct intel_link_bw_limits` holds `link_dsc_pipes`, `bpp_limit_reached_pipes`, and per-pipe `max_bpp_x16` in sixteenth-bpp units. Declarations cover initialization, bpp reduction, simple pipe bpp computation, per-pipe minimum limit setting, atomic shared-link check, and connector debugfs registration.

Control flow: atomic code creates limits, encoder/shared-link checks update them, and `-EAGAIN` asks the caller to recompute CRTC states.

State and persistence behavior: structure instances are transient atomic-check state; debugfs values persist in connector objects.

Dependencies and integration points: depends on `I915_MAX_PIPES`, `enum pipe`, Intel atomic state, CRTC state, and connector types.

Risks: callers must preserve the monotonic decreasing limit invariant and track which pipes have reached minimum bpp.

Test signals: compile coverage, atomic retry behavior, and debugfs availability on DP/eDP/HDMI/VGA/FDI-capable connectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_link_bw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_load_detect.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_load_detect.c

Purpose: provides legacy load-detection pipe allocation for connector probing paths that need to temporarily light up a CRTC at a known mode, then restore the previous atomic state.

Important APIs/types/functions: `intel_load_detect_get_pipe()` finds or allocates a suitable CRTC, commits a 640x480@72Hz load-detect mode, disables affected planes, and returns duplicated restore state. `intel_load_detect_release_pipe()` commits the duplicated state back. `intel_modeset_disable_planes()` adds affected planes to the temporary atomic state and detaches them.

Control flow: callers hold `connection_mutex` and pass an acquire context. If the connector already has a CRTC, that CRTC is used. Otherwise, the first disabled compatible CRTC from the encoder's possible CRTC mask is locked and selected. The function builds two internal atomic states: one for the temporary load-detect commit and one restore snapshot containing connector, CRTC, and affected planes. After committing the temporary state, it waits one vblank before returning the restore state. Release commits the duplicated old state and drops it.

State and persistence behavior: temporary state is internal atomic state. The live hardware CRTC/connector/plane state is changed during detection and restored later. No durable persistence exists.

Dependencies and integration points: depends on DRM atomic helpers, modeset acquire contexts and deadlock handling, i915 CRTC state, connector/encoder attachment, and `intel_crtc_wait_for_next_vblank()`.

Risks: failure returns `ERR_PTR(-EDEADLK)` only for lock backoff and `NULL` for other errors, so callers must distinguish both. If restore commit fails, the temporary mode may remain. Plane disabling avoids stale scanout during load detect but can visibly disturb active outputs if an already assigned CRTC is reused. Correct lock ownership is required by the warning on `connection_mutex`.

Test signals: legacy TV/CRT load detection, no-free-CRTC failure, deadlock retry paths, restoration after successful probe, restoration failure logging, and vblank wait before measurement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_load_detect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_load_detect.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_load_detect.h

Purpose: declares the load-detect temporary pipe API.

Important APIs/types/functions: `intel_load_detect_get_pipe()` returns restore state or an error/null result, and `intel_load_detect_release_pipe()` restores and releases that state.

Control flow: probe code gets a temporary pipe, performs load detection, then releases the pipe with the same acquire context.

State and persistence behavior: implementation temporarily changes atomic display state and restores it through the returned duplicated state.

Dependencies and integration points: used by connector detect code that needs a lit pipe, with DRM atomic state and modeset locking.

Risks: callers must always release a non-null/non-error state and must handle `-EDEADLK` retries.

Test signals: compile coverage and connector probe paths using load detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_load_detect.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lpe_audio.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lpe_audio.c

Purpose: implements the i915 bridge to the standalone HDMI/DP LPE audio platform driver on Atom-class platforms that lack the traditional HD-audio controller.

Important APIs/types/functions: `intel_lpe_audio_init()` detects and sets up the bridge, `intel_lpe_audio_teardown()` unregisters it, `intel_lpe_audio_irq_handler()` forwards display audio IRQs through a Linux IRQ descriptor, and `intel_lpe_audio_notify()` updates per-port ELD/link-clock/DP state and notifies the audio driver. Internal helpers create/destroy the `hdmi-lpe-audio` platform device, allocate IRQ descriptors, install an IRQ chip, and detect VLV/CHV systems without Atom HDAudio PCI devices.

Control flow: init detects Valleyview/Cherryview without matching HD-audio PCI IDs. Setup allocates a synthetic IRQ descriptor, installs a simple IRQ handler chip, creates a child platform device with IRQ and MMIO resources plus `intel_hdmi_lpe_audio_pdata`, marks it runtime-PM callback-free, and enables a VLV audio chicken bit. Display IRQ handling calls `generic_handle_irq()` for the allocated IRQ. Audio notify locks pdata, copies or clears ELD, pipe, link symbol clock, and DP-output flags for the port, unmutes or mutes the amplifier register, calls the platform driver's notification callback if present, and unlocks.

State and persistence behavior: runtime state lives in `display->audio.lpe.irq`, `display->audio.lpe.platdev`, platform device resources, and platform data copied at device registration. Per-port audio state is in platform data and protected by `lpe_audio_slock`. No durable persistence exists.

Dependencies and integration points: integrates i915 display audio register programming with the ALSA `hdmi-lpe-audio` platform driver, Linux platform device model, IRQ core, PCI resource BARs, runtime PM parentage, and Intel audio register definitions.

Risks: file documentation calls out platform-device lifetime risk if the audio module remains installed while i915 unregisters the child. `platform_device_register_full()` leaks its allocated DMA mask by platform core behavior, acknowledged in teardown. IRQ descriptor allocation and platform device registration must unwind correctly. Port indexing assumes ports B/C(/D) map to zero-based platform data entries. Notify must serialize register and pdata updates.

Test signals: VLV/CHV systems with and without HDAudio PCI device, platform device probe by ALSA driver, forwarded IRQ delivery, ELD updates on HDMI/DP plug/unplug, amp mute/unmute register writes, teardown with audio driver loaded/unloaded, and error paths for IRQ/platform allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lpe_audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lpe_audio.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lpe_audio.h

Purpose: declares or stubs the LPE audio bridge API depending on the i915 build context.

Important APIs/types/functions: when `I915` is defined, exposes init, teardown, IRQ forwarding, and ELD notification. Otherwise inline stubs return `-ENODEV` or no-op.

Control flow: display audio code can call these APIs without conditional compilation at each callsite.

State and persistence behavior: no header state; implementation stores platform device and IRQ state in `struct intel_display`.

Dependencies and integration points: bridges display audio logic, interrupt dispatch, and the standalone LPE audio platform driver.

Risks: stub behavior must match non-i915 build expectations; callers should tolerate `-ENODEV` from init.

Test signals: build coverage with and without `I915`, audio init skip behavior, and no-op stubs in non-i915 contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lpe_audio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lspcon.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lspcon.c

Purpose: manages DP-to-HDMI 2.0 LSPCON bridge chips on Intel digital ports, including probe, mode switching to PCON, vendor detection, HDR capability detection, AVI/HDR infoframe handling, infoframe readback, and resume recovery.

Important APIs/types/functions: `intel_lspcon_init()` probes and activates LSPCON. `intel_lspcon_resume()` restores PCON state after resume. `intel_lspcon_detect_hdr_capability()`, `intel_lspcon_active()`, `intel_lspcon_wait_pcon_mode()`, and `intel_lspcon_infoframes_enabled()` provide external state queries. Digital port hooks include `lspcon_write_infoframe()`, `lspcon_read_infoframe()`, `lspcon_set_infoframes()`, and `lspcon_infoframes_enabled()`. Internal helpers detect Parade/MegaChips OUIs, read/change LSPCON mode via dual-mode helpers, wake native AUX, and perform vendor-specific AVI infoframe writes.

Control flow: init wakes native AUX to infer expected mode, retries dual-mode adapter detection, waits for LS or PCON, forces PCON if needed, reads DPCD caps, detects vendor OUI, allows YCbCr420 on the connector, and marks the bridge active. AVI infoframe setup builds an HDMI AVI infoframe from the adjusted mode and connector state, adapts colorspace/quantization for RGB versus YCbCr444-to-420 conversion, packs it, and writes it through vendor-specific AUX sequences. MegaChips writes bytes to a DPCD window then kicks control bits; Parade writes four 8-byte blocks with firmware-ready polling. HDR/gamut metadata reuses HSW HDMI infoframe paths. Resume reinitializes inactive bridges, detects expected mode, applies a PCON resume workaround, waits for mode, and forces PCON if required.

State and persistence behavior: runtime state is in `dig_port->lspcon`: active flag, mode, vendor, and HDR support. Hardware state lives in the bridge's DPCD/I2C-controlled mode and infoframe registers and in i915 DIP registers for HDR metadata. No filesystem persistence exists.

Dependencies and integration points: depends on DRM DP dual-mode helpers, DP DPCD/AUX, HDMI infoframe helpers, EDID connector state, Intel DP and HDMI code, digital port hook tables, and HSW infoframe register helpers.

Risks: vendor-specific protocols have different timeouts and control bits; Parade firmware can be slow to accept blocks. Mode settling differs by vendor, with Parade using an 800 ms timeout. Native AUX wake behavior determines expected LS/PCON mode, so resume failures can leave descriptor mismatches. AVI readback is not implemented, so state verification is partial. Color-space handling assumes LSPCON may downsample YCbCr444 pipe output to YCbCr420.

Test signals: detection of Parade and MegaChips LSPCONs, PCON mode switch and settle timing, HDR capability DPCD reads, AVI infoframe writes on both vendors, HDR metadata enable/readback, YCbCr420 output modes, suspend/resume PCON recovery, native AUX down/up behavior, and failure logs for slow firmware or invalid OUI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lspcon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lspcon.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lspcon.h

Purpose: declares the LSPCON bridge lifecycle, capability, resume, and infoframe hook interface.

Important APIs/types/functions: includes activation/probe helpers, HDR capability detection, PCON wait/resume helpers, infoframe write/read/set hooks, and enabled-infoframe query helpers.

Control flow: digital port setup uses init and hook functions; resume paths call `intel_lspcon_resume()`; HDMI state verification can query enabled infoframes.

State and persistence behavior: implementation stores runtime bridge state in `struct intel_lspcon` embedded in `struct intel_digital_port`.

Dependencies and integration points: connects DP, HDMI, connector state, and CRTC state code to the bridge-specific implementation.

Risks: hook callers must only use infoframe operations when the bridge is active and vendor was detected.

Test signals: build coverage, hook registration on LSPCON VBT ports, and resume/capability paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lspcon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lt_phy.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lt_phy.c

Purpose: implements Xe3LPD LT PHY PLL state calculation, programming, enable/disable sequencing, signal-level programming, hardware readout, state comparison, and PLL table verification for DP, eDP, HDMI, and TBT modes.

Important APIs/types/functions: exported functions include `intel_lt_phy_pll_calc_state()`, `intel_lt_phy_tbt_pll_calc_state()`, `intel_lt_phy_pll_enable()`, `intel_lt_phy_pll_disable()`, `intel_lt_phy_set_signal_levels()`, `intel_lt_phy_pll_readout_hw_state()`, `intel_lt_phy_tbt_pll_readout_hw_state()`, `intel_lt_phy_calc_port_clock()`, `intel_lt_phy_pll_compare_hw_state()`, `intel_lt_phy_dump_hw_state()`, `intel_lt_phy_calculate_hdmi_state()`, `intel_xe3plpd_pll_enable()`, `intel_xe3plpd_pll_disable()`, and `intel_lt_phy_verify_plls()`. Static table sets cover DP RBR/HBR/UHBR, eDP-specific rates, and common HDMI clocks.

Control flow: state calculation selects DP/eDP/HDMI tables from CRTC encoder type and desired port clock. DP/eDP usually copies precomputed table state, sets eDP config bits and SSC when panel/downspread allow it. HDMI first tries precomputed states and then computes PLL register values algorithmically from the requested clock. Enable begins a transaction by pausing PSR and taking `POWER_DOMAIN_DC_OFF`, resets lanes and MacCLK, programs clock mux/SSC, moves lanes through powerdown states, programs VDR PLL registers if config changed, performs P2P rate-update transactions, updates `DDI_CLK_VALFREQ`, waits for PLL acks and calibration pulse status, moves lanes active, enables the right TXs for lane count/reversal/Type-C pin assignment, then resumes PSR and drops DC-off. Disable reverses by resetting lanes, dropping PLL request and `DDI_CLK_VALFREQ`, gating clocks, asserting MacCLK reset, and ending the transaction.

State and persistence behavior: persistent runtime state is the DPLL hardware state's `ltpll` structure, live LT PHY VDR registers, port clock control registers, DDI clock value registers, lane power states, and transmitter settings. Readout reconstructs lane count, VDR config, and data registers when the PLL is enabled. TBT mode is treated specially and can compare as always compatible.

Dependencies and integration points: depends on CX0 PHY message-bus helpers, DDI buffer translation tables, DPLL manager state, Type-C mode/pin assignment helpers, HDMI FRL clock classification, panel SSC/DPCD data, PSR pause/resume, display power domains, `intel_de` MMIO, and LT PHY register definitions.

Risks: sequencing is high risk and hardware-timing-sensitive. P2P writes have retry/reset behavior and require DC-off. The file notes that many VDR values cannot be reliably read back after power gating, so comparisons only use selected config registers. HDMI PLL math uses fixed-point arithmetic with overflow and DCO search constraints. Lane ownership differs in DP-alt mode, and wrong transmitter masks can break lane mapping. TBT mode bypasses normal LT PHY disable/readout. Several warnings indicate hardware acks or calibration pulse timeouts.

Test signals: PLL table verification at init/debug time, DP/eDP link rates including UHBR and panel SSC, HDMI clocks including computed non-table clocks, Type-C DP-alt lane ownership and pin assignments, lane reversal, TBT alt mode paths, signal level programming per training lane, suspend/resume readout compare, PSR pause/resume around PHY programming, and timeout/warning coverage for message-bus and PLL ack failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lt_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lt_phy.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lt_phy.h

Purpose: declares the LT PHY PLL, clock, readout, compare, signal-level, and Xe3LPD wrapper interface.

Important APIs/types/functions: declarations cover PLL enable/disable, state calculation, TBT state calculation/readout, port clock calculation, signal level programming, hardware state dump/compare/readout, HDMI PLL calculation, Xe3LPD wrappers, and table verification.

Control flow: DPLL manager and encoder enable paths call calc/enable/disable/readout helpers; training code calls signal-level programming; state checker calls compare/dump.

State and persistence behavior: APIs operate on `struct intel_dpll_hw_state`, `struct intel_lt_phy_pll_state`, encoder state, and live PHY hardware.

Dependencies and integration points: connects LT PHY implementation to DPLL, DDI, CRTC state, and display initialization code.

Risks: callers must supply matching encoder/CRTC state and respect TBT versus non-TBT paths.

Test signals: build coverage and DPLL manager integration across DP/eDP/HDMI/TBT outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lt_phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lt_phy_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lt_phy_regs.h

Purpose: defines LT PHY timing constants, MAC/VDR/P2P message bus registers, TX control fields, port buffer control fields, and PLL internal register addresses used by `intel_lt_phy.c`.

Important APIs/types/functions: latency constants define wait budgets for message bus, MacCLK, calibration, reset, and powerdown transitions. `LT_PHY_TXY_CTL*` macros address TX swing/cursor/lane-enable registers. `LT_PHY_VDR_*` macros define VDR config, rate/mode encoding, register address/data slots, and rate update. `XE3PLPD_PORT_BUF_CTL5()` and `XE3PLPD_PORT_P2M_MSGBUS_STATUS_P2P()` map port/lane MMIO. PLL address macros and `PLL_REG_ADDR()` select PLL type offset.

Control flow: LT PHY code uses these constants for sequencing, message-bus writes, state readout, signal level programming, and PLL table construction.

State and persistence behavior: definitions only; state resides in hardware registers and DPLL state.

Dependencies and integration points: depends on register helper macros, XeLPDP/CX0 port indexing, and LT PHY hardware programming model.

Risks: wrong offsets, bit masks, or latency budgets directly cause PHY programming failures. Address macros must match table values and HDMI calculation output.

Test signals: register programming traces, PLL enable/disable timeout behavior, signal-level register writes, and table verification using defined VDR fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lt_phy_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lvds.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lvds.c

Purpose: implements integrated LVDS connector/encoder support for older Intel platforms, including panel discovery, fixed-mode selection, PPS preservation/programming, LVDS port enable/disable, mode validation/configuration, backlight integration, DMI quirks, and dual-link detection.

Important APIs/types/functions: `intel_lvds_init()` creates and initializes the LVDS connector/encoder. `intel_lvds_port_enabled()` reads LVDS enable and pipe selection. `intel_get_lvds_encoder()` and `intel_is_dual_link_lvds()` query LVDS presence/configuration. Encoder hooks include `intel_lvds_get_hw_state()`, `intel_lvds_get_config()`, `intel_pre_enable_lvds()`, `intel_enable_lvds()`, `gmch_disable_lvds()`, `pch_disable_lvds()`, `pch_post_disable_lvds()`, `intel_lvds_shutdown()`, and `intel_lvds_compute_config()`. Connector hooks include `intel_lvds_get_modes()` and `intel_lvds_mode_valid()`.

Control flow: init rejects known false-LVDS DMI systems, checks VBT internal LVDS support, selects `LVDS` or `PCH_LVDS`, checks PCH detect bits and VBT/DDC pin presence, allocates connector/encoder objects, wires hooks, reads PPS and initial LVDS register state, then discovers the fixed mode by EDID, VBT LFP mode, or live encoder state. If no fixed mode exists, it cleans up and disables LVDS. Compute config enforces pipe restrictions, PCH encoder state, link bpp limits, LVDS 18/24 bpp, RGB formats, fixed panel timing, and panel fitter state. Enable programs preserved PPS and LVDS bits before powering the panel and backlight; disable powers down backlight/panel with GMCH versus PCH split sequencing.

State and persistence behavior: runtime state is stored in `struct intel_lvds_encoder`: dual-link flag, LVDS register address, A3 power bits, initial PPS snapshot, initial LVDS register value, and attached connector. Connector panel state stores fixed modes, VBT data, EDID, and backlight state. Hardware state persists in LVDS and panel power sequencing registers.

Dependencies and integration points: depends on DRM connector/encoder helpers, EDID/DDC including VGA switcheroo DDC, VBT panel data, DMI tables, GMBUS, panel/backlight helpers, panel fitter, FDI/link bandwidth helpers, DPLL assertions, PPS registers, and LVDS register definitions.

Risks: many systems falsely report LVDS, so DMI/VBT filtering is essential. Failure to preserve PPS and LVDS power bits can break panel power sequencing. Dual-link detection uses module params, fixed-mode clock, DMI quirks, BIOS/VBT register values, and can be wrong when BIOS leaves registers uninitialized. Gen2/3/4 have special pipe, dither, and fitter constraints. Cleanup on failed init must unwind partially registered DRM objects.

Test signals: LVDS panel detection by EDID, VBT, and live register fallback; false-LVDS DMI systems; dual-link quirks and `lvds_channel_mode`; PCH split versus GMCH enable/disable ordering; PPS timing preservation/defaults; fixed mode validation and panel fitter behavior; backlight enable/disable; suspend/resume readout; and no-mode failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lvds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lvds.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lvds.h

Purpose: declares LVDS support APIs and provides non-i915 stubs.

Important APIs/types/functions: exposes `intel_lvds_port_enabled()`, `intel_lvds_init()`, `intel_get_lvds_encoder()`, and `intel_is_dual_link_lvds()` when `I915` is defined, with false/null/no-op stubs otherwise.

Control flow: display initialization calls LVDS init; hardware readout and platform code query LVDS encoder and dual-link state.

State and persistence behavior: implementation state lives in the LVDS encoder and hardware registers.

Dependencies and integration points: integrates LVDS code with display initialization, encoder queries, and register readout while allowing stubs in non-i915 build contexts.

Risks: callers must handle absent LVDS and stub return values.

Test signals: build coverage with and without `I915`, LVDS init on supported platforms, and dual-link query users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lvds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lvds_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lvds_regs.h

Purpose: defines LVDS port control registers and bitfields for integrated and PCH LVDS.

Important APIs/types/functions: `LVDS` and `PCH_LVDS` MMIO addresses; `LVDS_PORT_EN`; pipe select fields for old and CPT/PCH platforms; dither, sync polarity, border, A0-A3/CLKB/B0-B3 power fields; and `LVDS_DETECTED`.

Control flow: LVDS code reads these fields for discovery/readout and writes them during pre-enable and disable.

State and persistence behavior: definitions only; state is in hardware LVDS registers.

Dependencies and integration points: depends on i915 register macros and is consumed by LVDS encoder code and related display readout.

Risks: LVDS port enable must be set before DPLL enable because DPLL semantics change when LVDS is assigned to a pipe. Pipe select masks differ between CPT and older platforms.

Test signals: readout of pipe selection and enable bits, pre-enable programming for single/dual link and sync polarity, and PCH detect bit handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_lvds_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_mg_phy_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_mg_phy_regs.h

Purpose: defines MG PHY register address macros and bitfields for Type-C PHY transmitters, DP mode, clock hub, DFLEX/FIA lane mapping, reference clock, PLL divider, loop filter, fractional lock, SSC, bias, and TDC controls.

Important APIs/types/functions: `MG_PHY_PORT_LN()` builds lane/port MMIO addresses. TX macros cover link params, PISO readload, swing control, driver control, DCC, and clock hub for TX1/TX2 lanes. DP mode macros define x1/x2 modes. FIA/DFLEX macros expose lane mapping registers. PLL macros define refclk, core clock, high-speed clock, divider, LF, FRAC_LOCK, SSC, BIAS, and TDC fields.

Control flow: other PHY/DPLL code includes this header to compute MMIO register addresses and bitfield values for MG PHY programming and readout.

State and persistence behavior: definitions only. Hardware register contents are persistent runtime device state controlled by consumers of the header.

Dependencies and integration points: depends on display register helper macros and Type-C port numbering. Integrates with MG PHY PLL and signal-level code outside this subset.

Risks: register formulas span multiple Type-C ports and lanes; wrong base offsets or lane increments can program the wrong transmitter. Several fields use raw shifts rather than `REG_FIELD_PREP`, so caller values must already fit. The header is shared hardware contract material with little runtime validation.

Test signals: MG PHY register programming traces, Type-C lane mapping validation, DP x1/x2 mode changes, PLL lock/readout across ports, and signal-level updates on each TX/lane combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_mg_phy_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_modeset_lock.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_modeset_lock.c

Purpose: implements a compact retry helper around DRM modeset acquire contexts and `-EDEADLK` backoff for i915 modeset locking blocks.

Important APIs/types/functions: `_intel_modeset_lock_begin()` initializes a `drm_modeset_acquire_ctx`, optionally attaches it to an Intel atomic state, and seeds the loop return value with `-EDEADLK`. `_intel_modeset_lock_loop()` turns an `-EDEADLK` marker into another loop iteration. `_intel_modeset_lock_end()` handles real `-EDEADLK` backoff, clears atomic state when needed, drops locks, and finalizes the acquire context.

Control flow: the macro in the header creates a `for` loop. Begin initializes context and sets the first iteration. User code attempts lock-taking work inside the loop and must use `continue` on error. End either backs off and repeats on deadlock or drops/finalizes locks when complete.

State and persistence behavior: state is transient in `drm_modeset_acquire_ctx`, the optional atomic state's acquire context pointer, and the caller's return code. No persistent storage exists.

Dependencies and integration points: wraps DRM modeset locking and optional DRM atomic state clearing for i915 call sites that need deadlock-retry loops.

Risks: the header warning is important: `break` or `return` inside the loop can bypass `_intel_modeset_lock_end()` and leak locks/context. Clearing atomic state on deadlock is required to retry with a clean state. Mismanaging `ret` can suppress needed backoff.

Test signals: lockdep and deadlock-injection tests, atomic paths using retry loops, early error handling using `continue`, and absence of leaked acquire contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_modeset_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_modeset_lock.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_modeset_lock.h

Purpose: declares the modeset lock retry helpers and defines the `intel_modeset_lock_ctx_retry()` loop macro.

Important APIs/types/functions: prototypes for `_intel_modeset_lock_begin()`, `_intel_modeset_lock_loop()`, `_intel_modeset_lock_end()`, and the macro that wraps them into a structured retry block.

Control flow: callers write a retry loop that initializes an acquire context, runs lock-taking work, and lets the end helper perform DRM backoff on `-EDEADLK`.

State and persistence behavior: no header state; implementation operates on acquire contexts, optional Intel atomic state, and caller `ret`.

Dependencies and integration points: used by modeset and atomic code needing DRM deadlock avoidance.

Risks: the macro contract requires `continue` for errors inside the block. Returning or breaking can skip cleanup.

Test signals: compile coverage and deadlock retry behavior under DRM modeset lock contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_modeset_lock.h -->
