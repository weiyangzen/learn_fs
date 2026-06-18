# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/process_pptables_v1_0.c

## Purpose

This file parses Tonga/Polaris-style PowerPlay table v1.0 data from VBIOS and builds normalized driver tables under `hwmgr->pptable`. It translates firmware offsets, counts, voltages, clock dependencies, fan controls, PowerTune limits, PCIe states, GPIO VRHot data, and VCE states into hwmgr structures.

## Important APIs, Types, and Functions

The exported `pptable_v1_0_funcs` provides `pptable_init` and `pptable_fini`. `get_number_of_powerplay_table_entries_v1_0()` returns the firmware state count. `get_powerplay_table_entry_v1_0()` converts a state entry and invokes an ASIC callback to fill hardware power-state data, patches boot states, and populates `hwmgr->vce_states`.

Key internal helpers include `get_powerplay_table()` for ATOM table lookup and caching, `set_platform_caps()` for platform capability mapping, `init_thermal_controller()`, `init_over_drive_limits()`, `init_clock_voltage_dependency()`, and `init_dpm_2_parameters()`. Revision-aware helpers parse SCLK, PCIe, fan, and PowerTune variants.

## Control Flow and State

Initialization allocates `struct phm_ppt_v1_information`, fetches or reuses `hwmgr->soft_pp_table`, validates table revision and state-array presence, maps platform caps, initializes thermal/fan data, overdrive limits, dependency tables, and DPM2/PPM fields. Cleanup frees every allocated subtable and clears pointers. Persistent state is stored in `hwmgr->pptable`, `hwmgr->dyn_state.cac_dtp_table`, `hwmgr->platform_descriptor`, `hwmgr->thermal_controller`, and cached VBIOS table fields.

## Dependencies and Integration

The parser depends on ATOM BIOS access through `smu_atom_get_data_table`, endian helpers, kernel allocation, `pp_debug` assertions, `phm_cap_set/unset`, and layout definitions from `pptable_v1_0.h`. ASIC hwmgr code consumes the resulting `phm_ppt_v1_information` and calls the exported entry APIs during power-state enumeration.

## Risks and Test Signals

Many offsets and counts are firmware-provided and used for pointer arithmetic; invalid VBIOS can cause failed assertions or unsafe reads if a path lacks bounds checks. `get_pcie_table()` assumes SCLK dependency data exists because it compares PCIe entries to `vdd_dep_on_sclk->count`. The entry-index checks use `<= ucNumEntries`, which is suspicious because valid zero-based indices normally end at `ucNumEntries - 1`. Test signals include boot logs for PP_ASSERT failures, correct DPM/fan/overdrive sysfs data, VCE state availability, and leak-free unload paths.
