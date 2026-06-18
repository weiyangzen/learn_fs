# sources/distributed-fs/ceph-client/drivers/mtd/parsers/bcm47xxpart.c

Purpose: MTD partition parser for BCM47XX flash layouts. It scans eraseblock-aligned offsets for CFE, board data, factory/POT/ML records, TRX firmware, squashfs rootfs, and NVRAM signatures, then emits a discovered `struct mtd_partition` array.

Important APIs/types/functions: `bcm47xxpart_parse()` is the parser entry registered by `module_mtd_part_parser()`. `bcm47xxpart_add_part()` fills common partition fields. `bcm47xxpart_bootpartition()` reads `bootpartition` from BCM47XX NVRAM to choose the active TRX. Local `struct trx_header` is used only to estimate TRX span and subparser eligibility. The parser exposes OF compatible `brcm,bcm947xx-cfe-partitions`.

Control flow: it clamps very small erase sizes to 4 KiB, allocates up to 20 partitions and a 0x4e8-byte scan buffer, then walks the flash block-by-block. Each block read checks multiple hard-coded magics at known offsets. TRX detection records up to two TRX partition indexes, creates a firmware partition, estimates TRX length from header length and sub-offsets, and skips ahead over the image. After the scan, it probes likely NVRAM sizes at the end of flash. Sizes are inferred from the next discovered partition offset or device end. Finally, TRX partitions are renamed: active TRX keeps `firmware` and receives `types = { "trx" }`; non-active TRX is renamed `failsafe`.

State and persistence: persistent state lives entirely on flash and NVRAM; runtime state is an allocated partition array, temporary read buffer, and two TRX indexes. The parser is read-only except for setting `MTD_WRITEABLE` mask flags on boot and board/factory-like partitions.

Dependencies and integration: depends on MTD core reads, BCM47XX NVRAM, Linux magic constants for squashfs, and parser chaining through the TRX subparser. Integration risk centers on magic offsets, endianness assumptions, NVRAM placement heuristics, and partition size inference from scan order. Test signals include synthetic MTD images with each magic, dual-TRX bootpartition selection, bitflip-tolerant reads, truncated/end-of-flash NVRAM, and max-partition overflow warnings.
