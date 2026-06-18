# subset-b-003735 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv6xx_dpm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv6xx_dpm.c

## Purpose
`rv6xx_dpm.c` implements dynamic power management for RV610/RV630/RV670-era Radeon ASICs. It programs register-based, non-SMC DPM state tables for engine clock, memory clock, voltage GPIO, backbias, PCIe Gen2, spread spectrum, thermal throttling, display-gap handling, UVD clock ordering, and debug/status reporting.

## Important APIs, Types, and Functions
The public entry points are `rv6xx_dpm_init`, `rv6xx_dpm_enable`, `rv6xx_dpm_disable`, `rv6xx_dpm_set_power_state`, `rv6xx_setup_asic`, `rv6xx_dpm_display_configuration_changed`, `rv6xx_dpm_print_power_state`, `rv6xx_dpm_debugfs_print_current_performance_level`, `rv6xx_dpm_get_current_sclk`, `rv6xx_dpm_get_current_mclk`, `rv6xx_dpm_get_sclk`, `rv6xx_dpm_get_mclk`, `rv6xx_dpm_force_performance_level`, and `rv6xx_dpm_fini`. Internally it uses `struct rv6xx_power_info`, `struct rv6xx_pm_hw_state`, `struct rv6xx_ps`, and `struct rv6xx_pl` from `rv6xx_dpm.h`.

Key helpers generate SCLK stepping tables (`rv6xx_convert_clock_to_stepping`, `rv6xx_generate_steps`, `rv6xx_output_stepping`), program MCLK and voltage entries, compute activity thresholds, and parse ATOM PowerPlay tables. Register helpers from `r600_dpm.h` write common R600 DPM blocks such as power-level entries, voltage pins, activity thresholds, thermal protection, and DPM start/stop controls.

## Control Flow
Initialization allocates `rdev->pm.dpm.priv`, reads platform caps, parses BIOS PowerPlay states, fills voltage response defaults, probes PLL dividers, spread-spectrum support, voltage GPIO support, and feature toggles. ASIC setup enables ACPI PM and optional ASPM L0s/L1/PLL sleep.

Enable refuses to run if DPM is already active, then enables backbias/spread spectrum, programs timing constants, BSP/GIT/TP/TPP/SSTP/FCP/voltage timing, display gap, power-level entry state, and voltage GPIO masks. It calculates the boot power state's stepping data, generates SCLK/MCLK/voltage tables, programs low/medium/high hardware levels, enables levels, enables thermal auto throttle, starts DPM, then enables dynamic PCIe Gen2 and gfx clock gating.

Power-state switching is staged through a safe low/transition state: UVD clocks may be lowered first, high/medium levels are disabled, transition SCLK and a context-switch MCLK entry are programmed, safe voltage/backbias/PCIe settings are applied, dynamic voltage/backbias is temporarily disabled, voltage is stepped up if needed, the engine moves through medium and low, new low entries are installed, voltage may be stepped down, dynamic controls are re-enabled, final low/medium/high tables are generated, and UVD clocks may be raised after the engine clock change.

## State and Persistence
Persistent state lives in `rdev->pm.dpm`: parsed power states, current/requested/boot pointers, platform caps, forced level, display CRT mask, and response times. Private RV6xx state in `struct rv6xx_power_info` tracks feature booleans, reference divider scale, active throttle sources, restricted forced levels, and the computed hardware state arrays. Hardware state persists in GPU registers until disabled or reprogrammed.

## Dependencies and Integration Points
This file depends heavily on ATOMBIOS (`radeon_atom_get_clock_dividers`, voltage GPIO, spread-spectrum and default-voltage queries), `r600_dpm` register helpers, PCIe indirect accessors, IRQ thermal handling, UVD clock callbacks, debugfs `seq_file`, and common Radeon PM policy. It integrates with the radeon ASIC callbacks for DPM lifecycle, display configuration changes, forced performance levels, and current-clock reporting.

## Risks
There are several hardware-sequencing risks: incorrect voltage stepping can undervolt during clock transitions; PCIe Gen2 toggling must fall back to Gen1 safely; spread-spectrum programming relies on valid ATOM data; display-gap changes depend on active CRTC masks; and DPM disable must unwind thermal IRQs and clock gating. The code also has a suspicious assignment in `rv6xx_calculate_voltage_stepping_parameters`: when low voltage differs from medium, it assigns `medium_vddc_index = R600_POWER_LEVEL_LOW` instead of `low_vddc_index`, which can affect voltage table selection.

## Test Signals
Useful signals include successful `rv6xx_dpm_enable`/disable without `-EINVAL`, debugfs current performance level matching `TARGET_AND_CURRENT_PROFILE_INDEX`, stable current SCLK/MCLK reads, clean thermal IRQ enable/disable, absence of hangs during PowerPlay state transitions and UVD state changes, correct forced high/low behavior, and suspend/resume coverage with DPM active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv6xx_dpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv6xx_dpm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv6xx_dpm.h

## Purpose
`rv6xx_dpm.h` defines the private data model used by `rv6xx_dpm.c` to translate BIOS PowerPlay states into register-programmable RV6xx DPM state.

## Important APIs, Types, and Functions
The header exports no functions. Its core types are `struct rv6xx_sclk_stepping` for a single VCO/post-divider engine-clock step, `struct rv6xx_pm_hw_state` for computed hardware indices and clock/voltage/backbias/PCIe arrays, `struct rv6xx_power_info` for driver-private feature and runtime state, `struct rv6xx_pl` for one logical power level, and `struct rv6xx_ps` for high/medium/low levels. It also defines default UVD VCLK/DCLK values in 10 kHz units.

## Control Flow
The header is consumed after `rv6xx_dpm_init` allocates `struct rv6xx_power_info` and attaches it to `rdev->pm.dpm.priv`. Parsed PowerPlay states allocate `struct rv6xx_ps` into each `radeon_ps.ps_priv`. Subsequent DPM enable and transition flows fill `rv6xx_pm_hw_state` from the requested `rv6xx_ps` and use the stored feature flags to decide which register blocks to program.

## State and Persistence
`struct rv6xx_power_info` persists for the DPM lifetime and is freed by `rv6xx_dpm_fini`. It stores probed platform capabilities, spread-spectrum flags, voltage-control availability, thermal/display/clock-gating booleans, PLL divider scaling, active auto-throttle sources, forced-level restrictions, and the current computed hardware state. `struct rv6xx_ps` instances persist as per-BIOS-state private payloads attached to `rdev->pm.dpm.ps`.

## Dependencies and Integration Points
The header includes `r600_dpm.h` for shared constants such as power-level counts. Its structs are not standalone ABI; they are internal to the radeon driver and tied to the R600/RV6xx register model, ATOMBIOS PowerPlay parsing, and common Radeon DPM callback wiring.

## Risks
Array sizes must stay aligned with R600 DPM constants. Since hardware indices are cached as `u8`, invalid generation of stepping indices or voltage indices can corrupt later register programming. Any extension must preserve the high/medium/low ordering assumed by parser, debugfs, and transition code.

## Test Signals
Build coverage is the primary signal for this header. Runtime validation comes indirectly from successful RV6xx DPM init/fini, power-state parsing, power-level transitions, forced-level changes, and debugfs current-level reporting using the structs defined here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv6xx_dpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv6xxd.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv6xxd.h

## Purpose
`rv6xxd.h` is the RV6xx register-definition header for power management, memory-controller timing, display-gap, thermal, spread-spectrum, and PCIe indirect registers used by `rv6xx_dpm.c`.

## Important APIs, Types, and Functions
The file contains macros only. Important register groups include `SPLL_CNTL_MODE`, `GENERAL_PWRMGT`, `MCLK_PWRMGT_CNTL`, `MPLL_FREQ_LEVEL_0`, `VID_RT`, `TARGET_AND_CURRENT_PROFILE_INDEX`, `VID_UPPER_GPIO_CNTL`, `CG_DISPLAY_GAP_CNTL`, `CG_THERMAL_CTRL`, `CG_SPLL_SPREAD_SPECTRUM_LOW`, `CG_MPLL_SPREAD_SPECTRUM`, memory-controller registers such as `RAMCFG`, `SQM_RATIO`, `ARB_RFSH_RATE`, and PCIe indirect registers `PCIE_P_CNTL`, `PCIE_LC_CNTL`, and `PCIE_LC_SPEED_CNTL`.

## Control Flow
These macros parameterize register writes and bitfield extraction throughout RV6xx DPM. The DPM code reads current profile bits from `TARGET_AND_CURRENT_PROFILE_INDEX`, writes `GENERAL_PWRMGT` to enable voltage/backbias/spread-spectrum/thermal/PCIe control, programs per-level MCLK fields under `MPLL_FREQ_LEVEL_0`, and updates memory refresh and display-gap registers during state transitions.

## State and Persistence
The header itself has no state, but its definitions represent persistent GPU MMIO state. Values written through these macros remain in hardware until subsequent driver writes, GPU reset, or power-state transitions. The current-profile register is also used as the live source for debugfs and current-clock helpers.

## Dependencies and Integration Points
`rv6xxd.h` is integrated with the radeon MMIO accessor macros `RREG32`, `WREG32`, `WREG32_P`, `RREG32_PCIE`, and `RREG32_PCIE_PORT`. It aligns RV6xx bit definitions with `rv6xx_dpm.c` and common `r600_dpm` helpers.

## Risks
Incorrect masks or shifts in this file can silently corrupt hardware programming. Shared macro names such as `SSEN`, `CLKS`, and `CLKV` overlap conceptually with RV730/RV740/RV770 headers but have different field positions, so including the wrong register header for a chip path would produce invalid writes.

## Test Signals
Signals are indirect: DPM enable should set expected `GENERAL_PWRMGT` bits, current-level debugfs should decode profile indices correctly, memory-refresh programming should remain stable across clock changes, and PCIe/thermal/display-gap features should respond without hangs or link-training failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv6xxd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv730_dpm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv730_dpm.c

## Purpose
`rv730_dpm.c` provides RV730/RV710-specific support for the RV770 SMC-based DPM framework. It encodes chip-specific SPLL/MPLL register images into SMC table fields, snapshots boot clock registers, builds initial and ACPI SMC states, programs memory timing tables, starts/stops DPM, and manages DC ODT values.

## Important APIs, Types, and Functions
Public helpers called from `rv770_dpm.c` include `rv730_populate_sclk_value`, `rv730_populate_mclk_value`, `rv730_read_clock_registers`, `rv730_populate_smc_acpi_state`, `rv730_populate_smc_initial_state`, `rv730_program_memory_timing_parameters`, `rv730_start_dpm`, `rv730_stop_dpm`, `rv730_program_dcodt`, and `rv730_get_odt_values`.

## Control Flow
`rv730_read_clock_registers` captures current SPLL/MPLL/spread-spectrum registers into `pi->clk_regs.rv730` during ASIC DPM setup. SMC table construction calls `rv730_populate_smc_initial_state` for the boot state and `rv730_populate_smc_acpi_state` for the low-power ACPI state. Runtime power-state conversion calls `rv730_populate_sclk_value` and `rv730_populate_mclk_value` for each logical power level. Enable/disable uses `rv730_start_dpm` and `rv730_stop_dpm` rather than the generic RV770 MCLK register path.

## State and Persistence
The file stores no standalone state; it reads and updates `struct rv7xx_power_info` attached to `rdev->pm.dpm.priv`. Captured clock registers seed SMC table entries so the firmware can restore or switch clock states. ODT values are persisted in `pi->odt_value_0/1` and later written around state switches when DC ODT threshold handling is active.

## Dependencies and Integration Points
It depends on `rv730d.h` bitfields, ATOMBIOS clock-divider and spread-spectrum queries, RV770 SMC table structures from `rv770_dpm.h`, generic voltage helpers such as `rv770_populate_vddc_value`, and memory timing helpers such as `radeon_atom_set_engine_dram_timings`. It is selected by `rv770_dpm.c` when `rdev->family` is `CHIP_RV730` or `CHIP_RV710`.

## Risks
Clock encoding is sensitive to ATOM divider semantics, endian conversion, and post-divider high/low field layout. The MCLK spread-spectrum code appears to clear `mpll_ss2` but OR `CLK_V(clk_v)` into `mpll_ss`, which is worth reviewing against hardware documentation. DPM stop depends on SMC acknowledgement and only logs a debug message if forcing low fails.

## Test Signals
Validation should include RV730/RV710 DPM enable/disable, SMC table upload success, power-state switches across all three levels, correct memory refresh/timing register staging, ODT transitions on mobile DDR2/DDR3 parts, and absence of clock or memory instability when spread spectrum is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv730_dpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv730d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv730d.h

## Purpose
`rv730d.h` defines RV730/RV710-specific clock, power-management, memory-timing, spread-spectrum, and ODT register addresses and bitfields used by the RV730 DPM overlay.

## Important APIs, Types, and Functions
The header exports macros only. Major groups include SPLL registers (`CG_SPLL_FUNC_CNTL*`), MPLL registers (`CG_MPLL_FUNC_CNTL*`), memory-clock power control (`TCI_MCLK_PWRMGT_CNTL`, `TCI_DLL_CNTL`), `GENERAL_PWRMGT`, `SCLK_PWRMGT_CNTL`, activity threshold register `CG_AT`, spread-spectrum registers, memory timing and refresh registers, and MC4 IO pad-control registers used for ODT programming.

## Control Flow
`rv730_dpm.c` reads the clock registers into `pi->clk_regs.rv730`, edits fields for each SMC state, writes refresh/timing registers for performance levels, toggles global DPM and clock power-off bits during start/stop, and updates MC4 IO pad controls around DC ODT transitions.

## State and Persistence
The header has no C state. Its macros describe persistent MMIO state in the ASIC. The current register values are captured during setup and reused as templates for SMC state table entries, so bit definitions must match the hardware reset and boot-programmed layout.

## Dependencies and Integration Points
The definitions are consumed with radeon `RREG32`/`WREG32_P` accessors, ATOMBIOS clock-divider results, and RV770 SMC table population. It must remain consistent with `rv730_dpm.c`; it is not interchangeable with RV740/RV770 register headers even when macro names are similar.

## Risks
The biggest risk is bitfield drift between ASIC variants. Macros for spread spectrum and PLL post dividers use RV730-specific layouts, and using them for RV740 or base RV770 would create invalid SMC register images. ODT pad-register writes alter low byte values only, so mask accuracy is important.

## Test Signals
Build coverage ensures macro references resolve. Runtime signals include successful RV730/RV710 clock register snapshots, correct SMC state encoding, stable memory timing programming, and ODT value restoration across DPM state switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv730d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv740_dpm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv740_dpm.c

## Purpose
`rv740_dpm.c` implements RV740-specific clock and ACPI-state encoding for the RV770 SMC DPM framework. RV740 differs from RV730/RV770 in SPLL post-divider layout, MCLK AD/DQ PLL fields, GDDR5 handling, memory spread spectrum, DLL speed selection, and strobe/EDC support.

## Important APIs, Types, and Functions
The file exports `rv740_get_decoded_reference_divider`, `rv740_get_dll_speed`, `rv740_populate_sclk_value`, `rv740_populate_mclk_value`, `rv740_read_clock_registers`, `rv740_populate_smc_acpi_state`, `rv740_enable_mclk_spread_spectrum`, and `rv740_get_mclk_frequency_ratio`. The local `dll_speed_table` maps memory data-rate ranges to DLL speed fields.

## Control Flow
ASIC setup calls `rv740_read_clock_registers` to snapshot SPLL/MPLL/DLL/spread-spectrum registers. SMC state conversion calls `rv740_populate_sclk_value` and `rv740_populate_mclk_value`, which fetch ATOM dividers, edit register templates, set spread-spectrum fields when available, encode DLL speed, and populate big-endian SMC table fields. ACPI state construction forces low-power PLL reset/bypass/sleep-style settings and zero clocks.

## State and Persistence
Runtime state resides in `struct rv7xx_power_info`, especially `pi->clk_regs.rv770`, `pi->mem_gddr5`, spread-spectrum flags, and MCLK thresholds. The DLL speed table is static constant-like driver data. Generated register images persist in SMC SRAM after upload and become active when the SMC switches states.

## Dependencies and Integration Points
This file depends on `rv740d.h`, `rv770.h`, `rv770_dpm.h`, ATOMBIOS divider/spread-spectrum APIs, and common helpers such as `rv770_map_clkf_to_ibias` and `rv770_populate_vddc_value`. `rv770_dpm.c` selects these helpers only for `CHIP_RV740`.

## Risks
Reference-divider encoding rejects unknown values; invalid ATOM data can abort state conversion. GDDR5 paths must keep AD and DQ PLL programming consistent. Spread-spectrum math uses integer division and a decoded reference divider; zero or unsupported dividers return errors. Incorrect DLL speed thresholds can destabilize memory at certain MCLK rates.

## Test Signals
Useful tests include RV740 DPM enable and power-state transitions on both GDDR3 and GDDR5 boards, SMC upload success, MCLK spread-spectrum enable/disable, strobe mode and EDC threshold behavior, ACPI low-power entry/exit, and memory stability across the DLL speed table boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv740_dpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv740d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv740d.h

## Purpose
`rv740d.h` defines RV740-specific clock-control and spread-spectrum register addresses and bitfields for SPLL, MPLL AD/DQ PLLs, DLL control, memory-clock power management, and spread-spectrum control.

## Important APIs, Types, and Functions
The header is macro-only. Important groups are `CG_SPLL_FUNC_CNTL*`, `MPLL_CNTL_MODE`, `MPLL_AD_FUNC_CNTL*`, `MPLL_DQ_FUNC_CNTL*`, `MCLK_PWRMGT_CNTL`, `DLL_CNTL`, `CG_SPLL_SPREAD_SPECTRUM*`, and `MPLL_SS1/2`. Field macros encode reference dividers, post dividers, feedback dividers, fractional feedback, IBIAS, VCO mode, reset/bypass/power bits, DLL speed, and spread-spectrum S/V values.

## Control Flow
`rv740_dpm.c` snapshots these registers, modifies template values for each SMC performance level, writes memory spread-spectrum enable bits in `MPLL_CNTL_MODE`, and builds ACPI-state register images that reset or bypass memory-clock paths.

## State and Persistence
The header stores no state. It defines MMIO state that is captured into `pi->clk_regs.rv770` and copied into SMC SRAM. Once uploaded, the SMC uses the encoded values to program hardware during DPM transitions.

## Dependencies and Integration Points
The macros are consumed by RV740-specific DPM helpers and selected from the generic RV770 DPM conversion path. They rely on standard radeon MMIO accessors and the SMC table layout defined elsewhere.

## Risks
RV740 shares macro names with RV730/RV770 but not necessarily identical layouts. `YCLK_POST_DIV_MASK`, `CLKR_MASK`, and spread-spectrum masks must match RV740 hardware or SMC-programmed MCLK transitions can fail. The header has no type safety, so misuse is caught only by review or hardware testing.

## Test Signals
Signals include successful compile of RV740 helpers, correct SMC table fields in debug instrumentation, stable DPM transitions, no memory corruption across MCLK changes, and correct spread-spectrum enable/disable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv740d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv770.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv770.c

## Purpose
`rv770.c` is the main RV7xx ASIC implementation for Radeon KMS. It covers UVD clock programming, golden-register setup, display page flips, temperature and legacy voltage handling, GART/AGP memory translation, memory-controller programming, CP microcode loading, GPU core initialization, VRAM/GTT placement, UVD init/resume, startup, suspend/resume, init, fini, and PCIe Gen2 link enablement.

## Important APIs, Types, and Functions
Major public entry points include `rv770_set_uvd_clocks`, `rv770_get_xclk`, `rv770_page_flip`, `rv770_page_flip_pending`, `rv770_get_temp`, `rv770_pm_misc`, `r700_cp_stop`, `r700_cp_fini`, `rv770_set_clk_bypass_mode`, `r700_vram_gtt_location`, `rv770_resume`, `rv770_suspend`, `rv770_init`, and `rv770_fini`. Static helpers include `rv770_init_golden_registers`, `rv770_pcie_gart_enable/disable/fini`, `rv770_agp_enable`, `rv770_mc_program`, `rv770_cp_load_microcode`, `rv770_gpu_init`, `rv770_mc_init`, `rv770_uvd_init/start/resume`, `rv770_startup`, and `rv770_pcie_gen2_enable`.

## Control Flow
`rv770_init` reads and validates ATOMBIOS, posts the card if needed, programs golden registers, initializes scratch/surface/clock/fence/AGP/MC/BO/firmware/PM/rings/UVD/IH/GART, then calls `rv770_startup`. Startup enables PCIe Gen2, initializes VRAM scratch, programs the MC, enables AGP or PCIe GART, initializes GPU graphics blocks, writeback, fences, UVD, IRQ/IH, rings, CP and DMA engines, IB pool, and audio. Suspend unwinds PM/audio/UVD/CP/DMA/IRQ/WB/GART; resume posts the card, reprograms golden registers, resumes PM, and reruns startup.

## State and Persistence
This file initializes persistent `rdev` state: chip configuration (`rdev->config.rv770`), memory controller placement, GART readiness, ring readiness, firmware pointers, UVD ring state, IRQ state, acceleration status, BIOS pointer, and GPU register state. Golden-register arrays are static data applied per family.

## Dependencies and Integration Points
It integrates with DRM framebuffer/CRTC objects, PCI resources, ATOMBIOS, firmware loading, radeon BO/TTM/GART/fence/ring/IB/audio/UVD/IRQ/PM subsystems, `rv770d.h` register definitions, and ASIC callback tables. It also delegates RV740 UVD clock programming to Evergreen code.

## Risks
Initialization ordering is critical: scratch before MC, GART before rings, firmware before CP resume, and IRQ before ring usage. Partial startup failure unwinds several but not all prior steps in the same local path, so error coverage matters. Golden-register tables are hardware-specific magic values; wrong family selection can break rendering. Page flip waits can time out, and PCIe Gen2 link changes depend on bridge capabilities.

## Test Signals
Signals include successful module probe, firmware load, `accel_working` true, GART enabled logs, CP/DMA/UVD ring tests, display page flips without stuck pending bits, suspend/resume cycles, temperature readings, audio init, and stable rendering on RV770/RV730/RV710/RV740 variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv770.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv770.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv770.h

## Purpose
`rv770.h` is a small private header exposing RV770-family helpers shared between the ASIC core and DPM implementation.

## Important APIs, Types, and Functions
It forward-declares `struct radeon_device` and `struct radeon_ps`, and declares `rv770_set_clk_bypass_mode`, `rv770_get_ps`, and `rv770_get_pi`. `rv770_get_ps` and `rv770_get_pi` are defined in `rv770_dpm.c` but used by chip-specific DPM overlays such as RV730/RV740.

## Control Flow
The header participates in cross-file call flow: the ASIC core can force clock bypass mode through `rv770_set_clk_bypass_mode`, while DPM overlays call `rv770_get_ps` and `rv770_get_pi` to retrieve typed private data from generic Radeon PM structures.

## State and Persistence
No state is defined here. The declared accessors expose persistent state owned by `rdev->pm.dpm.priv` and `radeon_ps.ps_priv`, both allocated and freed by DPM init/fini routines.

## Dependencies and Integration Points
This header decouples `rv730_dpm.c` and `rv740_dpm.c` from full private struct declarations at the call-site level while still sharing RV770 DPM accessors. It depends on struct definitions available through other included headers in implementation files.

## Risks
Because the header only forward-declares return types, callers must include the correct DPM headers before dereferencing fields. If the wrong DPM private type is attached to `rdev->pm.dpm.priv`, these accessors become unsafe casts.

## Test Signals
Compile coverage catches prototype mismatches. Runtime signals are indirect: RV770-family DPM setup must retrieve valid private pointers, and clock bypass mode must execute without accessing invalid registers on IGP paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv770.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv770_dma.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv770_dma.c

## Purpose
`rv770_dma.c` implements the RV7xx DMA copy callback used by the Radeon TTM memory manager to move GPU pages through the DMA ring instead of the graphics CP ring.

## Important APIs, Types, and Functions
The single exported function is `rv770_copy_dma(struct radeon_device *rdev, uint64_t src_offset, uint64_t dst_offset, unsigned num_gpu_pages, struct dma_resv *resv)`. It uses `struct radeon_sync`, `struct radeon_ring`, `struct radeon_fence`, DMA packet macros, reservation-object synchronization, and fence emission.

## Control Flow
The function creates a sync object, converts page count to DWORD count, splits the transfer into loops of at most `0xffff` DWORDs, locks the DMA ring for enough packet space, synchronizes against the reservation object and other rings, emits one DMA copy packet per chunk with low and high source/destination address fields, emits a fence, commits the ring, frees sync state, and returns the fence. Error paths undo the ring lock or free sync state and return `ERR_PTR`.

## State and Persistence
Persistent state is limited to ring write pointer advancement and emitted fences. The copy operation itself affects GPU memory at `dst_offset`. Reservation synchronization and the returned fence provide ordering state to callers.

## Dependencies and Integration Points
This file integrates with the radeon ring scheduler, TTM BO move path, DMA reservation objects, sync/fence subsystems, and RV770 DMA packet definitions from `rv770d.h`. The ring index comes from `rdev->asic->copy.dma_ring_index`.

## Risks
Address alignment is masked to 4-byte boundaries, so callers must provide page-aligned GPU addresses. Very large moves rely on correct loop chunking and ring-space accounting. Failure to synchronize reservations or emit fences correctly can cause memory corruption or use-before-copy races. If the DMA ring is not initialized, ring locking or fence emission fails.

## Test Signals
Signals include successful BO moves using the DMA ring, no `radeon: moving bo` errors, returned fences that signal, correct behavior for transfers larger than `0xffff` DWORDs, and memory validation after VRAM/GTT migration under rendering load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv770_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv770_dpm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv770_dpm.c

## Purpose
`rv770_dpm.c` implements SMC-backed dynamic power management for RV770-family ASICs and also provides shared parsing and helper logic reused by newer Evergreen-era code paths. It converts BIOS PowerPlay states into SMC state tables, uploads firmware/state to SMC SRAM, controls voltage/MVDD/backbias/PCIe Gen2/spread spectrum/thermal events/clock gating, and performs runtime power-state switching through SMC messages.

## Important APIs, Types, and Functions
Public helpers include `rv770_get_ps`, `rv770_get_pi`, `evergreen_get_pi`, `rv770_restore_cgcg`, `rv770_stop_dpm`, `rv770_dpm_enabled`, `rv770_enable_thermal_protection`, `rv770_enable_acpi_pm`, `rv770_get_seq_value`, `rv770_write_smc_soft_register`, `rv770_populate_smc_t`, `rv770_populate_smc_sp`, `rv770_map_clkf_to_ibias`, `rv770_populate_vddc_value`, `rv770_populate_mvdd_value`, `rv770_calculate_memory_refresh_rate`, `rv770_enable_backbias`, `rv770_setup_bsp`, `rv770_program_git/tp/tpp/sstp/vc`, `rv770_upload_firmware`, `rv770_populate_initial_mvdd_value`, `rv770_enable_voltage_control`, `rv770_halt_smc`, `rv770_resume_smc`, `rv770_set_sw_state`, `rv770_set_boot_state`, UVD clock ordering helpers, forced-level controls, SMC start/stop wrappers, setup/enable/late-enable/disable/set-state/init/fini/debug/current-clock functions, and `rv770_dpm_vblank_too_short`.

## Control Flow
`rv770_dpm_init` allocates `rv7xx_power_info`, probes max VDDC/platform caps, parses ATOM PowerPlay tables, initializes defaults and feature flags, and defines SMC SRAM layout. `rv770_dpm_setup_asic` snapshots clock and voltage registers, detects memory type and PCIe Gen2 status, configures ODT thresholds, enables ACPI PM, and applies ASPM settings.

`rv770_dpm_enable` enables voltage control, builds VDDC/MVDD tables, retrieves ODT values, enables backbias/spread-spectrum/thermal, programs timing and activity controls, enables dynamic PCIe Gen2, uploads SMC firmware, initializes the SMC state table, writes SMC soft-register response times, starts the SMC, starts global DPM, enables clock gating, and enables thermal auto throttle. `rv770_dpm_late_enable` configures thermal interrupt thresholds and tells the SMC to enable thermal interrupts.

Power-state switching restricts levels, orders UVD clocks, halts the SMC, uploads a converted driver state, programs memory timings, adjusts ODT before and after the transition when needed, resumes the SMC, and sends `SwitchToSwState`. Disable unwinds thermal/spread-spectrum/PCIe/IRQ/clock-gating/DPM/SMC state and resets SMIO status.

## State and Persistence
Private `rv7xx_power_info` stores SMC table image, clock-register templates, voltage and MVDD tables, thresholds, memory type, PCIe status, feature flags, soft-register offsets, ODT values, active throttle sources, and timing constants. Parsed `rv7xx_ps` objects persist in `radeon_ps.ps_priv`. SMC SRAM persists uploaded firmware, soft registers, initial/ACPI/driver state tables, and state transitions until reset or DPM disable.

## Dependencies and Integration Points
The file depends on `rv770d.h`, `rv770_dpm.h`, `r600_dpm.h`, `cypress_dpm.h`, ATOMBIOS PowerPlay/clock/voltage/spread-spectrum/memory-info APIs, SMC communication helpers, RV730/RV740 chip overlays, PCIe indirect registers, IRQ thermal handling, UVD clock callbacks, debugfs, and common Radeon PM policy.

## Risks
SMC sequencing is failure-prone: firmware upload, table copy, halt/resume, and message acknowledgement all need correct ordering. Voltage-table construction can fail if VREG steps exceed `MAX_NO_VREG_STEPS` or if requested voltages do not map to GPIO entries. Family dispatch must choose the correct clock encoder. Memory timing and ODT changes can destabilize memory if thresholds or ATOM timing calls are wrong. Thermal IRQ programming and dynamic PCIe Gen2 must be unwound during disable. `rv770_dpm_vblank_too_short` disables MCLK switching on desktop RV770 by forcing the limit high, which is intentional but affects performance/power behavior.

## Test Signals
Signals include successful SMC firmware upload and state-table copy, DPM enable/disable and late thermal enable without errors, SMC message acknowledgements, stable state transitions under AC/DC/UVD changes, correct forced high/low behavior, valid debugfs current-level output, stable suspend/resume with DPM active, thermal interrupt delivery, and no memory errors across MCLK/ODT changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/rv770_dpm.c -->
