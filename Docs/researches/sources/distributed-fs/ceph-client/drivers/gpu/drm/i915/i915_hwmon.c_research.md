# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_hwmon.c

## Purpose
Implements the i915 hwmon integration for discrete GPUs. It exposes package temperature, voltage, package power limits, rated power, I1 power/current critical limits, accumulated energy, and fan speed through Linux hwmon sysfs devices for the package and, where supported, per-GT energy devices.

## Important APIs, types, and functions
Key private types are `struct i915_hwmon`, `struct hwm_drvdata`, `struct hwm_reg`, `struct hwm_energy_info`, and `struct hwm_fan_info`. Public entry points are `i915_hwmon_register()`, `i915_hwmon_unregister()`, `i915_hwmon_power_max_disable()`, and `i915_hwmon_power_max_restore()`. The hwmon callbacks are routed through `hwm_is_visible()`, `hwm_read()`, and `hwm_write()`, with per-sensor helpers for temp, input voltage, power, energy, current, and fan. `hwm_get_preregistration_info()` discovers register availability and scale shifts before registration.

## Control flow
Registration exits early for non-dGFX, allocates `i915->hwmon`, initializes shared locking and package/per-GT driver data, snapshots static power-unit scaling and initial counter values, then registers a package hwmon device and optional per-GT energy devices. Reads take runtime PM wakerefs before MMIO or pcode access. Power-limit writes serialize on `hwmon_lock`, wait for any reset-time PL1 disable window, convert user microwatts/milliseconds to hardware fields, and update `PACKAGE_RAPL_LIMIT`.

## State and persistence
Persistent driver state lives in `i915->hwmon`: register addresses, power/energy/time scale shifts, per-device `hwm_drvdata`, energy accumulator snapshots, fan counter/time snapshots, reset-in-progress flag, and waitqueue. Hardware state persists in PCU package registers and pcode I1 setup. `hwm_energy()` extends 32-bit hardware energy counters into a long-lived software accumulator protected by `hwmon_lock`.

## Dependencies and integration points
Depends on hwmon core, sysfs attributes, runtime PM, intel uncore MMIO, pcode mailbox helpers, GT iteration, PCU/MCHBAR register definitions, and i915 reset flows that call the power-limit disable/restore helpers. Integrates with module/device teardown through `i915_hwmon_unregister()`.

## Risks
Counter wrap handling is lock-sensitive and off-by-one mistakes would skew energy. PL1 disable/restore coordination can block sysfs writers and must wake waiters after reset. Visibility probes call pcode reads and suppress DG1/DG2 unsupported I1 paths. Fan speed is interval-based and returns `-EAGAIN` on zero elapsed time. Wrong register validity or unit shifts can expose bogus sysfs values.

## Test signals
Build with `CONFIG_HWMON`, boot on DG1/DG2 and other dGFX, inspect `/sys/class/hwmon` package and `i915_gtN` devices, read/write `power1_max`, `power1_max_interval`, `power1_crit` or `curr1_crit`, sample `energy1_input` across counter wrap, read fan RPM twice with delay, and exercise GPU reset paths while writing PL1.
