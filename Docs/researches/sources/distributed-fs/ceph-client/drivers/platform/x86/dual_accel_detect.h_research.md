## sources/distributed-fs/ceph-client/drivers/platform/x86/dual_accel_detect.h

Purpose: header-only helper for platform x86 drivers to detect convertible systems with two accelerometers. Such systems often report unreliable firmware tablet-mode events unless Windows-specific hinge-angle methods are called, so drivers can suppress broken `SW_TABLET_MODE` reporting and let userspace infer posture from accelerometers.

Important APIs/functions: `dual_accel_detect_bosc0200()` finds the first ACPI `BOSC0200` device and uses `i2c_acpi_client_count()` to confirm it models two I2C clients. `dual_accel_detect()` returns true when either `KIOX010A` plus `KIOX020A`, `DUAL250E`, or the two-client `BOSC0200` pattern is present.

Control flow: consuming drivers call `dual_accel_detect()` during probe or quirk setup. The helper performs ACPI presence checks and, for BOSC0200, balances the ACPI device reference with `acpi_dev_put()`.

State and persistence: none. It performs live ACPI namespace/I2C enumeration checks and returns a boolean.

Dependencies and integration: ACPI device matching and I2C ACPI client counting. It is included directly in drivers, so functions are `static` and compiled into each consumer.

Risks: detection is heuristic and may miss new dual-accelerometer IDs or falsely identify systems where tablet-mode firmware is still valid. Since this is a header with function bodies, changes affect all include sites. Test signals include ACPI namespace fixtures or hardware with Kionix pair, DUAL250E, BOSC0200 with one client, BOSC0200 with two clients, and no accelerometer IDs. Consumers should test that tablet-mode input is disabled only when expected.
