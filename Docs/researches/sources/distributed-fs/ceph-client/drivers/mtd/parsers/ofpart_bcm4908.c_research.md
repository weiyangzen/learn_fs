# sources/distributed-fs/ceph-client/drivers/mtd/parsers/ofpart_bcm4908.c

Purpose: post-parse quirk for BCM4908 fixed partitions. It renames firmware slots as active `firmware` or `backup` using bootloader parameters.

Important APIs/types/functions: `bcm4908_partitions_post_parse()` is called by `ofpart_core.c` through `fixed_partitions_quirks`. `bcm4908_partitions_fw_offset()` scans the root node `brcm_blparms` string list for `NAND_RFS_OFS=`.

Control flow: the helper finds `/`, iterates bootloader parameter strings, parses the firmware offset with `kstrtoul()`, and returns offset in bytes by shifting the parsed KiB value left 10. The post-parse function walks all partitions and, for nodes compatible with `brcm,bcm4908-firmware`, names the partition `firmware` when the bootloader offset is missing or equal to the partition offset; otherwise it names it `backup`.

State and persistence: persistent state is in device tree bootloader parameters. Runtime changes are only partition names in the parsed array. No flash writes occur.

Dependencies and integration: depends on OF root properties and `of_device_is_compatible()` on each partition node. Risks include offset-unit assumptions, malformed parameter strings, missing root node, and defaulting to `firmware` when no bootloader offset exists. Test signals include valid and invalid `NAND_RFS_OFS`, multiple firmware nodes, missing property, and mismatch naming behavior.
