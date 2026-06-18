<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/Makefile

## Purpose
This Kbuild file defines how the second-generation Symbios/LSI 53C8XX PCI SCSI controller driver is linked when `CONFIG_SCSI_SYM53C8XX_2` is enabled.

## Important APIs, Types, And Functions
There are no runtime APIs. The important Kbuild variables are `sym53c8xx-objs`, which lists `sym_fw.o`, `sym_glue.o`, `sym_hipd.o`, `sym_malloc.o`, and `sym_nvram.o`, and `obj-$(CONFIG_SCSI_SYM53C8XX_2)`, which selects the composite `sym53c8xx.o`.

## Control Flow
At build time, Kbuild links the listed component objects into `sym53c8xx.o` when the config symbol is built-in or modular. Runtime control flow begins in the linked C objects, not in this file.

## State And Persistence Behavior
No runtime state or persistence exists. The file only controls build composition.

## Dependencies And Integration Points
It integrates with the kernel Kbuild system and the SCSI Kconfig symbol `CONFIG_SCSI_SYM53C8XX_2`. Link completeness depends on symbols supplied across the five component translation units.

## Risks
Risks are stale object names, omitted objects causing unresolved symbols, and accidental build exclusion if the config symbol changes. Because firmware tables and glue/hipd logic are separate objects, object ordering and inclusion are required for a complete driver.

## Test Signals
Build with `CONFIG_SCSI_SYM53C8XX_2=y` and `m`, run modpost, verify `sym53c8xx.o` contains firmware, glue, HIPD, allocator, and NVRAM objects, and check clean builds after any file rename or source split.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/Makefile -->
