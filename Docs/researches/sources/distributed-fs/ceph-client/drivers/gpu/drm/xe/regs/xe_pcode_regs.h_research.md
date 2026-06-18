# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_pcode_regs.h

## Purpose

`xe_pcode_regs.h` defines PCODE-visible GT MMIO registers for PVC power/energy telemetry and BMG fan/VRAM/package temperature telemetry.

## Important APIs, Types, and Definitions

- PVC telemetry: `PVC_GT0_PACKAGE_ENERGY_STATUS`, `PVC_GT0_PACKAGE_RAPL_LIMIT`, `PVC_GT0_PACKAGE_POWER_SKU_UNIT`, `PVC_GT0_PLATFORM_ENERGY_STATUS`, and `PVC_GT0_PACKAGE_POWER_SKU`.
- BMG telemetry: `BMG_FAN_1_SPEED`, `BMG_FAN_2_SPEED`, `BMG_FAN_3_SPEED`, `BMG_VRAM_TEMPERATURE_N(n)`, `BMG_VRAM_TEMPERATURE`, and `BMG_PACKAGE_TEMPERATURE`.
- Temperature fields: `TEMP_MASK_VRAM_N` and `TEMP_SIGN_MASK`.

## Control Flow

No executable logic exists. Consumers read the registers and decode fields to report package/platform energy, power limits, fan speeds, and temperatures.

## State and Persistence Behavior

The hardware state is telemetry and policy state. Energy values are changing counters, fan speed/temperature values are live sensor readings, and RAPL limits persist as platform policy state.

## Dependencies and Integration Points

It depends on `regs/xe_reg_defs.h` and integrates with Xe hwmon, power telemetry, PVC/BMG platform support, and diagnostics.

## Risks and Edge Cases

- Temperature sign/mask handling must be done by consumers; incorrect sign extension can produce invalid readings.
- `BMG_VRAM_TEMPERATURE_N(n)` uses `sizeof(u32)` as stride, tying the macro to C type width.
- Platform-specific registers must be gated by platform checks.

## Test Signals

Signals include plausible hwmon readings, sensor enumeration on BMG, PVC energy counter movement under load, and correct behavior when optional fans/VRAM sensors are absent.
