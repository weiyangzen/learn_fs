# sources/distributed-fs/ceph-client/fs/fuse/file.c

## Purpose
`file.c` implements regular-file behavior for the FUSE client: open and release, flush/fsync, cached reads and writes, direct I/O, async direct I/O completion, writeback, mmap, file locking, block mapping, lseek, poll notifications, fallocate, copy-file-range, splice and passthrough dispatch, and regular-file inode initialization. It turns VFS file operations into FUSE requests while coordinating Linux page cache state with the userspace server.

## Important APIs, Types, And Functions
The central object is `struct fuse_file`, allocated by `fuse_file_alloc()` and opened by `fuse_file_open()`/`fuse_do_open()`. It carries the userspace file handle `fh`, kernel handle `kh`, open flags, readdir state, polling RB-tree node, waitqueue, passthrough state, and I/O mode. `fuse_file_put()`, `fuse_prepare_release()`, `fuse_file_release()`, `fuse_release_common()`, and `fuse_sync_release()` own release request preparation and deferred/synchronous lifetime management.

I/O request state is carried by `struct fuse_io_priv`, `struct fuse_io_args`, `struct fuse_args_pages`, and local `struct fuse_writepage_args`. Read helpers include `fuse_read_args_fill()`, `fuse_send_read()`, `fuse_do_readfolio()`, `fuse_send_readpages()`, `fuse_read_folio()`, `fuse_readahead()`, and `fuse_cache_read_iter()`. Write helpers include `fuse_write_args_fill()`, `fuse_send_write()`, `fuse_fill_write_pages()`, `fuse_perform_write()`, `fuse_cache_write_iter()`, `fuse_write_update_attr()`, and the writeback functions `fuse_writepages()`, `fuse_launder_folio()`, `fuse_flush_writepages()`, and `fuse_writepage_end()`.

Direct and async I/O are exposed through exported `fuse_direct_io()` and internal `fuse_direct_IO()`, `fuse_direct_read_iter()`, `fuse_direct_write_iter()`, `fuse_aio_complete()`, and `fuse_aio_complete_req()`. The operation tables are `fuse_file_operations` and `fuse_file_aops`, installed by `fuse_init_file_inode()`.

## Control Flow
Open starts at `fuse_open()`: it rejects bad inodes, runs `generic_file_open()`, handles `atomic_o_trunc` writeback/DAX locking, sends `FUSE_OPEN` via `fuse_do_open()`, completes local open state via `fuse_finish_open()`, and invalidates or truncates page cache based on `FOPEN_KEEP_CACHE` and truncation. `fuse_file_open()` optimizes `-ENOSYS` by marking `no_open`/`no_opendir` and defaulting to keep-cache semantics when the daemon has no open method.

Release starts from VFS `.release` or error paths. `fuse_prepare_release()` removes the file from write and poll tracking, wakes poll waiters, prepares a forced/nocreds `FUSE_RELEASE` or `FUSE_RELEASEDIR`, and optionally holds the inode until the request completes. `fuse_file_put()` delays release until all I/O references are gone, sends release synchronously for required paths or asynchronously in the background otherwise, and has a special no-open fast path.

Cached reads go through `fuse_cache_read_iter()` and page-cache `read_folio`/`readahead` callbacks. Reads may first refresh size when auto-invalidation is enabled or the read crosses EOF. Folio reads build FUSE page requests and mark folios complete through iomap helpers. Short reads are treated as EOF and can shrink local `i_size` when writeback cache is disabled.

Cached writes run `generic_write_checks()`, `kiocb_modified()`, then either direct-write fallback, iomap buffered write for writeback-cache cases, or FUSE page-copy writes via `fuse_perform_write()`. `fuse_perform_write()` copies user data into locked folios, sends `FUSE_WRITE`, handles short writes as `-EIO`, updates `i_size`, and invalidates modsize attributes.

Direct I/O pins/extracts user pages or uses kvec pointers, splits requests by `max_read`/`max_write` and `max_pages`, sends `FUSE_READ`/`FUSE_WRITE` synchronously or through `fuse_simple_background()`, and completes nonblocking kiocbs through `fuse_aio_complete()`. Direct writes use exclusive or shared inode locks depending on `FOPEN_PARALLEL_DIRECT_WRITES`, append, EOF extension, and page-cache I/O mode. Direct-I/O open flags force page-cache writeback/invalidation around the transfer.

Writeback uses iomap writepage callbacks. Dirty folios are grouped into `fuse_writepage_args`, associated with an open write file, optionally counted in the syncfs bucket, queued under `fi->queued_writes`, and submitted while `fi->writectr >= 0`. Completion decrements `writectr`, marks writeback done, records mapping errors, invalidates modification attributes when not using writeback cache, and wakes waiters.

The tail operations are protocol wrappers: `fuse_file_mmap()` dispatches DAX/passthrough/direct-io mmap policy and installs VM ops; locks use `FUSE_GETLK`/`FUSE_SETLK` or local fallback; `fuse_lseek()` uses server `FUSE_LSEEK` for hole/data with fallback; `fuse_file_poll()` registers `kh` in an RB tree for `FUSE_NOTIFY_POLL`; `fuse_file_fallocate()` writes back or invalidates relevant ranges around `FUSE_FALLOCATE`; `__fuse_copy_file_range()` flushes source/destination ranges, tries 64-bit then legacy copy op, truncates destination cache, and falls back to splice on unsupported cases.

## State And Persistence Behavior
Open-file state persists in `struct fuse_file` until the final I/O reference and release request complete. Writeback state persists in `struct fuse_inode` lists (`write_files`, `queued_writes`), `writectr`, `page_waitq`, `direct_io_waitq`, and `iocachectr`. Per-operation state is request-local and is freed on request completion.

The file does not store durable data itself. It preserves coherency between kernel page cache and the userspace daemon through writeback, flush, fsync, release, truncate, and invalidation ordering. It updates `attr_version`, `i_size`, and invalidation masks after successful writes, fallocate, direct I/O, and copy operations so later getattr/cache decisions see local changes.

## Dependencies And Integration Points
`file.c` depends on request construction and connection state from `fuse_i.h`, metadata helpers from `dir.c`/`inode.c`, DAX helpers, passthrough helpers, iomode helpers, ioctl helpers, Linux iomap/page-cache/direct-I/O APIs, VFS locking APIs, pipe splice APIs, file locking APIs, and background request scheduling. `fuse_sync_fs_writes()` in `inode.c` relies on writepage bucket accounting performed here.

## Risks And Edge Cases
Risk centers on cache coherency and lock ordering. Direct I/O must not race with writeback or cached mmap; the code uses inode locks, uncached I/O counters, page-cache invalidation, and `FUSE_I_CACHE_IO_MODE`, but EOF-extending async writes are forced into blocking mode. Writeback can deadlock with reclaim if open-file references or `FUSE_NOWRITE` ordering regress. `copy_file_range()` has a documented partial-page mmap race where modifications outside the copied byte range can be lost after cache truncation.

Short reads/writes, server replies larger than requested, stale size replies under writeback cache, `-ENOSYS` feature downgrades, passthrough/direct-I/O precedence, DAX layout breaks, and release paths that can run in server context are all sensitive edge cases. Poll tracking depends on stable `kh` uniqueness and removal during release.

## Test Signals
High-value coverage includes no-open/no-opendir fallback, `FOPEN_KEEP_CACHE` invalidation behavior, `O_TRUNC` with writeback cache and DAX, flush/fsync error propagation, short-read EOF size update, buffered write short-write failure, async direct I/O completion and short read truncation, parallel direct writes versus mmap/cache mode, writeback congestion and `FUSE_NOWRITE` queue draining, mmap policy for DAX/passthrough/direct-io, POSIX and flock fallback, `SEEK_HOLE`/`SEEK_DATA` fallback, poll notify wakeups, fallocate hole-punch/zero-range invalidation, and copy-file-range 64-bit/legacy/fallback behavior.
