# sources/distributed-fs/ceph-client/fs/udf/partition.c

## Purpose
`partition.c` resolves UDF logical partition block addresses to physical block numbers. It supports plain type-1 mappings, VAT virtual mappings, sparable packet remapping, metadata partitions with mirror fallback, and writable sparing-table relocation.

## Important APIs, types, and functions
Public entry points are `udf_get_pblock`, `udf_get_pblock_virt15`, `udf_get_pblock_virt20`, `udf_get_pblock_spar15`, `udf_get_pblock_meta25`, and `udf_relocate_blocks`. Internal `udf_try_read_meta` uses `inode_bmap` to translate metadata-file logical blocks.

## Control flow
`udf_get_pblock` validates the partition index and dispatches through `s_partition_func` when a special map is installed by `super.c`; otherwise it returns partition root plus logical block and offset. VAT lookup reads entries from the VAT inode, handling inline and block-backed VAT storage, then recursively translates through the VAT inode's physical partition while rejecting direct recursion. Sparable lookup aligns to packet boundaries and searches the first available sparing table for remapped packets. Metadata partition lookup maps through the metadata file, and on failure lazily loads and tries the mirror file.

`udf_relocate_blocks` finds the partition containing an old physical block, computes its packet, searches sparing entries, inserts or reuses a remap entry, updates all loaded sparing tables, recomputes descriptor tags, and returns the replacement physical block.

## State and persistence
The file reads and mutates `udf_part_map` type-specific state, VAT inode contents, sparing table buffers, metadata-file inodes, and `MF_MIRROR_FE_LOADED`. Sparing relocation persists by marking sparing-table buffers dirty.

## Dependencies and integration points
It depends on partition maps populated in `super.c`, `inode_bmap` and `udf_bread` from inode code, `udf_update_tag` from `misc.c`, and `s_alloc_mutex` for sparing relocation serialization.

## Risks and test signals
Risks include off-by-one VAT bounds (`block > s_num_entries`), recursion through virtual partitions, invalid sparing table ordering, missing mirror metadata, and dirtying only partially loaded sparing tables. Test signals include VAT 1.50/2.00 media, packet-remapped sparable images, failed metadata primary reads with mirror fallback, invalid partition references, and simulated block relocation.
