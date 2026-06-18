# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ppatomfwctrl.c

## Purpose
`ppatomfwctrl.c` is the atomfirmware-era counterpart to `ppatomctrl.c`, used by Vega/SOC15-style power management. It reads atomfirmware v2.1 master data/command tables, normalizes voltage object v4, clock, AVFS, GPIO, boot, and SMC DPM information, and exposes those values to ASIC hwmgr code.

## Important APIs and functions
Exports include `pp_atomfwctrl_is_voltage_controlled_by_gpio_v4()`, `pp_atomfwctrl_get_voltage_table_v4()`, `pp_atomfwctrl_get_gpu_pll_dividers_vega10()`, `pp_atomfwctrl_get_avfs_information()`, `pp_atomfwctrl_get_gpio_information()`, `pp_atomfwctrl_get_clk_information_by_clkid()`, `pp_atomfwctrl_get_vbios_bootup_values()`, and `pp_atomfwctrl_get_smc_dpm_information()`. Private helpers walk voltage object v4 lists, fetch voltage info tables, and copy firmware info revisions 3.1/3.2.

## Control flow
Voltage functions fetch `voltageobject_info`, walk variable-size `union atom_voltage_object_v4` entries by `object_size`, and either copy GPIO LUT entries or SVID2 control metadata. PLL and clock functions execute atomfirmware command-table entries selected through `GetIndexIntoMasterCmdTable()` and decode the output overlay from the same parameter buffer. AVFS parsing handles `asic_profiling_info` revisions 4.1 and 4.2. Boot-value parsing handles `firmwareinfo` revisions 3.1 and 3.2, with optional SMU clock queries left as zero if command execution fails.

## State and persistence behavior
The file has no global mutable state. It mutates caller-provided output structs. Command-table calls query firmware-calculated values but this file does not retain firmware table pointers. Some output fields are explicitly zero-initialized on older table revisions, while most functions assume the caller supplied a clean or fully overwritten buffer.

## Dependencies and integration points
It depends on `ppatomfwctrl.h`, `atomfirmware.h`, `atom.h`, `pp_debug.h`, `smu_atom_get_data_table()`, `amdgpu_atom_execute_table()`, atomfirmware v2.1 master table index macros, and endian conversion helpers. Vega10 hwmgr uses AVFS information and fuse-related coefficients; Vega12 process PPTable code uses SMC DPM information; SOC15 clock setup uses PLL divider and SMU clock-info helpers.

## Risks and test signals
Variable-sized voltage object walking depends on nonzero, valid `object_size`. SVID2 mode fills metadata and leaves voltage entry `count` at zero, so callers must branch on mode. AVFS rejects unknown revisions, which can block newer firmware until code is updated. In the v4.2 AVFS branch, `ulPhyclk2GfxclkM1` is read from the base `profile` variable instead of `profile_v4_2`; the pointer is the same allocation but the mixed type is fragile. Tests should cover voltage object v4 lookup, over-limit entries, AVFS 4.1/4.2/unsupported revisions, firmwareinfo 3.1/3.2 boot paths, clock command failures, and SMC DPM table copies.
