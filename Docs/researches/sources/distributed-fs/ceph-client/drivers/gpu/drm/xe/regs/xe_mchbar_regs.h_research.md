# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_mchbar_regs.h

## Purpose

`xe_mchbar_regs.h` defines the Xe driver's mirrored MCHBAR power/thermal register addresses and field masks for package SKU power limits, unit conversion, energy status, package temperature, and RAPL limits.

## Important APIs, Types, and Definitions

- Base: `MCHBAR_MIRROR_BASE_SNB`.
- Power SKU: `PCU_CR_PACKAGE_POWER_SKU` with `PKG_TDP`, `PKG_MIN_PWR`, `PKG_MAX_PWR`, and window fields.
- Units/status: `PCU_CR_PACKAGE_POWER_SKU_UNIT`, `PKG_PWR_UNIT`, `PKG_ENERGY_UNIT`, `PKG_TIME_UNIT`, and `PCU_CR_PACKAGE_ENERGY_STATUS`.
- Thermal/RAPL: `PCU_CR_PACKAGE_TEMPERATURE`, `TEMP_MASK`, `PCU_CR_PACKAGE_RAPL_LIMIT`, `PWR_LIM_*`.

## Control Flow

No executable control flow is present. Power telemetry or management code reads these registers and applies bit masks to convert hardware units into driver-visible power, energy, time, and temperature values.

## State and Persistence Behavior

The hardware state represents package power limits, energy counters, temperature, and unit encodings. Energy counters are monotonically changing hardware counters; limit registers persist until firmware/driver/platform policy changes them.

## Dependencies and Integration Points

It depends on `regs/xe_reg_defs.h` and Linux/DRM bit helpers. It integrates with power management, telemetry, RAPL exposure, and platform diagnostics that use the MCHBAR mirror instead of directly mapping the host bridge MCHBAR.

## Risks and Edge Cases

- Unit fields must be applied correctly or telemetry values will be scaled incorrectly.
- Counter rollover must be handled by consumers, not this header.
- These addresses are mirror-specific; using them on platforms without the mirror or with different layout would produce invalid readings.

## Test Signals

Signals include plausible package temperature/energy readings, correct RAPL unit conversion, and no MMIO faults or zeroed telemetry on supported platforms.
