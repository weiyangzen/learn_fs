# sources/distributed-fs/ceph-client/fs/ocfs2/extent_map.h

Purpose: declares OCFS2 extent mapping data structures and APIs for translating file offsets to disk blocks, reporting extents, detecting overwrite I/O, and reading mapped metadata/data blocks.

Important APIs and types: defines `struct ocfs2_extent_map_item`, `OCFS2_MAX_EXTENT_MAP_ITEMS`, and `struct ocfs2_extent_map`. Declares `ocfs2_extent_map_init`, `ocfs2_extent_map_trunc`, `ocfs2_extent_map_insert_rec`, `ocfs2_get_clusters`, `ocfs2_extent_map_get_blocks`, `ocfs2_fiemap`, `ocfs2_overwrite_io`, `ocfs2_seek_data_hole_offset`, `ocfs2_xattr_get_clusters`, `ocfs2_read_virt_blocks`, `ocfs2_figure_hole_clusters`, and inline `ocfs2_read_virt_block`.

Control flow: the header's only executable path is `ocfs2_read_virt_block`, which validates that the caller supplied a buffer-head pointer and delegates to `ocfs2_read_virt_blocks` for one block.

State and persistence behavior: the map structs describe an in-memory, per-inode MRU cache of a few logical cluster runs and their physical mappings/flags. Persistent extent state remains on disk in OCFS2 dinode and extent block structures.

Dependencies and integration points: consumers include address-space operations, file write preparation, fiemap/lseek/ioctl code, xattr code, and metadata readers. The API assumes callers hold the proper metadata and allocation locks as documented in `extent_map.c`.

Risks: the small cache size is intentional; callers must not assume full mapping coverage. Misusing the APIs without `ip_alloc_sem` can race allocation changes. `ocfs2_read_virt_block` returns `-EINVAL` for a NULL output pointer and logs directly.

Test signals: compile coverage of all declarations, single-block virtual reads, cache initialization on inode setup, cache truncation after allocation changes, and callers handling holes and unwritten/refcounted extent flags.
