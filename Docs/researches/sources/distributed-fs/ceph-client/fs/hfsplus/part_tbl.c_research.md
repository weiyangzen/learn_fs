# sources/distributed-fs/ceph-client/fs/hfsplus/part_tbl.c

## Purpose
`part_tbl.c` parses legacy and Apple partition maps to locate an HFS/HFS+ partition within a block device. It is used when the filesystem is mounted from a whole disk image or media with Mac partition metadata rather than a raw HFS+ volume.

## Important APIs, types, and functions
The public entry point is `hfs_part_find(struct super_block *sb, sector_t *part_start, sector_t *part_size)`. Internal parsers are `hfs_parse_old_pmap()` and `hfs_parse_new_pmap()`. Local packed structures describe old partition-map entries and new Apple partition-map blocks. Important magic values include `HFS_OLD_PMAP_MAGIC` (`TS`), `HFS_NEW_PMAP_MAGIC` (`PM`), and `Apple_HFS` partition type matching.

## Control flow
`hfs_part_find()` allocates a buffer sized to `hfsplus_min_io_size()`, reads partition-map block 1 relative to the current `part_start` through `hfsplus_submit_bio()`, dispatches by the first big-endian signature, and frees the buffer on every path.

The old-map parser scans up to 42 embedded entries, looking for nonzero start/size, filesystem id `TFS1`, and either the requested partition index or any partition. The new-map parser reads the `pmMapBlkCnt` count, walks contiguous 512-byte partition entries, selects entries whose type starts with `Apple_HFS` and whose index matches `sbi->part` if set, and rereads the next media block when the current minimum-I/O buffer has been exhausted.

## State and persistence behavior
The code only reads disk partition metadata. On success it mutates the caller-provided `part_start` by adding the selected partition start and stores the selected partition size in sectors/512-byte blocks. It does not persist anything.

## Dependencies and integration points
It depends on HFS+ wrapper block I/O, superblock private mount option `part`, minimum I/O sizing, endian helpers, and slab allocation. It is normally reached from wrapper/superblock discovery before the volume header is interpreted.

## Risks and test signals
Risks include trusting `pmMapBlkCnt` from disk, off-by-one partition indices, partial-buffer pointer arithmetic across minimum I/O boundaries, weak partition-type string matching, and old-map support being limited to 42 entries and `TFS1`. Test signals include old and new Apple partition maps, requested `part=` success/failure, maps larger than one minimum-I/O block, malformed signatures/counts, I/O errors while walking entries, and raw volumes with no partition map.
