# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/int3401_thermal.c

## Purpose
ACPI INT3401 processor thermal reporting device driver. It is a small platform wrapper that allocates processor thermal private state and delegates lifecycle and PM operations to shared processor thermal helpers.

## Important APIs, Types, and Functions
- `int3401_device_ids[]` matches ACPI `INT3401`.
- `int3401_add()` allocates `struct proc_thermal_device`, calls `proc_thermal_add()`, and stores drvdata.
- `int3401_remove()` calls `proc_thermal_remove()`.
- PM callbacks delegate to `proc_thermal_suspend()` and `proc_thermal_resume()` when sleep PM is enabled.
- Platform driver name is `int3401 thermal`.

## Control Flow
On probe, the driver allocates managed private data and lets the common processor thermal layer set up sensors, trips, and cooling/controls. Remove retrieves private data and delegates teardown. Suspend/resume pass through to common processor thermal callbacks.

## State and Persistence
This wrapper owns only the allocated `proc_thermal_device` pointer stored in platform drvdata. All substantive state belongs to the shared processor thermal implementation.

## Dependencies and Integration Points
Depends on ACPI platform matching, `processor_thermal_device.h`, `int340x_thermal_zone.h`, thermal core, and the common processor thermal helper implementation built by the same int340x Makefile.

## Risks and Edge Cases
- Probe behavior and failures are entirely determined by `proc_thermal_add()`.
- The wrapper has no OF/DT fallback and only matches `INT3401`.
- PM callback availability depends on `CONFIG_PM_SLEEP`.

## Test Signals
Tests should verify allocation failure, `proc_thermal_add()` error propagation, drvdata setup, remove delegation, and suspend/resume delegation under PM_SLEEP builds.
