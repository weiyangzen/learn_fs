# sources/distributed-fs/ceph-client/drivers/platform/chrome/chromeos_acpi.c

Purpose: ACPI platform driver that exposes ChromeOS firmware ACPI package data as read-only sysfs attributes.

Important APIs, types, and functions: `chromeos_acpi_evaluate_method()` evaluates named ACPI methods. `chromeos_acpi_handle_package()` formats integer, string, and buffer package elements. `parse_attr_name()` maps sysfs names like `BINF.2` into ACPI method name plus package index. Macro-generated attributes expose first-level methods and up to eight `GPIO.N` attribute groups. `chromeos_acpi_device_probe()` records how many GPIO package groups firmware provides.

Control flow: sysfs reads parse the attribute name, call ACPI evaluation on the device handle, select the requested package/subpackage element, and format it to userspace. Probe only computes GPIO group visibility. `dev_groups` attaches all static groups to the platform device, with `is_visible` hiding GPIO groups above firmware count.

State and persistence: file-static `chromeos_acpi_gpio_groups` controls group visibility. Firmware data is read fresh on each sysfs access. No writable attributes or persistent kernel state.

Dependencies and integration points: ACPI platform IDs `GGL0001` and `GOOG0016`; sysfs device attributes; platform-driver core. The driver expects ChromeOS ACPI methods such as `BINF`, `CHSW`, `FMAP`, `FRID`, `FWID`, `GPIO`, `HWID`, `MECK`, `VBNV`, and `VDAT`.

Risks and edge cases: `chromeos_acpi_gpio_groups` is global, so multiple device instances would share visibility state. Buffers larger than PAGE_SIZE are truncated with a once-only info log. Unsupported ACPI object types fail with `-EINVAL`. Attribute-name parsing depends on exactly four-character method names plus dotted indexes.

Test signals: on ACPI Chromebook hardware, verify each expected sysfs file reads valid data, GPIO groups match firmware package count, oversized buffers truncate safely, and missing methods return errors without probe failure.
