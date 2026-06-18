# sources/distributed-fs/ceph-client/drivers/firmware/cirrus/test/cs_dsp_mock_regmap.c

## Purpose
This file creates cache-only mock regmaps for Cirrus DSP KUnit tests. It models valid address ranges, value widths, endian behavior, register defaults, and dirty-cache detection without allowing real bus IO.

## Important APIs, Types, And Functions
The mock `regmap_bus` implements read/write/gather_write callbacks that fail the KUnit test if actual bus access occurs. It defines regmap configs for ADSP2 32-bit, ADSP2 16-bit, and HALO, including access tables, defaults, strides, endian formats, and max registers. Exported constants expose mock system/core base addresses.

Utility APIs include `cs_dsp_mock_regmap_drop_range()`, `cs_dsp_mock_regmap_drop_regs()`, `cs_dsp_mock_regmap_drop_bytes()`, `cs_dsp_mock_regmap_drop_system_regs()`, `cs_dsp_mock_regmap_is_dirty()`, and `cs_dsp_mock_regmap_init()`.

## Control Flow, State, And Persistence
`cs_dsp_mock_regmap_init()` selects a config from `dsp->type` and `dsp->rev`, creates a devm regmap, and switches it to cache-only mode so production code writes accumulate in cache. Dirty checking temporarily disables cache-only and calls `regcache_sync()`; any remaining dirty entry triggers the mock bus write path and sets `priv->saw_bus_write`.

## Dependencies And Integration Points
The file depends on KUnit, regmap, WMFW memory types, and `struct cs_dsp_test`. It integrates with mock memory maps and firmware builders by providing the backing regmap used by `cs_dsp` production code during tests.

## Risks And Test Signals
Risks include stale or incomplete address ranges causing false failures, default registers masking expected writes, and dirty-check helpers dropping too much or too little. Test signals should cover initialization for each DSP type/revision, cache-only enforcement, system-register drop behavior, dirty detection after expected and unexpected writes, and access denial for out-of-range addresses.
