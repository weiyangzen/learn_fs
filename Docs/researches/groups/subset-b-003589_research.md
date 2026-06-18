# subset-b-003589 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dkl_phy_regs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dkl_phy_regs.h

### Purpose
`intel_dkl_phy_regs.h` defines the Dekel PHY register address model used by the i915 display driver for Type-C/TC PHY programming. It gives callers typed register descriptors that carry both the visible 4 KB MMIO aperture offset and the bank index needed to select the upper PHY address bits.

### Important APIs, Types, And Functions
The central type is `struct intel_dkl_phy_reg`, with a 24-bit `reg` field and 4-bit `bank_idx`. `_DKL_REG()`, `_DKL_REG_LN()`, `DKL_REG_MMIO()`, and `DKL_REG_TC_PORT()` are the important address helpers. The header then names lane and common registers such as `DKL_PCS_DW5()`, `DKL_PLL_DIV0()`, `DKL_PLL_DIV1()`, `DKL_PLL_SSC()`, `DKL_PLL_BIAS()`, `DKL_REFCLKIN_CTL()`, `DKL_TX_DPCNTL*()`, `DKL_TX_FW_CALIB()`, `DKL_DP_MODE()`, and `DKL_CMN_UC_DW_27()`. `HIP_INDEX_REG()`, `HIP_INDEX_VAL()`, and `_HIP_INDEX_SHIFT()` describe the indexing registers used to map a bank into the limited aperture.

### Control Flow
This header has no runtime control flow, but it encodes the register-selection flow used by its callers: derive the PHY base from a TC port, split an internal PHY offset into aperture offset plus bank index, program the appropriate HIP index register for the port group, then perform MMIO through the aperture. Lane-specific macros derive lane 1 offsets from lane 0/1 stride definitions.

### State, Persistence, And Dependencies
There is no stored software state. Hardware state lives in the Dekel PHY registers and HIP index registers. The file depends on `linux/types.h` and `intel_display_reg_defs.h` for integer types, `_MMIO`, `_PORT`, and `REG_BIT`/`REG_GENMASK` helpers.

### Integration Points
The macros are consumed by display PHY, PLL, and Type-C link training code that must program Dekel PHY lanes and common PLL blocks. The bank-aware descriptor is significant because callers need more than a plain `i915_reg_t` to reach the correct internal PHY bank.

### Risks
The bank/aperture split is easy to misuse: writing `DKL_REG_MMIO()` without setting the matching HIP index would address the wrong internal page. Port math assumes fixed 0x1000 spacing from PHY1 through PHY6. A macro typo exists in the formal parameter name of `DKL_CLKTOP2_HSCLKCTL(rc_port)`, while the body uses `tc_port`; this relies on macro expansion context and should be treated with caution. Bit masks are hardware contracts, so off-by-one shifts can break PLL or lane calibration.

### Test Signals
Useful signals are display bring-up on every supported TC port, PLL lock/link training success for DP/Type-C modes, register trace validation that HIP index writes precede banked MMIO, and static checks around generated offsets for lanes 0 and 1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dkl_phy_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dmc.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dmc.c

### Purpose
`intel_dmc.c` implements i915 Display Microcontroller firmware support. It selects the right DMC firmware blob for the platform, asynchronously loads and parses the container, stores main and pipe DMC payloads in memory, programs the firmware and its event/MMIO setup into display registers, manages suspend/resume lifetime, exposes debugfs state, and handles PipeDMC interrupts and event toggles.

### Important APIs, Types, And Functions
The internal `enum intel_dmc_id` identifies main DMC plus pipe A-D DMC images. `struct intel_dmc` owns the selected firmware path, maximum size, firmware version, DC6 allowed tracking, async work item, and per-DMC `dmc_fw_info` entries containing MMIO writes, start address, payload size, payload pointer, and package selection state. Firmware container structs include `intel_css_header`, `intel_package_header`, `intel_fw_info`, `intel_dmc_header_base`, `intel_dmc_header_v1`, and `intel_dmc_header_v3`.

Key exported APIs are `intel_dmc_init()`, `intel_dmc_load_program()`, `intel_dmc_wait_fw_load()`, `intel_dmc_disable_program()`, `intel_dmc_enable_pipe()`, `intel_dmc_disable_pipe()`, `intel_dmc_block_pkgc()`, `intel_dmc_configure_dc_balance_event()`, `intel_dmc_start_pkgc_exit_at_start_of_undelayed_vblank()`, `intel_dmc_suspend()`, `intel_dmc_resume()`, `intel_dmc_fini()`, `intel_dmc_has_payload()`, `intel_dmc_debugfs_register()`, snapshot helpers, PipeDMC IRQ/event helpers, `intel_pipedmc_start_mmioaddr()`, and PipeDMC DCB enable/disable helpers.

Important internal helpers include firmware selection (`dmc_firmware_default()`, `dmc_fallback_path()`), event programming (`disable_event_handler()`, `disable_all_event_handlers()`, `dmc_configure_event()`), platform workarounds (`pipedmc_clock_gating_wa()`, `fixup_dmc_evt()`, `disable_dmc_evt()`), parser stages (`parse_dmc_fw_css()`, `parse_dmc_fw_package()`, `parse_dmc_fw_header()`, `parse_dmc_fw()`), and load/assert helpers (`dmc_load_program()`, `dmc_load_mmio()`, `assert_dmc_loaded()`).

### Control Flow
Initialization exits early when the platform has no DMC. Otherwise it takes a runtime PM init wakeref to prevent runtime suspend before firmware is ready, allocates `struct intel_dmc`, resolves the default or module-parameter firmware path, and queues `dmc_load_work_fn()` on the unordered display workqueue. The worker calls `request_firmware()`, optionally falls back from unversioned ADL-P firmware to a legacy versioned blob, parses the CSS header, package header, and selected DMC headers, then programs all present DMC images through `intel_dmc_load_program()`. On success it drops the wakeref and logs the firmware version; on load/parse failure the wakeref intentionally remains held to keep runtime PM disabled.

Firmware parsing first records the CSS version, then selects package entries matching display stepping/substepping. Package v1 maps every entry to main DMC; package v2 uses the entry `dmc_id`. More specific entries win because a DMC id already marked present is skipped. Each selected DMC header is validated for version 1 or 3 layout, exact header length, MMIO count limits, MMIO address range, payload bounds, and maximum platform firmware size. MMIO entries are cached and known bad event definitions can be fixed in place before the payload is copied.

Program load disables all event handlers first, writes the payload dwords with firmware MMIO writes under `preempt_disable()`, then writes cached MMIO setup with `dmc_mmiodata()` applying default event disabling rules. Top-level load wraps this with PipeDMC clock-gating workarounds, reloads every present DMC id, asserts payload/MMIO contents, configures flip queue W2 PTS selection on display version 20+, clears `dc_state`, and sets the Gen9 DC-state debug mask.

Pipe enable validates that pipe firmware exists and that PSR does not make TGL pipe DMC unsafe, reloads program or MMIO when platform power-gating rules require it, resets flip queues and enables PipeDMC interrupts on display version 20+, then sets the pipe enable bit in either `MTL_PIPEDMC_CONTROL` or per-pipe `PIPEDMC_CONTROL`. Pipe disable reverses the enable bit, masks/acks interrupts, and resets flip queues. PipeDMC IRQ handling acks LNL+ interrupt bits, completes pending flip queue vblank events, reports ATS/GTT/error conditions, and also reports nonzero legacy interrupt vectors.

### State, Persistence, And Dependencies
Persistent driver state is `display->dmc.dmc`, per-payload heap allocations, `display->dmc.wakeref`, and the cached DC6 allowed counter. Hardware state is held in DMC program RAM, DMC event control/HTP registers, PipeDMC control/status/interrupt registers, DC state debug registers, and package C-state control registers. The firmware blob itself is released after parsing; only copied payload and MMIO setup remain. Suspend flushes pending load work and drops the wakeref if firmware never loaded; resume reacquires it in the same failure case; finalization frees all payloads and the DMC object.

The file depends on Linux firmware loading, debugfs, DRM vblank/event infrastructure, display runtime PM, display power wells, register accessors from `intel_de.h`, register definitions from `intel_dmc_regs.h` and display headers, CRTC state, DSB support, and flip queue helpers.

### Integration Points
This is wired into display driver load/unload, runtime/system power management, modeset pipe enable/disable, PSR/DC state decisions, flip queue event delivery, adaptive DCB programming, package C-state workarounds, debugfs `i915_dmc_info`, and GPU error/state snapshots. Firmware filenames are declared with `MODULE_FIRMWARE()` so distribution packaging can include the expected blobs.

### Risks
Firmware parsing is a high-trust boundary; the code mitigates truncation, oversized payloads, MMIO count, and address range problems, but any missing validation can lead to invalid display MMIO writes. Event handler rules are platform-specific and subtle: the file intentionally disables pipe DMC events by default, disables TGL main flip queue and HRR events, and rewrites TGL/ADL-S HRR vblank events. Regressions here can break DC state entry/exit, high refresh rate behavior, or flip queue completion. The runtime PM wakeref error path is intentional but can look like a leak. Pipe DMC reload rules differ by display generation and pipe, so new platforms must update `need_pipedmc_load_program()` and `need_pipedmc_load_mmio()` carefully. Interrupt handling assumes `crtc->flipq_event` is protected by the DRM event lock.

### Test Signals
High-value signals include boot logs showing successful firmware load/version, negative tests with missing/truncated/oversized firmware, debugfs `i915_dmc_info` showing loaded state and DC counters, runtime suspend/resume with DMC loaded and absent, system suspend/resume, PSR plus DC5/DC6 on TGL, pipe enable/disable across all pipes on display versions 12, 13/14, 20, and 30+, flip queue completion interrupts, ATS/GTT fault logging, and register readback from `assert_dmc_loaded()` remaining quiet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dmc.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dmc.h

### Purpose
`intel_dmc.h` is the public display-driver interface for DMC and PipeDMC support. It hides firmware parsing and hardware programming details behind lifecycle, power-management, pipe, interrupt, debug, and helper APIs.

### Important APIs, Types, And Functions
The header forward-declares `enum pipe`, `enum pipedmc_event_id`, `struct intel_display`, `struct intel_crtc`, `struct intel_crtc_state`, `struct intel_dsb`, `struct intel_dmc_snapshot`, and `struct drm_printer`. It declares DMC lifecycle functions (`intel_dmc_init()`, `intel_dmc_fini()`, `intel_dmc_suspend()`, `intel_dmc_resume()`, `intel_dmc_wait_fw_load()`), firmware programming functions (`intel_dmc_load_program()`, `intel_dmc_disable_program()`, `assert_main_dmc_loaded()`), pipe controls (`intel_dmc_enable_pipe()`, `intel_dmc_disable_pipe()`), power/workaround helpers (`intel_dmc_block_pkgc()`, `intel_dmc_configure_dc_balance_event()`, `intel_dmc_start_pkgc_exit_at_start_of_undelayed_vblank()`), debug/snapshot helpers, PipeDMC IRQ and event controls, PipeDMC start-address lookup, and adaptive DCB helpers.

### Control Flow
The header itself has no implementation flow. Its API shape reflects the intended sequence: initialize and wait for firmware load during driver bring-up, load the program when display power is available, enable or disable PipeDMC around pipe modesets, use event toggles for feature-specific handlers, service interrupts from the display IRQ path, snapshot or print state for diagnostics, suspend/resume around system sleep, then finalize at driver unload.

### State, Persistence, And Dependencies
No state is defined here. Implementations store state under `struct intel_display`, while callers pass CRTC state, pipes, and DSB command buffers as needed. The header depends only on `linux/types.h` and forward declarations, which keeps include coupling low for many display modules.

### Integration Points
This header is consumed by display init, modeset, power management, debugfs, interrupt, flip queue, and DCB code. It also bridges `intel_dmc.c` with register/event definitions in `intel_dmc_regs.h` by exposing `enum pipedmc_event_id` parameters without requiring every user to include implementation internals.

### Risks
Because most functions are void and silently no-op when firmware or hardware support is absent, callers must understand whether an operation is optional or required for correctness. The duplicate declaration of `intel_pipedmc_irq_handler()` is harmless at compile time but indicates header hygiene debt. Misordered calls, such as enabling pipe events before firmware has loaded, rely on implementation guards rather than type-system enforcement.

### Test Signals
Build coverage is the main header-level signal: all users should compile with only the forward declarations provided here. Runtime signals come from call-site tests that exercise DMC load, pipe enable/disable, event toggling, IRQ handling, snapshot printing, and DCB programming on platforms with and without DMC firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dmc_regs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dmc_regs.h

### Purpose
`intel_dmc_regs.h` defines DMC and PipeDMC event IDs, MMIO register addresses, address remapping helpers, and bitfields used by firmware loading, event handler programming, flip queues, wakelocks, package C-state controls, and adaptive DCB.

### Important APIs, Types, And Functions
The file defines `enum dmc_event_id`, a large `enum maindmc_event_id` for main DMC firmware events, and `enum pipedmc_event_id` for per-pipe firmware events. Core macros include `DMC_PROGRAM()`, `PIPEDMC_CONTROL()`, `MTL_PIPEDMC_CONTROL`, `PIPEDMC_LOAD_HTP()`, `PIPEDMC_CTL()`, `PIPEDMC_STATUS()`, `PIPEDMC_FQ_CTRL()`, `PIPEDMC_FQ_STATUS()`, PipeDMC flip queue pointer/status registers, scanline compare registers, interrupt/mask registers, package C-state block register, DMC event handler registers (`DMC_EVT_HTP()`, `DMC_EVT_CTL()`), firmware program base constants, DMC debug counters, wakelock registers, flip queue RAM entry bitfields for LNL and PTL+, PipeDMC execution timing variables, and adaptive DCB control registers.

### Control Flow
There is no executable flow, but the macros encode several control paths. Firmware load writes program dwords through `DMC_PROGRAM(start, i)` and configures handler pairs through `DMC_EVT_CTL()` and `DMC_EVT_HTP()`. Pipe enable/disable uses `PIPEDMC_CONTROL()` or `MTL_PIPEDMC_CONTROL`. Flip queue code programs RAM entries and tail/head pointers through `PIPEDMC_FPQ_*` registers. Interrupt handling reads/acks `PIPEDMC_INTERRUPT()` and checks `PIPEDMC_STATUS()`. Wakelock code toggles `DMC_WAKELOCK_CFG` and `DMC_WAKELOCK1_CTL`. DCB code writes the `PIPEDMC_DCB_*` register set.

### State, Persistence, And Dependencies
The header has no software state; it describes persistent hardware state in display MMIO. `_DMC_REG_MMIO_BASE()` and `_DMC_REG()` remap the main-DMC register layout to per-pipe DMC address spaces, with display-version-dependent PipeDMC bases. It depends on `intel_display_reg_defs.h` for `_MMIO`, `_MMIO_PIPE`, `_PICK_EVEN`, `REG_BIT`, field masks, and related register helpers.

### Integration Points
`intel_dmc.c` uses the firmware program, event, PipeDMC control, interrupt, package C-state, debug counter, and DCB definitions. `intel_dmc_wl.c` uses the wakelock registers. Flip queue code uses the FPQ register and RAM entry definitions. Power-management and debug code use DC counter and debug registers. This header is therefore the shared hardware contract across several display subsystems.

### Risks
Register definitions mix multiple hardware generations, so choosing the wrong base or display-version path can program unrelated MMIO. Event IDs are firmware ABI values; changing them breaks DMC event routing. Several macros are address factories and must be passed valid pipe/DMC IDs. The PipeDMC FPQ helper uses queue-id picking logic that assumes queue enum ordering. Magic undocumented PTL DMC variables are explicitly fragile. A typo-like macro form for `PIPEDMC_FPQ_LINES_TO_W1` and `PIPEDMC_FPQ_LINES_TO_W2` references `pipe` without a formal macro parameter, so use sites must be checked closely.

### Test Signals
Signals include successful DMC firmware load and event readback, PipeDMC enable/disable on every valid pipe, flip queue programming and completion on LNL/PTL+ formats, wakelock request/ack behavior, adaptive DCB enable/disable through DSB, package C-state workaround behavior, and register trace comparisons against hardware programming guides for each generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dmc_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dmc_wl.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dmc_wl.c

### Purpose
`intel_dmc_wl.c` implements DMC wakelock support. On platforms where display registers may be powered down in DC states, it explicitly asks DMC to exit the DC state before selected MMIO accesses and releases that request after a short hold time.

### Important APIs, Types, And Functions
The implementation uses `struct intel_dmc_wl` from the header, local `struct intel_dmc_wl_range`, and the module parameter value in `display->params.enable_dmc_wl`. Public functions are `intel_dmc_wl_init()`, `intel_dmc_wl_enable()`, `intel_dmc_wl_disable()`, `intel_dmc_wl_flush_release_work()`, `intel_dmc_wl_get()`, `intel_dmc_wl_put()`, `intel_dmc_wl_get_noreg()`, and `intel_dmc_wl_put_noreg()`. Important internal helpers are `intel_dmc_wl_sanitize_param()`, `__intel_dmc_wl_supported()`, `intel_dmc_wl_check_range()`, `intel_dmc_wl_reg_in_range()`, `__intel_dmc_wl_take()`, `__intel_dmc_wl_release()`, and delayed work callback `intel_dmc_wl_work()`.

### Control Flow
Initialization sanitizes the enable parameter: unsupported hardware is forced disabled, negative/default values enable wakelock only on display version 30+, out-of-range values are clamped to enabled, and always-locked mode seeds the refcount to one. Enabling dynamic DC states records the active DC state, writes `DMC_WAKELOCK_CFG_ENABLE`, marks the software state enabled, and takes the hardware lock immediately if references already exist. Disabling flushes pending release work, clears the config enable bit, clears the request bit, marks the lock not taken, and tolerates existing software users.

`intel_dmc_wl_get()` first filters by register range unless the mode is "any register" or the caller used the no-register variant. If the wakelock is not currently enabled, it only increments the refcount so a later enable can take it. If enabled, it cancels pending release work, increments or initializes the refcount, and when transitioning from zero calls `__intel_dmc_wl_take()` to set `DMC_WAKELOCK_CTL_REQ` and wait atomically for `DMC_WAKELOCK_CTL_ACK`. `intel_dmc_wl_put()` applies the same range filter, warns on underflow, decrements the refcount, and when it reaches zero queues delayed release work. The release worker clears the request bit and waits for ACK to clear, unless a new reference arrived first.

### State, Persistence, And Dependencies
Software state lives in `display->wl`: spinlock, `enabled`, `taken`, `refcount`, cached `dc_state`, and delayed release work. The spinlock protects all mutable state and allows use from atomic MMIO paths. Hardware state is `DMC_WAKELOCK_CFG` and `DMC_WAKELOCK1_CTL`. The 50 ms hold time avoids immediate churn after the last user drops the wakelock, and the 5000 us timeout bounds atomic waits. Dependencies include `intel_de` firmware MMIO accessors, DC state/register definitions, DRM warnings, Linux delayed work, spinlocks, and refcount APIs.

### Integration Points
This file integrates with the display MMIO access path through get/put calls around register programming, with dynamic DC state enable/disable, and with DMC register definitions from `intel_dmc_regs.h`. The range tables encode platform knowledge for powered-off registers and registers touched by DMC in DC3CO/DC5/DC6 modes.

### Risks
The code documents a possible race when wakelock is enabled while an existing user is between get and the protected MMIO; resolving it depends on hardware guidance. Range tables are manual and platform-specific, so missing a register can leave accesses unprotected in DC states, while broad matching hurts power/performance. Timeout warnings mean the display may not have exited or re-entered DC state as expected. Disable semantics with outstanding users are not fully specified by hardware. Always-locked mode intentionally holds the refcount and changes power behavior.

### Test Signals
Useful signals include parameter sanitization on unsupported and display version 30+ platforms, get/put nesting and underflow warnings, atomic-context register accesses through protected and unprotected ranges, enable with preexisting references, disable with outstanding references, delayed release cancellation/requeue behavior, timeout-free ACK transitions, and power tests showing DC state exit only for intended MMIO ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dmc_wl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dmc_wl.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dmc_wl.h

### Purpose
`intel_dmc_wl.h` declares the DMC wakelock state container and public API used by display code to protect MMIO accesses while low-power DC states may have powered down register blocks.

### Important APIs, Types, And Functions
`struct intel_dmc_wl` contains a spinlock, `enabled` flag, `taken` flag, `refcount_t`, cached `dc_state`, and delayed work item. The declared functions cover init, enable, disable, release-work flush, register-scoped get/put, and no-register get/put variants.

### Control Flow
The header has no executable logic, but it establishes the lifecycle expected by callers: initialize during display setup, enable when dynamic DC states are enabled, wrap relevant MMIO operations with get/put, flush release work before teardown or state transitions, and disable when DC states are disabled.

### State, Persistence, And Dependencies
The wakelock state persists inside `struct intel_display` via this struct. The lock comment states that the spinlock protects `enabled`, `taken`, `dc_state`, and `refcount`; the cached DC state avoids taking the display power-domain mutex in atomic MMIO contexts. Dependencies include Linux types, workqueue, refcount, spinlock availability through included kernel headers, `i915_reg_t`, and `struct intel_display`.

### Integration Points
This header is consumed by DMC wakelock implementation and display register access sites that need to acquire/release the DMC wakelock. It links the low-level register identifier type `i915_reg_t` with the display-wide state in `struct intel_display`.

### Risks
Correctness depends on callers balancing get/put calls and using the register-scoped variant whenever range filtering matters. The cached `dc_state` must be updated exactly when DC state policy changes, otherwise range checks can be too narrow or too broad. Because this can be called in atomic context, future API changes must preserve non-sleeping behavior.

### Test Signals
Header-level signals are build coverage for all call sites and lockdep-friendly use from atomic paths. Runtime tests should verify balanced get/put behavior, register and no-register variants, flush during teardown, and correct behavior when DC state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dmc_wl.h -->
