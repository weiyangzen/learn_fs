# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/alloc.h

Public interface for NILFS persistent allocation. It exposes allocator setup, entry block lookup, entry offset calculation, allocation/free prepare-commit-abort operations, batch freeing, and cache lifecycle helpers.

Important types:
- `struct nilfs_palloc_req`: carries entry number plus descriptor, bitmap, and entry buffer heads across transactional allocator steps.
- `struct nilfs_bh_assoc`: associates a block offset with a cached buffer head.
- `struct nilfs_palloc_cache`: holds cached descriptor, bitmap, and entry buffers under a spinlock.

It also defines little-endian bit operations through ext2 helpers and `find_next_*_bit_le`, tying allocator bitmaps to Linux kernel bitmap semantics.

Risk/notes: callers must pair prepare/commit/abort correctly or buffer references and allocation state can leak or become inconsistent.
