# sources/distributed-fs/ceph-client/drivers/hwmon/gpio-fan.c

## Purpose
`gpio-fan.c` drives fans controlled by discrete GPIO lines, optionally with an alarm GPIO, regulator supply, runtime power management, and thermal cooling-device integration. It translates a device-tree speed map into hwmon PWM and fan RPM attributes.

## Important APIs, Types, and Functions
`struct gpio_fan_data` stores device handles, hwmon and thermal devices, GPIO descriptors, speed table, current/resume speed indices, manual-control flag, alarm work, and regulator. Alarm handling uses `fan_alarm_irq_handler()` and `fan_alarm_notify()`. GPIO control is centered on `__set_fan_ctrl()`, `__get_fan_ctrl()`, `set_fan_speed()`, `get_fan_speed_index()`, and `rpm_to_speed_index()`. Sysfs handlers expose `pwm1`, `pwm1_enable`, `pwm1_mode`, `fan1_input`, `fan1_target`, min/max RPM, and optional `fan1_alarm`. Thermal callbacks map cooling states to speed indices.

## Control Flow
Probe allocates state, parses device-tree properties and GPIOs, initializes the mutex, gets the `fan` regulator, configures control GPIOs while preserving current values, registers a cleanup action that stops the fan and disables runtime PM, registers the hwmon device, configures optional alarm IRQs, enables runtime PM, marks an active initial speed as resumed, and registers an OF cooling device. Sysfs or thermal writes lock the device and call `set_fan_speed()`, which handles runtime PM transitions when moving between speed index zero and nonzero.

## State and Persistence
The active speed index, resume speed, and manual PWM enable are in memory. The physical GPIO outputs and regulator state persist while powered. Suspend stores the current speed, stops the fan, and resume restores it. Shutdown and devm cleanup drive the fan to speed index zero when control GPIOs exist.

## Dependencies and Integration Points
The driver depends on OF properties (`gpio-fan,speed-map`), GPIO descriptors, optional alarm IRQs, regulator framework, runtime PM, hwmon group registration, and thermal cooling registration.

## Risks
Speed-map ordering is assumed when mapping PWM/RPM to indices. `fan_alarm_irq_handler()` returns `IRQ_NONE` even after scheduling work, which is unusual for a handled interrupt. Runtime PM and regulator failures can leave `speed_index` out of sync with actual hardware in some error paths. Alarm-only configurations register only alarm attributes. `gpio_fan_shutdown()` calls `set_fan_speed()` without taking the mutex.

## Test Signals
Test DT parsing with missing/odd speed maps, GPIO preservation during init, sysfs visibility for alarm-only and control configurations, PWM and target RPM conversions, regulator enable/disable on zero/nonzero transitions, thermal state mapping, suspend/resume restoration, and alarm IRQ sysfs notifications.
