# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ppatomctrl.c

## Purpose
`ppatomctrl.c` is the legacy ATOM BIOS control adapter for AMD PowerPlay hwmgr code. It converts ATOM data-table and command-table formats into normalized hwmgr structures for memory-controller timing, PLL divider calculation, voltage/GPIO control, spread spectrum, eFuse/leakage values, AVFS parameters, SMC clock ranges, and voltage rails.

## Important APIs and functions
Exports cover MC timing (`atomctrl_initialize_mc_reg_table*`, `atomctrl_set_engine_dram_timings_rv770()`, `atomctrl_set_ac_timing_ai()`), PLL/clock helpers (`atomctrl_get_memory_pll_dividers_*`, `atomctrl_get_engine_pll_dividers_*`, `atomctrl_get_dfs_pll_dividers_vi()`, reference clocks), voltage/GPIO helpers (`atomctrl_get_voltage_table_v3()`, EVV helpers, SVID2, voltage ranges, GPIO pin lookup), spread spectrum/eFuse helpers, and AVFS/leakage helpers. Private helpers parse variable-sized BIOS structures for VRAM info, voltage objects, GPIO LUTs, spread-spectrum assignments, and EDC tables.

## Control flow
Most functions either fetch a data table via `smu_atom_get_data_table()` and copy little-endian firmware fields into native hwmgr structs, or prepare an ATOM command parameter block and execute it through `amdgpu_atom_execute_table()`. MC register initialization reads `VRAM_Info`, finds the memory clock patch table, extracts register addresses until the placeholder/end bit, then walks timing data blocks matching the requested VRAM module ID. Voltage helpers walk variable-sized voltage objects within `VoltageObjectInfo`; GPIO modes build voltage tables, while EVV paths call `GetVoltageInfo`.

## State and persistence behavior
The file stores no persistent mutable state. It mutates caller-provided output buffers and writes through pointers such as `*voltage`, `*efuse`, `*shared_rail`, `*max_vddc`, and `*min_vddc`. Several command-table calls can program or query firmware/BIOS state, especially dynamic memory settings and voltage/efuse commands. BIOS table pointers are borrowed from ATOM/SMU accessors and not retained.

## Dependencies and integration points
Dependencies include `atom.h`, `atombios.h`, `cgs_common.h`, `pp_debug.h`, `smu_atom_get_data_table()`, `amdgpu_atom_execute_table()`, endian helpers, ATOM table structs, and hwmgr dynamic state. It is used by SMU7/Fiji-era hwmgr code for voltage tables and leakage handling, by memory/clock setup code for PLL divider calculations, and by ASIC-specific paths that need ATOM BIOS-derived AVFS or SMC range data.

## Risks and test signals
The code parses variable-length firmware tables with pointer arithmetic, so malformed table sizes, missing sentinels, or too many entries are high-risk inputs. `atomctrl_get_svi2_info()` dereferences a voltage lookup result without checking for NULL. `atomctrl_get_smc_sclk_range_table()` copies `ucSclkEntryNum` entries without checking `MAX_SCLK_RANGE`. `atomctrl_read_efuse()` assumes sane bit ranges. `get_edc_leakage_table()` computes an offset but returns the original base pointer, which looks suspicious. Tests should cover invalid/missing VBIOS tables, voltage lookup misses, over-limit entries, spread-spectrum revision scaling, eFuse masks, leakage-bin mapping, and SCLK range overflow behavior.
