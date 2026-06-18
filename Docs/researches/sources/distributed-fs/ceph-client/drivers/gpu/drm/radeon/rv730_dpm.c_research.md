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
