# sources/distributed-fs/ceph-client/drivers/platform/x86/hp/hp_accel.c

Purpose: glue driver between HP ACPI BIOS accelerometer devices and the shared LIS3LV02D accelerometer core, with support for HP disk-protection LED and HPQ6000 keyboard-bus scan-code filtering.

Important APIs/types/functions: ACPI IDs `HPQ0004`, `HPQ6000`, and `HPQ6007` autoload the driver. `lis3lv02d_acpi_read()` and `lis3lv02d_acpi_write()` call ACPI methods `ALRD` and `ALWR`. DMI axis conversion tables populate `lis3_dev.ac`. `hpled_set()` drives ACPI method `ALED`. `hp_accel_i8042_filter()` suppresses accelerometer scan codes from the keyboard stream.

Control flow: probe attaches ACPI companion data to `lis3_dev`, optionally records IRQ, selects axis conversion from DMI or default, initializes the shared LIS3 device, installs the i8042 filter for HPQ6000, initializes deferred LED work, and registers the LED class device. Remove reverses filter, joystick, power, LED, work, and filesystem state. PM suspend powers off the sensor; resume powers it back on.

State and persistence: uses the global LIS3 core device plus a static delayed LED device. Axis mapping is runtime-detected; LED brightness is runtime state only.

Dependencies and integration: depends on ACPI, platform bus, i8042/serio, LED class, and `drivers/misc/lis3lv02d` core APIs.

Risks: DMI axis mappings are model-specific and incomplete; wrong mapping gives inverted/swapped motion. The i8042 filter uses static extended-prefix state and must not consume unrelated keyboard bytes. Test signals include ACPI read/write method failures, DMI axis logs, LED registration failure cleanup, HPQ6000 scan-code filtering, and suspend/resume power behavior.
