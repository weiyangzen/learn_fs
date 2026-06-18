# sources/distributed-fs/ceph-client/include/linux/leds-regulator.h

Purpose: supplies platform data for regulator-driven LEDs that use a regulator named `vled` as the physical output.

Important APIs and types: `struct led_regulator_platform_data` contains the LED class name and initial `enum led_brightness`.

Control flow: platform code binds regulator consumers to `leds-regulator.<id>` devices and passes this data; the driver enables/disables or adjusts the regulator according to LED brightness.

State and persistence: static platform state only. Runtime power state belongs to the regulator framework and LED driver.

Dependencies and integration points: depends on LED brightness definitions and integrates LED class devices with regulator consumers.

Risks and test signals: risks are supply-id mismatch, invalid initial brightness, and regulator errors during brightness changes. Test probe with `vled`, multiple IDs, initial state, suspend/resume, and regulator failure paths.
