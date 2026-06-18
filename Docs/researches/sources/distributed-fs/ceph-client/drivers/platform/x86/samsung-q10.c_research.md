# sources/distributed-fs/ceph-client/drivers/platform/x86/samsung-q10.c

Purpose: This small legacy backlight driver supports Samsung Q10/Q20/Q25 and Dell Latitude X200 systems by driving brightness through embedded-controller ACPI query methods.

Important APIs, types, and functions: `ec_handle` stores the ACPI EC handle. `samsungq10_bl_set_intensity()` implements backlight updates by repeatedly evaluating `_Q63` to step down to minimum, then `_Q64` to step up to the requested brightness. `samsungq10_probe()` registers a `BACKLIGHT_PLATFORM` device named `samsung`. DMI entries gate supported systems unless `force` is set.

Control flow: Module init checks DMI or `force`, obtains the EC handle via `ec_get_handle()`, and creates a bundled platform device/driver. Probe registers the backlight device with max brightness 7. Update status performs step-down then step-up ACPI method calls. Exit unregisters the platform device and driver.

State and persistence: The driver has no cached brightness; hardware state is modified by EC ACPI query methods. Brightness may persist in firmware. Software state is just the EC handle and platform device pointer.

Dependencies and integration points: It integrates with ACPI EC, DMI, platform device bundle creation, and the backlight class.

Risks and edge cases: Brightness setting is destructive stepping rather than absolute hardware write; if `_Q63` or `_Q64` semantics differ, brightness can drift or fail. There is no `get_brightness`, so the backlight core cannot query actual state. Forced load can execute EC methods on unsupported systems if an EC exists.

Test signals: Test DMI and forced loading, EC handle absence, backlight registration/removal, all brightness values 0-7, and ACPI method failure propagation from `_Q63`/`_Q64`.
