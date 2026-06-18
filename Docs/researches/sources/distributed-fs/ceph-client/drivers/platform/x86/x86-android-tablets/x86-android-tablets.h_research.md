# sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/x86-android-tablets.h

Purpose: central interface for the x86 Android tablet DMI quirk subsystem. It defines the board-description structures used by vendor shards and declares helper functions, GPIO software-node arrays, DMI IDs, and all exported `x86_dev_info` records.

Important APIs/types/functions: defines `enum x86_acpi_irq_type`, `enum x86_gpiochip_type`, `struct x86_acpi_irq_data`, `struct x86_i2c_client_info`, `struct x86_spi_dev_info`, `struct x86_serdev_info`, and `struct x86_dev_info`. Declares `x86_android_tablet_get_gpiod()` and `x86_acpi_irq_helper_get()`, the Bay Trail and Cherry Trail GPIO-chip software nodes, all board-info externs, and `x86_android_tablet_ids`.

Control flow: no implementation lives here, but it describes how the core driver consumes board records: optional modules and software-node groups are loaded/registered, I2C/SPI/platform/serdev devices are instantiated, GPIO button nodes are converted to gpio-keys devices, board init hooks run, and optional exit hooks clean up.

State and persistence: the header defines structure layouts for boot-time board data. Persistence is limited to the devices and GPIO/IRQ resources instantiated by the core driver based on these descriptors.

Dependencies/integration: includes GPIO consumer, I2C, IRQ domain, and SPI definitions because descriptor structs embed kernel board-info types. It is shared by all x86 tablet board files and by the core DMI driver that owns helper implementations.

Risks: this is a cross-file ABI inside the driver. Adding fields to `x86_dev_info` or changing IRQ semantics affects every board shard. `adapter_path`, `ctrl_path`, GPIO chip names, and ACPI/PCI serdev controller descriptors are string/topology contracts that must match helper lookup behavior. `__initconst` board records depend on the core copying or consuming data during init.

Test signals: all board shards compile against the header, DMI records resolve to the expected externs, GPIO/APIC/PMIC IRQ helper paths work for representative descriptors, and board init/exit hooks execute in the expected lifetime order.
