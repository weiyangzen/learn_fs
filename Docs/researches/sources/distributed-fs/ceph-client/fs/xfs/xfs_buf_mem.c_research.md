# sources/distributed-fs/ceph-client/fs/xfs/xfs_buf_mem.c

Purpose: Implements memory-backed XFS buffer targets for online fsck and ephemeral btree/recordset users that need buffer-cache behavior without a block device.

Important APIs, types, and functions: Provides `xmbuf_alloc()`, `xmbuf_free()`, `xmbuf_map_backing_mem()`, `xmbuf_verify_daddr()`, `xmbuf_finalize()`, and `xmbuf_trans_bdetach()`. Uses a private unlinked shmem file stored in `bt_file`, PAGE_SIZE block geometry, and a private inode lock class.

Control flow: Allocation creates a shmem kernel file, assigns private locking, disables highmem folios, expands file size, initializes a no-bdev buftarg, and returns it. Mapping validates page-sized single-map buffers and maps shmem folios directly into `bp->b_addr`. Finalization truncates stale folios or runs verifiers. Transaction detach clears BLI dirty/logged/stale state and detaches until the buffer is clean.

State and persistence: Data lives only in private shmem page cache and disappears at `xmbuf_free()`. Stale buffers discard backing folios with `shmem_truncate_range()`.

Dependencies and integration points: Depends on tmpfs/shmem, XFS buftarg setup/teardown, buffer items, transaction detach, verifiers, tracepoints, and `CONFIG_XFS_MEMORY_BUFS`.

Risks and test signals: Risks are accidental userspace exposure, highmem assumptions, non-page-sized misuse, stale folio leaks, and detach loops from inconsistent flags. Test online repair btrees, stale recycling, writeback-error injection, lockdep, and non-memory buftarg rejection.
