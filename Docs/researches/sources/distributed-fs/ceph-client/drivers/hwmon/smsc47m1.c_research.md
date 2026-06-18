
# sources/distributed-fs/ceph-client/drivers/hwmon/smsc47m1.c

Purpose: legacy Super-I/O hwmon driver for SMSC LPC47M1xx and related fan/PWM blocks. It exposes configured fan tachometers, fan minimums and divisors, PWM duty and enable controls, alarms, and chip name.

Important APIs, types, and functions: `struct smsc47m1_sio_data` preserves detected chip type and original activation state. `struct smsc47m1_data` holds base address, type, cache arrays, and hwmon device. `smsc47m1_find()` detects chip IDs and enables the logical fan device if needed. `smsc47m1_handle_resources()` checks or reserves only used I/O subranges. `smsc47m1_update_device()` refreshes fan/PWM/divisor/alarm cache and clears latched alarm bits. Store handlers update fan minimum, fan divisor, PWM duty, and PWM enable.

Control flow, state, and persistence: init detects Super-I/O, creates a platform device, and probes once through `platform_driver_probe()`. Probe checks pin configuration before exposing only actually enabled fan and PWM groups. On exit or probe failure it restores the Super-I/O activation bit if the driver enabled it.

Dependencies and integration points: uses port I/O, ACPI resource checks, platform devices, sysfs groups, and legacy `hwmon_device_register()`.

Risks and test signals: alarms are cleared during cache refresh, which affects repeated reads. PWM disabled at 0 percent can suppress tach monitoring. Test pin-config gating, LPC47M292 third-channel paths, resource-region subsets, restore-on-exit, fan divisor changes preserving minimum RPM, invalid PWM and divisor writes, and cleanup after partial sysfs group creation.
