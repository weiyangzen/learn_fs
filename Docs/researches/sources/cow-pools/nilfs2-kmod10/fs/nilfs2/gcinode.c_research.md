# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/gcinode.c

Implements dummy GC inodes used to cache blocks being moved by garbage collection. These inodes hold data and B-tree node buffers separately from normal dirty data.

Key behavior:
- Submits GC reads for data blocks, optionally translating virtual block numbers through DAT.
- Submits GC reads for B-tree node blocks through the btnode cache.
- Waits for read completion, validates uptodate state, checks B-tree node integrity, and marks buffers dirty for relocation.
- Initializes GC inodes with regular-file mode, buffer-cache address ops, GC bmap operations, and B-tree node cache.
- Removes all pending GC inodes by truncating data pages, clearing node cache pages, and dropping inode references.

Integration: depends on DAT translation, B-tree node validation, buffer cache helpers, and the filesystem-wide `ns_gc_inodes` list.

Risk/notes: GC buffers use `b_blocknr` to preserve virtual block number identity after submitting physical reads. Read errors and broken B-tree nodes abort relocation with `-EIO`.
