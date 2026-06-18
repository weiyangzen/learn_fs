# sources/distributed-fs/ceph-client/drivers/iio/addac/Kconfig

## Purpose
This Kconfig file defines the Industrial I/O ADDAC submenu and the build-time options for three mixed analog input/output drivers: AD74115, AD74413R, and STX104.

## Important APIs, Types, And Functions
There are no C APIs, but the configuration symbols are important integration contracts. `CONFIG_AD74115` enables the Analog Devices AD74115H single-channel configurable input/output driver and selects CRC8, IIO buffers, triggered buffers, and REGMAP over SPI. `CONFIG_AD74413R` enables AD74412R/AD74413R quad-channel configurable I/O support, depending on GPIOLIB and SPI, selecting REGMAP_SPI, CRC8, and IIO buffered infrastructure. `CONFIG_STX104` enables the Apex Embedded Systems PC/104 card driver, depending on PC104 and X86, selecting ISA bus API, REGMAP_MMIO, GPIOLIB, GPIO_REGMAP, and I8254.

## Control Flow
Kconfig evaluation gates whether the corresponding objects can be built, either built-in or as modules. The submenu is ordered alphabetically and each entry documents the module name expected by userspace/package maintainers.

## State And Persistence
The file persists only build configuration. It indirectly controls which runtime drivers and module aliases are available in the kernel image or module tree.

## Dependencies And Integration Points
It integrates with the kernel configuration system, the ADDAC Makefile, SPI/regmap/IIO/GPIO/I8254 subsystems, and architecture/platform availability for STX104. The selected symbols ensure dependencies needed by the C files are present without requiring users to select all helpers manually.

## Risks And Test Signals
Risks include missing selects when C files gain new mandatory subsystems, dependency expressions that allow invalid builds, and symbol ordering drift. Test signals are `allyesconfig`/`allmodconfig` build coverage, individual module builds for each symbol, dependency checks on non-X86 builds for STX104, and verification that module names in help text match Makefile outputs.
