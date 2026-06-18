# subset-b-003734 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs600d.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs600d.h

### Purpose
`rs600d.h` is the register-definition header for RS600-class Radeon integrated graphics. It supplies MMIO, memory-controller, display, interrupt, PLL, and power-management register offsets plus the bitfield helpers used by `rs600.c` and related legacy ASIC code.

### Important APIs, Types, And Functions
There are no C functions or types; the public surface is preprocessor constants. Key groups include interrupt control/status (`R_000040_GEN_INT_CNTL`, `R_000044_GEN_INT_STATUS`), bus control (`R_00004C_BUS_CNTL`), indirect memory-controller access (`R_000070_MC_IND_INDEX`, `R_000074_MC_IND_DATA`), soft reset and busy status (`R_0000F0_RBBM_SOFT_RESET`, `R_0007C0_CP_STAT`, `R_000E40_RBBM_STATUS`), display vblank and hotplug registers, HDMI audio status/ack bits, MC aperture/page-table registers, priority-watermark registers, and PLL/dynamic-clock controls.

### Control Flow
The header has no runtime control flow. Its macros are consumed by code paths that enable interrupts, poll idle state, program MC apertures, configure display priorities, and force clock/power blocks on or off. The `S_`, `G_`, and `C_` macros encode set/get/clear-mask operations that keep call sites from hard-coding shifts.

### State, Persistence, And Dependencies
The state is hardware state, not memory owned by the header. Writes through `WREG32`, `WREG32_MC`, or PLL helpers persist in RS600 device registers until later driver programming, reset, suspend, or firmware/BIOS action changes them. It depends on the surrounding Radeon register-access convention and on callers honoring whether an offset is normal MMIO, MC-indirect, PLL, or display-register space.

### Integration Points
`rs600.c` includes this header for RS600 initialization, GART and MC programming, IRQ handling, bandwidth updates, and power-management setup. Some definitions mirror or align with RS690/RV515-era registers, which supports shared helper reuse such as AVIVO display priority programming and MC-stop/resume sequences.

### Risks
The main risk is incorrect bitfield metadata: a bad mask or shift can silently corrupt unrelated hardware bits. MC-indirect offsets must be accessed through the correct index/data registers, and display interrupt bits require correct acknowledge semantics. Several definitions are low-level hardware contracts with little type safety, so regressions usually appear as hangs, missing interrupts, broken hotplug/vblank, memory faults, or resume failures.

### Test Signals
Useful signals are successful RS600 boot and modeset, vblank and hotplug interrupt delivery, GART enable/disable, suspend/resume, GPU reset recovery, display priority behavior under high-resolution modes, and lack of MC protection faults or CP/RBBM busy timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs600d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs690.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs690.c

### Purpose
`rs690.c` implements RS690/RS740 integrated Radeon ASIC support. It covers MC idle polling, IGP memory sizing and placement, BIOS-derived bandwidth data, line-buffer and display-watermark programming, MC indirect access, startup/resume/suspend/fini lifecycle, GART/writeback/fence/ring/audio setup, and integration with the Radeon ASIC callback table.

### Important APIs, Types, And Functions
Externally used functions include `rs690_mc_wait_for_idle()`, `rs690_pm_info()`, `rs690_line_buffer_adjust()`, `rs690_bandwidth_update()`, `rs690_mc_rreg()`, `rs690_mc_wreg()`, `rs690_resume()`, `rs690_suspend()`, `rs690_fini()`, and `rs690_init()`. Important internal helpers are `rs690_gpu_init()`, `rs690_mc_init()`, `rs690_crtc_bandwidth_compute()`, `rs690_compute_mode_priority()`, `rs690_mc_program()`, and `rs690_startup()`. `union igp_info` abstracts ATOM integrated-system-info revisions, and `struct rs690_watermark` carries fixed-point display-watermark inputs and outputs.

### Control Flow
Initialization disables VGA rendering, prepares scratch/surface/sanity state, obtains and initializes ATOM BIOS, resets and verifies posting, reads clock info, initializes the MC, registers debugfs, initializes fences, BOs, RS400 GART, safe registers, PM, and then calls `rs690_startup()`. Startup reprograms MC FB/HDP location while clients are stopped, starts clocks, initializes pipes, enables GART, writeback, fences, IRQs, CP, IB pool, and HDMI audio. Resume disables GART, restarts clocks, resets/posts through ATOM, restores surfaces, and reuses startup. Suspend tears down PM, audio, CP, writeback, IRQs, and GART.

### State, Persistence, And Dependencies
Persistent driver state lives in `rdev->mc`, `rdev->pm`, `rdev->mode_info`, `rdev->irq`, rings, writeback, fences, and audio state. Hardware state includes MC FB location, HDP FB start, DCP control, line-buffer split, MC latency timers, display priority counters, and indirect MC registers. The code depends on ATOM BIOS tables, RS400 GART helpers, RV515 clock and MC client-stop/resume helpers, R100 CP/ring paths, RS600 IRQ setup, Radeon TTM/BO/fence infrastructure, fixed-point math, and `rs690d.h` register definitions.

### Integration Points
`radeon_asic.c` wires these functions into the RS690 ASIC callbacks and assigns `rs690_mc_rreg/wreg` as the MC accessor for RS690-class devices. `rs690_pm_info()` is also reused by later integrated chips for bandwidth estimates. `rs690_line_buffer_adjust()` is shared by RV515 display watermark code. The DPM path for RS780/RS880 can feed low/high SCLKs into RS690-style bandwidth calculations.

### Risks
The bandwidth code is sensitive to fixed-point math, BIOS clocks, sideport/UMA detection, and dual-CRTC mode combinations; wrong values can cause display underruns. MC programming must stop clients, wait for idle, and restore display access in the right order. FastFB direct mapping is guarded for 32-bit non-PAE and sideport cases; mistakes can expose invalid aperture addresses. Lifecycle failures after partial startup must leave acceleration disabled without leaking initialized subsystems.

### Test Signals
Test signals include boot on RS690/RS740 with UMA and sideport configurations, correct VRAM sizing for the 384 MiB sideport quirk, GART and CP ring tests, fence completion, HDMI audio init, dual-display modes at high width, displaypriority option behavior, suspend/resume, GPU reset recovery, and absence of MC idle timeouts or underrun artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs690.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs690d.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs690d.h

### Purpose
`rs690d.h` defines RS690-specific MMIO and indirect memory-controller registers used by `rs690.c`. It describes K8 UMA framebuffer mapping, MC index/data access, memory size and framebuffer-location registers, CP/RBBM status registers, line-buffer split and display-priority registers, DCP control, outstanding line-buffer request limits, MC system idle status, and MC latency timers.

### Important APIs, Types, And Functions
The file exports only macros. Key definitions include `R_00001E_K8_FB_LOCATION`, `R_00005F_MC_MISC_UMA_CNTL` with `G_00005F_K8_ADDR_EXT`, `R_000078_MC_INDEX`/`R_00007C_MC_DATA`, `R_000100_MCCFG_FB_LOCATION`, `R_000090_MC_SYSTEM_STATUS`, `R_006520_DC_LB_MEMORY_SPLIT`, `R_006D58_LB_MAX_REQ_OUTSTANDING`, `R_006548_D1MODE_PRIORITY_A_CNT`, and `R_006D48_D2MODE_PRIORITY_A_CNT`.

### Control Flow
There is no executable flow. Consumers poll `G_000090_MC_SYSTEM_IDLE()` during MC wait paths, program MC FB top/start with `S_000100_MC_FB_*`, read the K8 direct-map address for FastFB, and update display priority and line-buffer allocation when modes change.

### State, Persistence, And Dependencies
The represented state is hardware-visible register state. `rs690_mc_rreg()` and `rs690_mc_wreg()` use the index/data definitions under `rdev->mc_idx_lock` to serialize MC indirect access. Display and DCP registers are programmed through normal MMIO. The header depends on Radeon naming conventions for set/get/clear masks and on the hardware register map matching RS690/RS740.

### Integration Points
`rs690.c` includes this header directly. The line-buffer and priority definitions support `rs690_bandwidth_update()`, while MC system status supports `rs690_mc_wait_for_idle()`. K8 mapping definitions integrate with PCI aperture handling and the `radeon_fastfb` module option.

### Risks
Incorrect register offsets or masks can break MC programming, direct framebuffer mapping, or display watermark behavior. MC index width differs from other families, so using RS600/RV515 accessors with these definitions would hit the wrong registers. Line-buffer split constants encode policy choices that affect dual-display stability.

### Test Signals
Validation comes from RS690 boot, correct reported VRAM and aperture base, successful MC idle polling, no CP/RBBM busy hangs after reset, stable dual-CRTC modes, correct high-display-priority behavior, and suspend/resume without corrupted framebuffer base registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs690d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs780_dpm.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs780_dpm.c

### Purpose
`rs780_dpm.c` implements dynamic power management for RS780/RS880 integrated GPUs. It parses ATOM PowerPlay and integrated-system-info tables, constructs IGP power states, initializes SCLK and voltage-scaling hardware, handles DPM enable/disable and power-state transitions, reports current levels, and supports forced performance levels.

### Important APIs, Types, And Functions
Public callback functions are `rs780_dpm_init()`, `rs780_dpm_enable()`, `rs780_dpm_disable()`, `rs780_dpm_set_power_state()`, `rs780_dpm_setup_asic()`, `rs780_dpm_display_configuration_changed()`, `rs780_dpm_fini()`, `rs780_dpm_get_sclk()`, `rs780_dpm_get_mclk()`, `rs780_dpm_print_power_state()`, `rs780_dpm_debugfs_print_current_performance_level()`, `rs780_dpm_get_current_sclk()`, `rs780_dpm_get_current_mclk()`, and `rs780_dpm_force_performance_level()`. Internal helpers manage PLL divider programming, FVTHROT registers, voltage/PWM ranges, UVD clock ordering, PowerPlay table parsing, and display refresh parameters. `struct igp_power_info` and `struct igp_ps` are defined in `rs780_dpm.h`.

### Control Flow
`rs780_dpm_init()` allocates private power info, gets platform caps, parses PowerPlay states into `radeon_ps` plus `igp_ps`, and reads integrated-system-info fields for voltage control and UMA clock. `rs780_dpm_enable()` captures active CRTC/refresh, disables VBIOS power saving, rejects already-enabled dynamic PM, initializes R600 DPM parameter registers, starts dynamic PM, sets feedback-divider and PWM ranges, enables clock/voltage scaling, programs activity thresholds, and optionally enables graphics clock gating. Power-state changes update UVD clocks before or after engine scaling depending on direction, force max voltage, program new feedback-divider limits, select vblank source, reactivate scaling, and re-enable voltage scaling.

### State, Persistence, And Dependencies
Driver state is stored in `rdev->pm.dpm.priv`, `rdev->pm.dpm.ps`, current/requested/boot/uvd power-state pointers, and forced-level state. Hardware state includes FVTHROT control, feedback-divider, PWM, activity-threshold, SPLL bypass, CG_INTGFX_MISC, and graphics clock-gating registers. Dependencies include ATOM BIOS table parsing, R600 DPM helper functions, Radeon clock divider APIs, UVD clock programming, IRQ thermal state, debugfs `seq_file`, and `rs780d.h` register definitions.

### Integration Points
`radeon_asic.c` wires these functions into the RS780 DPM callback table. `rs690_bandwidth_update()` can query `radeon_dpm_get_sclk()` for low/high watermark calculations on RS780/RS880. The debug and print callbacks feed Radeon PM sysfs/debugfs reporting. UVD state classification uses shared R600 helpers.

### Risks
PowerPlay and integrated-system-info parsing assumes table offsets and entry sizes are valid; malformed BIOS data can cause init failure or bad clocks. Engine-clock scaling requires low/high/current dividers to share reference and post dividers, otherwise it returns `-EINVAL`. Voltage control is disabled when BIOS values are inconsistent, but PWM inversion and device-ID-specific defaults still carry board risk. Ordering around SPLL bypass, forced voltage, UVD clocks, and vblank selection is hardware-sensitive.

### Test Signals
Strong signals are successful DPM init/enable on RS780 and RS880 device IDs, correct parsed boot/UVD states, transitions between battery/performance/UVD profiles, forced low/high/auto behavior, debugfs current SCLK matching FVTHROT status, stable UVD playback during transitions, display reconfiguration refresh-threshold updates, suspend/resume with DPM disabled and re-enabled, and no thermal IRQ or clock-gating regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs780_dpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs780_dpm.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs780_dpm.h

### Purpose
`rs780_dpm.h` declares the private RS780/RS880 IGP DPM data model and default tuning constants used by `rs780_dpm.c`. It captures voltage-level enums, BIOS-derived power-info fields, per-power-state clock/voltage fields, feedback-divider/PWM defaults, clock-gating defaults, and fallback UVD clocks.

### Important APIs, Types, And Functions
The important types are `enum rs780_vddc_level`, `struct igp_power_info`, and `struct igp_ps`. `igp_power_info` holds feature flags, PWM/voltage limits, boot UMA clock, system config, active CRTC/refresh rate, and voltage timing values. `igp_ps` holds low/high SCLK, low/high voltage levels, and flags. The rest of the header is default constants for FVTHROT timing, PWM ranges, RS780D/RS880D feedback-divider ranges, slow-clock feedback, clock gating, and default UVD VCLK/DCLK.

### Control Flow
The header has no execution. `rs780_dpm.c` fills these structs during BIOS parsing, then uses the constants while initializing FVTHROT, voltage scaling, clock scaling, activity thresholds, and fallback UVD clocks.

### State, Persistence, And Dependencies
Instances of the structs persist as allocated DPM private state under `rdev->pm.dpm`. The constants become persistent hardware settings only after `rs780_dpm.c` writes the corresponding registers. The header depends on kernel integer and bool definitions already provided by including C files and on RS780 ATOM table semantics.

### Integration Points
This header is included only by the RS780 DPM implementation. Its struct layout is the bridge between ATOM PowerPlay/integrated-system-info parsing and later transition code. Its default constants pair with bitfield definitions in `rs780d.h`.

### Risks
Wrong defaults or struct interpretation can produce bad voltage/PWM ranges or unstable feedback-divider behavior. `RS880D_FVTHROTPWMFBDIVRANGEREG2_DFLT` uses mixed-case hex spelling but resolves correctly; any value changes must be validated on real hardware. If future BIOS revisions encode different units, the current fields would be insufficient.

### Test Signals
Test by parsing crev 1 and crev 2 integrated-system-info tables, enabling voltage and non-voltage-control paths, comparing programmed PWM/feedback-divider registers with expected defaults per device ID, verifying fallback UVD clocks for UVD states missing VCLK/DCLK, and checking forced/per-state SCLK behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs780_dpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs780d.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs780d.h

### Purpose
`rs780d.h` defines RS780/RS880 SPLL and FVTHROT register offsets and bitfields used by the DPM implementation. It is the low-level map for engine-clock feedback-divider scaling, activity thresholds, PWM voltage control, current-clock status, vblank selection, and macro bypass control.

### Important APIs, Types, And Functions
The header exports macros for `CG_SPLL_FUNC_CNTL` and its reset/sleep/divider/bypass/status fields; `FVTHROT_CNTRL_REG` and activity-target/countback registers; up/down trend count registers; feedback-divider min/max/force/start registers; PWM control, min/max hightime, up/down step, and feedback-divider range registers; `FVTHROT_STATUS_REG0` current feedback divider; `CG_INTGFX_MISC` vblank selection; and `GFX_MACRO_BYPASS_CNTL` SPLL/UPLL bypass control.

### Control Flow
There is no direct flow. `rs780_dpm.c` uses these definitions to temporarily bypass SPLL, force feedback dividers and PWM hightime, enable or disable FV throttling and FV update, program activity thresholds from display refresh, and read current SCLK from the active feedback divider.

### State, Persistence, And Dependencies
Writes to these registers persist in GPU power-management hardware until changed by DPM disable, forced-level transitions, suspend/resume, reset, or BIOS/driver reinitialization. The macros depend on correct register-access routing through standard `RREG32`/`WREG32` helpers and on the bit widths matching RS780/RS880 hardware.

### Integration Points
`rs780_dpm.c` includes this file with `rs780_dpm.h`. `radeon_asic.c` exposes the DPM callbacks that ultimately program these registers. The current SCLK debugfs path reads `FVTHROT_STATUS_REG0` and `CG_SPLL_FUNC_CNTL` fields defined here.

### Risks
The SPLL feedback divider masks/shifts are safety-critical; an incorrect value can force an invalid engine clock. PWM hightime and period fields are board-voltage sensitive. Enabling FV throttling or FV throttle I/O with wrong ranges can destabilize display or the northbridge. Register definitions have no range checking, so callers must validate BIOS-derived values.

### Test Signals
Signals include clean DPM enable/disable, forced feedback-divider changes, current SCLK reads matching expected low/high states, stable voltage transitions, successful vblank-source changes after CRTC selection, UVD playback across state changes, and no lockups around SPLL bypass toggling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rs780d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv200d.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv200d.h

### Purpose
`rv200d.h` is a tiny RV200 register-definition header. It defines the upper AGP base-address register and bitfield helpers required by older Radeon AGP memory-controller setup.

### Important APIs, Types, And Functions
There are no functions or types. The exported macros are `R_00015C_AGP_BASE_2`, `S_00015C_AGP_BASE_ADDR_2(x)`, `G_00015C_AGP_BASE_ADDR_2(x)`, and `C_00015C_AGP_BASE_ADDR_2`.

### Control Flow
The header has no control flow. Code in the older R100/RV200 AGP path includes it to compose or decode the high nibble of the AGP base address when programming aperture registers.

### State, Persistence, And Dependencies
The only represented state is the high 4 bits of an AGP base address in hardware. The value persists in the device until AGP teardown, MC reprogramming, reset, or suspend/resume reinitialization. It depends on legacy Radeon register-access helpers and on callers pairing it with lower AGP base registers from shared headers.

### Integration Points
`r100.c` includes this header together with `rv250d.h`. It supports the older ASIC memory aperture path rather than the RS690/RV515 PCIe GART flow.

### Risks
A wrong high-address nibble maps AGP/GART traffic to the wrong physical range, which can cause DMA corruption, faults, or hangs. Since the file has only macros, risk is concentrated in register correctness and caller unit/address shifting.

### Test Signals
Useful validation is booting RV200 AGP hardware, initializing AGP without aperture faults, running command submission and BO movement through AGP GART, suspend/resume, and checking that high-memory AGP apertures above 32 bits are programmed correctly when supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv200d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv250d.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv250d.h

### Purpose
`rv250d.h` defines RV250/M6-era dynamic SCLK control bits. The single register described here, `R_00000D_SCLK_CNTL_M6`, controls clock source selection, dynamic-stop latency bits, and force-on bits for CP, HDP, display, 2D/3D, video, texture, memory, and other blocks.

### Important APIs, Types, And Functions
There are no functions or structs. The macro group around `R_00000D_SCLK_CNTL_M6` includes `S_`, `G_`, and `C_` helpers for `SCLK_SRC_SEL`, per-block `*_MAX_DYN_STOP_LAT`, and `FORCE_*` fields such as `FORCE_CP`, `FORCE_HDP`, `FORCE_DISP1`, `FORCE_DISP2`, `FORCE_E2`, `FORCE_SE`, `FORCE_IDCT`, `FORCE_VIP`, `FORCE_RE`, `FORCE_PB`, `FORCE_TAM`, `FORCE_TDM`, `FORCE_RB`, `FORCE_TV_SCLK`, `FORCE_SUBPIC`, and `FORCE_OV0`.

### Control Flow
The header has no runtime behavior. Legacy power/clock code includes it to manipulate dynamic clocks or force blocks on before accessing them. A typical caller reads the PLL register, applies clear masks and set macros, then writes the value back through PLL accessors.

### State, Persistence, And Dependencies
The represented state is PLL/power-management hardware state controlling whether blocks can dynamically stop clocks or must remain forced on. Settings persist until later clock-management writes, reset, or suspend/resume. The definitions depend on the Radeon PLL register access path and on the RV250/M6 register layout.

### Integration Points
`r100.c` includes this header for old-generation Radeon clock handling. It complements RV350-specific additions in `rv350d.h` and older AGP definitions in `rv200d.h`.

### Risks
Clock gating definitions are hardware-sensitive: forcing too little can hang a block during register access or command execution, while forcing too much can waste power. Incorrect masks can alter adjacent force or latency fields and cause display, overlay, or command processor instability.

### Test Signals
Validation signals include successful dynamic clock enable/disable on RV250-class hardware, no hangs during CP/2D/3D/video use, correct display and TV-out behavior, suspend/resume stability, and power-management tests showing blocks can enter and leave forced states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv250d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv350d.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv350d.h

### Purpose
`rv350d.h` adds RV350/RV380-specific force bits for the shared SCLK control register. It extends older dynamic-clock handling with force controls for VAP, SR, PX, TX, US, and SU blocks.

### Important APIs, Types, And Functions
There are no functions or structs. The exported macros are `S_00000D_FORCE_VAP`, `G_00000D_FORCE_VAP`, `C_00000D_FORCE_VAP`, and equivalent helpers for `FORCE_SR`, `FORCE_PX`, `FORCE_TX`, `FORCE_US`, and `FORCE_SU`. The base register definition is commented out, implying it is supplied by another header such as the RV250/R100 clock-control definitions.

### Control Flow
The header has no direct control flow. Consumers compose PLL register values that force individual graphics pipeline blocks on or allow them to participate in dynamic clock gating.

### State, Persistence, And Dependencies
The macros describe persistent hardware clock-control bits. They depend on the shared `R_00000D_SCLK_CNTL` register layout and the correct PLL write path. State remains in hardware until modified by clock-management code, reset, or resume reinitialization.

### Integration Points
`r300.c` includes this header for RV350/RV380 ASIC handling. It complements broader SCLK definitions in older Radeon headers and helps power-management code cover blocks introduced or renamed in the RV3xx pipeline.

### Risks
Misprogramming these force bits can leave shader/texture/setup blocks clock-gated while in use or unnecessarily powered, causing hangs or power regressions. Since the register symbol is not defined here, include-order and shared-register consistency matter.

### Test Signals
Test signals are RV350/RV380 boot, 2D and 3D command execution under dynamic clocks, suspend/resume, reset recovery, and power-management toggles that do not cause VAP/shader/texture pipeline lockups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv350d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv515.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv515.c

### Purpose
`rv515.c` implements RV515 ASIC support for the Radeon driver. It provides ring startup packets, MC idle polling and indirect access, VRAM sizing, MC stop/resume/programming, clock startup, debugfs hooks, lifecycle init/suspend/resume/fini, safe-register setup, TV scaler programming, and AVIVO display bandwidth/watermark updates.

### Important APIs, Types, And Functions
Externally used functions include `rv515_ring_start()`, `rv515_mc_wait_for_idle()`, `rv515_vga_render_disable()`, `rv515_mc_rreg()`, `rv515_mc_wreg()`, `rv515_debugfs()`, `rv515_mc_stop()`, `rv515_mc_resume()`, `rv515_clock_startup()`, `rv515_resume()`, `rv515_suspend()`, `rv515_set_safe_registers()`, `rv515_fini()`, `rv515_init()`, `atom_rv515_force_tv_scaler()`, `rv515_bandwidth_avivo_update()`, and `rv515_bandwidth_update()`. Internal helpers include `rv515_gpu_init()`, `rv515_vram_get_type()`, `rv515_mc_init()`, `rv515_mc_program()`, `rv515_startup()`, `rv515_crtc_bandwidth_compute()`, and `rv515_compute_mode_priority()`.

### Control Flow
Initialization prepares scratch/surface/sanity state, loads and initializes ATOM BIOS, resets/posts the GPU, reads clocks, initializes AGP if present, sizes and locates VRAM/GTT, creates debugfs entries, initializes fences/BOs/PCIe GART/safe registers/PM, then runs startup. Startup programs MC while display clients are stopped, forces clocks on, initializes pipes, enables PCIe GART, allocates writeback, starts fences, installs IRQs, starts the CP ring, and initializes the IB pool. Suspend disables PM, CP, writeback, IRQs, and PCIe GART. Resume disables GART, restarts clocks, resets/posts, restores surfaces, and reruns startup.

### State, Persistence, And Dependencies
Driver state is held in `rdev->mc`, AGP/PCIe GART state, BO/TTM, rings, fences, writeback, IRQ, PM, debugfs, and safe-register bitmap pointers. Hardware state includes CP ring registers, MC FB/AGP/HDP locations, VGA render/HDP control, CRTC/GRPH surface addresses and update locks, R600+ blackout bits when helpers are reused by newer ASICs, PLL dynamic-control registers, and display priority/watermark registers. Dependencies include ATOM BIOS, R100/R300/R400 helper code, RV370 PCIe GART, RS600 IRQs, RS690 line-buffer adjustment, fixed-point math, `rv515d.h`, `rv515_reg_safe.h`, and Radeon core memory/ring/fence APIs.

### Integration Points
`radeon_asic.c` wires RV515 callbacks and reuses `rv515_ring_start()` for related R5xx ASIC rings. Newer R600/R700 paths reuse `rv515_mc_stop()`, `rv515_mc_resume()`, and `rv515_vga_render_disable()` around MC programming. `atombios_crtc.c` calls `atom_rv515_force_tv_scaler()` for TV scaler setup. `rs690.c` reuses RV515 clock/debug/MC client helpers.

### Risks
MC stop/resume is delicate because it blanks or disables CRTCs, waits for frame counters, locks/unlocks double-buffered registers, updates surface bases, and may blackout newer MCs. Ring startup packet order must flush caches and initialize graphics state correctly. TV scaler programming is a large literal register table with little self-documentation. Bandwidth calculations are fixed-point and mode-dependent. Partial startup failure paths must clean up initialized acceleration components without disturbing unrelated user state.

### Test Signals
Signals include RV515 boot on PCIe and AGP systems, CP ring and IB tests, fence completion, BO moves through GART, debugfs pipe/GA reads, modeset and dual-display stress, TV-out scaler validation, displaypriority option behavior, suspend/resume, GPU reset recovery, and lack of MC idle timeouts, vblank waits that never advance, display corruption, or underruns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv515.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv515d.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv515d.h

### Purpose
`rv515d.h` is the RV515 register and packet definition header. It covers PCIe and MC indirect access, CP command/ring status, graphics pipeline setup registers, cache flush controls, AVIVO line-buffer and display-priority registers, MC FB/AGP apertures, VGA and CRTC surface/update registers, PLL dynamic clock controls, and PM4 packet encoding.

### Important APIs, Types, And Functions
There are no C functions or structs. Important macro groups include `PACKET0/2/3` PM4 encoders, CP packet opcodes, `MC_IND_INDEX/DATA`, `RBBM_STATUS`, `WAIT_UNTIL`, `ISYNC_CNTL`, `GB_*`, `GA_*`, `RB3D_DSTCACHE_CTLSTAT`, `ZB_ZCACHE_CTLSTAT`, `DC_LB_MEMORY_SPLIT`, `D1/D2MODE_PRIORITY_*`, `LB_MAX_REQ_OUTSTANDING`, MC aperture registers, VGA render/HDP/base registers, D1/D2 CRTC control and update-lock registers, D1/D2 graphics surface addresses, and PLL dynamic control registers for CP/E2/IDCT force-on.

### Control Flow
The header is declarative. `rv515.c` uses packet macros to emit ring initialization commands, MC macros to program VRAM/AGP aperture state, display macros to stop/resume scanout safely, and PLL macros to force hardware blocks on during clock startup.

### State, Persistence, And Dependencies
The represented state is persistent device register state and command stream packet format. Writes persist until the driver, BIOS, reset, or suspend/resume changes them. PM4 packet definitions depend on `REG_SET` and command-processor conventions from shared Radeon headers. Register definitions depend on the RV515/R5xx hardware map and are accessed through normal MMIO, MC-indirect, or PLL helpers as appropriate.

### Integration Points
`rv515.c` includes this header directly. Related ASIC files reuse RV515 helper functions that rely on these definitions. The PM4 macros feed the Radeon ring buffer, and display register definitions pair with AVIVO mode-setting structures from shared headers.

### Risks
Packet count/base encoding errors can corrupt the command stream. MC aperture masks and shifts affect DMA address translation. CRTC update-lock and surface-address definitions affect modeset and resume correctness. PLL force-on bits can hang blocks if wrong or waste power if left forced unnecessarily. Many macros are untyped, so caller-side unit mistakes are not caught at compile time.

### Test Signals
Validation includes successful CP ring startup, cache flush completion, MC aperture programming, AGP and PCIe GART operation, CRTC stop/resume without display corruption, PM4 packet decoding by hardware, suspend/resume, and debugfs reads of pipe/tile state matching expected register values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv515d.h -->
