# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ci_dpm.h

## Purpose

`ci_dpm.h` is the private interface and state definition header for the CIK Radeon DPM implementation. It defines the Bonaire/Hawaii DPM constants, private power-state structures, SMC table caches, Powertune defaults, feature flags, and prototypes shared between `ci_dpm.c` and `ci_smc.c`. It also includes `smu7_discrete.h`, which supplies the firmware-facing SMC table layouts that the DPM code populates.

## Important APIs, Types, and Functions

Key constants define SMU DPM level counts, local CIK limits (`CISLANDS_MAX_HARDWARE_POWERLEVELS`, `MAX_REGULAR_DPM_NUMBER`, `CISLAND_MINIMUM_ENGINE_CLOCK`), unused GPIO encoding, power-containment feature bits, DPM table update bits, voltage-control modes, Q8.8 conversion, default virtual-counter values, ULV/default activity values, and ACPI PCIe performance request IDs.

Core private types:

- `struct ci_pl` is one performance level: memory clock, engine clock, PCIe generation, and lane count.
- `struct ci_ps` is the CIK-private representation of a Radeon power state with up to two hardware performance levels.
- `struct ci_dpm_level`, `struct ci_single_dpm_table`, and `struct ci_dpm_table` are host-side DPM table abstractions for SCLK, MCLK, PCIe speed, VDDC, VDDCI, and MVDD.
- `struct ci_mc_reg_entry` and `struct ci_mc_reg_table` cache memory-controller register addresses and per-MCLK register data before conversion to `SMU7_Discrete_MCRegisters`.
- `struct ci_ulv_parm`, `struct ci_leakage_voltage`, `struct ci_dpm_level_enable_mask`, `struct ci_vbios_boot_state`, `struct ci_clock_registers`, `struct ci_thermal_temperature_setting`, and `struct ci_pcie_perf_range` store specific DPM substate.
- `enum ci_pt_config_reg_type`, `struct ci_pt_config_reg`, and `struct ci_pt_defaults` describe Powertune/DIDT register programming and ASIC-specific defaults.
- `struct ci_power_info` is the master private state object used as `rdev->pm.dpm.priv`.

Shared function prototypes expose SMC SRAM and firmware helpers implemented in `ci_smc.c`: byte copy, SMC start/reset/clock control, startup jump programming, running check, firmware load, and dword read/write. `ci_wait_for_smc_inactive()` is declared, but its visible implementation is compiled out in `ci_smc.c`.

## Control Flow

The header has no executable control flow, but it defines the state carried through the lifecycle. `ci_dpm_init()` allocates and fills `struct ci_power_info`; `ci_dpm_enable()` uses it to build and upload SMC DPM, MC, and Powertune tables; runtime transitions mutate DPM tables, masks, update flags, media flags, and current/requested power-state copies; disable/fini consume the same fields to restore hardware state and free allocations.

## State and Persistence Behavior

`struct ci_power_info` persists across the DPM lifetime and groups SMC location state, SMC image state, host policy state, voltage/leakage/boot/thermal/fan/PCIe state, feature/capability flags, current/requested power-state copies, runtime masks, and fan-control ownership. This reduces reparsing and allows incremental SMC table updates, but it means stale or partially updated fields can affect later transitions after an error.

## Dependencies and Integration Points

The header depends directly on `ppsmc.h`, `radeon.h`, and `smu7_discrete.h`. It is included by `ci_dpm.c` and `ci_smc.c`; public ASIC hooks are declared separately in `radeon_asic.h`. It is indirectly tied to ATOM BIOS/PowerPlay structures, CIK register definitions, firmware constants in `radeon_ucode.h`, and the Radeon DPM function table.

## Risks and Edge Cases

- The two-level `CISLANDS_MAX_HARDWARE_POWERLEVELS` truncates richer PowerPlay states into low/high behavior.
- `MAX_REGULAR_DPM_NUMBER` and SMU7 table sizes must stay synchronized with firmware-facing layouts.
- `ci_wait_for_smc_inactive()` is declared while the implementation is disabled.
- `struct ci_power_info` mixes immutable capabilities, parsed VBIOS data, SMC offsets, runtime masks, and fan state, so reinitialization and error handling need care.
- `caps_*`, `*_enabled`, `*_power_gated`, and fan booleans have different meanings: hardware support, desired policy, or current runtime state.

## Test Signals

Meaningful signals are compile/integration oriented: build `ci_dpm.c` and `ci_smc.c` together, exercise init/enable/disable/fini, verify forced performance, UVD/VCE, fan, thermal, and display-change paths, and run static analysis for table bounds, uninitialized private fields, endian conversion mistakes, and declarations without definitions.
