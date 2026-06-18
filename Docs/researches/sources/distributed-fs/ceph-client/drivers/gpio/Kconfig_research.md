# sources/distributed-fs/ceph-client/drivers/gpio/Kconfig

## Purpose
`drivers/gpio/Kconfig` is the top-level Linux GPIO configuration menu for the source tree. It enables the generic GPIO library, legacy and character-device userspace ABIs, GPIO IRQ-chip support, shared GPIO support, generic helper libraries, and a large set of concrete GPIO controller/expander/test drivers grouped by bus or device class.

## Important APIs, types, and functions
This is Kconfig rather than C code, so the important units are symbols and menu blocks. Core symbols include `GPIOLIB`, `GPIOLIB_FASTPATH_LIMIT`, `OF_GPIO`, `GPIO_ACPI`, `GPIOLIB_IRQCHIP`, `GPIO_SHARED`, `DEBUG_GPIO`, `GPIO_SYSFS`, `GPIO_SYSFS_LEGACY`, `GPIO_CDEV`, `GPIO_CDEV_V1`, `GPIO_GENERIC`, `GPIO_REGMAP`, `GPIO_SWNODE_UNDEFINED`, `GPIO_MAX730X`, `GPIO_IDIO_16`, and `GPIO_I8255`. Driver menus group memory-mapped GPIO controllers, port-mapped I/O controllers, I2C/SPI/USB expanders, MFD GPIO providers, PCI expanders, virtual GPIO drivers, and debugging utilities.

## Control flow
The top-level `menuconfig GPIOLIB` gates almost the entire file through `if GPIOLIB`. Selecting `GPIOLIB` exposes core ABI/debug options and driver menus. Each driver symbol declares `bool`/`tristate` type, dependencies such as architecture, bus, firmware, ACPI/OF, `HAS_IOMEM`, `HAS_IOPORT`, or `COMPILE_TEST`, and helper selections such as `GPIO_GENERIC`, `GPIO_REGMAP`, `GPIOLIB_IRQCHIP`, `REGMAP_*`, `IRQ_DOMAIN`, `GENERIC_IRQ_CHIP`, `CONFIGFS_FS`, and `AUXILIARY_BUS`. Defaults are mostly platform-driven, for example SoC GPIO drivers defaulting to `y` on their native architecture or USB/MFD proxy drivers defaulting with their parent.

## State and persistence behavior
The file produces build-time `.config` state. It does not execute at runtime, but the selected symbols determine which GPIO core features and drivers are built in, built as modules, or omitted. ABI choices such as `GPIO_SYSFS`, `GPIO_CDEV`, and `GPIO_CDEV_V1` determine runtime userspace interfaces. `GPIOLIB_FASTPATH_LIMIT` stores a numeric configuration that affects stack versus dynamic allocation thresholds in GPIO core code.

## Dependencies and integration points
The file integrates GPIO drivers with architecture symbols, bus subsystems (`I2C`, `SPI_MASTER`, `USB`, `PCI`, `MCB`, `SIOX`, `VIRTIO`), firmware interfaces (`OF`, `ACPI`, Raspberry Pi firmware, ZynqMP firmware), MFD parent devices, regmap, irqdomain/generic IRQ chip support, configfs/debugfs test infrastructure, and auxiliary bus support. It also nudges userspace toward the modern character device ABI by making `GPIO_SYSFS` select `GPIO_CDEV`.

## Risks and edge cases
Kconfig mistakes can create invalid build combinations: missing `depends on HAS_IOMEM/HAS_IOPORT` can expose drivers on unsupported architectures, missing `select GPIOLIB_IRQCHIP` or IRQ domain dependencies can break interrupt-capable drivers, and careless `select` use can force dependencies without their prerequisites. `GPIOLIB_FASTPATH_LIMIT` warns that incorrect values can cause stack corruption. Deprecated ABIs (`GPIO_SYSFS`, `GPIO_CDEV_V1`, and `GPIO_MOCKUP`) remain selectable for compatibility and need regression coverage. Large menu organization also risks duplicate or misplaced symbols when adding new drivers.

## Test signals
Relevant validation includes `olddefconfig`/`allmodconfig`/`allyesconfig`/`randconfig` builds across representative architectures, `COMPILE_TEST` coverage, dependency checks for each bus menu, ABI checks for `GPIO_CDEV` and deprecated sysfs/v1 paths, GPIO IRQ-chip build combinations, configfs/debugfs virtual driver tests, and scripts/kconfig checks for unmet direct dependencies or recursive selects.
