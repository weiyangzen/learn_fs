# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/direct.c

Direct block pointer implementation for small NILFS bmaps. It stores direct pointers inside the inode bmap area and provides the direct-map `nilfs_bmap_operations`.

Key behavior:
- Looks up single and contiguous direct entries.
- Inserts mappings after allocating a physical or DAT virtual pointer.
- Deletes mappings by ending the pointer and clearing the slot.
- Finds first/last keys and gathers direct entries for conversion.
- Converts from B-tree back to direct after deletion when the mapping becomes small.
- Propagates dirty direct data blocks by updating or marking DAT entries.
- Assigns physical block numbers and writes segment `nilfs_binfo` records.

Integration: used initially by `nilfs_bmap_read` unless `NILFS_BMAP_LARGE` is set. Conversion to B-tree is triggered by generic bmap insert when `nilfs_direct_check_insert` reports the key exceeds direct range.

Risk/notes: direct insert receives a buffer-head pointer encoded in an integer-like `ptr` argument. Metadata corruption is reported if a dirty buffer key points at an invalid direct slot.
