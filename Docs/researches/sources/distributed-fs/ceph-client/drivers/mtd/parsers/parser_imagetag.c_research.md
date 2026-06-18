# sources/distributed-fs/ceph-client/drivers/mtd/parsers/parser_imagetag.c

Purpose: BCM963XX CFE image-tag subparser. It splits a firmware partition into kernel and rootfs regions based on the CFE image tag at partition offset 0.

Important APIs/types/functions: `bcm963xx_parse_imagetag_partitions()` is the parser entry for `brcm,bcm963xx-imagetag`. `bcm963xx_read_imagetag()` reads `struct bcm_tag`, checks the header CRC via `crc32_le()`, and null-terminates fixed strings before parsing numeric fields.

Control flow: it reads the tag, parses rootfs start, kernel start, kernel length, and total length as decimal strings, rejects addresses below `BCM963XX_EXTENDED_SIZE`, and converts absolute flash addresses into partition-relative offsets. It handles Broadcom rootfs-first layout and OpenWrt kernel-first layout, computes spare area at erase-aligned total length, and may fold spare space into rootfs for OpenWrt-style images. It allocates only the needed kernel/rootfs partitions and orders them according to physical layout.

State and persistence: persistent state is the image tag embedded in flash. Runtime state is temporary `vmalloc()` tag buffer and the returned partition array. The parser is read-only.

Dependencies and integration: depends on BCM963XX tag definitions, CRC32, MTD parser core, and parent parsers assigning this parser type to firmware partitions. Risks include trusting decimal ASCII fields, tag CRC mismatch, address conversion mistakes, spare length underflow if total length exceeds device size, and layout inference from address order. Test signals include valid Broadcom and OpenWrt tags, bad CRC, unterminated fields, invalid numeric strings, rootfs/kernel zero-length handling, and erase-size alignment.
