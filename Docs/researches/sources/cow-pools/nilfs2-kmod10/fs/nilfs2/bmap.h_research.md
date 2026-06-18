# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/bmap.h

Core block-map abstraction header. It defines the bmap operation table, bmap state object, pointer request union, stats structure, pointer-type constants, dirty-state helpers, and public bmap APIs.

Important contracts:
- `NILFS_BMAP_PTR_P` means physical block pointers.
- `NILFS_BMAP_PTR_VS` and `NILFS_BMAP_PTR_VM` use DAT-backed virtual block numbers.
- `NILFS_BMAP_LARGE` selects B-tree representation over direct representation in on-disk bmap flags.
- Inline helper functions bridge bmap allocation/end operations to DAT or local pointer counters.

Integration: used by direct, B-tree, inode, DAT, GC, and segment-write paths. It includes `alloc.h` and `dat.h`, making bmap pointer lifecycle tightly coupled to persistent allocator and address translation state.

Risk/notes: several inline helpers assume the caller already holds the bmap semaphore. Misuse can race dirty-state or pointer target updates.
