# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600_dpm.c

## Purpose

`r600_dpm.c` provides shared dynamic power-management helpers for R600-family Radeon ASICs. It prints PowerPlay classifications, computes display timing and transition thresholds, programs clock/voltage/power-level registers, starts and stops DPM, configures thermal interrupt ranges, parses AtomBIOS PowerPlay extension tables into Radeon runtime structures, and exposes PCIe capability helpers.

## Important APIs, Types, and Functions

- `r600_utc` and `r600_dtc`: default up/down trend-control arrays sized by `R600_PM_NUMBER_OF_TC`.
- Diagnostic helpers `r600_dpm_print_class_info`, `r600_dpm_print_cap_info`, and `r600_dpm_print_ps_status`: log PowerPlay state metadata.
- Display helpers `r600_dpm_get_vblank_time` and `r600_dpm_get_vrefresh`: inspect enabled CRTCs to derive vblank duration and refresh rate.
- Transition math helpers `r600_calculate_u_and_p` and `r600_calculate_at`: compute bitfield parameters for bias/threshold programming.
- Register wrappers such as `r600_dynamicpm_enable`, `r600_enable_sclk_control`, `r600_enable_mclk_control`, `r600_set_bsp`, `r600_set_at`, `r600_set_tc`, `r600_engine_clock_entry_*`, `r600_vid_rt_*`, `r600_voltage_control_*`, and `r600_power_level_*`: small, named writes to DPM control registers.
- `r600_start_dpm` and `r600_stop_dpm`: enable/disable the hardware dynamic power manager around clock-control and SPLL-bypass sequencing.
- `r600_dpm_late_enable`: enables internal thermal interrupts after IRQ installation.
- `r600_parse_extended_power_table` and `r600_free_extended_power_table`: ingest and release optional PowerPlay fan, dependency, leakage, VCE/UVD/SAMU/ACP/PPM/PowerTune data.
- `r600_get_platform_caps`, `r600_get_pcie_gen_support`, `r600_get_pcie_lane_support`, and `r600_encode_pci_lane_width`: expose firmware/platform capability interpretation.

## Control Flow

Most register helpers are direct read-modify-write wrappers. Higher-level start/stop flow disables software clock controls, enables global DPM, waits for vblank on both CRTCs, toggles SPLL bypass twice while polling `SPLL_CHG_STATUS`, then re-enables SCLK and MCLK control. Stop simply clears global DPM enable.

Thermal late enable checks whether IRQs are installed and whether the configured thermal sensor is an internal type. If so, it clamps the supported range to `R600_TEMP_RANGE_MIN` and `R600_TEMP_RANGE_MAX`, writes high/low/DPM thermal thresholds, records the range in `rdev->pm.dpm.thermal`, sets `rdev->irq.dpm_thermal`, and updates IRQ programming.

Power table parsing starts from AtomBIOS `PowerPlayInfo`. `r600_get_platform_caps` reads platform caps and response times. `r600_parse_extended_power_table` conditionally parses structures based on `usTableSize`, table format, and extended-header size. It fills fan control parameters, SCLK/MCLK/VDDC/VDDCI/MVDD dependency tables, DC clock-voltage limits, phase-shedding limits, TDP and CAC fields, leakage entries, and extended VCE/UVD/SAMU/PPM/ACP/PowerTune tables. Each table uses BIOS offsets relative to `data_offset` and converts little-endian fields into host-order Radeon structures.

Allocation failures trigger partial cleanup either by freeing specific earlier dependency arrays or by calling `r600_free_extended_power_table`. Normal teardown calls `r600_free_extended_power_table`, which frees every dynamically allocated dependency table and optional structure.

## State and Persistence Behavior

The file persists parsed BIOS data into `rdev->pm.dpm`, especially `platform_caps`, response times, fan settings, thermal thresholds, power-control limits, media clock states, and `dyn_state` dependency tables. Register helpers persist state directly in GPU MMIO registers. `r600_power_level_get_current_index` and `r600_power_level_get_target_index` read current hardware profile state. Allocated BIOS-derived tables remain until explicitly freed.

## Dependencies and Integration Points

Dependencies include `radeon_device`, DRM CRTC/mode structures, AtomBIOS table structures from `atom.h`, endian helpers, Radeon IRQ setup, Radeon mode info, and `r600d.h` register/bitfield macros. ASIC-specific DPM implementations call these shared helpers while building or switching power states. Display timing helpers integrate DPM decisions with active KMS CRTCs; video-state helpers classify UVD states; PCIe helpers feed link-speed/link-width selection.

## Risks and Edge Cases

- AtomBIOS offsets and table counts are trusted after limited size/header checks. Malformed BIOS data can point parsing beyond the image or create oversized allocations.
- Several hardware wait loops poll for up to `usec_timeout` but do not report timeout failure to callers.
- Partial allocation rollback is manual and nonuniform; newly added tables must be added to both failure cleanup and `r600_free_extended_power_table`.
- `r600_free_extended_power_table` frees pointers but does not null them or reset counts, so callers must avoid double-free or reuse after free.
- Thermal constants are marked with a comment questioning whether they are appropriate; wrong thresholds can affect reliability or fan behavior.
- Display helpers return the first enabled CRTC only, which may not reflect multi-display worst-case timing.
- Direct register wrappers assume callers supply valid enum indices and bitfield values.

## Test Signals

Test signals include boot/resume on R600/R700 boards with varied PowerPlay table revisions, DPM enable/disable traces, thermal interrupt delivery, fan-control behavior, power-state switching under 2D/3D/UVD/VCE loads, memory-leak testing around parse/free failure injection, malformed BIOS table fuzzing in a harness, and PCIe link-gen/lane negotiation checks. Runtime telemetry should confirm expected SCLK/MCLK/voltage transitions and no timeout-induced hangs during SPLL or power-level waits.
