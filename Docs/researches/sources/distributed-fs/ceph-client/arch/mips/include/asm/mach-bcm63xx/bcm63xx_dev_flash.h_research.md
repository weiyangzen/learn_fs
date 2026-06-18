# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_dev_flash.h

**Purpose:** Declares BCM63xx flash type identifiers and flash device registration.

**Important APIs/types/functions:** Defines flash types `BCM63XX_FLASH_TYPE_PARALLEL`, `BCM63XX_FLASH_TYPE_SERIAL`, and `BCM63XX_FLASH_TYPE_NAND`, plus `bcm63xx_flash_register()`.

**Control flow:** Board setup detects or selects flash type, then calls registration to create the appropriate MTD/SPI/NAND/parallel flash platform device.

**State and persistence behavior:** No state in the header. Registered flash devices expose persistent storage; wrong type selection affects boot-critical partitions.

**Dependencies and integration points:** Integrated with NVRAM, MTD, SPI/NAND/parallel flash drivers, chip-select setup, and board registration.

**Risks:** Incorrect type causes probe failure or destructive writes through the wrong bus protocol. Flash registration must coordinate with NVRAM and partition parsing.

**Test signals:** Boot each flash type, verify MTD layout, read JEDEC/NAND IDs, mount/read rootfs, and run safe read-only checks on bootloader/NVRAM partitions.
