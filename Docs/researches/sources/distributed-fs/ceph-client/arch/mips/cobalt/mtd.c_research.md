# sources/distributed-fs/ceph-client/arch/mips/cobalt/mtd.c

Purpose: registers Cobalt firmware flash as a `physmap-flash` platform device.

Important APIs and data: `cobalt_mtd_partitions` defines a single `"firmware"` partition of `0x80000` bytes. `cobalt_flash_data` sets bus width 1. `cobalt_mtd_resource` maps `0x1fc00000..0x1fc7ffff`. `cobalt_mtd_init()` registers the static platform device.

State and integration: partition and resource state are static and handed to MTD/physmap. There is no runtime mutation.

Risks and test signals: partition boundaries are fixed and must match firmware flash layout. Test by checking MTD device enumeration and read-only/read-write policy in the consuming driver.
