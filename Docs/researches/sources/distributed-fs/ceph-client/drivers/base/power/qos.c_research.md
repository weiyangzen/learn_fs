# sources/distributed-fs/ceph-client/drivers/base/power/qos.c

## Purpose
Implements per-device PM QoS constraints for resume latency, latency tolerance, min/max frequency, and flags, including kernel request APIs, notifier registration, userspace sysfs exposure, and cleanup on device removal.

## Important APIs, Types, And Functions
Exports flag/read APIs `dev_pm_qos_flags()` and `dev_pm_qos_read_value()`, request APIs `dev_pm_qos_add_request()`, `dev_pm_qos_update_request()`, `dev_pm_qos_remove_request()`, notifier APIs, `dev_pm_qos_add_ancestor_request()`, sysfs exposure/hide APIs for latency limit, flags, and latency tolerance, and `dev_pm_qos_update_user_latency_tolerance()`. State is protected by `dev_pm_qos_mtx`, `dev_pm_qos_sysfs_mtx`, and `dev->power.lock`.

## Control Flow
First use allocates `struct dev_pm_qos`, initializes resume-latency and latency-tolerance constraint lists, frequency constraints, flag list, and notifier heads, then installs it under the device power lock. Request add/update/remove validates request state and type, traces the operation, and dispatches to `pm_qos_update_target()`, `freq_qos_apply()`, or `pm_qos_update_flags()`. Cleanup removes sysfs files, hides user requests, drains every constraint list, marks `dev->power.qos` as `ERR_PTR(-ENODEV)`, and frees memory. Sysfs exposure creates a dedicated request, installs it in the QoS object under locks, then adds the sysfs attribute, rolling back if sysfs creation fails.

## State And Persistence
State is per-device in `dev->power.qos`: constraints, notifiers, user-space request pointers, frequency constraints, and flags. The `ERR_PTR(-ENODEV)` sentinel prevents new use after device removal. Userspace-visible values persist only while the device and exposed sysfs files exist.

## Dependencies And Integration
Depends on PM QoS core plist handling, freq QoS, runtime PM for flag/latency-tolerance sysfs safety, tracepoints, driver-core PM cleanup, and sysfs helpers declared in `power.h`.

## Risks And Test Signals
Risks include request object reuse without removal, races between sysfs removal and request updates, stale requests after device removal, runtime-suspended devices when mutating flags, notifier leaks, and locking-order regressions. Test signals include KUnit frequency QoS tests, device removal with active requests/notifiers, sysfs expose/hide cycles, latency tolerance callbacks, and tracepoints for add/update/remove behavior.
