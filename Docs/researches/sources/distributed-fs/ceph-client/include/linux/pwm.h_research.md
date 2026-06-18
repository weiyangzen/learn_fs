# sources/distributed-fs/ceph-client/include/linux/pwm.h

Purpose: defines the PWM framework's consumer and provider API, including PWM state, waveform representation, chip registration, apply/capture operations, lookup tables, device-tree translation, and config-disabled stubs.

Important APIs and types: `enum pwm_polarity`, `struct pwm_args`, `struct pwm_waveform`, `struct pwm_state`, `struct pwm_device`, `struct pwm_capture`, `struct pwm_ops`, `struct pwm_chip`, and `struct pwm_lookup` form the core model. Consumer helpers read/init state, get/set relative duty cycle, round/get/set waveform, apply state in sleeping or atomic context, get hardware state, adjust config, legacy config/enable/disable, and get/put PWM devices. Provider APIs allocate/register/remove chips, support devm registration, translate OF specifiers, expose chip driver data, and manage lookup tables.

Control flow: providers allocate a `pwm_chip`, fill ops, register it, and the framework creates per-channel `pwm_device` objects. Consumers obtain a PWM by device/connection, initialize state from board args, modify duty/period/polarity/enabled fields, and call `pwm_apply_might_sleep()` or `pwm_apply_atomic()` depending on chip atomic capability. Waveform callbacks provide a more expressive offset-aware representation when supported.

State and persistence: PWM framework state includes chip device/cdev, per-channel flags, args, last applied state, optional debug last implemented state, operational flag, locks, and lookup tables. Hardware PWM state may persist through consumer lifetime or hardware reset.

Dependencies and integration points: depends on device model, cdev, GPIO integration, OF/fwnode lookup, modules, mutex/spinlock, and driver callbacks. It integrates backlight, LED, regulator-like, motor, fan, and SoC PWM controller users.

Risks and test signals: risks include applying invalid duty > period, using sleeping apply in atomic context, provider `atomic` flag mismatch, waveform conversion inconsistencies, chip removal while consumers hold devices, lookup table module ownership, and disabled `CONFIG_PWM` stubs returning different errors. Test consumer get/apply/put, atomic vs might-sleep paths, provider registration/removal, OF lookup, waveform exact/rounded paths, relative duty helpers, capture timeouts, and no-PWM builds.
