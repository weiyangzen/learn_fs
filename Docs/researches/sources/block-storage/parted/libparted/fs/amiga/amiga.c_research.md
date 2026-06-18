# File Research: sources/block-storage/parted/libparted/fs/amiga/amiga.c

Shared Amiga RDB helper code used by the Amiga filesystem probes. It defines Rigid Disk Block constants, block identifiers, checksum helpers, and partition-list traversal for finding the RDB partition block matching a `PedGeometry`.

`_amiga_add_id()`, `_amiga_free_ids()`, and `_amiga_id_in_list()` maintain a small linked list of acceptable Amiga block IDs. `_amiga_read_block()` reads a 512-byte block, verifies an allowed ID when supplied, checks the Amiga checksum, and offers to fix bad checksums by recalculating and writing the block. `_amiga_find_rdb()` scans the first 16 blocks for an `RDSK` block.

`amiga_find_part()` reads the RDB, follows the partition block linked list up to 128 entries, detects loops, derives each partition’s start/end from cylinders, surfaces, and blocks-per-track, and returns the partition block whose geometry exactly matches the caller’s geometry. This lets filesystem probes determine Amiga block size and reserved blocks.

Important risks: most code uses big-endian conversions, but the `part->pb_ID != IDNAME_PARTITION` comparison is raw and may depend on host/layout assumptions. The checksum-fix path can write during probing if the exception handler selects fix.
