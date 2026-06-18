# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dmc.h

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
