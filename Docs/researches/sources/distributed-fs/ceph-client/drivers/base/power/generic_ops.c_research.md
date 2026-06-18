# sources/distributed-fs/ceph-client/drivers/base/power/generic_ops.c

## Purpose
Supplies generic subsystem PM callbacks that simply dispatch to the currently bound driver's `struct dev_pm_ops` when present.

## Important APIs, Types, And Functions
The `CALL_PM_OP()` macro safely locates `dev->driver->pm` and invokes a named callback or returns success when absent. Runtime exports include `pm_generic_runtime_suspend()` and `pm_generic_runtime_resume()`. Sleep-state helpers cover prepare, suspend, freeze, poweroff, thaw, resume, restore, noirq, late/early, and complete phases.

## Control Flow
Each helper is a thin pass-through for one PM phase. Return-valued helpers propagate the driver callback return code; `pm_generic_complete()` calls `complete()` only when present. Compile-time `CONFIG_PM` and `CONFIG_PM_SLEEP` gates expose only the helpers relevant to the build.

## State And Persistence
No state is stored. These functions are dispatch adapters used by buses, classes, domains, and platform PM operations to avoid duplicating driver callback checks.

## Dependencies And Integration
Depends on `struct device`, `struct device_driver`, `struct dev_pm_ops`, runtime PM config, and symbol exports consumed by platform bus and other subsystems.

## Risks And Test Signals
Risks are low but include calling through stale driver pointers if invoked outside driver-core locking expectations and missing a PM phase when `dev_pm_ops` grows. Test signals are compile coverage for PM config variants and subsystem PM tests verifying callback ordering and return-code propagation.
