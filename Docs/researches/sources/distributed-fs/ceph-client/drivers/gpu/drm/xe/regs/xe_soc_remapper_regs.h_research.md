# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_soc_remapper_regs.h

## Purpose

`xe_soc_remapper_regs.h` defines a SoC remapper index register and masks for telemetry and system-control remap selections.

## Important APIs, Types, and Definitions

- `SG_REMAP_INDEX1` at `SOC_BASE + 0x08`.
- `SG_REMAP_TELEM_MASK` for telemetry remap selection.
- `SG_REMAP_SYSCTRL_MASK` for system-control remap selection.

## Control Flow

The file has no executable flow. SoC remapper code writes or reads the index register to select remapped telemetry and system-control regions before using related MMIO windows.

## State and Persistence Behavior

The remapper index is persistent hardware routing state until changed or reset. It affects where subsequent SoC-aperture accesses land.

## Dependencies and Integration Points

It includes `xe_regs.h` for `SOC_BASE` and integrates with SoC telemetry, PMT, I2C, and system-control remapping code.

## Risks and Edge Cases

- Incorrect index fields can route accesses to the wrong SoC target.
- Callers must serialize remapper changes if multiple subsystems share the same window.
- Platform gating is required for SoCs without this remapper layout.

## Test Signals

Signals include successful telemetry/system-control access after remap programming and no cross-subsystem corruption when remap users run concurrently.
