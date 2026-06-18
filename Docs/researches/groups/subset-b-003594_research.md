# Research: subset-b-003594

Grouped research for `subset-b-003594`. Each section preserves the source path in its title and is intended to be split into the mapped source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fbc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fbc.c

Purpose: implements i915 Frame Buffer Compression management. It chooses per-platform FBC programming hooks, allocates compressed frame buffer storage from stolen memory, validates whether a primary plane state can be compressed, coordinates FBC disable/reenable around atomic plane updates, responds to frontbuffer writes, disables FBC after FIFO underruns, supports dirty-rect updates on newer hardware, and exposes debugfs status/false-color controls.

Important APIs/types/functions: private `struct intel_fbc`, `struct intel_fbc_state`, and `struct intel_fbc_funcs` hold runtime state and hardware hooks. Public entry points include `intel_fbc_init()`, `intel_fbc_cleanup()`, `intel_fbc_sanitize()`, `intel_fbc_atomic_check()`, `intel_fbc_update()`, `intel_fbc_disable()`, `intel_fbc_pre_update()`, `intel_fbc_post_update()`, `intel_fbc_invalidate()`, `intel_fbc_flush()`, `intel_fbc_handle_fifo_underrun_irq()`, `intel_fbc_reset_underrun()`, `intel_fbc_prepare_dirty_rect()`, `intel_fbc_dirty_rect_update_noarm()`, `intel_fbc_min_cdclk()`, and debugfs registration helpers. Platform hook tables cover i8xx, i965, g4x, ILK, SNB, and IVB+ register programming.

Control flow: initialization sanitizes `enable_fbc`, creates one `intel_fbc` per runtime FBC bit, allocates stolen-node descriptors, selects function tables, initializes locks/work, and resets system-cache ownership. Atomic check annotates each plane with `no_fbc_reason` after checking module params, stolen memory, vGPU/VT-d, workarounds, mode properties, PSR/selective update conflicts, format, tiling, rotation, stride, alpha, size, Y alignment, fence availability, CFB size, and CDCLK limits. Update either preserves existing active state, disables when the state becomes invalid, or allocates/programs CFB storage and workarounds for a newly eligible plane. Pre-update disables FBC unless the change can be handled by a flip nuke; post-update clears pending bits and activates. Frontbuffer invalidate/flush stop compression during CPU/GPU writes and restart or nuke when writes finish. Underrun IRQs schedule work that disables FBC until reset.

State and persistence: persistent state lives in `display->fbc.instances[]`, per-FBC mutex-protected fields (`state`, `busy_bits`, `active`, `activated`, `flip_pending`, `underrun_detected`, `no_fbc_reason`, `false_color`), stolen nodes for compressed FB/LLB, and shared `display->fbc.sys_cache`. Hardware state persists in FBC/DPFC registers until sanitize, disable, power reset, or reprogramming. `busy_bits` tracks outstanding frontbuffer writers; `underrun_detected` suppresses future enablement until explicitly cleared.

Dependencies and integration: integrates with i915 display atomic state, primary planes, frontbuffer tracking, DSB dirty-rect writes, stolen memory/GGTT fence helpers, runtime PM/debugfs, display workarounds, display version/platform feature flags, FIFO underrun handling, CDCLK limits, and register definitions in `intel_fbc_regs.h`.

Risks: stolen-memory allocation and compression-limit fallback can silently reduce power savings or fail FBC enablement. Register sequencing and platform workarounds are very generation-specific. Locking must keep `fbc->lock` outside stolen locks and avoid races between frontbuffer writes, flips, underrun work, and debugfs. Dirty-rect programming requires valid non-empty line ranges. Enabling FBC with unsupported PSR/selective update, bad Y alignment, invalid fences, or wrong stride can produce underruns, flicker, stale scanout, or corruption.

Test signals: exercise boot sanitize, suspend/resume, module-param toggling, debugfs status/false-color, atomic flips that can and cannot flip-nuke, CPU and GPU frontbuffer rendering, dirtyfb paths, stolen-memory exhaustion, tiled/linear modifiers, rotations, alpha formats, FP16 pixel-normalizer cases, PSR/selective-update combinations, FIFO underrun injection/reset, and IGT FBC tests verifying active/compressing state and no stale scanout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fbc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fbc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fbc.h

Purpose: declares the i915 FBC interface consumed by display atomic, plane, frontbuffer, FIFO underrun, dirty-rect, debugfs, and init/cleanup code. It hides the internal `struct intel_fbc` implementation while exposing lifecycle and update hooks.

Important APIs/types/functions: defines `enum intel_fbc_id` for FBC instances A-D and `I915_MAX_FBCS`. Declares `intel_fbc_atomic_check()`, `intel_fbc_min_cdclk()`, `intel_fbc_pre_update()`, `intel_fbc_post_update()`, `intel_fbc_update()`, `intel_fbc_disable()`, `intel_fbc_init()`, `intel_fbc_cleanup()`, `intel_fbc_sanitize()`, frontbuffer callbacks, underrun handlers, debugfs helpers, dirty-rect helpers, `intel_fbc_add_plane()`, and `intel_fbc_need_pixel_normalizer()`.

Control flow: no executable code is defined here; the header documents the call surface. Atomic modeset code calls check/pre/update/post/disable hooks, frontbuffer code calls invalidate/flush, underrun IRQ code calls handler/reset/read-debug helpers, and plane setup links planes to FBC instances.

State and persistence: declares opaque state only. Persistent data is owned by `intel_fbc.c` and `struct intel_display`.

Dependencies and integration: forward-declares i915 display types and `enum fb_op_origin`; consumers include display core, frontbuffer tracking, CRTC debugfs, FIFO underrun, and plane initialization.

Risks: the interface has ordering assumptions not encoded in the header: atomic check must precede update, pre/post update bracket plane register changes, and underrun handling may asynchronously disable active FBC. Misusing these hooks can leave stale compression state or lost frontbuffer invalidations.

Test signals: build coverage with FBC enabled/disabled in config and module params; modeset paths should link against all declared hooks and exercise check/pre/post/update ordering through atomic display tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fbc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fbc_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fbc_regs.h

Purpose: defines MMIO register offsets and bitfields for legacy FBC, DPFC, FBC render-state nuke, dirty-rect, underrun debug, stride override, and Xe3p system-cache usage.

Important APIs/types/functions: contains register macros such as `FBC_CONTROL`, `FBC_STATUS`, `FBC_CFB_BASE`, `FBC_LL_BASE`, `FBC_TAG()`, `DPFC_CONTROL`, `ILK_DPFC_CONTROL()`, `ILK_DPFC_CB_BASE()`, `GLK_FBC_STRIDE()`, `XE3_FBC_DIRTY_RECT()`, `XE3_FBC_DIRTY_CTL()`, `FBC_DEBUG_STATUS()`, `SNB_DPFC_CTL_SA`, `MSG_FBC_REND_STATE()`, and `XE3P_LPD_FBC_SYS_CACHE_USAGE_CFG`, plus field helpers for enable bits, compression status, plane/fence selection, compression ratio limits, dirty line ranges, and cache ranges.

Control flow: no runtime flow exists in the header. `intel_fbc.c` uses these constants to program CFB bases, activate/deactivate compression, nuke compression state, select planes/fences, enable dirty-rect tracking, apply workarounds, inspect underrun status, and configure system cache.

State and persistence: the header itself has no state; it describes persistent hardware MMIO state that survives until explicitly reprogrammed or reset.

Dependencies and integration: depends on `intel_display_reg_defs.h` for `_MMIO`, `_MMIO_PIPE`, and `REG_*` helpers. The macros are tightly coupled to the per-generation function tables in `intel_fbc.c`.

Risks: bitfield mistakes can corrupt display registers, select the wrong plane/fence, allocate CFB outside accessible stolen ranges, or leave FBC active during unsafe updates. Some field names overlap across generations, so callers must use the right macro for the active platform.

Test signals: compile all platform variants, inspect register writes with debug logs or MMIO tracing during FBC enable/disable, and run underrun/dirty-rect/system-cache paths on hardware that advertises those feature bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fbc_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fbdev.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fbdev.c

Purpose: implements i915 fbdev emulation setup, including BIOS framebuffer reuse, fallback fb allocation, GGTT pinning, fb_info population, deferred I/O operations, mmap support, suspend handling, and frontbuffer invalidation for fbcon writes.

Important APIs/types/functions: private `struct intel_fbdev` stores the selected `intel_framebuffer`, pinned `i915_vma`, and pin flags. Key functions are `intel_fbdev_setup()`, `intel_fbdev_driver_fbdev_probe()`, `intel_fbdev_framebuffer()`, `intel_fbdev_vma_pointer()`, `intel_fbdev_get_map()`, `intel_fbdev_init_bios()`, `__intel_fbdev_fb_alloc()`, fb_ops wrappers for set_par/blank/pan/mmap/destroy, and helper callbacks `intelfb_dirty()`, `intelfb_restore()`, and `intelfb_set_suspend()`.

Control flow: setup allocates `intel_fbdev`, attempts to reuse the largest active BIOS framebuffer if it can satisfy all active pipes, picks preferred bpp, and calls DRM client setup. Probe validates or allocates the framebuffer, pins it into the GGTT for CPU-visible `screen_base`, fills `fb_info`, clears non-shmem allocations when needed, and records VMA state. fb_ops delegate to DRM fb helper operations then invalidate frontbuffer state so FBC/PSR/DRRS can react. Destroy finalizes fb helper, unpins the VMA, removes the framebuffer, and releases the DRM client.

State and persistence: `display->fbdev.fbdev` persists for device lifetime through drmm allocation. The framebuffer object, VMA pin, `info->screen_base`, and `info->screen_size` persist while fbdev is registered. BIOS fb reuse holds an extra framebuffer reference. Suspend state is propagated to fb_info, and stolen/lmem contents may be cleared on resume/allocation.

Dependencies and integration: integrates with DRM fb helper/client setup, i915 framebuffer creation, GEM object helpers, GGTT pinning, frontbuffer tracking, runtime PM, fbdev deferred I/O, console/sysrq infrastructure, and `intel_fbdev_fb.c` allocation/mapping helpers.

Risks: BIOS framebuffer reuse must verify pitch/size across all active CRTCs or fbcon can draw outside valid memory. Error paths around VMA pinning and `screen_base` mapping are delicate; comments intentionally rely on object-free/unpin cleanup. Stolen memory can contain garbage after hibernation. Missing invalidation after fbdev writes can leave FBC/PSR displaying stale contents.

Test signals: boot with firmware fb takeover, multi-pipe BIOS configurations, forced new fb allocation, fbcon text and pan/blank operations, fbdev mmap writes, suspend/hibernate resume, stolen/lmem/shmem allocations, remove/unbind cleanup, and DRM fbdev emulation disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fbdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fbdev.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fbdev.h

Purpose: declares the i915 fbdev emulation interface and provides no-op stubs when `CONFIG_DRM_FBDEV_EMULATION` is disabled.

Important APIs/types/functions: exposes `INTEL_FBDEV_DRIVER_OPS`, `intel_fbdev_driver_fbdev_probe()`, `intel_fbdev_setup()`, `intel_fbdev_framebuffer()`, `intel_fbdev_vma_pointer()`, and `intel_fbdev_get_map()` under fbdev emulation. The disabled path maps driver ops to `.fbdev_probe = NULL` and returns harmless defaults.

Control flow: no runtime flow beyond inline stubs. Driver registration uses `INTEL_FBDEV_DRIVER_OPS`; display initialization calls `intel_fbdev_setup()` only if the feature is compiled in.

State and persistence: no state is defined here. Opaque `struct intel_fbdev` state is owned by `intel_fbdev.c`.

Dependencies and integration: forward-declares DRM fb helper, i915 display/framebuffer, and `iosys_map` types. It is consumed by driver setup, display code, and callers that need the fbdev framebuffer/VMA mapping.

Risks: call sites must tolerate NULL framebuffer/VMA when fbdev is disabled or setup failed. The macro-based driver op must stay synchronized with DRM helper expectations.

Test signals: compile with and without `CONFIG_DRM_FBDEV_EMULATION`; verify non-fbdev builds link cleanly and fbdev-enabled builds register the probe callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fbdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fbdev_fb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fbdev_fb.c

Purpose: provides fbdev backing-object allocation and fb_info mapping helpers shared by i915 fbdev setup.

Important APIs/types/functions: `intel_fbdev_fb_pitch_align()` aligns pitches to 64 bytes. `intel_fbdev_fb_prefer_stolen()` decides whether stolen memory is acceptable, skipping Meteor Lake and requiring at least twice the requested size. `intel_fbdev_fb_bo_create()` allocates lmem, stolen, or shmem GEM backing. `intel_fbdev_fb_bo_destroy()` drops the GEM object. `intel_fbdev_fb_fill_info()` fills fb_info physical aperture fields and pins an iomap for `screen_base`.

Control flow: allocation prefers contiguous user lmem on discrete GPUs; otherwise it tries stolen memory only when policy allows and falls back to shmem. Fill-info computes `fix.smem_start` from lmem IO aperture or GGTT gmadr+VMA offset, locks the object with a ww context, pins an iomap, and stores screen base/size.

State and persistence: the GEM object persists through fbdev lifetime. `info->fix.smem_*`, `info->screen_base`, and `info->screen_size` persist in fb_info until fbdev teardown. The iomap pin persists until the VMA/object cleanup path unpins it.

Dependencies and integration: depends on GEM lmem/stolen/shmem allocation, GGTT offsets, memory-region IO ranges, VMA iomap pinning, ww locking, and DRM fbdev code in `intel_fbdev.c`.

Risks: wrong smem_start calculation breaks fbdev mmap/console access. Stolen preference competes with features such as FBC. Mapping failures must propagate cleanly. Meteor Lake stolen avoidance is a workaround-sensitive policy.

Test signals: allocate fbdev on integrated, discrete/lmem, and low-stolen systems; validate fb_info mmap/write behavior, fallback from stolen to shmem, iomap pin failures, and object cleanup without leaked pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fbdev_fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fbdev_fb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fbdev_fb.h

Purpose: declares fbdev framebuffer allocation, destruction, pitch alignment, policy, and fb_info filling helpers.

Important APIs/types/functions: `intel_fbdev_fb_pitch_align()`, `intel_fbdev_fb_bo_create()`, `intel_fbdev_fb_bo_destroy()`, `intel_fbdev_fb_fill_info()`, and `intel_fbdev_fb_prefer_stolen()`.

Control flow: no executable code; the header separates low-level backing-object concerns from the main fbdev helper implementation.

State and persistence: no state is owned by the header. The declared functions populate GEM object and fb_info state.

Dependencies and integration: forward-declares DRM device/GEM, fb_info, and i915 VMA types. Used by `intel_fbdev.c`.

Risks: callers must pass a pinned/valid VMA to fill-info and must destroy objects only after failed framebuffer creation or final teardown.

Test signals: compile coverage and fbdev allocation tests that verify each declared helper is available under fbdev emulation builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fbdev_fb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fdi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fdi.c

Purpose: implements FDI link bandwidth calculation, atomic validation, PLL control, link training, enable-state assertions, and disable sequencing for pre-DDI PCH display links and Haswell FDI-over-DDI mode.

Important APIs/types/functions: private `struct intel_fdi_funcs` selects platform link-training hooks. Public functions include `intel_fdi_init_hook()`, `intel_fdi_link_train()`, `intel_fdi_add_affected_crtcs()`, `intel_fdi_pll_freq_update()`, `intel_fdi_link_freq()`, `ilk_fdi_compute_config()`, `intel_fdi_atomic_check_link()`, `intel_fdi_normal_train()`, `ilk_fdi_pll_enable()`, `ilk_fdi_pll_disable()`, `ilk_fdi_disable()`, `hsw_fdi_link_train()`, `hsw_fdi_disable()`, and assertion helpers for TX/RX/PLL state.

Control flow: mode computation derives required FDI lanes from adjusted dotclock, link frequency, and pipe bpp, then computes M/N values. Atomic bandwidth checks enforce lane limits: max four lanes generally, Haswell/Broadwell two lanes, and Ivy Bridge pipe B/C sharing rules, with fallback through bpp reduction and `-EAGAIN`. Training sequences program TU size, unmask lock interrupts, enable TX/RX in pattern 1, poll bit lock, switch to pattern 2, poll symbol lock, then switch to normal training. Haswell trains DDI E with PCH RX and SPLL, iterating voltage/emphasis entries. Disable paths turn off TX/RX, DDI buffers, clocks, PLLs, PCDCLK, and reset training patterns.

State and persistence: persistent fields include `display->funcs.fdi`, `display->fdi.pll_freq`, `display->fdi.rx_config`, and per-CRTC `fdi_lanes`/`fdi_m_n`. Hardware FDI TX/RX/PLL/training/bifurcation state persists in MMIO registers until reprogrammed.

Dependencies and integration: depends on intel atomic state, CRTC state, link bandwidth reduction, DP M/N helpers, DDI buffer/clock helpers, display register access, PCH type/platform checks, and register definitions in `intel_fdi_regs.h`.

Risks: FDI training is timing-sensitive and platform-specific. Shared Ivy Bridge lane bifurcation can require modesetting an otherwise unchanged pipe. Continuing after training failure may preserve state checker expectations but can leave a blank output. PLL and PCDCLK sequencing errors can hang or corrupt PCH output. Assertions differ for DDI platforms where TX state is represented through transcoder/DDI registers.

Test signals: test Ironlake, Sandy Bridge, Ivy Bridge 3-pipe sharing, Haswell/Broadwell PCH connectors, bpp fallback under high bandwidth, link training failure logs, hotplug/modeset cycles, PLL enable/disable sequencing, and state checker assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fdi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fdi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fdi.h

Purpose: declares the FDI programming interface used by modeset, DDI/PCH encoder, state checker, and atomic bandwidth code.

Important APIs/types/functions: exposes lane/bandwidth helpers (`intel_fdi_add_affected_crtcs()`, `intel_fdi_link_freq()`, `ilk_fdi_compute_config()`, `intel_fdi_atomic_check_link()`), training and normal-mode helpers (`intel_fdi_link_train()`, `intel_fdi_normal_train()`, `hsw_fdi_link_train()`), disable/PLL helpers, initialization/frequency update hooks, and assertion helpers for TX/RX/PLL states.

Control flow: no executable flow; the header defines the legal call surface for FDI-capable platforms.

State and persistence: no storage is defined. State lives in `struct intel_display`, `struct intel_crtc_state`, and hardware registers.

Dependencies and integration: forward-declares display atomic, CRTC, encoder, and link-bandwidth types. Used by PCH encoder code, modeset compute/check paths, and state verification.

Risks: platform code must call the right sequence: compute config, atomic link check, PLL enable, train, normal mode, and disable. The header cannot enforce generation restrictions.

Test signals: compile all FDI and non-FDI platform paths; state checker tests should call assertion helpers around enable/disable transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fdi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fdi_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fdi_regs.h

Purpose: defines MMIO registers and bitfields for FDI PLL, TX control, RX control, RX misc, TU size, and RX interrupt status/mask registers.

Important APIs/types/functions: includes `FDI_PLL_BIOS_*`, `FDI_PLL_FREQ_CTL`, `FDI_TX_CTL()`, `FDI_RX_CTL()`, `FDI_RX_MISC()`, `FDI_RX_TUSIZE1/2()`, `FDI_RX_IIR()`, `FDI_RX_IMR()`, and bitfields for enable, link-training patterns, voltage/pre-emphasis presets, port width, PLL enable, enhanced framing, composite sync, auto training, PCDCLK, BPC, lane powerdown, delay, and lock/error interrupts.

Control flow: no executable code. `intel_fdi.c` uses these definitions to compute PLL frequency, train links, poll bit/symbol lock, control RX/TX/PLL state, and report errors.

State and persistence: the header has no software state; it maps hardware register state retained by the display engine/PCH.

Dependencies and integration: depends on `intel_display_reg_defs.h`. The bit encodings are coupled to platform branches for ILK, SNB, IVB, CPT/PCH, and Haswell FDI-over-DDI paths.

Risks: FDI bit definitions include generation-specific encodings, especially IVB training bits and CPT RX patterns. Mixing them can train the wrong pattern or leave PLLs enabled. Register offsets are pipe-indexed and must match fixed pipe/PCH transcoder mappings.

Test signals: MMIO trace FDI training on supported hardware, verify lock bits and error bits are interpreted correctly, and compile state checker/enable paths for ILK/SNB/IVB/HSW.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fdi_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fifo_underrun.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fifo_underrun.c

Purpose: manages CPU pipe and PCH transcoder FIFO underrun reporting, logging, debug-register collection, immediate polling, and interrupt masking to avoid repeated underrun storms.

Important APIs/types/functions: public functions are `intel_init_fifo_underrun_reporting()`, `intel_set_cpu_fifo_underrun_reporting()`, `intel_set_pch_fifo_underrun_reporting()`, `intel_cpu_fifo_underrun_irq_handler()`, `intel_pch_fifo_underrun_irq_handler()`, `intel_check_cpu_fifo_underruns()`, and `intel_check_pch_fifo_underruns()`. Internal helpers handle underrun debug registers, GMCH PIPESTAT, ILK display IRQ bits, IVB `GEN7_ERR_INT`, BDW pipe IRQs, IBX/CPT south display interrupts, and shared interrupt enable policy.

Control flow: enabling reporting clears stale debug info where needed and unmasks the platform interrupt. IRQ handlers disable further reporting for the affected pipe/transcoder, log once, read and clear debug info, and notify FBC that underruns occurred. Polling paths check latch bits on platforms where interrupts are shared or absent. PCH reporting stores state in pipe-mapped CRTC fields, with special handling for LPT's single PCH transcoder.

State and persistence: per-CRTC `cpu_fifo_underrun_disabled` and `pch_fifo_underrun_disabled` persist across modesets until reinitialized or toggled. Debug status bits are hardware-latched and cleared by write. Interrupt mask state persists in display/PCH interrupt registers.

Dependencies and integration: integrates with `display->irq.lock`, intel display IRQ helpers, PCH display interrupt helpers, FBC underrun handling, tracepoints, pipe/transcoder helpers, and underrun debug register definitions in broader display regs.

Risks: several platforms have shared underrun interrupt enables, so disabling one pipe can suppress others. Debug bits can be stale unless cleared before reenable. IRQ handlers may run early during init. Missing FBC notification can leave FBC active after dangerous underruns.

Test signals: inject underruns on GMCH, ILK/SNB, IVB, BDW+, IBX, and CPT paths; verify one-shot logging, interrupt masking/unmasking around modesets, debug info clearing/logging, FBC disable response, and no interrupt storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fifo_underrun.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fifo_underrun.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fifo_underrun.h

Purpose: declares the i915 FIFO underrun reporting and IRQ handling interface.

Important APIs/types/functions: exposes initialization, CPU/PCH reporting toggles, CPU/PCH IRQ handlers, and immediate CPU/PCH underrun check helpers.

Control flow: no executable code; modeset code uses the toggles to suppress expected underruns and IRQ code uses the handlers for real underruns.

State and persistence: no state in the header; state lives in CRTC flags and hardware interrupt/debug registers.

Dependencies and integration: forward-declares `enum pipe`, `struct intel_crtc`, and `struct intel_display`. Used by display IRQ and modeset code.

Risks: callers must pass CPU pipe vs PCH transcoder consistently. Enabling reporting too early or disabling it without later restoration can hide real watermark failures.

Test signals: compile coverage and modeset/IRQ tests that verify all declared paths are reachable on relevant platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fifo_underrun.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fixed.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fixed.h

Purpose: provides small unsigned 16.16 fixed-point arithmetic helpers for i915 display calculations.

Important APIs/types/functions: defines `uint_fixed_16_16_t`, `FP_16_16_MAX`, and inline helpers for zero tests, `u32` conversion, rounded conversion to `u32`, min/max, clamping, division, multiplication, addition, and round-up variants (`mul_round_up_u32_fixed16()`, `mul_fixed16()`, `div_fixed16()`, `div_round_up_u32_fixed16()`, `mul_u32_fixed16()`, `add_fixed16()`).

Control flow: all helpers are inline arithmetic operations using 64-bit intermediates and `WARN_ON()` overflow checks before narrowing to 32 bits.

State and persistence: no persistent state. Values are passed by value in the fixed-point wrapper.

Dependencies and integration: depends on kernel math helpers (`DIV_ROUND_UP`, `DIV_ROUND_UP_ULL`, `mul_u32_u32`) and bug/warn infrastructure. Intended for display code needing deterministic fractional arithmetic without floating point.

Risks: `u32_to_fixed16()` warns if the integer exceeds 16 bits; callers must avoid zero divisors; `mul_u32_fixed16()` intentionally returns a fixed-point scaled product rather than a rounded integer. Overflow warnings do not prevent truncated results after clamping.

Test signals: unit-style arithmetic checks for conversion, rounding, overflow boundaries, min/max, multiplication/division identities, and divide-by-zero avoidance in callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fixed.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_flipq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_flipq.c

Purpose: implements DMC firmware flip queues, allowing i915 to enqueue DSB command buffers for execution at presentation timestamps on supported platforms.

Important APIs/types/functions: public functions include `intel_flipq_supported()`, `intel_flipq_init()`, `intel_flipq_reset()`, `intel_flipq_enable()`, `intel_flipq_disable()`, `intel_flipq_add()`, `intel_flipq_exec_time_us()`, `intel_flipq_wait_dmc_halt()`, `intel_flipq_unhalt_dmc()`, and `intel_flipq_dump()`. Internal helpers compute queue offsets/sizes, entry sizes, execution time, preempt timeout, current head, tail writes, DMC wake, and Lunar Lake/Panther Lake queue-entry formats.

Control flow: init waits for DMC firmware and records per-CRTC queue MMIO starts. Enable programs scanline compare windows before vblank, enables the relevant pipe DMC event, and turns on queue control. Add checks ring space, converts relative PTS to DMC timestamp domain, preempts the queue, writes one entry in the per-platform format, advances software tail, atomically updates all hardware tail pointers, unpreempts, and wakes DMC. Disable preempts, disables control/event, and clears scanline compares. Reset clears hardware head/tail pointers and software tails.

State and persistence: each `intel_crtc` stores `flipq[]` metadata including `start_mmioaddr`, `flipq_id`, and software `tail`. Hardware queue RAM, head/tail pointers, timestamp, scanline compares, and DMC event enables persist until reset/disable. Supported state depends on module param, DMC firmware, display version, and VRR timing generator policy.

Dependencies and integration: integrates with pipe DMC firmware/registers, DSB command buffers, CRTC state/mode timing, CDCLK/SAGV timing, VRR policy, display workarounds, and MMIO helpers.

Risks: queue overflow detection depends on synchronized head/tail state. Incorrect execution-time estimates can schedule too close to vblank. Platform entry layouts differ between LNL and PTL. Preempt timeouts indicate DMC did not halt in time. Feature support depends on firmware and VRR timing-generator assumptions.

Test signals: run on supported display versions with DMC loaded, enqueue plane/general DSB updates, exercise reset/enable/disable, queue overflow warnings, timestamp scheduling, VRR configurations, DMC preempt timeout injection, and debug dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_flipq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_flipq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_flipq.h

Purpose: declares the DMC flip-queue interface for display update scheduling.

Important APIs/types/functions: exposes support/init/reset, enable/disable, add, execution-time calculation, DMC halt/unhalt workaround helpers, and dump functions.

Control flow: no implementation here. Atomic/DSB code can query support, enable queues for a CRTC, enqueue DSB buffers with PTS, and disable/reset queues during modeset transitions.

State and persistence: no state in the header. Per-CRTC software tail and hardware queue state are managed by `intel_flipq.c`.

Dependencies and integration: forward-declares DSB IDs, flip queue IDs, pipe, CRTC, CRTC state, display, and DSB types. Used by DSB/modeset code on platforms with DMC flip queues.

Risks: callers must only enqueue when supported and enabled, and must use the correct queue ID/DSB pairing.

Test signals: compile with display versions that both support and do not support flip queues; modeset tests should verify no calls enqueue when unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_flipq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_frontbuffer.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_frontbuffer.c

Purpose: tracks which GEM frontbuffers are currently associated with scanout slots and dispatches invalidate/flush/flip notifications to display power-saving features such as PSR, FBC, DRRS, and TDF.

Important APIs/types/functions: implements `intel_frontbuffer_flip()`, `__intel_frontbuffer_invalidate()`, `__intel_frontbuffer_flush()`, `intel_frontbuffer_queue_flush()`, `intel_frontbuffer_init()`, `intel_frontbuffer_fini()`, and `intel_frontbuffer_track()`. Internal `frontbuffer_flush()` filters busy bits and calls subsystem flush hooks.

Control flow: rendering start invalidates frontbuffer bits, optionally marking them busy for command-stream origin. Rendering completion flushes only bits still busy for that render and clears them. Dirtyfb-origin flush also calls the parent display flush hook. Flip removes stale busy bits for the old buffer and immediately flushes with `ORIGIN_FLIP`. Queued flush takes a frontbuffer reference, schedules work, flushes dirtyfb, then drops the reference.

State and persistence: each `intel_frontbuffer` stores `display`, atomic `bits`, and a `flush_work`. Global `display->fb_tracking.busy_bits` tracks outstanding CS rendering under a spinlock. Bit ownership is guarded by plane mutexes but updated atomically for whole-object RMW.

Dependencies and integration: integrates with DRM GEM objects, i915 parent frontbuffer references, PSR, FBC, DRRS, TDF, tracepoints, and display tracking locks.

Risks: incorrect bit tracking can restart FBC/PSR while rendering is still in flight or fail to restart power-saving after rendering. Queued work must hold a reference. The bit layout assumes all pipe/plane bits fit in `atomic_t` and 32 bits.

Test signals: exercise CPU writes, GPU rendering, dirtyfb, cursor updates, flips, queued flush after fences, multi-plane/pipe tracking, frontbuffer finalization warnings, and PSR/FBC/DRRS reactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_frontbuffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_frontbuffer.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_frontbuffer.h

Purpose: defines frontbuffer tracking types, operation origins, bit layout, inline invalidate/flush wrappers, and public tracking lifecycle functions.

Important APIs/types/functions: `enum fb_op_origin` identifies CPU, command streamer, flip, dirtyfb, and cursor update origins. `struct intel_frontbuffer` stores display, atomic bitmask, and flush work. Macros define per-pipe frontbuffer slots: `INTEL_FRONTBUFFER_BITS_PER_PIPE`, `INTEL_FRONTBUFFER()`, `INTEL_FRONTBUFFER_OVERLAY()`, and `INTEL_FRONTBUFFER_ALL_MASK()`. Public functions include flip, invalidate/flush internals and wrappers, queue_flush, track, init, and fini.

Control flow: inline wrappers read the atomic bitmask, skip work when no slots are tracked, and dispatch to the non-inline implementations.

State and persistence: bitmask state persists while a GEM object is considered a frontbuffer. Work item state persists until queued flush completes.

Dependencies and integration: depends on Linux atomics/workqueue and is used by GEM/framebuffer/plane code and display power-saving subsystems.

Risks: macro bit allocation must remain large enough for all i915 planes/pipes. Callers must pass correct origin so CS busy filtering and flip/cursor exceptions work as intended.

Test signals: compile-time build bugs for bit capacity, runtime warnings on mismatched track/untrack, and rendering/flip tests that validate power-saving invalidation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_frontbuffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_global_state.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_global_state.c

Purpose: implements i915 display global atomic objects, allowing shared display state to participate in DRM atomic transactions with duplicate/destroy callbacks, locking, serialization, commit dependency tracking, swap, and cleanup.

Important APIs/types/functions: private `struct intel_global_objs_state` stores per-atomic-state object entries and `struct intel_global_commit` tracks serialized commit completion with kref/completion. Public functions include `intel_atomic_global_obj_init()`, `intel_atomic_global_obj_cleanup()`, `intel_atomic_get_global_obj_state()`, old/new getters, `intel_atomic_swap_global_state()`, `intel_atomic_clear_global_state()`, `intel_atomic_lock_global_state()`, `intel_atomic_serialize_global_state()`, `intel_atomic_global_state_is_serialized()`, `intel_atomic_global_state_setup_commit()`, `intel_atomic_global_state_wait_for_dependencies()`, and `intel_atomic_global_state_commit_done()`.

Control flow: fetching a global object state asserts at least one CRTC mutex is read-locked, grows the atomic state's global-object array, duplicates current object state, references old/new states, and attaches it to the transaction. Locking all CRTC mutexes marks the object changed; serialization also requests a completion-backed commit. Swap replaces the live object state only for changed objects after write-lock assertion. Setup carries old serialized commits or creates new ones; wait blocks on prior commit completions; commit_done completes serialized commits after hardware programming.

State and persistence: each `intel_global_obj` has a live `state` and list node in `display->global.obj_list`. Each `intel_global_state` carries kref, object pointer, owning atomic state, optional commit, and changed/serialized flags. Commit objects persist until all referenced old/new states drop them.

Dependencies and integration: depends on DRM modeset locking/acquire contexts, i915 atomic state, CRTC mutexes, kref/completion, and object-specific duplicate/destroy callbacks supplied by subsystem users.

Risks: global state correctness relies on broad CRTC locking for read/write safety. Forgetting to mark changed discards new state. Serialized objects can deadlock or timeout if commit_done is not called. Cleanup expects exactly one reference to live object state.

Test signals: atomic tests with global state read-only, changed, and serialized objects; lockdep for modeset locks; dependency timeout injection; cleanup reference warnings; and concurrent commits touching shared watermarks/bandwidth-like state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_global_state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_global_state.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_global_state.h

Purpose: declares the generic i915 display global atomic object/state framework.

Important APIs/types/functions: defines `struct intel_global_state_funcs` with duplicate/destroy callbacks, `struct intel_global_obj` with list node/live state/function table, and `struct intel_global_state` with object pointer, atomic-state owner, commit pointer, kref, and `changed`/`serialized` flags. Declares init/cleanup, state getters, swap/clear, lock/serialize, commit setup/done/wait, and serialization-status helpers.

Control flow: no executable flow except data-shape declaration; callers embed/derive these base structs in subsystem-specific global state.

State and persistence: the structs declared here form the persistent live state and per-transaction duplicated state used by `intel_global_state.c`.

Dependencies and integration: depends on kref/list infrastructure and i915 atomic/display types. Used by shared display resource managers.

Risks: subsystem states must implement duplicate/destroy correctly and preserve the base fields. Mismanaging `changed` or `serialized` flags breaks swap and dependency ordering.

Test signals: compile users of embedded global states, run atomic commits that mutate shared resources, and verify no leaked references during driver unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_global_state.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_gmbus.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_gmbus.c

Purpose: implements Intel GMBUS/DDC I2C adapters, including platform pin maps, hardware GMBUS transfers, GPIO bit-banging fallback, HDCP Aksv output, power-domain handling, bus locking, IRQ wakeups, and setup/teardown.

Important APIs/types/functions: private `struct intel_gmbus` embeds `i2c_adapter`, force-bit state, `reg0`, GPIO register, bit-bang algorithm data, and display pointer. Public functions include `intel_gmbus_setup()`, `intel_gmbus_teardown()`, `intel_gmbus_get_adapter()`, `intel_gmbus_is_valid_pin()`, `intel_gmbus_force_bit()`, `intel_gmbus_is_forced_bit()`, `intel_gmbus_reset()`, `intel_gmbus_output_aksv()`, and `intel_gmbus_irq_handler()`. Internal transfer helpers implement wait, idle wait, read/write chunks, index transfers, retry, stop cycles, error clearing, and pin GPIO operations.

Control flow: setup selects MMIO base, initializes mutex/waitqueue, creates one adapter per valid platform pin, wires hardware and bit-bang algorithms, and registers adapters. `gmbus_xfer()` takes the GMBUS power domain, uses bit-banging if forced or after prior timeout, otherwise runs hardware transfers. Hardware transfer programs GMBUS0, combines index messages when possible, handles chunked reads/writes and burst-read override, waits for ready/wait/idle, emits STOP, clears NAK/errors, retries first NAK once, and falls back to bit-banging with `-EAGAIN` on timeout. GPIO fallback resets GMBUS, handles clock-gating workarounds, sets open-drain lines, and preserves required mask/pull-up bits.

State and persistence: `display->gmbus.bus[]` stores adapters; each adapter persists until teardown. `force_bit` is a counter plus retry flag; `reg0` stores pin/rate. `display->gmbus.mutex`, waitqueue, and `mmio_base` persist for device lifetime. GMBUS controller and GPIO line state persist in MMIO registers across transfers until reset or reprogramming.

Dependencies and integration: integrates with Linux I2C core, i2c-algo-bit, DRM HDCP helper, i915 display power domains, IRQ enable state, display workarounds, PCH/platform pin maps, and `intel_gmbus_regs.h`.

Risks: GMBUS hardware only handles one interrupt-enable bit, so wait logic must poll NAKs. Returning `-ENXIO` too eagerly can suppress EDID retries; timeouts should fall back to bit-banging. Force-bit counter underflow is possible if callers unbalance requests. Pin maps vary by PCH/platform. Clock-gating and GPIO mask workarounds are transfer-critical.

Test signals: EDID/DDC reads across VGA/HDMI/DP/Type-C pins, long burst reads including 512-byte special case, indexed transfers, NAK and timeout injection, bit-bang fallback, HDCP Aksv write, adapter setup/teardown, IRQ wakeups, power-domain balance, and platform pin validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_gmbus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_gmbus.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_gmbus.h

Purpose: declares GMBUS pin identifiers and the public GMBUS adapter/control API.

Important APIs/types/functions: defines legacy and platform-specific pin constants such as `GMBUS_PIN_VGADDC`, `GMBUS_PIN_DPB`, `GMBUS_PIN_1_BXT`, Type-C pins, and `GMBUS_NUM_PINS`. Declares setup/teardown, valid-pin check, adapter lookup, forced bit-banging controls, controller reset, HDCP Aksv output, and IRQ handler.

Control flow: no executable code; display connector code uses pin constants to obtain adapters and DDC/HDCP code uses the exported transfer controls.

State and persistence: no state is defined here. Adapter arrays and force-bit state are owned by `intel_gmbus.c`.

Dependencies and integration: forward-declares `i2c_adapter` and `intel_display`; consumed by connector/DDC/HDCP/display setup code.

Risks: pin constants are reused differently across platform generations, so callers must use platform-appropriate pin assignments from VBT/connector setup.

Test signals: compile connector code using each pin family and verify invalid pins are rejected at runtime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_gmbus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_gmbus_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_gmbus_regs.h

Purpose: defines MMIO offsets and bitfields for Intel GPIO DDC pins and GMBUS controller registers.

Important APIs/types/functions: `GPIO(display, gpio)` maps GPIO line registers with clock/data direction/value/pull-up bits. `GMBUS0` selects pin, clock rate, Aksv source, hold time, and byte-count override. `GMBUS1` encodes commands, cycle type, byte count, slave index/address, read/write, software ready, and clear interrupt. `GMBUS2` exposes status bits such as active, SATOER/NAK, ready, wait phase, interrupt, and timeout. `GMBUS3` is data, `GMBUS4` interrupt enables, and `GMBUS5` 2-byte index support.

Control flow: no executable code. `intel_gmbus.c` uses these macros to implement hardware I2C transactions and GPIO bit-banging fallback.

State and persistence: the header holds no state; it describes hardware register state that persists across transfers until reset/clear.

Dependencies and integration: depends on `intel_display_reg_defs.h` and `display->gmbus.mmio_base`.

Risks: wrong byte-count limits, status bits, or command encodings can wedge the DDC bus or corrupt EDID/HDCP transactions. GPIO mask/value semantics are subtle because writes include direction/value mask bits.

Test signals: MMIO trace short/long reads, indexed writes, NAK/timeout clearing, STOP generation, byte-count override, and GPIO bit-bang line toggling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_gmbus_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_gvt_api.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_gvt_api.c

Purpose: exports a small namespace-scoped display-device API for GVT code to query i915 display MMIO offsets and valid pipe presence without reaching directly into display macros.

Important APIs/types/functions: exported GPL namespace functions are `intel_display_device_pipe_offset()`, `intel_display_device_trans_offset()`, `intel_display_device_cursor_offset()`, `intel_display_device_mmio_base()`, and `intel_display_device_pipe_valid()`.

Control flow: each offset function returns the corresponding `INTEL_DISPLAY_DEVICE_*` or `DISPLAY_MMIO_BASE` macro result. Pipe-valid first bounds-checks `pipe` against `PIPE_A` and `I915_MAX_PIPES`, then checks `DISPLAY_RUNTIME_INFO(display)->pipe_mask`.

State and persistence: no state is mutated. Results reflect persistent runtime display info and platform MMIO layout.

Dependencies and integration: depends on `intel_display_core.h`, display register/layout macros, runtime info, and Linux symbol export namespace `I915_GVT`.

Risks: the API trusts the passed `intel_display *`; invalid callers can still crash. Offset semantics must remain stable for GVT consumers when display register layout macros evolve.

Test signals: module/link tests for `I915_GVT` namespace consumers, pipe-mask validation on platforms with fewer than max pipes, and offset comparisons against direct macro expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_gvt_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_gvt_api.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_gvt_api.h

Purpose: declares the GVT-facing i915 display offset and pipe-validity API.

Important APIs/types/functions: declares functions for pipe, transcoder, cursor, display MMIO base offsets, and pipe validity. Forward-declares `enum pipe`, `enum transcoder`, and `struct intel_display`.

Control flow: no executable code; consumers call into `intel_gvt_api.c`.

State and persistence: no state in the header. Returned values reflect display runtime info and MMIO layout.

Dependencies and integration: includes Linux types and is intended for GVT namespace consumers.

Risks: callers must treat this as a query interface only and not assume every enum value is valid on every platform.

Test signals: compile GVT consumers and verify all declared symbols resolve from the `I915_GVT` namespace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_gvt_api.h -->
