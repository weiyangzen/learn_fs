# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_uio.c

## Purpose

Linux kernel implementation of OpenZFS `zfs_uio_t` data movement helpers. It copies data between ZFS buffers and kernel iovecs, bio vectors, block requests, or Linux `iov_iter`s, supports prefaulting, supports non-consuming copies/skips/alignment checks, and manages direct-I/O page pinning.

## Copy Paths

- `zfs_uiomove_iov()` handles `UIO_SYSSPACE` iovecs using `memcpy()`, updating skip, iov pointer/count, resid, and logical offset.
- `zfs_uiomove_bvec_impl()` handles `UIO_BVEC` arrays by mapping each page with `zfs_kmap_local()`, copying into or out of the page window, unmapping, and updating progress.
- `zfs_copy_bvec()` is the single-bio-vec copy helper.
- `zfs_uiomove_bvec_rq()` handles `struct request`-backed UIOs by iterating request segments, finding segments intersecting `uio_loffset`, copying only needed ranges, updating resid/loffset, and setting resid to zero when no segment matched.
- `zfs_uiomove_bvec()` chooses request-backed or plain bvec copying.
- `zfs_uiomove_iter()` uses `copy_to_iter()` / `copy_from_iter()`, returns `EFAULT` on zero-byte pipe progress, optionally reverts the iterator for copy-only mode, and treats partial move copies as `EFAULT`.
- `zfs_uiomove()` dispatches by `uio_segflg` and is exported.

## Prefault, Copy, Skip, Alignment

`zfs_uio_prefaultpages()` does nothing for kernel-space, bvec, or direct-I/O pages, but uses `iov_iter_fault_in_readable()` for user iterators.

`zfs_uiocopy()` copies without consuming the original UIO by cloning the struct and, for iterators, reverting consumed bytes. It returns copied byte count.

`zfs_uioskip()` advances over `n` bytes in bvec, iterator, or sysspace iovec forms, updating skip/pointer/count/offset/resid.

`zfs_uio_page_aligned()` verifies page-aligned base and length for sysspace iovecs, uses `iov_iter_alignment()` for iterators, and currently returns false for other segment types.

## Direct I/O Page Handling

For kernels where `ZERO_PAGE()` is unavailable or unsuitable, marker macros collapse to no-ops. Otherwise ZFS marks replacement pages with a private value (`ZFSPAGE`) so it can later identify and free them.

`zfs_uio_dio_check_for_zero_page()` scans direct-I/O pages for the kernel zero page on writes. When found, it drops the zero page and allocates a private zero-filled page so user mappings cannot change data while a direct-I/O write is in flight.

`zfs_uio_free_dio_pages()` releases direct-I/O pages. It unpins pages when GUP pinning was used, otherwise it unmarks/frees ZFS replacement pages or `put_page()`s normal pages, then frees the page pointer array.

When `pin_user_pages_unlocked()` is available, `zfs_uio_pin_user_pages()` pins user-backed iterator pages for direct I/O, handling `ITER_UBUF` separately when supported and otherwise walking iovecs. It uses `FOLL_WRITE` for reads into userspace and reports partial pinning as `EFAULT`.

`zfs_uio_get_dio_pages_iov_iter()` uses `iov_iter_get_pages2()` or `iov_iter_get_pages()` to collect pages, manually advancing/reverting when required, asserting page alignment, and leaving the original iterator unchanged.

`zfs_uio_get_dio_pages_alloc()` allocates the direct-I/O page vector, chooses pinning or iterator page extraction for `UIO_ITER`, cleans up on errors, verifies expected page count, substitutes zero pages for non-pinned direct write pages, and marks the UIO with `UIO_DIRECT`.
