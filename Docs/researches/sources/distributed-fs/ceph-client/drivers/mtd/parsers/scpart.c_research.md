# sources/distributed-fs/ceph-client/drivers/mtd/parsers/scpart.c

Purpose: Sercomm partition parser. It combines an on-flash `SCFLMAPOK` partition map with device-tree partition nodes that name Sercomm partition IDs.

Important APIs/types/functions: `scpart_parse()` is the parser entry for `sercomm,sc-partitions`. `scpart_find_partmap()` scans eraseblocks for up to two mirrored magic blocks. `scpart_scan_partmap()` reads one map block and extracts valid `struct sc_part_desc` entries starting at offset 0x800.

Control flow: the parser requires an MTD OF node and `partitions` child. It scans from flash start until mirrors are found, flash ends, or a bad block is hit. A valid map is copied into memory, then each OF child with `sercomm,scpart-id` is matched against the map. Matching entries become MTD partitions with offset/size from flash, `of_node` from DT, optional label, and read-only/lock flags. Matched map entries are marked `ID_ALREADY_FOUND` to prevent duplicate use.

State and persistence: persistent state is the Sercomm map stored in flash and DT metadata. Runtime state is the copied descriptor array and returned partitions. The parser is read-only.

Dependencies and integration: depends on MTD reads/bad-block detection, OF child properties, and static magic/layout constants. Risks include native-endian descriptor assumptions, stopping scan on first bad block, fixed descriptor offset, no bounds check against flash size for map offsets, and explicit `of_node_put(pp)` after `for_each_child_of_node()` that must match iterator semantics. Test signals include mirrored maps, invalid descriptors, unmatched DT IDs, duplicate IDs, read-only/lock properties, bad-block early stop, and endian/corrupt map cases.
