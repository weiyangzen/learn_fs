# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/thermal.c

Purpose: Implements ath10k thermal cooling and hwmon integration using firmware quiet-mode throttling and WMI temperature reads.

Important APIs and functions: Public functions are `ath10k_thermal_register()`, `ath10k_thermal_unregister()`, `ath10k_thermal_event_temperature()`, and `ath10k_thermal_set_throttling()`. It also defines `thermal_cooling_device_ops` callbacks and an hwmon `temp1_input` sysfs attribute.

Control flow: Registration checks `WMI_SERVICE_THERM_THROT`, creates a cooling device, adds a `cooling_device` symlink, initializes quiet period, and optionally registers an hwmon device if firmware and kernel config support temperature reads. Setting cooling state validates 0..100, stores the throttle state under `conf_mutex`, and sends WMI quiet-mode with duration as a percentage of quiet period when the device is ON. Reading temperature sends a WMI get-temperature command, waits up to five seconds for `wmi_sync`, and emits millidegrees Celsius. WMI temperature events store Celsius under `data_lock` and complete the waiter.

State and persistence: Mutates `ar->thermal.cdev`, `wmi_sync`, `throttle_state`, `quiet_period`, and `temperature`. No durable persistence exists; thermal state is runtime-only and depends on firmware service availability.

Dependencies and integration points: Uses Linux thermal cooling, sysfs, hwmon, ath10k WMI ops, firmware service map, `conf_mutex`, `data_lock`, and crash-flush flag handling.

Risks: Temperature reads fail when the device is off, during crash flush, or if firmware never completes the WMI request. Quiet-mode support depends on both service bit and WMI op presence. Unregister assumes a registered cooling device whenever the service bit is set, so partial registration failures need careful unwind.

Test signals: Register/unregister with and without thermal service, set throttle 0/50/100 and out of range, verify WMI quiet-mode parameters, read temperature success/timeout/offline/crash paths, hwmon disabled builds, and symlink cleanup after hwmon registration failure.
