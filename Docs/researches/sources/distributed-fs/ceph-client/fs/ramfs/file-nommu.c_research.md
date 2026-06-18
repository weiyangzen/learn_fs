# sources/distributed-fs/ceph-client/fs/ramfs/file-nommu.c

Purpose: Supplies ramfs regular-file operations for no-MMU systems, including special handling to create physically contiguous page-cache backing for shared mappings.

Important APIs, types, and functions: Defines `ramfs_mmap_capabilities()`, `ramfs_file_operations`, `ramfs_file_inode_operations`, `ramfs_nommu_expand_for_mapping()`, `ramfs_nommu_resize()`, `ramfs_nommu_setattr()`, `ramfs_nommu_get_unmapped_area()`, and `ramfs_nommu_mmap_prepare()`.

Control flow: On size growth from zero, `ramfs_nommu_resize()` treats the operation as preparation for shared mmap and calls `ramfs_nommu_expand_for_mapping()`, which allocates a high-order contiguous page set, splits it, clears it, inserts pages into the mapping, marks them dirty and uptodate, and pins them in ramfs page cache. On shrink, no-MMU mappings are checked by `nommu_shrink_inode_mappings()`. The get-unmapped-area path verifies the requested range is within EOF and backed by physically adjacent folios.

State and persistence: File contents live in ramfs page cache with dirty, uptodate pages. The implementation depends on contiguous physical memory for direct shared mappings and has no disk persistence.

Dependencies and integration points: Selected when `CONFIG_MMU` is disabled. Integrates with no-MMU mmap APIs, folio batches, page cache insertion, generic read/write/splice helpers, and VFS setattr.

Risks and test signals: Risks include high-order allocation failure, partial page-cache insertion leaks, incorrect shrink refusal while mapped, physical-contiguity detection mistakes, and size overflows beyond 32 bits. Test shared mmap setup, truncate up/down, sparse or missing pages, high memory pressure, non-shared mmap fallback, and no-MMU read/write/splice paths.
