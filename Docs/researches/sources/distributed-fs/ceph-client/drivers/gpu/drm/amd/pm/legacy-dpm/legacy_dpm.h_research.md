# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/legacy_dpm.h

## Purpose

`legacy_dpm.h` declares the shared helper API implemented by `legacy_dpm.c` for older AMDGPU DPM backends. It lets ASIC-specific files parse common ATOM PowerPlay data, print/debug power states, register thermal controllers, retrieve VCE states, compute clocks, and use the common thermal work handler.

## Important APIs

The declarations are `amdgpu_dpm_dbg_print_class_info()`, `amdgpu_dpm_dbg_print_cap_info()`, `amdgpu_dpm_dbg_print_ps_status()`, `amdgpu_get_platform_caps()`, `amdgpu_parse_extended_power_table()`, `amdgpu_free_extended_power_table()`, `amdgpu_add_thermal_controller()`, `amdgpu_get_vce_clock_state()`, `amdgpu_pm_print_power_states()`, `amdgpu_legacy_dpm_compute_clocks()`, and `amdgpu_dpm_thermal_work_handler()`.

## Control Flow

There is no implementation in this header. ASIC DPM modules include it during initialization and callback registration. A typical flow is: parse platform caps, parse extended power table, parse ASIC-specific state tables, install `amdgpu_legacy_dpm_compute_clocks` as the PM compute callback, and initialize thermal work with `amdgpu_dpm_thermal_work_handler`.

## State and Persistence Behavior

The functions declared here operate on `struct amdgpu_device`, especially `adev->pm.dpm` and `adev->powerplay.pp_funcs`. Memory ownership for extended table allocations is paired: parse allocates, free releases. Thermal work persists as a `work_struct` embedded in `adev->pm.dpm.thermal`.

## Dependencies and Integration Points

The header assumes AMDGPU core types, `u32`, and `struct work_struct` are visible to including translation units. It is used by `kv_dpm.c` and other legacy ASIC DPM files to share common DPM policy and BIOS parsing.

## Risks and Edge Cases

Because this header exposes un-namespaced legacy helpers, prototype changes affect multiple ASIC backends. The parse/free pairing is not enforced by the type system. The returned `struct amd_vce_state *` points into `adev->pm.dpm` storage and is valid only while that DPM state remains allocated.

## Test Signals

Compile coverage across all legacy DPM ASICs is the primary signal. Runtime signals include successful init/fini without leaks, power-state debug output, clock recomputation through the shared callback, and thermal work executing after ASIC IRQ handlers schedule it.
