# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_hwmon.c

## Purpose
`xe_hwmon.c` implements the Xe DRM driver's Linux hwmon interface for discrete GPUs. It exposes package/card power limits, power averaging windows, energy counters, temperatures, voltage, current limits, and fan speed through `devm_hwmon_device_register_with_info()`. It is disabled for integrated GPUs and SR-IOV VFs.

## Important APIs, Types, And Functions
- Internal state is held in `struct xe_hwmon`, including the registered hwmon device, `struct xe_device *`, `hwmon_lock`, power/energy/time unit shifts, accumulated energy state, cached fan counters, boot power limits, and thermal metadata.
- Register abstraction is centralized in `xe_hwmon_get_reg()`, which maps logical sensor registers to platform-specific MMIO registers for PVC, DG2, and Battlemage.
- Power limit handling is split between MMIO RAPL registers and PCode mailbox paths: `xe_hwmon_pcode_read_power_limit()`, `xe_hwmon_pcode_rmw_power_limit()`, `xe_hwmon_power_max_read()`, and `xe_hwmon_power_max_write()`.
- Energy accounting uses `xe_hwmon_energy_get()` to accumulate 32-bit hardware counters into a long-lived software total and avoid short hardware counter wrap intervals.
- Temperature handling uses direct MMIO for package/VRAM channels, PCode thermal data for MCTRL/PCIe, and dynamic per-channel VRAM labels.
- `xe_hwmon_read()`, `xe_hwmon_write()`, `xe_hwmon_is_visible()`, and `xe_hwmon_read_label()` are the hwmon callbacks.
- `xe_hwmon_register()` is the public registration entry point.

## Control Flow
Registration checks `IS_DGFX()` and excludes `IS_SRIOV_VF()`, allocates managed state, initializes the mutex, assigns `xe->hwmon`, preloads sensor metadata with `xe_hwmon_get_preregistration_info()`, then registers the hwmon chip. Visibility callbacks perform capability probing so unsupported attributes do not appear in sysfs. Runtime reads and writes enter through the hwmon core, take a runtime-PM guard, dispatch by sensor type, and often take `hwmon_lock` around MMIO/PCode update sequences.

## State And Persistence
The driver persists unit scaling read at registration, boot-time PL1/PL2 defaults for mailbox-backed power limits, accumulated energy deltas, and previous fan pulse counters. Energy and fan values are derived from monotonic deltas, so reset/reprobe resets their software baselines. Power-limit writes persist in hardware or firmware state until reset or later firmware/driver writes. Managed allocations and the hwmon device are cleaned up by device-managed lifetime.

## Dependencies And Integration Points
This file depends on hwmon/sysfs, Xe MMIO, PCode mailbox APIs, PM runtime guards, PMT telemetry for Battlemage energy, VSEC/PMT register definitions, and platform capability flags in `xe->info`. It integrates with the Xe probe path through `xe_hwmon_register()` and exposes user-facing sysfs ABI via Linux hwmon.

## Risks
Power-limit paths are hardware- and firmware-sensitive: unit conversion, clamping, and mailbox failure handling can expose incorrect sysfs values or reject writes. Energy accumulation depends on reads happening often enough and on correct initial baseline capture. Visibility checks may have side effects such as reading sensors and filling VRAM labels. Fan RPM is time-delta based and returns `-EAGAIN` for zero elapsed time. PCode mailbox limits are clamped to boot defaults, which protects hardware but may surprise users.

## Test Signals
Useful tests include hwmon sysfs presence/absence on dGPU, iGPU, and VF; power limit read/write/disable attempts; mailbox failure paths; 32-bit energy wrap behavior; dynamic VRAM channel visibility; fan RPM consecutive reads; and runtime PM coverage around all callbacks. The PMT telemetry import should be verified on Battlemage energy paths.
