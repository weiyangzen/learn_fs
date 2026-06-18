# sources/distributed-fs/ceph-client/drivers/mfd/kempld-core.c

Purpose: Kontron PLD MFD core. It discovers supported boards via DMI, forced module parameter, or ACPI; serializes access to the PLD hardware mutex; exposes register helpers; reads firmware/spec information; and registers feature-driven child devices.

Important APIs/types/functions: exported `kempld_get_mutex()`, `kempld_release_mutex()`, `kempld_read8/16/32()`, `kempld_write8/16/32()`, `kempld_probe()`, `kempld_detect_device()`, and `kempld_platform_data_generic`.

Control flow: module init may create a DMI-backed platform device, then registers the platform driver. Probe chooses ACPI or DMI platform data, maps two IO ports, initializes locks, detects non-empty IO space, releases stale hardware mutex, reads PLD info/feature mask, and registers cells for I2C/watchdog/GPIO/UART according to feature bits.

State and persistence: `struct kempld_device_data` stores IO base, index/data ports, PLD clock, firmware info, feature mask, and a software mutex. Sysfs exposes version/spec/type. Hardware mutex state is external and shared with firmware.

Dependencies and integration: depends on DMI/ACPI tables, platform devices, IO port mapping, `linux/mfd/kempld.h`, and child drivers `kempld-i2c`, `kempld-wdt`, `kempld-gpio`, and `kempld-uart`.

Risks: hardware mutex acquisition can block while firmware holds access. DMI and ACPI paths intentionally avoid double probing. Forced IDs use substring matching. Register helpers require callers to hold the mutex.

Test signals: DMI and ACPI discovery, forced-device-id path, sysfs info fields, feature-mask child enumeration, mutex behavior under firmware access, and child register helper use.
