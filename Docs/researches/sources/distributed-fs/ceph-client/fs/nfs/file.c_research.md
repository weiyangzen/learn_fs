# sources/distributed-fs/ceph-client/fs/nfs/file.c

## Purpose
`file.c` implements regular-file VFS operations for the NFS client. It covers open/release, read/write dispatch, direct-I/O handoff, mmap setup and page-mkwrite, fsync and flush, buffered write begin/end, address-space operations, swapfile support, and POSIX/flock locking integration.

## Important APIs, types, and functions
Public exports include `nfs_check_flags`, `nfs_file_release`, `nfs_file_read`, `nfs_file_splice_read`, `nfs_file_mmap_prepare`, `nfs_file_fsync`, `nfs_truncate_last_folio`, `nfs_file_write`, `nfs_lock`, `nfs_flock`, `nfs_file_aops`, and `nfs_file_operations`.

Important internal functions include `nfs_revalidate_file_size`, `nfs_file_flush`, `nfs_file_fsync_commit`, `nfs_write_begin`, `nfs_write_end`, `nfs_invalidate_folio`, `nfs_release_folio`, `nfs_check_dirty_writeback`, `nfs_launder_folio`, `nfs_swap_activate`, `nfs_swap_deactivate`, `nfs_vm_page_mkwrite`, `do_getlk`, `do_unlk`, and `do_setlk`.

## Control flow
Open validates incompatible `O_APPEND|O_DIRECT`, calls `nfs_open`, and marks the file as capable of direct I/O. Reads dispatch to `nfs_file_direct_read` for `IOCB_DIRECT`; otherwise they take NFS read I/O exclusion, revalidate the mapping, use generic file read/splice helpers, and update statistics.

Buffered writes first check key expiry, reject writes to active swapfiles, revalidate size for append or beyond-EOF writes, clear invalid mapping state, take NFS write I/O exclusion, run generic write checks, and call `generic_perform_write`. `nfs_write_begin` truncates/zeros the last folio for extending writes, flushes incompatible pending writes, and may do read-modify-write for partial folio writes depending on pNFS layout requirements and file open mode. `nfs_write_end` zeroes uninitialized folio regions, calls `nfs_update_folio`, and may force writeback when the open context key is expiring.

Fsync loops until no redirtied pages were observed across writeback, commit, and pNFS sync. Flush writes all dirty pages for writable files and reports writeback errors through errseq state. `mmap_prepare` installs NFS vm operations after generic mmap validation and mapping revalidation; `nfs_vm_page_mkwrite` serializes against fscache, invalidation, and writeback before converting a shared mapping write into an NFS dirty folio update.

Locking flushes or syncs pending writes before remote lock transitions. GETLK consults local locks first, then remote locks unless a delegation or local-lock mount option avoids RPC. SETLK/UNLK call protocol locks or local lock helpers and use lock acquisition as a cache-coherency boundary.

## State and persistence behavior
NFS file data persistence is remote. Local runtime state includes page-cache folios, NFS private folio/writeback state, open contexts, writeback error cursors, fscache state, mmap dirtying state, redirtied-page counters, and lock contexts. Fsync/flush force dirty pages and unstable writes through NFS writeback and commit machinery so server-side durability is reflected to the caller.

Swap activation checks that the NFS file has no holes based on `i_blocks` and `i_size`, activates SUNRPC swap mode, installs one synthetic swap extent, and lets protocol code enable or disable swap-specific behavior.

## Dependencies and integration points
The file is the bridge between VFS file operations, Linux address-space operations, NFS read/write/commit paths, direct I/O from `direct.c`, pNFS layout sync and read-whole-page policy, fscache, MM mmap/pagefault code, swap subsystem, file locking, NFS delegations, mount flags, and NFS statistics/tracepoints.

## Risks
Cache coherency is the main risk. Reads must revalidate stale mappings; writes must not collide with incompatible pending NFS private state; locks and mmap writes must act as coherency points. Fsync must loop on redirtied pages or risk returning before unstable writes settle. Direct and buffered I/O interleaving relies on `nfs_start_io_*` exclusion and page-cache invalidation.

Folio paths are sensitive to partial writes, zeroing beyond EOF, fscache private state, writeback cancellation during invalidation, and reclaim contexts that cannot block. Locking paths risk deadlocks or stale data if writeback is not drained before remote lock calls.

## Test signals
Cover buffered and direct reads/writes, append with remote size changes, partial folio writes requiring read-modify-write, pNFS read-whole-page layouts, mmap shared writes, fsync with redirtied pages, writeback errors `EDQUOT/EFBIG/ENOSPC`, eager/wait mount flags, swap activation on sparse and nonsparse NFS files, local-lock mount options, delegation-aware locks, and cache invalidation around lock acquire/release.
