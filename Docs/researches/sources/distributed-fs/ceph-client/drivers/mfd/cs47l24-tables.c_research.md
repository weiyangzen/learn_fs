# sources/distributed-fs/ceph-client/drivers/mfd/cs47l24-tables.c

## Purpose
This file provides CS47L24-specific Arizona regmap data: a revision-A patch, a regmap IRQ chip, register defaults, readable/volatile predicates, ADSP memory range detection, and the exported SPI regmap configuration. It supplies static policy consumed by the Arizona MFD core.

## Important APIs, types, and functions
`cs47l24_patch()` applies `cs47l24_reva_patch` through `regmap_register_patch()`. `cs47l24_irqs` maps Arizona logical IRQ IDs across six interrupt status registers, covering GPIO, DSP RAM ready and DSP IRQs, speaker overheat/shutdown/shorts, write sequencer, DRC/ASRC/FLL/clock events, control-interface errors, mixer dropped samples, headphone completion/short-circuit, and boot done. `cs47l24_irq` exports the regmap IRQ chip with status, mask, and ack bases.

`cs47l24_reg_default` seeds defaults for SPI control, tones, haptics, clocks/FLLs, mic bias, inputs, outputs, AIFs, mixers, EQ/DRC/HPLPF/ASRC/ISRC, DSP2/DSP3 controls, GPIO/pads, and interrupt masks. `cs47l24_is_adsp_memory()` recognizes DSP2 and DSP3 PM/ZM/XM/YM memory ranges. `cs47l24_readable_register()` admits the supported Arizona control, routing, DSP, IRQ, status, and ADSP-memory address set. `cs47l24_volatile_register()` marks reset/revision, write sequencer, haptics/sample-rate/async/HP/input/output/IRQ/raw IRQ/FX/ASRC/DSP status and DMA/scratch/control registers as volatile, plus ADSP memory.

`cs47l24_spi_regmap` configures 32-bit big-endian register addresses, 16-bit big-endian values, 16 pad bits, `CS47L24_MAX_REGISTER` covering DSP3 YM, Maple cache, defaults, and the readable/volatile callbacks.

## Control flow
There is no probe function in this file. The Arizona parent driver imports the patch, IRQ chip, and regmap config during device setup. The patch helper is the only active function; the remaining callbacks classify addresses for regmap access and caching.

## State and persistence behavior
Persistence is governed by the default table and volatility callback. Stable control registers can live in the Maple cache; volatile status/IRQ/DSP/DMA regions are fetched from hardware. IRQ state is acknowledged through regmap-irq using the exported chip configuration.

## Dependencies and integration points
The file depends on Arizona MFD core/register headers, Linux regmap IRQ definitions through included core headers, module exports, and device definitions. It integrates with the Arizona parent and with downstream codec/DSP/GPIO/IRQ users that rely on these access policies.

## Risks and edge cases
Manual register allowlists can silently block valid access or cache changing state if incomplete. `CS47L24_NUM_ISR` is defined but not used in this file, so IRQ register count is governed by `cs47l24_irq.num_regs = 6`; future edits should avoid stale constants. Only an SPI regmap config is exported here; if another bus is added it needs an explicit config. IRQ mapping array size is `ARIZONA_NUM_IRQ`, so logical IRQ enum changes can create sparse or missing mappings.

## Test signals
Test signals include patch application, regmap readable/volatile classification for representative audio, IRQ, DSP2/DSP3 memory, and DMA addresses, regmap IRQ chip registration and virtual IRQ mapping, cache behavior for interrupt/status registers, and hardware boot smoke tests covering Arizona child drivers.
