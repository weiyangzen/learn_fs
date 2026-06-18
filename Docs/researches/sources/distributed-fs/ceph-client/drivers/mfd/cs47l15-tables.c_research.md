# sources/distributed-fs/ceph-client/drivers/mfd/cs47l15-tables.c

## Purpose
This file provides CS47L15-specific Madera regmap data: a revision patch, 16-bit register defaults, readable/volatile predicates for 16-bit and 32-bit windows, ADSP memory detection, and exported I2C/SPI regmap configurations. It is data/control policy for the Madera core rather than a probing driver.

## Important APIs, types, and functions
`cs47l15_patch()` applies `cs47l15_reva_16_patch` with `regmap_register_patch()` and logs failures. The large `cs47l15_reg_default` table seeds the Maple cache for 16-bit control registers, including tone/haptics, clocks/FLLs, accessory detection, inputs, outputs, AIFs, mixers, EQ/DRC/filter coefficients, GPIOs, and IRQ masks.

`cs47l15_is_adsp_memory()` recognizes DSP1 PM/XM/YM/ZM memory ranges. `cs47l15_16bit_readable_register()` permits the main Madera 16-bit register map, including status, control, audio routing, DSP-facing controls, GPIO, and IRQ registers. `cs47l15_16bit_volatile_register()` marks reset/revision, write sequencer controls, hardware status, sample-rate status, HP/mic/headphone-detect status, output/input status, SPDIF status, FX status, and IRQ status/raw status as uncached volatile. The 32-bit readable and volatile callbacks cover write-sequencer storage, OTP HP detect calibration, DSP1 configuration/status/error registers, and ADSP memory; they treat all 32-bit ranges as volatile.

Four exported regmap configs are provided: `cs47l15_16bit_spi_regmap`, `cs47l15_16bit_i2c_regmap`, `cs47l15_32bit_spi_regmap`, and `cs47l15_32bit_i2c_regmap`. SPI variants include pad bits; 32-bit variants use `reg_stride = 2` and have no defaults.

## Control flow
Runtime control flow is minimal. The Madera parent calls the patch helper during device initialization, then uses the exported regmap configs to decide which registers can be read and cached. The callbacks are pure switch/range classifiers.

## State and persistence behavior
State persistence is through regmap cache defaults and volatility policy. Nonvolatile 16-bit registers can be cached/restored from defaults; volatile registers and 32-bit DSP/memory regions are read from hardware. The register patch changes hardware/cache initialization behavior for affected revision registers.

## Dependencies and integration points
The file depends on Madera core/register headers, Linux regmap, module exports, and device logging. It integrates into Madera bus/core code that selects CS47L15-specific regmaps and patch routines.

## Risks and edge cases
The access tables are large and manual; missing readable entries break legitimate child-driver access, while missing volatile entries can cache status or IRQ state incorrectly. Treating all ADSP memory as volatile is conservative but expensive. Patch failure abort behavior depends on callers checking `cs47l15_patch()`. Divergence between I2C/SPI 16-bit configs would be a regression; they should differ only by SPI pad bits.

## Test signals
Useful signals include regmap access-table tests for representative clock/audio/IRQ/DSP addresses, verification that volatile status registers are not cached, patch application failure injection, I2C/SPI config parity, and boot tests with Madera children exercising codec, GPIO, IRQ, and DSP access.
