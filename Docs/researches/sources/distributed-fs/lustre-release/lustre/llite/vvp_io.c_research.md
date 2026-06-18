<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/vvp_io.c -->
# sources/distributed-fs/lustre-release/lustre/llite/vvp_io.c

## Purpose
`vvp_io.c` implements VVP `cl_io_operations`, bridging Linux VFS page-cache and VM operations to Lustre cl/lov/osc I/O. It manages DLM lock descriptions, layout-version validation, read/write iteration, dirty-page commit, truncate/fallocate/setattr, page faults and mkwrite, fsync bookkeeping, readahead preparation, and lseek locking.

## Important APIs, Types, And Functions
Externally relevant functions are `vvp_io_init()` and `vvp_io_write_commit()`. Major internal functions include `vvp_prep_size()`, `vvp_io_rw_lock()`, `vvp_io_read_start()`, `vvp_io_write_start()`, `vvp_io_commit_sync()`, `vvp_set_batch_dirty()`, `vvp_io_setattr_start/end()`, `vvp_io_fault_start/end()`, `vvp_io_lseek_start/end()`, and the `vvp_io_ops` table.

## Control Flow
`vvp_io_init()` adds the VVP slice, records byte counts/job info, refreshes layout for most operations, and optionally locks page-cache invalidation. Lock callbacks build page-index lock extents, account for group locks, nonblocking/no-expand flags, lockless I/O, direct I/O, and mmap buffers. Read start validates layout, reserves LRU pages, prepares size/KMS with possible glimpse, initializes readahead, and calls `generic_file_read_iter()` with retry on page invalidation sequence changes. Write start handles append position, max file size, LRU reserve, generic write, writeback sync, and `vvp_io_write_commit()`. Fault start handles normal faults and mkwrite quota/dirty preparation. Fini checks restore/write-intent/layout changes and requests restarts as needed.

## State And Persistence
Per-I/O state is kept in `struct vvp_io`: iterator position, remaining bytes, layout generation, readahead span, file/iocb, and read/write or fault queues. Persistent inode state affected here includes `lli_trunc_sem`, `lli_setattr_mutex`, `lli_layout_gen`, `lli_jobinfo`, `lli_page_inv_lock`, `LLIF_DATA_MODIFIED`, and restoring/layout flags. Page dirty/writeback state is updated through Linux page-cache and cl-page ownership.

## Dependencies And Integration Points
This file integrates with cl locks/pages/queues, llite layout refresh/write intent/restore, LOV/OSC async commit, Linux generic file read/write/fault helpers, memcg dirty accounting compatibility shims, mmap VMA scanning, PCC file helpers, HSM restore bits, LSOM attr merge, and LDLM group-lock semantics.

## Risks And Edge Cases
Layout can change mid-I/O, so many paths set `ci_need_restart` or stop continuation. Append writes must re-check size under locks. Async commit can fall back to sync on quota or high priority. mkwrite must avoid dirtying pages beyond EOF and convert quota failures to VM-visible errors. The batching dirty path relies on pages sharing a mapping and on kernel-version-specific dirty accounting behavior.

## Test Signals
Use buffered and direct reads/writes, append races, truncate/fallocate/setattr under load, mmap reads and writes, page fault versus truncate races, HSM restore, layout swap/write-intent restarts, group-lock files, quota exhaustion, dirty accounting across supported kernels, lseek past EOF, and failpoints for lost layout, short commit, and fault pauses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/vvp_io.c -->
