# sources/distributed-fs/ceph-client/drivers/hwmon/pwm-fan.c

Purpose: platform hwmon driver for fans controlled by a PWM line, optional regulator, tachometer IRQs, and optional thermal cooling levels.

Important APIs/types/functions: `struct pwm_fan_ctx` stores PWM state, regulator state, tachometer data, timer, cooling levels, and stop/start/shutdown policy. `set_pwm()`/`__set_pwm()` change duty cycle and power. `sample_timer()` calculates RPM from IRQ pulse counts. Thermal callbacks expose cooling states.

Control flow: probe gets PWM/regulator, sets `usage_power`, validates period math, parses `cooling-levels`, starts fan at maximum/default, sets cleanup action, configures tachometer IRQs and pulses-per-revolution, parses stop/start and shutdown properties, registers hwmon and thermal cooling device.

State and persistence: `pwm_value`, `enable_mode`, `enabled`, `regulator_enabled`, RPM values, cooling state, and PWM hardware state persist. Cleanup either sets shutdown duty or forces power off.

Dependencies/integration: PWM framework, regulator API, platform IRQs, hwmon, thermal OF cooling, timers, device properties, PM suspend/resume.

Risks: `pwm_fan_update_enable()` ignores return values from some PWM/regulator updates when disabled. Tachometer accuracy depends on correct pulses-per-revolution and one-second sampling. Stop-to-start boost timing is property-driven. Suspend powers off and resume restores stored PWM.

Test signals: PWM sysfs read/write, enable modes 0-3, regulator transitions, tachometer RPM with known pulses, cooling-level state changes, suspend/resume, shutdown percent behavior, and invalid property handling.
