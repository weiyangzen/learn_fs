# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/bmap.c

Generic NILFS block mapping layer. It wraps direct-map and B-tree implementations behind `struct nilfs_bmap_operations`, provides locking, converts internal corruption signals to filesystem errors, and handles virtual-block translation through DAT.

Key behavior:
- Looks up single or contiguous mappings, translating virtual block numbers with `nilfs_dat_translate` when the bmap uses VBNs.
- Inserts and deletes mappings, converting direct maps to B-tree when direct range is exceeded and converting B-tree back to direct when small enough.
- Truncates mappings by repeatedly deleting the last key.
- Propagates dirty state and assigns physical block numbers through implementation-specific callbacks.
- Initializes bmap state from on-disk inode data and selects pointer type based on special inode numbers: DAT uses physical pointers, cpfile/sufile use single-version virtual pointers, and normal/ifile mappings use multi-version virtual pointers.
- Provides save/restore helpers for bmap state snapshots.

Concurrency: public operations take `b_sem` read/write locks around implementation callbacks. Separate lockdep classes are assigned for DAT and metadata bmaps.

Risk/notes: missing DAT entries after a bmap lookup are treated as metadata corruption. Pointer-type choice is coupled to special NILFS inode numbers.
