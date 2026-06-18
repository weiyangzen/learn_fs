# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_hwmgr.h

## Purpose

This header defines the SMU10 hardware-manager data model, power-state structures, constants, and initialization entry point used by `smu10_hwmgr.c`.

## Important APIs, Types, and Functions

The main exported function is `smu10_init_function_pointers(struct pp_hwmgr *hwmgr)`. Key types include `struct smu10_hwmgr` for persistent backend state, `struct smu10_power_state` for per-power-state hardware data, `struct smu10_power_level`, `struct smu10_dpm_entry`, `struct smu10_clock_voltage_information`, and `struct smu10_voltage_dependency_table`. Constants define feature-scoreboard masks, DPM flags, PCIe powergating targets, UMD pstate defaults, and clock limits.

## Control Flow and State

The header itself has no control flow, but it describes the state owned by the SMU10 backend: DPM flags, current frequency constraints, display and watermark data, power-gating booleans, CC6 settings, VCN/GFX state, clock tables, fine-grain tuning status, and allocated voltage dependency tables.

## Dependencies and Integration

It includes `hwmgr.h`, `smu10_inc.h`, `smu10_driver_if.h`, and `rv_ppsmc.h`, making it the local contract between generic hwmgr code, SMU firmware interfaces, and SOC register definitions. `smu10_power_state.magic` ties into cast helpers in the C file.

## Risks and Test Signals

Because this structure stores many cached firmware and user-control values, stale fields can desynchronize driver assumptions from SMU firmware state. Flexible-array voltage tables require allocation and cleanup discipline. Test signals are compile-time structure use, backend init/fini leak checks, sysfs clock output, forced DPM behavior, and suspend/resume restoration of cached fine-grain limits.
