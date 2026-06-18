# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/Kconfig

## Purpose
`raw/Kconfig` declares the raw/parallel NAND subsystem menu and controller feature options. It gates which raw NAND controller drivers can be built, selects shared ECC/core dependencies, and documents platform dependencies.

## Important APIs, Types, and Functions
This is Kconfig metadata, not C code. The top-level `menuconfig MTD_RAW_NAND` is a tristate that selects `MTD_NAND_CORE` and `MTD_NAND_ECC`. Individual symbols include many controller options such as `MTD_NAND_AMS_DELTA`, `MTD_NAND_OMAP2`, `MTD_NAND_QCOM`, `MTD_NAND_ARASAN`, `MTD_NAND_ATMEL`, `MTD_NAND_GPIO`, and simulation/misc options such as `MTD_NAND_NANDSIM`, `MTD_NAND_RICOH`, and `MTD_NAND_DISKONCHIP`. It also sources subdirectory Kconfigs for some controller families.

## Control Flow
Kconfig evaluation starts at `MTD_RAW_NAND`; when disabled, the contained controller symbols are not offered. Dependencies constrain visibility and buildability by architecture, OF, DMA, clocks, I/O memory, bus helpers, and ECC helper libraries. Some options select helper symbols such as `BCH`, `GENERIC_ALLOCATOR`, `MFD_ATMEL_SMC`, `REED_SOLOMON`, or controller-family core symbols. The `MTD_NAND_OMAP_BCH_BUILD` def_tristate bridges OMAP controller and optional BCH support.

## State and Persistence
The file has no runtime state. Its persistent effect is the generated kernel configuration, which determines object inclusion and compiled code paths.

## Dependencies and Integration Points
It integrates with `drivers/mtd/nand/raw/Makefile`, subdirectory Kconfig files, architecture symbols, MTD core symbols, and helper library symbols. Driver source files rely on the matching config symbols for compilation.

## Risks
Incorrect dependencies can expose drivers on platforms that cannot link or hide valid compile-test coverage. Missing `select` entries can produce link failures for helper APIs; over-broad selects can force unwanted libraries. Because this menu covers many SoCs, changes can have broad build-matrix impact.

## Test Signals
Run `olddefconfig`/`allmodconfig`/`allyesconfig` and targeted randconfig builds across representative architectures. Confirm that `CONFIG_MTD_NAND_ARASAN` pulls BCH, `CONFIG_MTD_NAND_ATMEL` descends into the atmel Makefile, and each visible symbol produces the object listed in `raw/Makefile`.
