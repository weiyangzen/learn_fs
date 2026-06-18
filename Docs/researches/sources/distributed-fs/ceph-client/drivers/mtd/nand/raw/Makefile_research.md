# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/Makefile

## Purpose
`raw/Makefile` maps raw NAND Kconfig symbols to the object files and subdirectories built by Kbuild. It also defines the composite `nand.o` core from raw NAND base, legacy, BBT, timing, ID, ONFI/JEDEC, and vendor-specific ID support.

## Important APIs, Types, and Functions
This is build metadata. Important entries include `obj-$(CONFIG_MTD_RAW_NAND) += nand.o`, controller object mappings such as `obj-$(CONFIG_MTD_NAND_AMS_DELTA) += ams-delta.o`, `obj-$(CONFIG_MTD_NAND_QCOM) += qcom_nandc.o`, `obj-$(CONFIG_MTD_NAND_ARASAN) += arasan-nand-controller.o`, and subdirectory descents such as `atmel/`, `ingenic/`, `gpmi-nand/`, `brcmnand/`, and `bcm47xxnflash/`. `omap2_nand-objs := omap2.o` aliases the OMAP object into a module name.

## Control Flow
Kbuild evaluates each `obj-*` line after configuration. Enabled symbols add object files or directories to the build. The final `nand-objs` list composes the raw NAND core module from multiple implementation files and vendor helpers.

## State and Persistence
No runtime state exists. Persistent effects are generated build artifacts and module composition.

## Dependencies and Integration Points
The file must stay synchronized with `raw/Kconfig` symbols and actual source filenames. Composite object names affect module names and symbol linkage. Subdirectory entries depend on child Makefiles.

## Risks
Stale object mappings cause enabled Kconfig options to build nothing or fail. Composite `nand-objs` omissions can remove required core/vendor support. Always-built `obj-y += ingenic/` means that subdirectory Makefile must internally gate objects by config.

## Test Signals
Build with `CONFIG_MTD_RAW_NAND=m` and selected controller symbols as both built-in and module where applicable. Verify expected `.o`/`.ko` outputs and that each source added by Kconfig has a corresponding Makefile entry.
