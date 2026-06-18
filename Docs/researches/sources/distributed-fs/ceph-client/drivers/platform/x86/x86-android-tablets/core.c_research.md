# sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/core.c

Purpose: runtime engine for DMI-based x86 Android tablet fixups. It selects a board manifest, registers required software nodes, instantiates missing I2C/SPI/serdev/platform devices, wires IRQs, and unwinds everything on removal.

Important APIs and control flow: `x86_android_tablet_init()` uses `platform_create_bundle()` so probe runs at module init. Probe DMI-matches `x86_android_tablet_ids`, preloads required modules, registers GPIO-chip and board software-node groups, calls optional board init, creates I2C/SPI/serdev/platform devices, and optionally adds a gpio-keys platform device. Helpers resolve GPIO descriptors before consumer devices exist, map APIC/GPIO/PMIC IRQs, find I2C adapters by ACPI handle or PCI parent, create SPI devices, and bind serdev ACPI nodes to chosen controllers.

State and persistence: global arrays track instantiated clients/devices and counts for reverse-order cleanup. `exit_handler` stores a board-specific cleanup callback. Software-node groups remain registered for the module lifetime and are unregistered on removal.

Dependencies and integration: depends on DMI table data, ACPI, GPIO lookup tables, IRQ domains, I2C/SPI/serdev/platform buses, PCI, software node APIs, and `serdev_helpers.h`.

Risks and test signals: this code runs from module init and cannot rely on normal deferred probing, so module preloading and probe ordering are important. Error unwinding spans many object types. Tests should cover each IRQ type, missing adapters/controllers, partial failure cleanup, gpio-button registration, module unload after all object types are created, and every DMI board manifest selected by `dmi.c`.
