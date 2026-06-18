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
