# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ni_dpm.c

## Purpose

`ni_dpm.c` implements dynamic power management for Northern Islands/Cayman Radeon GPUs. It parses ATOM PowerPlay tables, constructs driver-private NI power states, initializes SMC firmware tables, programs voltage/clock/memory timing data, manages clock gating and PCIe gen2 behavior, enables CAC/power containment, and performs runtime power-state transitions.

The file is highly stateful: it bridges VBIOS policy, driver dynamic limits, hardware registers, SMC SRAM layouts from `nislands_smc.h`, and runtime requested/current power states.

## Important APIs, Types, and Data

Static data includes Cayman CAC weight tables for XT/Pro/LE device IDs and register sequences for coarse/fine grain clock gating and light sleep.

Key helpers:

- `ni_get_pi()` and `ni_get_ps()` return NI-specific power-info and power-state private structures.
- `ni_dpm_vblank_too_short()` and `ni_apply_state_adjust_rules()` adjust requested states around display constraints, DC limits, blacklisted clocks, voltage dependencies, and monotonic clock/voltage requirements.
- `ni_dpm_force_performance_level()` sends SMC messages to force high, low, or automatic DPM levels.
- `ni_process_firmware_header()` reads SMC SRAM offsets for state, soft registers, MC register tables, fan, arb, CAC, and SPLL tables.
- `ni_init_smc_table()`, `ni_upload_sw_state()`, `ni_convert_power_state_to_smc()`, and related helpers synthesize `NISLANDS_SMC_STATETABLE` and `NISLANDS_SMC_SWSTATE` records.
- `ni_calculate_sclk_params()`, `ni_populate_sclk_value()`, `ni_populate_mclk_value()`, and `ni_init_smc_spll_table()` compute PLL register values and the SMC SPLL lookup table.
- `ni_initialize_mc_reg_table()`, `ni_populate_mc_reg_table()`, and `ni_upload_mc_reg_table()` parse/copy dynamic AC memory register tables and convert them to SMC format.
- `ni_initialize_smc_cac_tables()`, `ni_initialize_hardware_cac_manager()`, `ni_enable_smc_cac()`, and `ni_enable_power_containment()` configure CAC leakage/power tables and TDP clamping.
- `ni_dpm_setup_asic()`, `ni_dpm_enable()`, `ni_dpm_disable()`, `ni_dpm_pre_set_power_state()`, `ni_dpm_set_power_state()`, `ni_dpm_post_set_power_state()`, `ni_dpm_init()`, and `ni_dpm_fini()` are the main lifecycle entry points.

## Control Flow

`ni_dpm_init()` allocates `struct ni_power_info`, initializes embedded Evergreen/RV770 power info, reads platform capabilities, parses PowerPlay and extended power tables, builds a display-clock voltage dependency table, patches leakage placeholders, chooses default response times and reference dividers, sets clock-gating/power feature flags, reads voltage-control capabilities, chooses CAC weights by PCI device ID, enables default CAC/power-containment/SQ ramping policy, and normalizes DC clock limits.

`ni_dpm_setup_asic()` performs early hardware setup: load MC firmware, snapshot boot clock registers, read arb registers and memory type, advertise PCIe gen2 where ACPI supports performance requests, read current PCIe gen2 status, and enable ACPI PM.

`ni_dpm_enable()` is the main activation sequence. It programs default clock-gating sequences, enables voltage control and voltage tables, initializes dynamic AC memory tables, enables spread spectrum/thermal/display-gap/voltage-control support, enables dynamic PCIe gen2, uploads SMC firmware, reads SMC table offsets, copies MC arb timing from F0 to F1, initializes the SMC state table, SPLL table, arb index, MC register table, CAC tables, hardware CAC registers, TDP limits, response times, starts the SMC, notifies display state, enables SCLK/MCLK control, starts DPM, enables clock gating, enables thermal auto-throttle, and records the boot power state as current.

Power-state switching is split into three public phases. `ni_dpm_pre_set_power_state()` copies the requested state and applies display/DC/voltage adjustment rules. `ni_dpm_set_power_state()` restricts levels, adjusts UVD clocks before lowering engine clocks, disables power containment/CAC, halts SMC, optionally notifies UVD high-speed policy, uploads the new SMC software state and MC register table, programs memory timings, resumes SMC, asks SMC to switch state, adjusts UVD clocks after raising engine clocks, re-enables CAC and power containment, and updates TDP limits. `ni_dpm_post_set_power_state()` makes the requested state current.

`ni_dpm_disable()` reverses runtime policy: clears voltage control, disables thermal protection, power containment, CAC, spread spectrum, thermal auto-throttle, dynamic PCIe gen2, thermal IRQ, clock-gating sequences, DPM global enable, resets defaults, stops SMC, forces MC arb back to F0, and restores boot state as current.

## State and Persistence Behavior

`rdev->pm.dpm.priv` owns `struct ni_power_info`, which embeds Evergreen/RV770 state, clock-register snapshots, MC register tables, CAC data, SMC offsets, current/requested `struct ni_ps`, and scratch SMC table buffers. `rdev->pm.dpm.ps` owns parsed `struct radeon_ps` entries, each with a heap-allocated `struct ni_ps`.

The file writes persistent runtime policy into SMC SRAM using `rv770_copy_bytes_to_smc()` and `rv770_write_smc_sram_dword()`. It writes hardware registers for CAC weights, MC timing, PCIe link behavior, clock gating, PLL programming source tables, and soft registers. Current/requested power states are copied into `evergreen_power_info` with `ps_priv` redirected to stable storage inside `ni_power_info`.

Memory allocated in init is released by `ni_dpm_fini()`: per-state `ps_priv`, the power-state array, NI private info, display-clock dependency entries, and the extended power table.

## Dependencies and Integration Points

This file depends on ATOMBIOS PowerPlay table definitions, SMC layout definitions from `nislands_smc.h`, RV770/Evergreen/BTC/Cypress DPM helpers, Radeon PM core state, ACPI PCIe performance request helpers, clock-divider calculation, voltage table construction, thermal/IRQ support, UVD clock helpers, and MC firmware loading from `ni.c`.

It integrates with `ni.h`/`ni.c` for ASIC setup and MC firmware, with display code through vblank/display-clock constraints, with UVD through special UVD clock ordering and SMC notifications, with ACPI for PCIe gen2 requests, and with debugfs/PM reporting through current SCLK/MCLK and performance-level print helpers.

## Risks and Edge Cases

- Many functions assume valid parsed PowerPlay data and at least one performance level; malformed VBIOS tables can lead to failed init or invalid states.
- `ni_apply_state_adjust_rules()` mutates a copied requested state; callers must use the adjusted `eg_pi->requested_rps`, not the original pointer.
- DPM enable order is fragile: SMC firmware upload, header processing, state-table upload, SPLL table, arb index, CAC, TDP, and SMC start must happen in sequence.
- Endianness conversion is pervasive because SMC structures are big-endian. Missing `cpu_to_be*()`/`be*_to_cpu()` conversions corrupt firmware tables.
- CAC and power containment can be disabled dynamically on table/init failure, changing later behavior without failing the whole enable path in some cases.
- Dynamic AC timing depends on ATOM MC tables and limited SMC array sizes; bounds failures disable or fail the feature.
- Display constraints can force all MCLK/VDDCI levels to the highest requested value when multiple CRTCs or short vblank make switching unsafe.
- SMC message failures during forced levels, CAC, power containment, or state switch produce `-EINVAL` and can leave hardware in an intermediate policy state unless caller unwinds.
- `ni_dpm_init()` has early returns after allocation paths where cleanup responsibility must be understood by the caller or future edits.

## Test Signals

Validation should include boot with DPM enabled, successful SMC firmware upload and header parsing, no DPM enable error logs, stable idle/load SCLK and MCLK transitions, correct behavior under AC versus DC limits, multi-display and short-vblank scenarios that disable MCLK switching, UVD playback state changes, PCIe gen2 link switching, thermal auto-throttle behavior, CAC/power-containment messages, suspend/resume with DPM, and debugfs current performance-level output matching hardware load. VBIOS diversity is important: Cayman XT/Pro/LE boards, GDDR5 threshold variants, and boards with/without voltage GPIO and ACPI PCIe performance requests exercise distinct branches.
