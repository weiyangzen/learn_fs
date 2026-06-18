<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/mtd/parsers/Kconfig

Purpose: Configuration menu for MTD partition parsers.

Important APIs/types/functions: Defines parser symbols for BCM47XX, BCM63XX, Broadcom U-Boot, command-line partitions, OF/device-tree partitions and BCM4908/Linksys NS extensions, ImageTag, AFS, TP-Link safeloader, TRX, SharpSL, RedBoot and its options, Qualcomm SMEM, and Sercomm.

Control flow: Kernel configuration selects which parser source files are built by the companion Makefile. Some symbols select dependencies such as `CRC32` or `MTD_PARSER_IMAGETAG`; some depend on architecture/platform symbols or `COMPILE_TEST`; `MTD_OF_PARTS` defaults to y when OF is available.

State and persistence: No runtime state. The selected symbols determine which partition parsers are registered and therefore which on-flash partition tables can be discovered at boot.

Dependencies/integration: Integrates MTD partition parsing with board families and bootloader formats. Parser modules later register `struct mtd_part_parser` implementations via source files in this folder.

Risks: Misconfigured dependencies can hide parsers needed for boot media, causing missing rootfs partitions. Default-y OF parser can alter parser ordering/availability. RedBoot options affect whether unallocated regions are exposed and whether system images are forced read-only.

Test signals: Kconfig dependency tests for each platform/COMPILE_TEST combination, build coverage for every symbol as module/built-in where applicable, and boot tests with command-line, DT, RedBoot, AFS, TRX, SMEM, and vendor-specific partition maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/Kconfig -->
