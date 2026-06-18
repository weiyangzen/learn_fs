# sources/distributed-fs/ceph-client/drivers/hwmon/cros_ec_hwmon.c

Purpose: ChromeOS EC hwmon platform driver. It exposes EC temperature sensors, fan speeds/faults/targets, PWM duty/mode controls, thermal thresholds, and registers EC fans as thermal cooling devices when supported.

Important APIs, types, and functions: `cros_ec_hwmon_priv` stores the EC pointer, discovered temperature sensor names, usable fan bitmask, command-support booleans, and manual fan state saved for suspend. `cros_ec_hwmon_read_fan_speed()`, `read_pwm_value()`, `read_pwm_enable()`, `read_fan_target()`, `read_temp()`, and `read_temp_threshold()` wrap EC memory map or EC commands. `cros_ec_hwmon_probe_temp_sensors()` discovers sensor labels, `cros_ec_hwmon_probe_fans()` discovers usable fans, and `cros_ec_hwmon_probe_fan_control_supported()` checks command versions. Thermal cooling callbacks reuse PWM read/write helpers.

Control flow: probe obtains the parent `cros_ec_dev`, reads thermal version from EC memory, rejects version zero, discovers temps/fans and optional feature support, registers cooling devices for controllable fans, then registers the `cros_ec` hwmon device. Reads branch by hwmon type and attribute, converting EC special error values to `-ENODATA` or fault booleans. PWM writes support manual duty only when the EC fan is already in manual mode and mode writes switch between manual and auto. Suspend records manual PWM settings; resume restores manual PWM values, which also switches fans back to manual.

State and persistence: discovery state is stored at probe. Sensor values are read live from EC memory or commands, with no cache. `manual_fans` and `manual_fan_pwm[]` persist across system suspend/resume in driver memory to restore manual control. EC itself may reset fan control to automatic during suspend.

Dependencies and integration points: depends on ChromeOS EC protocol/memory map, platform child registration, hwmon, thermal cooling framework, command version discovery, unit conversion from EC Kelvin offsets, and optional PM callbacks.

Risks: `pwm_input` writes reject auto mode, so users must set `pwm_enable=1` first. `fan_target` visibility calls the EC from `is_visible()`, which may be relatively expensive and can hide only on `-EOPNOTSUPP`. `manual_fan_pwm` is sized by `EC_FAN_SPEED_ENTRIES`, while `manual_fans` is a `u8`, so assumptions about fan count matter. Sensor labels are absent if info commands fail, hiding otherwise readable sensors. Resume restoration may fail partially.

Test signals: test EC thermal versions before and after v2, boards with no fans, multiple fans, unsupported PWM commands, temp thresholds, fan target unsupported, error sentinel values for fans/temps, cooling-device registration, and suspend/resume preserving manual fan settings. Verify labels from `EC_CMD_TEMP_SENSOR_GET_INFO` and Kelvin-to-millicelsius conversion.
