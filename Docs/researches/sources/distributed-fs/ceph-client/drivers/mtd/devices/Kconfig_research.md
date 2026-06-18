## sources/distributed-fs/ceph-client/drivers/mtd/devices/Kconfig

Purpose: defines Kconfig entries for self-contained MTD device drivers, including PCI/NVRAM/RAM emulation, SPI memories, BCMA serial flash, block-device-backed MTD, PowerNV flash, Intel DG flash, DiskOnChip G3, and ST SPI FSM.

Important APIs, types, and functions: configuration symbols include `MTD_MCHP23K256`, `MTD_MCHP48L640`, `MTD_BCM47XXSFLASH`, `MTD_BLOCK2MTD`, and `MTD_DOCG3`, matching files in this work item. `MTD_DOCG3` selects BCH support and bit-reversal helpers. The menu depends on `MTD != n` and `HAS_IOMEM`.

Control flow: this is build-time control. Symbols gate object inclusion through the Makefile and express dependencies such as `SPI_MASTER`, `BCMA_SFLASH && (MIPS || ARM)`, `BLOCK`, `PPC_POWERNV`, and auxiliary bus/DRM requirements.

State and persistence: no runtime state. It persists kernel configuration choices and selected dependencies.

Dependencies and integration points: consumed by Kbuild, defconfigs, randconfig, and module builds. Help text documents intended hardware and module names.

Risks: incorrect dependencies can expose drivers on unsupported architectures or hide testable drivers from `COMPILE_TEST`. `MTD_DOCG3` help notes write support is experimental/limited, while the current driver does implement write paths, so expectations need care.

Test signals: `olddefconfig`/`menuconfig` visibility, successful builds for each selected symbol, dependency closure for BCH/bitreverse/SPI/BLOCK/BCMA, and module names matching Makefile outputs.
