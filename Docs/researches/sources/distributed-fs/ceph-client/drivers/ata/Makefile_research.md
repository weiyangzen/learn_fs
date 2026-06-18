# sources/distributed-fs/ceph-client/drivers/ata/Makefile

## Purpose
`drivers/ata/Makefile` maps ATA Kconfig symbols to built objects and defines the composed `libata.o` object. It is the build graph for libata core, SATA/AHCI, SFF, PATA, platform, fallback, and legacy ATA drivers.

## Important APIs, Types, And Functions
There are no runtime APIs. Important build entries include `obj-$(CONFIG_ATA) += libata.o`, `obj-$(CONFIG_SATA_AHCI) += ahci.o libahci.o`, `obj-$(CONFIG_SATA_ACARD_AHCI) += acard-ahci.o libahci.o`, many platform AHCI entries with `libahci_platform.o`, numerous SFF/PATA driver objects, and `libata-y` composition from `libata-core.o`, `libata-scsi.o`, `libata-eh.o`, `libata-transport.o`, and `libata-trace.o`. Conditional `libata-*` entries add SATA, SFF, PMP, ACPI, ZPODD, and PATA timing support.

## Control Flow
Kbuild expands active `obj-*` lines based on `.config`. Some drivers share helper objects, so enabling multiple AHCI drivers can include `libahci.o` through multiple entries as Kbuild resolves composite objects. `libata.o` is built from its core list plus conditional helper objects.

## State And Persistence
No runtime state exists. Build outputs persist as built-in objects or modules according to config choices.

## Dependencies
The Makefile depends on config symbols defined in `Kconfig`, Kbuild object semantics, and source files in the same directory and `pata_parport/` subdirectory.

## Integration Points
The file is consumed by the kernel build when entering `drivers/ata`. It directly links `acard-ahci.c` to `CONFIG_SATA_ACARD_AHCI` and `libahci.o`, tying the ACard variant to shared AHCI support.

## Risks
Object/config drift can cause a driver to be selectable but not built, or built without required helper objects. Ordering comments for generic fallback and legacy drivers matter because driver probe order can affect hardware binding. Shared helper objects must remain compatible with all drivers that include them.

## Test Signals
Build with focused configs for `CONFIG_ATA`, `CONFIG_SATA_ACARD_AHCI`, platform AHCI, SFF PATA, and fallback drivers; inspect `modules.order` or built-in object lists; run `make W=1 drivers/ata/`; and test module load/probe order for fallback drivers.
