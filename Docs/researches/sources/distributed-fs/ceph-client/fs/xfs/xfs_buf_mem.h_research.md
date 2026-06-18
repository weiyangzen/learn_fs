# sources/distributed-fs/ceph-client/fs/xfs/xfs_buf_mem.h

Purpose: Declares the memory-buffer target API and PAGE_SIZE block geometry used by xmbuf.

Important APIs, types, and functions: Defines `XMBUF_BLOCKSIZE`, `XMBUF_BLOCKSHIFT`, `xfs_buftarg_is_mem()`, and xmbuf allocation, free, daddr verification, transaction detach, finalize, and backing-memory mapping declarations. Non-memory-buffer builds provide false/no-op style stubs for most helpers.

Control flow: Callers check `xfs_buftarg_is_mem()` before taking memory-specific buffer paths; config stubs keep regular builds clean.

State and persistence: No state is stored in the header; it defines the contract that xmbuf data lives in page cache and uses PAGE_SIZE blocks.

Dependencies and integration points: Shared by buffer cache, online fsck, transaction code, and xmbuf implementation.

Risks and test signals: Risks are config mismatches and use without predicate checks. Test `CONFIG_XFS_MEMORY_BUFS=y/n` builds and paths where `bt_bdev == NULL`.
