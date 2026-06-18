# sources/distributed-fs/ceph-client/fs/nfs/nfs4file.c

## Purpose

`nfs4file.c` defines NFSv4 VFS file operations and adapts Linux file operations such as open, flush, copy_file_range, llseek, fallocate, remap_file_range, leases, and server-side-copy helper hooks to NFSv4/NFSv4.2 procedure code.

## Important APIs, Types, and Functions

The primary exported object is `const struct file_operations nfs4_file_operations`. Core functions are `nfs4_file_open`, `nfs4_file_flush`, `nfs4_copy_file_range`, `nfs4_file_llseek`, `nfs42_fallocate`, `nfs42_remap_file_range`, `nfs42_ssc_register_ops`, and `nfs42_ssc_unregister_ops`.

## Control Flow

`nfs4_file_open` allocates an NFS open context, prepares truncation attributes if `O_TRUNC`, calls the protocol `open_context`, rejects stale lookup results by dropping the dentry and returning `-EOPENSTALE`, then attaches the open context and enables direct I/O. `nfs4_file_flush` starts writeback for normal writes or fully flushes and checks writeback errors when delegation policy requires flush-on-close.

Under NFSv4.2, `nfs4_copy_file_range` tries server-side copy and falls back to splice copy on unsupported/cross-device errors. `nfs42_fallocate` maps accepted fallocate modes to allocate/deallocate/zero-range procedures. `nfs42_remap_file_range` maps clone/remap to `nfs42_proc_clone` after flag, swapfile, alignment, locking, direct-I/O blocking, and inode sync checks.

## State and Persistence Behavior

This file owns VFS-visible open contexts and file operation dispatch, but server-side state is created or mutated through lower procedure code. It attaches open contexts to files, initializes fscache file state, clears SSC pseudo-file state flags on close, and forces writeback or page-cache truncation before/after offloaded operations to maintain coherence.

## Dependencies and Integration Points

It depends on generic NFS read/write/mmap/fsync/lock/splice helpers, NFS delegation logic, fscache, pNFS/direct-I/O blockers, NFSv4 open/state owner helpers, and NFSv4.2 procedures. `nfs4proc.c` exposes `nfs4_file_operations` through the NFS RPC ops table.

## Risks and Edge Cases

Open must distinguish stale cached dentries from valid positive dentries. Copy and clone must not expose stale data: source dirty data is synchronized and destination cache is invalidated/truncated. Clone alignment follows `server->clone_blksize`, with an EOF exception for unaligned final ranges. SSC pseudo-open manually constructs file/open/state objects and needs careful cleanup.

## Test Signals

Tests should cover cached open retry via `-EOPENSTALE`, `O_TRUNC` open, close-to-open flush/writeback errors, `copy_file_range` same-server and cross-server fallback, fallocate modes and invalid modes, clone alignment/swapfile rejection, SEEK_HOLE/DATA fallback, and SSC open/close registration under NFSv4.2.
