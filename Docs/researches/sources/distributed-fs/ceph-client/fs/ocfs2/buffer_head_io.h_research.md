# sources/distributed-fs/ceph-client/fs/ocfs2/buffer_head_io.h

## Purpose
`buffer_head_io.h` declares OCFS2 metadata buffer I/O helpers and read flags used by the filesystem’s metadata cache users.

## Important APIs, types, and functions
It declares `ocfs2_write_block`, `ocfs2_read_blocks_sync`, `ocfs2_read_blocks`, `ocfs2_write_super_or_backup`, and the inline single-block wrapper `ocfs2_read_block`. Flags are `OCFS2_BH_IGNORE_CACHE` for forced disk reads and `OCFS2_BH_READAHEAD` for asynchronous metadata prefetch.

## Control flow
Callers pass a caching object, block number, buffer array, flags, and optional validator. `ocfs2_read_block` checks for a null output pointer then delegates to `ocfs2_read_blocks` for one block.

## State and persistence behavior
The header has no state, but its flags govern whether callers consult or bypass the clustered metadata uptodate cache and whether validation is delayed to a later synchronous read.

## Dependencies and integration points
It depends on Linux buffer heads and OCFS2 `struct ocfs2_super`/`struct ocfs2_caching_info` definitions. It is included by metadata users that need consistent cache-aware I/O behavior.

## Risks and test signals
Risks are invalid flag combinations, null buffer arrays, and validators that assume they are called for cached buffers. Test signals include one-block and multi-block reads, forced reads, readahead plus later validation, and superblock backup writes.
