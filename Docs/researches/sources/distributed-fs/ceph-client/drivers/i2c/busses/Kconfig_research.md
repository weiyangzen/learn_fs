<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/i2c/busses/Kconfig

Purpose: full I2C hardware bus-driver Kconfig menu. It groups host adapters into PC SMBus, ACPI, Mac, embedded/SoC, external USB/parallel, and other bus-driver categories.

Important symbols in this subset: `I2C_ALI1535`, `I2C_ALI1563`, `I2C_ALI15X3`, `I2C_AMD756`, `I2C_AMD8111`, `I2C_AMD_MP2`, `I2C_AMD_ASF`, `I2C_ALTERA`, `I2C_ASPEED`, and `I2C_ACORN`. Dependencies cover PCI, ACPI, HAS_IOPORT, OF, architecture gates, `I2C_PIIX4`, and slave support. Several entries select helper algorithms or SMBus/slave helpers.

Control flow and state: no runtime code; Kconfig state controls build inclusion and dependency legality. It integrates directly with `busses/Makefile` and indirectly with platform firmware descriptions, PCI IDs, ACPI IDs, and OF compatible strings in the drivers.

Risks and tests: wrong dependencies can enable drivers on unsupported buses or hide valid compile-test coverage. Test by generating configs for PCI-only, OF-only, ACPI-only, and COMPILE_TEST combinations, then building targeted modules and checking selected helper symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/Kconfig -->
