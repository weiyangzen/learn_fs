# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_hwmon.c

## Purpose

`bnxt_hwmon.c` exposes BNXT adapter temperature telemetry through the Linux hwmon subsystem when `CONFIG_BNXT_HWMON` is enabled. It queries firmware temperature sensors through HWRM, registers `temp1_*` attributes, reports warning/critical/emergency thresholds and alarms, optionally exposes shutdown threshold attributes, and notifies hwmon on asynchronous thermal threshold events.

## Important APIs and functions

- `bnxt_hwmon_init()` probes firmware temperature support and registers an hwmon device with `hwmon_device_register_with_info()`.
- `bnxt_hwmon_uninit()` unregisters the hwmon device.
- `bnxt_hwmon_notify_event()` maps firmware thermal event threshold type to hwmon alarm attributes and emits `hwmon_notify_event()`.
- `bnxt_hwrm_temp_query()` sends `HWRM_TEMP_MONITOR_QUERY`; with a non-NULL temp pointer it returns current temperature, and with NULL it caches firmware threshold capability and threshold values in `struct bnxt`.
- `bnxt_hwmon_is_visible()` controls which standard temp attributes are visible based on firmware threshold support.
- `bnxt_hwmon_read()` serves `temp1_input`, max/crit/emergency thresholds, and alarm booleans.
- `temp1_shutdown_show()` and `temp1_shutdown_alarm_show()` implement extra sysfs attributes for the firmware shutdown threshold.

## Control flow

Initialization calls `bnxt_hwrm_temp_query(bp, NULL)`. If firmware denies access or does not support the command, any existing hwmon device is unregistered and init returns. Otherwise, if no hwmon device is registered yet, the driver registers one named `DRV_MODULE_NAME`, using `bp` as drvdata and passing both standard channel info and optional extra shutdown attribute groups.

Read callbacks either query firmware for live temperature or return cached thresholds from `bp`. Alarm reads query live temperature and compare it against cached warning, critical, fatal, or shutdown thresholds. Visibility callbacks hide threshold and alarm files when firmware did not report threshold values, and hide shutdown attributes when the shutdown threshold is zero.

Async thermal events set `bp->thermal_threshold_type` elsewhere, then call `bnxt_hwmon_notify_event()`, which selects the matching hwmon alarm type and notifies userspace.

## State and persistence behavior

- `bp->hwmon_dev` stores the registered hwmon device pointer.
- `bp->fw_cap` gains `BNXT_FW_CAP_THRESHOLD_TEMP_SUPPORTED` when firmware reports threshold values.
- Threshold caches include `warn_thresh_temp`, `crit_thresh_temp`, `fatal_thresh_temp`, and `shutdown_thresh_temp`.
- `bp->thermal_threshold_type` drives event notification mapping.
- No durable persistence is performed; all threshold values are queried/cached firmware data.

## Dependencies and integration points

- Linux hwmon and hwmon-sysfs APIs.
- HWRM request framework and `HWRM_TEMP_MONITOR_QUERY` firmware command.
- BNXT async event handling, which invokes `bnxt_hwmon_notify_event()` after thermal events.
- Conditional compilation wrapper in `bnxt_hwmon.h`.

## Risks and edge cases

- If firmware supports current temperature but not thresholds, only `temp1_input` should be visible.
- `bnxt_hwrm_temp_query(bp, NULL)` mutates `bp->fw_cap` and threshold caches; repeated init/probe calls should preserve consistent visibility.
- Alarm reads return `-EIO` for shutdown alarm query failure but return raw HWRM errors for standard alarm reads.
- The hwmon event notification uses `&bp->pdev->dev` rather than `bp->hwmon_dev`; this must match hwmon expectations for the registered parent device.

## Test signals

- Build with `CONFIG_BNXT_HWMON=y` and disabled.
- Simulate HWRM success with thresholds, success without thresholds, `-EACCES`, `-EOPNOTSUPP`, and transient read failures.
- Verify sysfs visibility for standard and shutdown attributes under each threshold configuration.
- Verify alarm values at temperatures just below/equal/above thresholds.
- Verify async thermal events produce max, crit, and emergency hwmon notifications.
