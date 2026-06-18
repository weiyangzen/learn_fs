# sources/distributed-fs/ceph-client/fs/affs/bitmap.c

## Purpose
`bitmap.c` manages AFFS free-space accounting and allocation. It initializes bitmap metadata from the root block, counts free blocks, allocates blocks with small preallocation, frees blocks, and releases bitmap caches.

## Important APIs, types, and functions
Public functions are `affs_count_free_blocks()`, `affs_free_block()`, `affs_alloc_block()`, `affs_init_bitmap()`, and `affs_free_bitmap()`.

## Control flow
Mount calls `affs_init_bitmap()` unless read-only. It checks root bitmap validity, reads bitmap blocks and extensions, validates checksums, records per-bitmap free counts, and masks unused tail bits. Allocation consumes an inode's preallocation first, otherwise locates a bitmap with free bits, reads/caches it, clears a bit, adjusts checksum, marks buffers/superblock dirty, and preallocates adjacent bits within a word. Freeing sets the bit, updates checksum/free count, and dirties state.

## State and persistence
Runtime state includes `s_bitmap`, `s_bmap_count`, `s_bmap_bits`, `s_last_bmap`, and cached `s_bmap_bh`. Persistent state is the big-endian bitmap blocks and root-block bitmap pointers. `s_bmlock` serializes all bitmap access.

## Dependencies and integration points
It integrates with block allocation in `file.c`, inode allocation in `inode.c`, metadata deletion in `amigaffs.c`, statfs in `super.c`, and delayed superblock dirtying.

## Risks and test signals
Risks include off-by-one range checks, double frees, bitmap checksum drift, stale cached bitmap buffers, invalid bitmap extensions, and preallocation leaks on close/evict. Test signals include full filesystem allocation, freeing already-free blocks, last-bitmap tail masking, remount read/write transitions, statfs free counts, and ENOSPC paths during writes and creates.
