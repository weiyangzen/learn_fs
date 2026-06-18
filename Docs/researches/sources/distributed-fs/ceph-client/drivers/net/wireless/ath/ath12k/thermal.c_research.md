## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/thermal.c

Purpose: registers per-radio hwmon temperature reporting for ath12k and synchronizes sysfs reads with firmware WMI temperature responses.

Important APIs/functions: `ath12k_thermal_register()` registers `temp1_input` via `hwmon_device_register_with_groups()`, `ath12k_thermal_unregister()` removes devices, `ath12k_thermal_event_temperature()` stores firmware-reported temperatures, and `ath12k_thermal_temp_show()` implements the sysfs read.

Control flow: a sysfs read takes the wiphy guard, rejects non-ON hardware, reinitializes `ar->thermal.wmi_sync`, sends `ath12k_wmi_send_pdev_temperature_cmd()`, checks crash-flush state, waits up to `ATH12K_THERMAL_SYNC_TIMEOUT_HZ`, then returns the cached Celsius value in millidegrees. Firmware event handling stores the value under `data_lock` and completes waiters.

State and persistence: `ar->thermal.temperature`, `wmi_sync`, and `hwmon_dev` are runtime-only per-radio fields. Registration rollback unregisters previously registered hwmon devices if a later radio fails.

Dependencies/integration: uses Linux hwmon/sysfs APIs, completion synchronization, ath12k WMI temperature commands, `ATH12K_HW_STATE_ON`, `ATH12K_FLAG_CRASH_FLUSH`, and `ar->data_lock`.

Risks: the implementation is gated by `IS_REACHABLE(CONFIG_HWMON)` in the C file while the header gates declarations on `CONFIG_THERMAL`; mismatched Kconfig assumptions should be checked. Reads are synchronous and can time out if firmware events are lost. Completion is global to one radio thermal object, so concurrent reads collapse onto the same latest firmware event.

Test signals: build with hwmon/thermal combinations, register/unregister multi-radio devices, read `temp1_input` while ON/OFF/crash-flush, inject temperature WMI events, and validate timeout behavior.
