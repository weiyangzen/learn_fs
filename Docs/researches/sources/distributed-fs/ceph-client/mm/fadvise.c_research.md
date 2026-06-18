# sources/distributed-fs/ceph-client/mm/fadvise.c

## Purpose
`fadvise.c` implements generic and VFS-level handling for `posix_fadvise()` style advice. It lets callers tune read-ahead behavior, prefetch expected pages, mark no-reuse access, or discard clean cached pages over a byte range without changing file contents.

## Important APIs, types, and functions
`generic_fadvise()` is the main implementation and is exported for filesystem use. `vfs_fadvise()` dispatches to `file->f_op->fadvise` when provided, otherwise calls the generic implementation. `ksys_fadvise64_64()` resolves an fd and calls `vfs_fadvise()`. Syscall wrappers are conditionally compiled for native `fadvise64_64`, optional `fadvise64`, and compat `fadvise64_64`.

## Control flow
The generic path rejects FIFOs with `-ESPIPE`, rejects negative offsets/lengths or missing mappings with `-EINVAL`, and ignores valid advice for DAX or noop backing devices. It computes an inclusive `endbyte`, treating `len == 0` or overflow as "to end of addressable range".

For `POSIX_FADV_NORMAL`, it resets readahead pages to the backing device default and clears random/no-reuse mode bits. `POSIX_FADV_RANDOM` sets `FMODE_RANDOM`; `POSIX_FADV_SEQUENTIAL` doubles `ra_pages` and clears random mode. `POSIX_FADV_WILLNEED` computes page indexes and calls `force_page_cache_readahead()`. `POSIX_FADV_NOREUSE` sets `FMODE_NOREUSE`. `POSIX_FADV_DONTNEED` first starts writeback for the range, then invalidates only full pages: it rounds the start up, handles the inclusive end page carefully so partial tail pages are preserved unless page-aligned or EOF, drains local LRU additions, tries `mapping_try_invalidate()`, and if failures remain drains all CPU LRU caches and retries with `invalidate_mapping_pages()`.

## State and persistence
Persistent effects are limited to `file->f_ra.ra_pages` and `file->f_mode` advice bits under `file->f_lock`. `WILLNEED` and `DONTNEED` affect page-cache residency but not file data. The operation does not store advice in the inode or on disk.

## Dependencies and integration points
The file integrates with fd lookup, VFS file operations, backing-device readahead settings, DAX detection, page-cache readahead, writeback, LRU drain logic, page-cache invalidation, and syscall compatibility glue. Filesystems can override behavior through `f_op->fadvise`.

## Risks and test signals
Range arithmetic and partial-page handling are the main correctness risks, especially around `len == 0`, overflow, EOF, and unsigned `pgoff_t` underflow. `DONTNEED` must avoid discarding dirty data, hence the flush and retry behavior. Useful tests include syscall ABI tests for native and compat argument packing, FIFO `-ESPIPE`, invalid-advice `-EINVAL`, DAX/noop backing no-op behavior, readahead mode observation, and cache residency checks before and after `WILLNEED` or `DONTNEED`.
