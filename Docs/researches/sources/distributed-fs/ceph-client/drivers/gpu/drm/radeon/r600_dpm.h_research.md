# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600_dpm.h

## Purpose

`r600_dpm.h` declares the shared R600 dynamic power-management interface and constants used by R600-family ASIC-specific DPM implementations. It defines default tuning values, table sizes, temperature bounds, power-level/display enums, exported default trend-control arrays, and prototypes for register programming, BIOS parsing, thermal, display-timing, and PCIe helper functions implemented by `r600_dpm.c`.

## Important APIs, Types, and Functions

- Default constants such as `R600_ASI_DFLT`, `R600_BSP_DFLT`, `R600_VOLTAGERESPONSETIME_DFLT`, SPLL/MPLL timing defaults, transition-control defaults, and `R600_PM_NUMBER_OF_*` sizes define expected array dimensions and fallback tuning values.
- `R600_TEMP_RANGE_MIN` and `R600_TEMP_RANGE_MAX` define the internal thermal interrupt range used by late DPM enable.
- `enum r600_power_level`, `enum r600_td`, `enum r600_display_watermark`, and `enum r600_display_gap` provide shared symbolic values for profile slots, trend direction, display watermark, and display-gap policy.
- `extern const u32 r600_utc[]` and `r600_dtc[]` expose the default up/down transition control tables.
- Function prototypes cover DPM diagnostics, vblank/vrefresh discovery, UVD-state classification, transition math, clock/voltage register programming, power-level control, DPM start/stop, thermal sensor classification, platform caps, extended PowerPlay table parsing/freeing, and PCIe speed/lane helpers.

## Control Flow

This header has no executable control flow. It shapes control flow by giving ASIC-specific source files a common call surface. Typical users parse platform and extended PowerPlay tables during initialization, program clock/voltage entries and power levels through the setters, call `r600_start_dpm` when ready, use display timing helpers while selecting power states, and call `r600_free_extended_power_table` during teardown.

## State and Persistence Behavior

The header itself stores no state, but its constants and enums define persistent ABI-like expectations between DPM modules. Array size macros must match `r600_utc`/`r600_dtc` definitions and hardware table capacities. The function prototypes mutate persistent GPU registers and `rdev->pm.dpm` state through their implementations.

## Dependencies and Integration Points

The header includes `radeon.h`, so it depends on Radeon core type definitions such as `struct radeon_device`, `struct radeon_ps`, `enum radeon_int_thermal_type`, and `enum radeon_pcie_gen`. It is included by `r600_dpm.c` and by ASIC-specific DPM files that share R600 helpers.

## Risks and Edge Cases

- Changing size macros can silently break array bounds or hardware table programming in implementation files.
- Temperature defaults affect interrupt thresholds and thermal protection behavior.
- The many register-wrapper prototypes expose low-level hardware programming; invalid caller-provided indices or values are not constrained at the type level.
- `enum r600_display_gap` uses spaces rather than the prevailing tab indentation style, a minor maintainability signal but not a runtime issue.
- Header/API drift between prototypes and implementation can break nonlocal ASIC-specific users.

## Test Signals

Build coverage across all Radeon ASIC DPM files is the primary signal for prototype and enum consistency. Runtime DPM tests should indirectly cover constants by validating parsed table sizes, programmed transition tables, thermal thresholds, and power-level slot usage. Static analysis can flag out-of-range enum or index usage by callers.
