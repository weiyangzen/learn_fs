<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-usbio.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-usbio.c

Purpose: implements Intel USBIO GPIO support as an auxiliary-bus client, exposing firmware-described USBIO GPIO banks through gpiolib and USBIO control messages.

Important APIs, types, and functions: `struct usbio_gpio_bank` stores per-pin cached config bytes and a firmware bitmap. `struct usbio_gpio` stores the config mutex, bank array, gpiochip, and auxiliary device. GPIO callbacks are get_direction, direction_input, direction_output, get, set, and set_config. `usbio_gpio_update_config()` serializes config cache updates and sends `USBIO_GPIOCMD_INIT`.

Control flow: auxiliary probe obtains bank descriptors from platform data, allocates state, initializes a mutex, binds ACPI companion IDs, copies bank bitmaps until an empty descriptor, fills a sleeping gpiochip with `ngpio = bank_count * USBIO_GPIOSPERBANK`, registers it, then clears ACPI dependencies. Read/write operations send `USBIO_GPIOCMD_READ` and `USBIO_GPIOCMD_WRITE`; direction and bias/drive configuration send INIT messages.

State and persistence behavior: per-pin config bytes are cached in memory and updated under `config_mutex`. Actual GPIO state and config live behind USBIO firmware/control messages. Firmware bitmaps are advisory; invalid bitmap bits warn once but do not block access.

Dependencies and integration points: depends on auxiliary bus, Intel USBIO namespace APIs, ACPI IDs, USBIO platform data, pinconf bias/drive parameters, and gpiolib.

Risks and test signals: config cache starts zeroed rather than read from hardware, so first config update may clear firmware defaults outside the masked field only if masks are wrong. Control message short transfers are protocol errors on read but write return values are passed through directly. Test ACPI binding, bank bitmap warnings, read short-transfer handling, direction/value commands, bias configuration, dependency clearing, and namespace import.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-usbio.c -->
