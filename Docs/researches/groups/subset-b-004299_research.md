# subset-b-004299 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/bcm47xxpart.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/parsers/bcm47xxpart.c

Purpose: MTD partition parser for BCM47XX flash layouts. It scans eraseblock-aligned offsets for CFE, board data, factory/POT/ML records, TRX firmware, squashfs rootfs, and NVRAM signatures, then emits a discovered `struct mtd_partition` array.

Important APIs/types/functions: `bcm47xxpart_parse()` is the parser entry registered by `module_mtd_part_parser()`. `bcm47xxpart_add_part()` fills common partition fields. `bcm47xxpart_bootpartition()` reads `bootpartition` from BCM47XX NVRAM to choose the active TRX. Local `struct trx_header` is used only to estimate TRX span and subparser eligibility. The parser exposes OF compatible `brcm,bcm947xx-cfe-partitions`.

Control flow: it clamps very small erase sizes to 4 KiB, allocates up to 20 partitions and a 0x4e8-byte scan buffer, then walks the flash block-by-block. Each block read checks multiple hard-coded magics at known offsets. TRX detection records up to two TRX partition indexes, creates a firmware partition, estimates TRX length from header length and sub-offsets, and skips ahead over the image. After the scan, it probes likely NVRAM sizes at the end of flash. Sizes are inferred from the next discovered partition offset or device end. Finally, TRX partitions are renamed: active TRX keeps `firmware` and receives `types = { "trx" }`; non-active TRX is renamed `failsafe`.

State and persistence: persistent state lives entirely on flash and NVRAM; runtime state is an allocated partition array, temporary read buffer, and two TRX indexes. The parser is read-only except for setting `MTD_WRITEABLE` mask flags on boot and board/factory-like partitions.

Dependencies and integration: depends on MTD core reads, BCM47XX NVRAM, Linux magic constants for squashfs, and parser chaining through the TRX subparser. Integration risk centers on magic offsets, endianness assumptions, NVRAM placement heuristics, and partition size inference from scan order. Test signals include synthetic MTD images with each magic, dual-TRX bootpartition selection, bitflip-tolerant reads, truncated/end-of-flash NVRAM, and max-partition overflow warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/bcm47xxpart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/bcm63xxpart.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/parsers/bcm63xxpart.c

Purpose: Broadcom BCM63XX CFE partition parser that creates the top-level NOR layout around CFE, NVRAM, and the Linux firmware region.

Important APIs/types/functions: `bcm63xx_parse_cfe_partitions()` is the registered parser. `bcm63xx_detect_cfe()` verifies a CFE boot environment on MIPS by checking `fw_arg3 == CFE_EPTSEAL`. `bcm63xx_read_nvram()` reads and validates `struct bcm963xx_nvram` using `bcm963xx_nvram_checksum()`. `bcm63xx_parse_cfe_nor_partitions()` builds three partitions and marks `linux` with `types = { "bcm963xx-imagetag" }`.

Control flow: the parser rejects non-CFE boots, allocates an NVRAM buffer with `vzalloc()`, reads NVRAM at offset 0x580, warns on checksum mismatch, defaults missing PSI size, and only supports non-NAND devices. NOR partition creation rounds CFE and NVRAM sizes to at least 64 KiB erase alignment, creates `CFE` at offset 0, `nvram` at the end of flash, and `linux` spanning the remaining area. The `linux` partition is passed to the BCM963XX imagetag subparser.

State and persistence: persistent inputs are CFE boot ABI and NVRAM flash contents. The function does not modify flash; it only marks partition metadata. Runtime state is temporary NVRAM and allocated partition structures.

Dependencies and integration: depends on BCM963XX NVRAM/tag headers, MIPS CFE bootinfo when built for MIPS, MTD type helpers, and parser chaining to `bcm963xx-imagetag`. Risks include false negatives outside MIPS, unsupported NAND, invalid PSI sizes, and continued operation after NVRAM checksum warnings. Test signals include CFE/non-CFE boot simulation, bad checksum NVRAM, zero `psi_size`, erase-size rounding, NAND rejection, and validation that the `linux` partition invokes imagetag parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/bcm63xxpart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/brcm_u-boot.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/parsers/brcm_u-boot.c

Purpose: parser for Broadcom U-Boot environment partitions. It discovers up to two environment blobs by scanning for a small `uEnv` header.

Important APIs/types/functions: `brcm_u_boot_parse()` is the parser entry for compatible `brcm,u-boot`. `struct brcm_u_boot_header` stores little-endian magic and length. `names[]` assigns `u-boot-env` and `u-boot-env-backup`.

Control flow: the parser allocates a two-entry partition array, scans from offset 0 to the smaller of flash size and 2 MiB in 0x1000-byte steps, reads the header at each step, tolerates corrected bitflips, and compares the magic to `BRCM_U_BOOT_MAGIC`. For each hit it sets name, offset, and size as `sizeof(header) + length`, then stops after two hits.

State and persistence: all persistent data is the on-flash environment header and payload. Runtime state is the partition array; there is no cleanup callback because names are static. The parser does not mutate flash.

Dependencies and integration: integrates with MTD parser core and OF matching. Risks include trusting unbounded length, fixed scan window/step, and returning an allocated empty partition array when no headers are found. Test signals include primary and backup env images, malformed lengths, flash smaller than 2 MiB, read failures versus bitflips, and max-two behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/brcm_u-boot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/cmdlinepart.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/parsers/cmdlinepart.c

Purpose: command-line MTD partition parser for `mtdparts=` syntax. It converts boot/module parameters into `struct mtd_partition` arrays matched by MTD device name.

Important APIs/types/functions: `mtdpart_setup()` stores the raw command-line string via `__setup("mtdparts=", ...)`. `mtdpart_setup_real()` parses one or more MTD definitions. `newpart()` recursively parses comma-separated partition definitions and performs one combined allocation for partition structs, names, and the per-MTD descriptor. `parse_cmdline_partitions()` resolves offsets/sizes for a concrete `mtd_info` and returns a duplicated partition array. Module parameter `mtdparts` allows runtime module input.

Control flow: parsing is lazy; the first `parse_cmdline_partitions()` call parses the saved string into a global linked list. `newpart()` handles `-` remaining-size partitions, optional `@offset`, optional `(name)`, and flags `ro`, `lk`, and `slc`. During device matching, continuous offsets are calculated, remaining sizes are expanded, oversized partitions are truncated at flash end, and zero-sized partitions are removed by `memmove()`.

State and persistence: parser state is global and lasts for module lifetime: `partitions`, `cmdline`, and `cmdline_parsed`. The returned partitions are `kmemdup()` copies so later size mutation of the global template does not directly share with MTD core callers, though the template itself is updated during resolution. It does not touch flash.

Dependencies and integration: uses `memparse()`, MTD parser registration, MTD flags, and kernel/module parameter infrastructure. Risks include recursive parsing depth, global mutable parse state, syntax ambiguity around colons in names, and accepting overlapping/out-of-order partitions by design. Test signals include complex names containing colons, fill-up partition rejection when followed by more entries, truncation at device size, zero-size removal, all flag combinations, module parameter versus boot parameter, and multiple MTD IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/cmdlinepart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/ofpart_bcm4908.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/parsers/ofpart_bcm4908.c

Purpose: post-parse quirk for BCM4908 fixed partitions. It renames firmware slots as active `firmware` or `backup` using bootloader parameters.

Important APIs/types/functions: `bcm4908_partitions_post_parse()` is called by `ofpart_core.c` through `fixed_partitions_quirks`. `bcm4908_partitions_fw_offset()` scans the root node `brcm_blparms` string list for `NAND_RFS_OFS=`.

Control flow: the helper finds `/`, iterates bootloader parameter strings, parses the firmware offset with `kstrtoul()`, and returns offset in bytes by shifting the parsed KiB value left 10. The post-parse function walks all partitions and, for nodes compatible with `brcm,bcm4908-firmware`, names the partition `firmware` when the bootloader offset is missing or equal to the partition offset; otherwise it names it `backup`.

State and persistence: persistent state is in device tree bootloader parameters. Runtime changes are only partition names in the parsed array. No flash writes occur.

Dependencies and integration: depends on OF root properties and `of_device_is_compatible()` on each partition node. Risks include offset-unit assumptions, malformed parameter strings, missing root node, and defaulting to `firmware` when no bootloader offset exists. Test signals include valid and invalid `NAND_RFS_OFS`, multiple firmware nodes, missing property, and mismatch naming behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/ofpart_bcm4908.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/ofpart_bcm4908.h -->
# sources/distributed-fs/ceph-client/drivers/mtd/parsers/ofpart_bcm4908.h

Purpose: tiny conditional declaration header for the BCM4908 fixed-partition post-parse quirk.

Important APIs/types/functions: declares `bcm4908_partitions_post_parse(struct mtd_info *mtd, struct mtd_partition *parts, int nr_parts)` only when `CONFIG_MTD_OF_PARTS_BCM4908` is enabled.

Control flow and state: there is no executable logic or persistent state. It constrains compilation so `ofpart_core.c` can refer to the quirk only under matching Kconfig.

Dependencies and integration: depends on forward-visible MTD types from including C files. Risks are limited to build configuration drift: if the C implementation or caller conditionals diverge from this guard, link or compile errors result. Test signals are build coverage with the option enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/ofpart_bcm4908.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/ofpart_core.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/parsers/ofpart_core.c

Purpose: core device-tree MTD partition parser. It supports modern `fixed-partitions`, optional vendor quirks, direct-child legacy fallback, and an obsolete `partitions` property parser.

Important APIs/types/functions: `parse_fixed_partitions()` handles nodes and subnodes. `parse_ofoldpart_partitions()` handles the old flat binding. `struct fixed_partitions_quirks` allows post-parse callbacks from BCM4908 and Linksys NS helpers. `ofpart_parser_init()` registers both `fixed-partitions` and `ofoldpart` parsers.

Control flow: for master devices, the parser prefers a `partitions` child and otherwise scans direct children; for MTD partitions, it parses the node itself. Dedicated `partitions` nodes must match the parser OF table. Direct-child fallback skips nodes with `compatible` to avoid consuming real devices. It counts usable children, allocates the partition array, validates each `reg` length against address and size cells, computes offset/size, stores `of_node`, selects `label` or `name`, and maps `read-only`, `lock`, and `slc-mode` properties into MTD flags. Vendor `post_parse` hooks may rename slots. Failure unwinds nodes and allocations.

State and persistence: persistent inputs are device-tree properties. Runtime state is the partition array and referenced OF nodes; no flash writes occur. `ofoldpart` reads big-endian offset/length pairs, treats low length bit as read-only, and derives names from `partition-names`.

Dependencies and integration: integrates with OF, MTD parser core, and vendor quirk files. Risks include fallback behavior for invalid direct child nodes, incorrect `#size-cells = <0>` workaround, OF node lifetime mistakes, and partition name absence. Test signals include dedicated and direct-child layouts, compatible child skipping, bad/missing `reg`, read-only/lock/slc flags, quirk callbacks, old binding with name exhaustion, and module aliases for parser autoloading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/ofpart_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/ofpart_linksys_ns.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/parsers/ofpart_linksys_ns.c

Purpose: Linksys Northstar fixed-partition post-parse quirk that names the active firmware slot using CFE NVRAM.

Important APIs/types/functions: `linksys_ns_partitions_post_parse()` is invoked from `ofpart_core.c`. `ofpart_linksys_ns_bootpartition()` reads NVRAM key `bootpartition` through `bcm47xx_nvram_getenv()`.

Control flow: the helper tries to parse `bootpartition` into an integer, warning when the key is missing or malformed and defaulting to 0. The post-parse loop increments a firmware-slot index for partitions compatible with `linksys,ns-firmware`; the indexed active slot becomes `firmware`, all others become `backup`.

State and persistence: persistent state is CFE NVRAM and device-tree partition compatibility. Runtime state is only mutated partition names. The code is read-only with respect to flash/NVRAM.

Dependencies and integration: depends on BCM47XX NVRAM support and the fixed-partition quirk hook. Risks include NVRAM absence, invalid slot indexes, assumptions about firmware-node ordering, and defaulting to slot 0. Test signals include missing and malformed bootpartition, multiple firmware nodes, slot indexes beyond count, and Kconfig enabled/disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/ofpart_linksys_ns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/ofpart_linksys_ns.h -->
# sources/distributed-fs/ceph-client/drivers/mtd/parsers/ofpart_linksys_ns.h

Purpose: conditional declaration header for the Linksys NS fixed-partition post-parse quirk.

Important APIs/types/functions: declares `linksys_ns_partitions_post_parse(struct mtd_info *mtd, struct mtd_partition *parts, int nr_parts)` only under `CONFIG_MTD_OF_PARTS_LINKSYS_NS`.

Control flow and state: no executable logic or persistence. It provides a compile-time boundary between the optional quirk implementation and `ofpart_core.c`.

Dependencies and integration: relies on including files to have MTD declarations in scope. Risks are build-only: missing guard symmetry would cause unresolved symbols or unused references. Test signals are allmodconfig and builds with the option disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/ofpart_linksys_ns.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/parser_imagetag.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/parsers/parser_imagetag.c

Purpose: BCM963XX CFE image-tag subparser. It splits a firmware partition into kernel and rootfs regions based on the CFE image tag at partition offset 0.

Important APIs/types/functions: `bcm963xx_parse_imagetag_partitions()` is the parser entry for `brcm,bcm963xx-imagetag`. `bcm963xx_read_imagetag()` reads `struct bcm_tag`, checks the header CRC via `crc32_le()`, and null-terminates fixed strings before parsing numeric fields.

Control flow: it reads the tag, parses rootfs start, kernel start, kernel length, and total length as decimal strings, rejects addresses below `BCM963XX_EXTENDED_SIZE`, and converts absolute flash addresses into partition-relative offsets. It handles Broadcom rootfs-first layout and OpenWrt kernel-first layout, computes spare area at erase-aligned total length, and may fold spare space into rootfs for OpenWrt-style images. It allocates only the needed kernel/rootfs partitions and orders them according to physical layout.

State and persistence: persistent state is the image tag embedded in flash. Runtime state is temporary `vmalloc()` tag buffer and the returned partition array. The parser is read-only.

Dependencies and integration: depends on BCM963XX tag definitions, CRC32, MTD parser core, and parent parsers assigning this parser type to firmware partitions. Risks include trusting decimal ASCII fields, tag CRC mismatch, address conversion mistakes, spare length underflow if total length exceeds device size, and layout inference from address order. Test signals include valid Broadcom and OpenWrt tags, bad CRC, unterminated fields, invalid numeric strings, rootfs/kernel zero-length handling, and erase-size alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/parser_imagetag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/parser_trx.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/parsers/parser_trx.c

Purpose: TRX firmware subparser that exposes loader, Linux, and data/rootfs/UBI subpartitions inside a TRX image.

Important APIs/types/functions: `parser_trx_parse()` is the registered parser for `brcm,trx`. `parser_trx_data_part_name()` reads the first word of the data area and returns `ubi` when it sees UBI EC magic, otherwise `rootfs`. Local `struct trx_header` mirrors the TRX header.

Control flow: it optionally reads `brcm,trx-magic` from DT, allocates up to four partitions, reads the header from offset 0, and rejects non-matching magic with `-ENOENT`. If `offset[2]` is nonzero it treats `offset[0]` as an LZMA loader. It then creates `linux` and data partitions for subsequent nonzero offsets. Sizes are inferred by the next partition offset or MTD partition end.

State and persistence: persistent input is the TRX header and optional UBI magic in flash. Runtime state is the allocated partition array. The parser performs no writes.

Dependencies and integration: depends on OF for magic override, MTD reads, and MTD parser chaining from parent firmware partitions. Risks include little/native-endian assumptions, malformed offset ordering causing underflow sizes, limited validation of offsets against device size, and incomplete handling of unusual TRX layouts. Test signals include default and custom magic, loader/no-loader images, UBI data detection, out-of-order offsets, short reads/errors, and bitflip behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/parser_trx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/qcomsmempart.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/parsers/qcomsmempart.c

Purpose: Qualcomm SMEM-backed flash partition parser. It reads a shared-memory partition table provided by firmware and creates MTD partitions from block offsets.

Important APIs/types/functions: `parse_qcomsmem_part()` is the parser entry for `qcom,smem-part`. `struct smem_flash_ptable` and `struct smem_flash_pentry` model SMEM table versions 3 and 4. `parse_qcomsmem_cleanup()` frees dynamically duplicated names.

Control flow: the parser rejects NOR devices when 4 KiB sectors are configured because SMEM tables use eraseblock units. It first reads only the header via `qcom_smem_get()`, validates magic, partition count, and version, calculates the full table length, then reads the complete table. It counts non-empty names, allocates exactly that many `mtd_partition` entries, lowercases duplicated names, and converts offset/length from eraseblock units to bytes.

State and persistence: partition definitions persist in Qualcomm SMEM, not in the flash being parsed. Runtime state consists of allocated partition names and array. The cleanup callback owns those names. No flash writes occur.

Dependencies and integration: depends on Qualcomm SMEM service ID 9 in host 0, MTD erase size, ctype lowercasing, and parser OF matching. Risks include SMEM probe deferral, version drift beyond v4, attr-to-`mask_flags` semantic assumptions, multiplication overflow on large devices, and incompatibility with 4 KiB-sector NOR. Test signals include v3/v4 tables, empty names, uppercase names, excessive partition count, invalid magic/version, `-EPROBE_DEFER`, and cleanup leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/qcomsmempart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/redboot.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/parsers/redboot.c

Purpose: RedBoot FIS partition parser. It reads the Flash Image System directory and converts image descriptors into sorted MTD partitions.

Important APIs/types/functions: `parse_redboot_partitions()` is the parser entry and module alias `RedBoot`. `struct fis_image_desc` models the 256-byte RedBoot descriptor. `parse_redboot_of()` optionally overrides the module `directory` block using `fis-index-block`. `redboot_checksum()` currently accepts all descriptors.

Control flow: it chooses the FIS directory eraseblock from the configured index, supporting negative indexes from the end and skipping bad blocks. It reads one eraseblock into a vmalloc buffer, locates the `FIS directory` descriptor, detects byte-swapped tables, updates slot count from descriptor size, and optionally byte-swaps all entries. It builds a sorted linked list by `flash_base`, adjusting origin from parser data or masking by device size. It then allocates partition structs plus names, optionally inserts `unallocated` gaps, marks RedBoot/config/FIS directory read-only when configured, and frees the temporary list and buffer.

State and persistence: persistent state is the RedBoot FIS table in flash and optional DT/module directory setting. Runtime state is a vmalloc directory buffer, linked list, and returned partition array. No flash writes occur.

Dependencies and integration: depends on MTD bad-block handling, OF, Kconfig options for read-only and unallocated gaps, and parser origin data. Risks include accepting unchecked descriptors, global mutable `directory`, endian heuristic mistakes, name `strlen()` on corrupt non-terminated data, and gap math tied to eraseblock size. Test signals include positive/negative directory indexes, bad block skipping, swapped and native tables, deleted/end markers, origin adjustment, unallocated gaps, read-only config, and no-table returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/redboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/scpart.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/parsers/scpart.c

Purpose: Sercomm partition parser. It combines an on-flash `SCFLMAPOK` partition map with device-tree partition nodes that name Sercomm partition IDs.

Important APIs/types/functions: `scpart_parse()` is the parser entry for `sercomm,sc-partitions`. `scpart_find_partmap()` scans eraseblocks for up to two mirrored magic blocks. `scpart_scan_partmap()` reads one map block and extracts valid `struct sc_part_desc` entries starting at offset 0x800.

Control flow: the parser requires an MTD OF node and `partitions` child. It scans from flash start until mirrors are found, flash ends, or a bad block is hit. A valid map is copied into memory, then each OF child with `sercomm,scpart-id` is matched against the map. Matching entries become MTD partitions with offset/size from flash, `of_node` from DT, optional label, and read-only/lock flags. Matched map entries are marked `ID_ALREADY_FOUND` to prevent duplicate use.

State and persistence: persistent state is the Sercomm map stored in flash and DT metadata. Runtime state is the copied descriptor array and returned partitions. The parser is read-only.

Dependencies and integration: depends on MTD reads/bad-block detection, OF child properties, and static magic/layout constants. Risks include native-endian descriptor assumptions, stopping scan on first bad block, fixed descriptor offset, no bounds check against flash size for map offsets, and explicit `of_node_put(pp)` after `for_each_child_of_node()` that must match iterator semantics. Test signals include mirrored maps, invalid descriptors, unmatched DT IDs, duplicate IDs, read-only/lock properties, bad-block early stop, and endian/corrupt map cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/scpart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/sharpslpart.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/parsers/sharpslpart.c

Purpose: Sharp SL NAND partition parser for devices whose partition table is stored behind the Sharp FTL logical-address mapping.

Important APIs/types/functions: `sharpsl_parse_mtd_partitions()` is the parser entry. `struct sharpsl_ftl` holds `logmax` and a logical-to-physical table. `sharpsl_nand_check_ooblayout()`, `sharpsl_nand_get_logical_num()`, `sharpsl_nand_init_ftl()`, and `sharpsl_nand_read_laddr()` reconstruct enough FTL mapping to read the partition info sectors. `struct sharpsl_nand_partinfo` stores start/end/magic.

Control flow: it verifies OOB bytes 8-15 are free for FTL metadata, scans the first 7 MiB worth of physical blocks, skips bad blocks, reads OOB, decodes logical block numbers from three redundant copies with parity, and builds `log2phy`. It tries partition info at logical addresses 0x60000 and 0x64000, validates BOOT/FSRO/FSRW magics and monotonically increasing boundaries, fixes the final end to the actual MTD size, then creates `smf`, `root`, and `home` partitions.

State and persistence: persistent state is NAND OOB FTL metadata and partition info records. Runtime mapping is temporary and freed before returning. No flash writes occur, but bad block/OOB behavior directly affects discoverability.

Dependencies and integration: depends on MTD OOB layout APIs, raw OOB reads, bad-block checks, bit operations, and historical Sharp SL media layout constants. Risks include fixed 7 MiB FTL area, ignoring duplicate logical mappings after first hit, inability to read across logical block boundaries, strict OOB layout requirements, and hardcoded three-part output. Test signals include OOB layout coverage, redundant logical-number corruption, bad blocks, invalid first table with valid second table, boundary sanity failures, and older 64 MiB fixup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/sharpslpart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/tplink_safeloader.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/parsers/tplink_safeloader.c

Purpose: TP-Link Safeloader partition table parser. It reads an ASCII partition table embedded in firmware and exposes its entries as MTD partitions.

Important APIs/types/functions: `mtd_parser_tplink_safeloader_parse()` is the parser entry for `tplink,safeloader-partitions`. `mtd_parser_tplink_safeloader_read_table()` locates and reads the table using DT property `partitions-table-offset`. `mtd_parser_tplink_safeloader_cleanup()` frees dynamic names.

Control flow: the table reader obtains the relevant OF node, reads a big-endian size header, allocates `size + 1`, reads the table body, and NUL-terminates it. The parser scans from offset 4 using `sscanf("partition %64s base 0x%llx size 0x%llx%zn\n", ...)`, creating up to 32 partitions and duplicating each name. Cleanup frees names and the array on failure or MTD parser teardown.

State and persistence: persistent state is the Safeloader table in flash and the DT offset. Runtime state is the table buffer and dynamic partition names. The parser does not write flash.

Dependencies and integration: depends on OF, MTD reads, and a specific ASCII table grammar. Risks include trusting header size, parse offset assumptions, node reference handling when the table is on a partition versus master, and partial parsing if formatting deviates. Test signals include master and partition MTD nodes, missing offset property, large/truncated size, max partition count, malformed lines, dynamic-name cleanup, and corrected bitflip reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/parsers/tplink_safeloader.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/rfd_ftl.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/rfd_ftl.c

Purpose: Resident Flash Disk block translation layer for General Software Embedded BIOS RFD media. It presents NOR/RAM MTD devices with RFD headers as 512-byte-sector block devices.

Important APIs/types/functions: `struct partition` owns the blktrans device, header geometry, RAM sector map, block metadata, and reclaim state. `scan_header()` discovers layout and builds `sector_map`. `rfd_ftl_readsect()`, `rfd_ftl_writesect()`, and `rfd_ftl_discardsect()` implement block I/O. `erase_block()`, `mark_sector_deleted()`, `find_writable_block()`, `reclaim_block()`, and `move_block_contents()` handle append/write and garbage collection. `rfd_ftl_add_mtd()` and `rfd_ftl_remove_dev()` integrate with `mtd_blktrans_ops`.

Control flow: on add, the driver accepts NOR/RAM devices under 4 GiB, chooses `block_size` from module parameter or erase size, computes header/data sectors per erase unit, derives CHS geometry, allocates header cache, block table, and sector map, then scans every erase unit for RFD magic. Header map entries locate current physical sectors; duplicate or out-of-range entries mark the device read-only. Reads map logical sectors to physical data or return zeroes for unmapped sectors. Writes append nonzero sectors to a free slot in the current erase unit, write the data first, then update the map entry, then mark the old entry deleted. All-zero writes just clear the sector map and delete old data. Reclaim chooses a block with low live-sector plus erase score, moves live sectors out, and erases the block.

State and persistence: persistent state is the RFD magic and per-block sector map in flash headers plus deleted/free markers. Runtime state mirrors this in `sector_map`, `blocks`, `reserved_block`, and `current_block`. Write persistence uses an append-then-header-update pattern and old-sector deletion, so power-fail ordering matters.

Dependencies and integration: depends on MTD blktrans, MTD erase/read/write/sync, vmalloc for the sector map, jiffies to rotate free-block search, and HD geometry. Risks include no explicit mutex in this file, comments noting races without sync, wear/reclaim heuristics, duplicate mappings causing read-only mode, reserved-block absence preventing writes, and header update failures after data writes. Test signals include clean RFD images, duplicate/out-of-range entries, no empty erase unit, all-zero write/discard semantics, reclaim under full media, erase failure marking, read/write retlen errors, and remove-time cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/rfd_ftl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/sm_ftl.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/sm_ftl.c

Purpose: SmartMedia/xD MTD translation layer. It exposes raw SmartMedia/xD NAND or ROM devices as block devices, reconstructing zone/LBA mappings from OOB metadata and maintaining a write-back block cache.

Important APIs/types/functions: `struct sm_ftl` and `struct ftl_zone` are declared in `sm_ftl.h` and used throughout. Main interfaces are `sm_add_mtd()`, `sm_remove_dev()`, `sm_read()`, `sm_write()`, `sm_flush()`, and `sm_release()` through `mtd_blktrans_ops`. Core helpers include OOB LBA encode/decode (`sm_read_lba()`, `sm_write_lba()`), low-level sector I/O (`sm_read_sector()`, `sm_write_sector()`), zone initialization (`sm_init_zone()`), media validation (`sm_find_cis()`, `sm_recheck_media()`), block write/erase/bad marking, and cache operations.

Control flow: module init creates a freezable workqueue and registers blktrans. Add path derives media geometry from size/write/OOB characteristics, allocates CIS buffer, zones, cache, and blktrans device, finds/validates the CIS, creates a sysfs vendor attribute from CIS data, and registers the block device. Zones initialize lazily by scanning every physical block, reading OOB, classifying erased/bad/valid blocks, building LBA-to-physical mappings, resolving collisions by block validation/erase, and queueing free blocks. Reads translate sector to zone/LBA/block offset, consult dirty cache first, then read and ECC-check physical sectors. Writes populate a single-block cache; a timer schedules asynchronous flush. Flush fills missing cache sectors from old media, writes the full block to a free physical block with updated OOB/ECC, updates mapping, and erases the old block.

State and persistence: persistent state is SmartMedia/xD OOB LBA copies, block/sector valid markers, ECC, CIS signature/vendor data, and physical block contents. Runtime state includes per-zone maps/free FIFOs, unstable/readonly flags, cache contents and invalid bitmap, timer/workqueue, geometry, and sysfs attributes. If CIS reread fails, `unstable` is set and writes are refused.

Dependencies and integration: depends on `nand/raw/sm_common.h`, software Hamming ECC, MTD OOB operations, kfifo, timers/workqueues, sysfs, blktrans, and HD geometry. Risks include complex card-removal handling, retry loops, assumptions by media size, collision resolution that may erase a valid duplicate, no discard operation, cache flush failure leaving dirty state, writes forbidden to CIS/block 0, and cleanup ordering around timers/work. Test signals include 1/2/4/8/16+ MiB media geometry, small-page ECC path, CIS discovery and vendor sysfs, lazy zone init, LBA collision handling, card removal/unstable transition, cache read-after-write, timer flush, no-free-block errors, erase/write failures causing bad marking, and readonly ROM behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/sm_ftl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/sm_ftl.h -->
# sources/distributed-fs/ceph-client/drivers/mtd/sm_ftl.h

Purpose: private header for the SmartMedia/xD FTL implementation.

Important APIs/types/functions: `struct ftl_zone` stores lazy zone initialization state, an LBA-to-physical table, and a FIFO of free blocks. `struct sm_ftl` stores the blktrans device pointer, mutex, media geometry, CIS location and buffer, cache state, flush work/timer, CHS geometry, and sysfs attribute group. `struct chs_entry` maps media size to BIOS geometry. It declares internal helpers `sm_erase_block()`, `sm_mark_block_bad()`, and `sm_recheck_media()`.

Control flow and state: the header itself has no executable flow, but it defines the state machine used by `sm_ftl.c`: media-level state, per-zone mapping/free queues, and a single dirty block cache protected by `mutex` and flushed by work/timer.

Dependencies and integration: includes blktrans, kfifo, scheduler/completion, and MTD headers. It also defines `SM_FTL_PARTN_BITS` and debug print macros tied to the C file's `debug` symbol. Risks are structural: fields must remain coherent with allocation/free logic, cache bitmap width must match block sector count assumptions, and macros rely on a visible `debug` variable. Test signals are compile coverage, allocation/free path validation, and exercising cache/zone fields through `sm_ftl.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/sm_ftl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/Kconfig

Purpose: Kconfig menu for the SPI NOR subsystem and its software write-protection policy.

Important APIs/types/functions: `menuconfig MTD_SPI_NOR` enables the SPI NOR framework, depends on MTD and SPI master support, and selects SPI_MEM. `MTD_SPI_NOR_USE_4K_SECTORS` controls default small-sector erase use. The SWP choice selects one of disable-all, disable-only-volatile, or keep-current behavior. It sources controller Kconfig entries.

Control flow and state: not runtime code, but it shapes build-time availability and defaults. The selected symbols drive compiled objects and behavior in SPI NOR core and related parsers/drivers.

Dependencies and integration: integrates with `drivers/mtd/spi-nor/Makefile`, controller Kconfig, and code paths checking `CONFIG_MTD_SPI_NOR_USE_4K_SECTORS` such as `qcomsmempart.c`. Risks include default 4 KiB sectors breaking UBIFS or firmware partition expectations, SWP policy changing write availability, and duplicate `depends on MTD` line noise. Test signals include config matrix builds for each SWP choice, 4K-sector enabled/disabled behavior, and controller submenu visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/Makefile -->
# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/Makefile

Purpose: build recipe for the SPI NOR framework and manufacturer tables.

Important APIs/types/functions: `spi-nor-objs` aggregates core files (`core.o`, `sfdp.o`, `swp.o`, `otp.o`, `sysfs.o`), manufacturer modules including `atmel.o`, optional `debugfs.o`, and emits `spi-nor.o` under `CONFIG_MTD_SPI_NOR`. It also descends into `controllers/` when SPI NOR is enabled.

Control flow and state: build-time only. Object list order determines what is linked into the composite SPI NOR module/built-in object.

Dependencies and integration: depends on Kconfig symbol `CONFIG_MTD_SPI_NOR` and `CONFIG_DEBUG_FS`. Risks include missing manufacturer object registration, controller directory not built when expected, and debugfs object coverage. Test signals include built-in and module builds, debugfs enabled/disabled builds, and verifying `spi_nor_atmel` and other manufacturer tables link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/atmel.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/atmel.c

Purpose: Atmel/Adesto SPI NOR manufacturer table and vendor-specific locking fixups.

Important APIs/types/functions: `atmel_nor_parts[]` lists supported JEDEC IDs, names, sizes, flags, no-SFDP capabilities, and fixups. `spi_nor_atmel` exports the manufacturer descriptor. `at25fs_nor_locking_ops` supports legacy whole-chip unlock for AT25FS parts. `atmel_nor_global_protection_ops` implements whole-chip global protect/unprotect for parts using Atmel global BP bits.

Control flow: late init fixups replace `nor->params->locking_ops`. AT25FS only allows whole-flash unlock by writing status register 0 and returns unsupported for lock/is_locked. Global protection reads SR, clears SRWD if needed, sets or clears BP bits 5:2, sets SRWD when protecting, and writes SR using `spi_nor_write_sr()` because the command is effectively a protect/unprotect pseudo-command. `is_locked` verifies range and checks all global BP bits.

State and persistence: persistent state is SPI NOR status-register protection bits. Runtime state is manufacturer/part metadata and selected locking ops. These operations can change flash write-protection state.

Dependencies and integration: depends on SPI NOR core helpers, `core.h`, status register definitions, and Kconfig SWP policy. Risks include whole-chip-only locking returning `-EINVAL` for partial ranges, WP# preventing SRWD changes, table entries without explicit size relying on SFDP, and legacy unlock behavior that may reduce protection unexpectedly. Test signals include JEDEC ID matching, late fixup invocation, whole-chip lock/unlock/is_locked, partial range rejection, SRWD asserted failure, and SWP policy boot behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/atmel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/controllers/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/controllers/Kconfig

Purpose: Kconfig entries for SPI NOR memory controllers in this subset.

Important APIs/types/functions: `SPI_HISI_SFC` enables the HiSilicon FMC SPI NOR controller for `ARCH_HISI` or compile testing with I/O memory. `SPI_NXP_SPIFI` enables the NXP LPC SPIFI controller for OF and `ARCH_LPC18XX` or compile testing.

Control flow and state: build-time only; selected symbols control inclusion of `hisi-sfc.o` and `nxp-spifi.o`.

Dependencies and integration: sourced by the parent SPI NOR Kconfig and tied to the controllers Makefile. Risks include insufficient dependency coverage for clocks/platform resources and hidden compile-test warnings. Test signals include native and `COMPILE_TEST` builds, OF-disabled builds for SPIFI, and symbol-to-object mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/controllers/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/controllers/Makefile -->
# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/controllers/Makefile

Purpose: build mapping for SPI NOR controller drivers.

Important APIs/types/functions: maps `CONFIG_SPI_HISI_SFC` to `hisi-sfc.o` and `CONFIG_SPI_NXP_SPIFI` to `nxp-spifi.o`.

Control flow and state: build-time only. It has no runtime state.

Dependencies and integration: depends directly on controller Kconfig symbols and parent SPI NOR Makefile recursion. Risks are limited to stale symbol/object names. Test signals are config builds with each controller enabled singly and together.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/controllers/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/controllers/hisi-sfc.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/controllers/hisi-sfc.c

Purpose: platform driver for HiSilicon FMC SPI NOR controller. It registers up to two child SPI NOR flashes as MTD devices and implements controller register, DMA read, and DMA write operations for SPI NOR core.

Important APIs/types/functions: `struct hifmc_host` stores MMIO bases, clock, DMA buffer, lock, and registered NOR devices. `struct hifmc_priv` stores chipselect and clock rate per flash. Controller ops are `hisi_spi_nor_prep()`, `unprep()`, `read_reg()`, `write_reg()`, `read()`, and `write()`. Probe uses `hisi_spi_nor_register_all()` and `hisi_spi_nor_register()`.

Control flow: probe maps `control` and `memory` resources, gets the clock, sets a 32-bit DMA mask, allocates a coherent 4 KiB DMA buffer, enables the clock long enough to initialize timings and scan/register children, then disables it. Per operation, `prepare` locks the host and enables the clock at the child `spi-max-frequency`; `unprepare` disables and unlocks. Register ops program command/data-count/chipselect registers, optionally copy payload through the I/O window, start an operation, and poll for done. DMA transfers configure normal mode, address width, address, DMA address/length, chipselect, protocol interface type, dummy cycles, opcode, and operation direction; read/write split requests into 4 KiB chunks through the coherent buffer.

State and persistence: runtime state includes host lock, clock state, per-child chipselect/rate, DMA buffer, and registered MTD devices. Persistent flash contents are changed through write/program operations; controller registers are transient.

Dependencies and integration: depends on platform resources named `control` and `memory`, clocks, DMA API, OF child nodes with `reg` and `spi-max-frequency`, SPI NOR core scanning, and MTD registration. Risks include max two chipselects, 32-bit DMA address assumption, no erase controller op because SPI NOR core handles erase via register ops, timeout handling returning short failure, and clock/lock pairing correctness. Test signals include probe resource failures, multiple child nodes, protocol mapping for standard/dual/quad, 3- and 4-byte address modes, chunked DMA boundaries, timeout paths, unregister on partial registration failure, and suspend-like clock sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/controllers/hisi-sfc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/controllers/nxp-spifi.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/controllers/nxp-spifi.c

Purpose: platform driver for NXP LPC SPIFI controller. It supports command mode for register/program/erase and memory-mapped mode for fast reads, then exposes the flash through SPI NOR/MTD.

Important APIs/types/functions: `struct nxp_spifi` holds device, clocks, register and flash windows, embedded `spi_nor`, memory-mode state, and precomputed memory read command. Controller ops include `read_reg`, `write_reg`, `read`, `write`, and `erase`. Setup functions include `nxp_spifi_reset()`, `nxp_spifi_set_memory_mode_on/off()`, `nxp_spifi_setup_memory_cmd()`, and `nxp_spifi_setup_flash()`.

Control flow: probe maps `spifi` and `flash` resources, enables `spifi` and `reg` clocks, resets the controller, clears IDATA/MCMD, obtains the first available flash child, and sets it up. Flash setup parses `spi-rx-bus-width`, CPHA, and CPOL; configures control register timeout/chip-select high/feedback clock/dual-mode bits; supports only SPI mode 0 or 3; performs a dummy RDID workaround; scans SPI NOR with read/fast-read/page-program capabilities plus dual/quad read when configured; builds the memory-mode command; and registers MTD. Reads enter memory mode and copy directly from the mapped flash window. Writes/erases force command mode, program address/opcode/frame form, push bytes through DATA, and poll for completion.

State and persistence: runtime state is clock-enabled MMIO, memory-mode boolean, embedded NOR parameters, and MTD registration. Persistent flash contents are changed by write and erase paths. Memory-mode state affects subsequent command legality and must be reset before register/program/erase commands.

Dependencies and integration: depends on OF, named MMIO resources, two clocks, SPI NOR core, MTD registration, and child flash node properties. Risks include only one child flash, very short 30 us poll timeout constants, unsupported protocol modes beyond 1-1-1/1-1-2/1-1-4 reads, byte-wise programmed writes, memory-mode transition failures, and first-ID-read hardware quirk. Test signals include mode 0/3 and invalid mode, rx width 1/2/4 and invalid width, dummy ID read before scan, memory-mode read after register operations, write/erase command-mode transitions, timeout paths, and MTD unregister on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/controllers/nxp-spifi.c -->
