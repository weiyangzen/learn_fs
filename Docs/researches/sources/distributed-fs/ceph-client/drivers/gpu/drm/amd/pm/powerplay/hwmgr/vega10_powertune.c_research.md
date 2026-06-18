# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_powertune.c

## Purpose

This file implements Vega10 PowerTune and DiDt/EDC programming for the AMD PowerPlay hardware manager. It translates platform capability bits and runtime registry settings into SMC feature toggles, SMC messages, and direct or indirect register programming for power containment, current limits, package power limits, and graphics-domain droop/current throttling behavior.

## Important APIs, Types, and Functions

The public entry points are `vega10_initialize_power_tune_defaults`, `vega10_set_power_limit`, `vega10_enable_power_containment`, `vega10_disable_power_containment`, `vega10_power_control_set_level`, `vega10_enable_didt_config`, and `vega10_disable_didt_config`. Internal helpers include `vega10_program_didt_config_registers` for indirect DIDT/GC_CAC/SE_CAC register writes, `vega10_program_gc_didt_config_registers` for direct GC register writes, and `vega10_didt_set_mask` for feature-gated enable bits and the `PPSMC_MSG_ConfigureGfxDidt` message. The file is driven by many sentinel-terminated `struct vega10_didt_config_reg` arrays that encode register offset, mask, shift, and value tuples for SE DiDt, SE EDC, PSM GC DiDt/EDC, AVFS PSM reset/init, stall patterns, thresholds, and droop controls.

## Control Flow, State, and Persistence

Power containment setup pulls `phm_tdp_table` data from `hwmgr->pptable`, stores `default_power_limit` and `power_limit`, enables `GNLD_PPT` and `GNLD_TDC` SMC features when supported, and sends `PPSMC_MSG_SetPptLimit` when package tracking is enabled. PowerTune defaults are copied into `data->smc_state_table.pp_table`, including socket/TDC/EDC limits, temperature limits, load-line resistance, and I2C monitor lines.

DiDt enable/disable dispatches on `data->registry_data.didt_mode`. Modes select CAC-driven SE DiDt, PSM GC DiDt, SE EDC, PSM GC EDC, or SE EDC force-stall setup. Most enable paths enter RLC safe mode, lock `adev->grbm_idx_mutex`, iterate shader engines via `GRBM_GFX_INDEX`, program the selected register tables, restore broadcast indexing, update DIDT/EDC masks, and exit safe mode. Successful public enable/disable calls also toggle `data->smu_features[GNLD_DIDT].enabled`.

## Dependencies and Integration Points

This code depends on `vega10_hwmgr` backend state, SMC feature metadata, `vega10_smumgr`/SMC message helpers, CGS register access, SOC15 register macros, GRBM indexing, and AMDGPU RLC safe-mode helpers. It is called from the Vega10 hwmgr initialization/start/stop paths and consumes table data prepared by `vega10_processpptables.c`.

## Risks and Test Signals

The register tables are hardware-specific constants with little runtime validation beyond the sentinel offset and null-table checks. A malformed mask/shift/value tuple can silently program the wrong field. Several internal enable helpers accumulate errors but return `0` after the loop, so partial failures can be hidden. DiDt mode selection depends on registry data and platform caps, so tests should cover each mode, unsupported feature paths, VF short-circuit behavior, SMC message failures, GRBM index restoration, safe-mode enter/exit pairing, and endian conversion of PowerTune defaults into the SMC PPTable.
