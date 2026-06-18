<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/Kconfig

Purpose: Kconfig entry for the SPI NAND framework.

Important APIs/types/functions: Defines `menuconfig MTD_SPI_NAND` as a tristate named "SPI NAND device Support". It selects `MTD_NAND_CORE`, `MTD_NAND_ECC`, and `SPI_MEM`, and depends on `SPI_MASTER`.

Control flow: Build configuration enables `drivers/mtd/nand/spi/Makefile` to produce `spinand.o` when `CONFIG_MTD_SPI_NAND` is built-in or a module. Selecting the option pulls in the generic NAND core, NAND ECC support, and SPI memory operation framework required by `core.c`.

State and persistence: No runtime state. The symbol determines whether SPI NAND support is compiled and whether the driver can probe devices with compatible `"spi-nand"` or SPI ID `"spi-nand"`.

Dependencies/integration: Bridges MTD NAND and SPI controller subsystems. The selected `SPI_MEM` dependency is critical because the framework uses `struct spi_mem_op`, direct mappings, operation-size adjustment, and status polling.

Risks: Missing `SPI_MASTER` prevents SPI NAND support from being offered. Because the symbol selects dependencies, configuration changes in the NAND ECC or SPI memory subsystems can affect all vendor tables compiled into `spinand.o`.

Test signals: Kconfig tests should verify `CONFIG_MTD_SPI_NAND=m/y` compiles with SPI master support and that deselecting SPI master hides or disables the option. Build outputs should include `spinand.o` and all listed vendor object files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/Kconfig -->
