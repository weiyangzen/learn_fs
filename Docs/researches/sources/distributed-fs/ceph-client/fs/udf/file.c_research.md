# sources/distributed-fs/ceph-client/fs/udf/file.c

## Purpose

`sources/distributed-fs/ceph-client/fs/udf/file.c` implements UDF regular-file VFS operations, mmap write-fault handling, write iteration, ioctls, release-time cleanup, fsync, and file setattr behavior. The source was read as a complete 261-line implementation.

## Important APIs, Types, and Functions

Important functions are `udf_page_mkwrite`, `udf_file_write_iter`, `udf_ioctl`, `udf_release_file`, `udf_file_mmap`, `udf_fsync`, and `udf_setattr`. The exported operation tables are `udf_file_operations` and `udf_file_inode_operations`; the VM operation table is `udf_file_vm_ops`.

## Control Flow

`udf_file_write_iter` locks the inode, runs generic write checks, expands in-ICB files to extent-backed files if the write will no longer fit in the file entry, performs generic buffered write, updates `i_lenAlloc` for still-in-ICB files, marks the inode dirty, and performs synchronous writeback if required. `udf_page_mkwrite` handles mmap write faults by starting a pagefault, updating time, locking invalidation and folio state, allocating blocks for non-in-ICB files through `__block_write_begin`, committing the block write, dirtying the folio, and waiting for stable pages. `udf_ioctl` handles volume ID, block relocation, extended-attribute size, and extended-attribute data queries. `udf_release_file` discards preallocation and truncates tail extents when the last writer closes a file. `udf_setattr` validates ownership/mode/size changes, enforces mount UID/GID override policies, delegates size changes to `udf_setsize`, updates extra UDF permissions, and dirties the inode.

## State and Persistence Behavior

The file modifies inode size, timestamps, dirty state, `i_lenAlloc`, preallocated extents, tail extents, and UDF extra permissions. Persistent metadata updates are written through inode dirtying, `udf_setsize`, extent truncation, and `udf_fsync`/`mmb_fsync` for metadata buffer tracking. Ioctls expose persistent volume identity and inode extended-attribute bytes.

## Dependencies and Integration Points

This file integrates with generic VFS read/write/mmap/splice/lease helpers, UDF block mapping (`udf_get_block`), in-ICB expansion (`udf_expand_file_adinicb`), preallocation/truncation helpers, metadata-buffer fsync, UDF mount flags and superblock identity, block relocation, and Linux permission/capability/user-copy APIs.

## Risks and Edge Cases

In-ICB files require special handling because file data lives inside the inode allocation area until it no longer fits. Mmap write faults must reject folios beyond EOF and allocate only the bytes up to file size for the last page. `UDF_RELOCATE_BLOCKS` requires `CAP_SYS_ADMIN`; other ioctls require read permission and valid user pointers. Release-time cleanup runs only for the last writer. UID/GID mount override flags can reject chown-like setattr attempts. Error paths around in-ICB expansion and page faults must not leave stale page-cache state.

## Test Signals

Tests should cover small in-ICB writes, expansion from in-ICB to extent-backed files, mmap writes at EOF and within EOF, direct and buffered write sync behavior, last-close preallocation discard, `truncate` grow/shrink through `setattr`, UID/GID override enforcement, fsync metadata persistence, and ioctl permission/user-copy behavior.
