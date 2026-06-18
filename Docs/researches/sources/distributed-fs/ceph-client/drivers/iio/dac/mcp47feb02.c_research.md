## sources/distributed-fs/ceph-client/drivers/iio/dac/mcp47feb02.c

Purpose: I2C regmap IIO driver for the Microchip MCP47FEBxx and MCP47FVBxx multi-channel DAC families. It covers 1/2/4/8-channel devices, 8/10/12-bit resolutions, EEPROM and non-EEPROM variants, VDD/internal/external VREF selections, per-channel labels, scale lists, powerdown modes, and PM restore.

Important APIs/types/functions: `struct mcp47feb02_features` describes device family/resolution/channel count/vref1/eeprom. `struct mcp47feb02_data` stores channel data, locks, scale tables, active channel mask, labels, regmap, and reference-buffer flags. Important functions include `mcp47feb02_parse_fw()`, `mcp47feb02_init_ctrl_regs()`, `mcp47feb02_init_scales_avail()`, `mcp47feb02_set_scale()`, `mcp47feb02_write_to_eeprom()`, `store_eeprom_store()`, and suspend/resume.

Control flow: Probe selects EEPROM-capable or volatile-only regmap config, parses child nodes as the active channel set with required labels, initializes a mutex, enables `vdd` and optional `vref`/`vref1`, reads control registers to populate channel reference/gain/powerdown cache, builds scale lists from supplies or internal bandgap, and registers. Raw and scale writes update hardware and cache under lock. EEPROM devices expose `store_eeprom`; FVB devices omit it.

State and persistence: Volatile channel state is mirrored in `chdata`. EEPROM-capable devices can persist DAC, VREF, powerdown, gain, and I2C address bits after wiperlock checks and EEWA polling. Suspend writes selected powerdown modes and cached DAC data; resume rewrites DAC data, VREF/gain, and normal operation.

Dependencies and integration points: Uses I2C regmap with access tables/cache, regulators, firmware child nodes/properties, IIO labels/ext-info, and PM sleep ops. It integrates many compatible IDs through shared feature tables.

Risks and test signals: High-risk areas include firmware requiring labels and active child nodes, odd-channel use of VREF1 on 4/8-channel devices, reference mismatch handling that logs but does not rewrite until scale write, EEPROM lock/EEWA polling, and resume register sequencing. Tests should cover EEPROM vs FVB configs, all resolutions, sparse active channels, scale availability for VREF/VREF1 absent/present, powerdown mode encoding, and store_eeprom failure paths.
