<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/Makefile

Purpose: Builds the SPI NAND framework composite object.

Important APIs/types/functions: `spinand-objs := core.o otp.o` starts the composite object. The next lines add manufacturer files: AllianceMemory, ATO, Dosilicon, ESMT, FMSH, Foresee, GigaDevice, Macronix, Micron, Paragon, SkyHigh, Toshiba, Winbond, and XTX. `obj-$(CONFIG_MTD_SPI_NAND) += spinand.o` links the composite into the kernel or module.

Control flow: Kbuild compiles every listed source into `spinand.o`; `core.c` references exported manufacturer descriptors from these files through `spinand_manufacturers[]`, so missing an object breaks device matching.

State and persistence: No runtime state. The object list determines which IDs and manufacturer callbacks exist in the final SPI NAND driver.

Dependencies/integration: Integrates Kconfig symbol `CONFIG_MTD_SPI_NAND` with Kbuild. It also encodes the supported manufacturer surface for `core.c`.

Risks: Adding a new manufacturer descriptor in source without adding the object here makes it unreachable or causes link failures if referenced. Removing `otp.o` breaks vendor OTP operation hooks used by Micron and ESMT tables.

Test signals: `make M=drivers/mtd/nand/spi` or full kernel builds should confirm all objects compile and link into `spinand.o` for both module and built-in configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/Makefile -->
