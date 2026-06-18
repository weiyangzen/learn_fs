## sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/thermal.h

Purpose: defines ath12k thermal runtime state and compile-time thermal API stubs.

Important APIs/types: `struct ath12k_thermal` contains `completion wmi_sync`, `int temperature`, and `struct device *hwmon_dev`. Public functions are `ath12k_thermal_register()`, `ath12k_thermal_unregister()`, and `ath12k_thermal_event_temperature()`. `ATH12K_THERMAL_SYNC_TIMEOUT_HZ` is five seconds.

Control flow: enabled builds call into `thermal.c`; disabled builds return success or do nothing. The structure is embedded in per-radio state and used by WMI event and sysfs paths.

State and persistence: the struct stores only live kernel state; there is no persistence across driver reloads or firmware restarts.

Dependencies/integration: depends on core ath12k types and Linux completion/device concepts. It integrates with WMI temperature events and hwmon registration.

Risks: declaration gating uses `IS_REACHABLE(CONFIG_THERMAL)`, while implementation checks hwmon reachability; that split can cause unexpected stubbing if thermal and hwmon options diverge. The comment requires `temperature` protection by `data_lock`.

Test signals: compile matrix for thermal/hwmon options and lockdep/sysfs testing around concurrent temperature updates.
