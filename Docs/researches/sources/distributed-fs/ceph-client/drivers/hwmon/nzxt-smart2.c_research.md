# sources/distributed-fs/ceph-client/drivers/hwmon/nzxt-smart2.c

Purpose: reverse-engineered HID hwmon driver for NZXT Smart Device v2 and RGB & Fan Controller devices. It exposes three fan channels with RPM, PWM duty/mode/enable, voltage, current, labels, and update interval control.

Important APIs/types/functions: packed report structs model fan configuration, status, and set-speed output reports. `struct drvdata` stores HID/hwmon handles, cached fan telemetry, received flags, waitqueue, mutex, update interval, and output buffer. Key functions are `handle_fan_config_report()`, `handle_fan_status_report()`, hwmon read/write/string callbacks, `send_output_report()`, `set_pwm()`, `set_pwm_enable()`, update interval conversion helpers, `init_device()`, raw-event, reset-resume, probe, and remove.

Control flow: probe parses and opens HID, starts I/O, sends fan detection and update interval commands, then registers hwmon. Raw events parse config report `0x61` and status report `0x67` for speed or voltage data. Hwmon reads wait on report-backed flags with the waitqueue lock held so fancontrol sees coherent initial PWM/fan values. Writes serialize output reports with a mutex and optimistically update cached PWM duty after successful writes.

State and persistence: cached telemetry and fan type live in memory and are reset on resume before reinitialization. Device state includes update interval and commanded fan duty. `fan_config_received` gates status acceptance because fan detection can reset PWM values.

Dependencies and integration: depends on HID/hidraw coexistence, hwmon chip info, wait queues, spinlocks, mutexes, unaligned little-endian helpers, and NZXT USB IDs.

Risks: report formats are reverse engineered and include unknown static fields. Waiting sysfs reads can block until reports arrive. `pwm_enable` writes are mostly compatibility shims and only accept the current expected value. PWM values are scaled between 0-255 and 0-100 percent, preserving nonzero positive duty.

Test signals: fan-detect handshake, speed and voltage report parsing, blocking-read wakeups, PWM write immediate readback, update interval conversion, unexpected fan type warnings, resume flag reset and reinit, and all listed product IDs.
