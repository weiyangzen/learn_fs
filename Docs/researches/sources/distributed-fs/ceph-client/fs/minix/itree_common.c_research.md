<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/itree_common.c -->
# sources/distributed-fs/ceph-client/fs/minix/itree_common.c

## Purpose
`itree_common.c` is a generic include-file implementation for Minix direct/indirect block trees. It is included by both V1 and V2 wrappers after they define `block_t`, `DEPTH`, `DIRECT`, `i_data()`, `block_to_cpu()`, `cpu_to_block()`, and `block_to_path()`. It provides block lookup/allocation for buffered I/O and subtree truncation for file size changes.

## Important APIs, Types, and Functions
The central helper type is `Indirect`, a cached pointer-chain element containing a pointer to a block slot, the slot's saved key, and the buffer holding it. `get_block()` maps a logical block to a physical zone and optionally allocates missing direct/indirect blocks. `get_branch()` reads and validates an existing pointer chain. `alloc_branch()` allocates a run of new indirect/data blocks and initializes indirect blocks. `splice_branch()` atomically attaches a newly allocated branch. Truncation is implemented by `truncate()`, `find_shared()`, `free_data()`, `free_branches()`, and `all_zeroes()`. `nblocks()` estimates total data plus metadata blocks for stat reporting.

## Control Flow
Lookup begins with version-specific `block_to_path()`, producing offsets through direct and indirect levels. `get_branch()` walks from the inode's zone array through buffer-head-backed indirect blocks, checking that previously read slots still match with `verify_chain()`. If the path exists, `get_block()` calls `map_bh()`. If a block is missing and `create` is false, it returns the lookup error or hole. If allocation is requested, `alloc_branch()` allocates the missing tail, initializes intermediate buffers, and `splice_branch()` rechecks the old chain under `pointers_lock` before publishing the first pointer. Races with truncate return `-EAGAIN` and restart.

Truncation computes the first block beyond `i_size`, truncates partial pagecache with `block_truncate_page()`, frees direct slots after the new end, finds any shared indirect branch that must be partially preserved, clears and frees the detached subtree, then frees whole indirect subtrees after the shared branch.

## State and Persistence Behavior
Persistent state is the inode's direct/indirect zone array and indirect blocks on disk. Newly allocated indirect buffers are zeroed, marked uptodate, and dirtied through `mmb_mark_buffer_dirty()` so Minix fsync/eviction can track metadata buffers. Publishing a pointer marks either the indirect buffer or inode dirty and updates ctime. Truncation clears pointers before freeing blocks, marks affected buffers/inodes dirty, updates mtime/ctime, and releases or forgets buffers so stale metadata is not written after block reuse.

## Dependencies and Integration Points
The file depends on definitions supplied by `itree_v1.c` or `itree_v2.c`, plus `minix_new_block()`, `minix_free_block()`, `minix_i()`, buffer-head I/O, and mapping metadata buffer tracking. Its `get_block()` is consumed by `inode.c` address-space operations through version-specific wrappers. It assumes Minix zone size equals block size, which `minix_check_superblock()` enforces.

## Risks
This is concurrency-sensitive code. The global `pointers_lock` only protects pointer-chain validation and splicing; buffer I/O and allocation happen outside it, so every publish must revalidate. Error paths must free every allocated block and forget initialized buffers or leaks/corruption result. Failure to dirty metadata buffers can lose indirect-block updates after fsync. Truncation must handle sparse holes, partially shared indirect paths, and races with readers/writers without freeing still-referenced blocks.

## Test Signals
Exercise direct, single-indirect, double-indirect, and V2 triple-indirect boundaries; sparse reads; ENOSPC during each branch allocation level; truncate to direct/indirect boundaries and to the middle of indirect blocks; concurrent write/truncate stress; fsync after indirect allocation; and corruption/fault-injection for unreadable indirect blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/itree_common.c -->
