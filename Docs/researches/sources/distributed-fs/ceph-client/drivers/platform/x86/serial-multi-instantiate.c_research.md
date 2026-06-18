# sources/distributed-fs/ceph-client/drivers/platform/x86/serial-multi-instantiate.c

Purpose: This pseudo-driver instantiates multiple I2C or SPI client devices from one ACPI fwnode when firmware represents several serial-bus clients under a single ACPI device. It is used for sensor and audio amplifier packages such as Bosch sensors, TPS6598x, Cirrus amps, and TAS2781.

Important APIs, types, and functions: `struct smi_instance` records client type and IRQ resource flags/index. `struct smi_node` records bus type and instance array. `smi_get_irq()` resolves GPIO, APIC/platform, auto, and optional IRQs. `smi_i2c_probe()` creates clients with `i2c_acpi_new_device()`. `smi_spi_probe()` allocates ACPI SPI devices, fills modalias/irq/init_name, and calls `spi_add_device()`. `smi_devs_unregister()` removes instantiated clients.

Control flow: Probe looks up ACPI match data, allocates `struct smi`, and chooses I2C, SPI, or auto-detect. Auto-detect tries I2C first for compatibility and only attempts SPI when no I2C serial resources exist. Each bus probe counts ACPI resources, allocates a device-pointer array, loops over resources and instance entries, resolves IRQs, creates devices, and fails if the resource count exceeds the instance list. Remove unregisters all created children.

State and persistence: Per-platform-device state is the count and arrays of created I2C/SPI children. No hardware settings are persisted by this driver; it delegates runtime behavior to instantiated client drivers.

Dependencies and integration points: It integrates with ACPI serial resource helpers, I2C core, SPI core, platform IRQs, GPIO IRQ translation, and ACPI ID tables. The comment notes new device IDs must also be added to ACPI scan ignore lists so this pseudo-driver owns enumeration.

Risks and edge cases: A mismatch between ACPI resource count and instance array aborts and unregisters all children. Dummy instance names are used for alias or nonexistent resources and require matching no-op behavior elsewhere. IRQ auto-detect treats nonpositive IRQs carefully, with optional IRQ support only for flagged instances. SPI init names are stack buffers copied through `init_name` before `spi_add_device()`, which is acceptable only because device registration consumes the name immediately.

Test signals: Test each ACPI ID mapping, I2C and SPI creation, auto-detect precedence, GPIO/APIC/optional IRQ resolution, resource-count mismatch cleanup, remove cleanup, and coordination with `drivers/acpi/scan.c` ignore-list entries.
