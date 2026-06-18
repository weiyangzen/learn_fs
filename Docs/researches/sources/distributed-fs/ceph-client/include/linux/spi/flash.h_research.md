<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/flash.h -->
# sources/distributed-fs/ceph-client/include/linux/spi/flash.h

Purpose: This header defines board-specific data for SPI flash devices, especially legacy non-DT/static partition configurations.

Important APIs/types/functions: `flash_platform_data` contains optional MTD device name, static partition array, partition count, and optional flash type string for devices that cannot be queried reliably.

Control flow: Board initialization supplies this data; SPI NOR/DataFlash drivers consume it during probe to name the MTD, choose type hints, and register partitions.

State and persistence: The header stores static layout hints. Persistent state is flash contents and partition layout exposed by MTD.

Dependencies/integration: Forward declares `mtd_partition` and integrates with SPI flash, MTD partition registration, and board files.

Risks and test signals: Risks include partition misalignment, wrong type override, stale static layouts, and DataFlash non-power-of-two geometry assumptions. Test MTD partition table, JEDEC/type fallback, erase/write/read across partition boundaries, and boot arguments such as `mtdparts=`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spi/flash.h -->
