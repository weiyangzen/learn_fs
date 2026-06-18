# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_uio.c

## Scope

FreeBSD SPL UIO bridge for ZFS. It wraps FreeBSD `struct uio` operations, provides copy-without-advancing behavior, implements skip/fault-safe movement helpers, checks page alignment, and pins user pages for direct I/O.

## Main Interfaces

- `zfs_uiomove()` wraps `uiomove()` and asserts direction consistency.
- `zfs_uiocopy()` clones a uio, copies via `vn_io_fault_uiomove()`, and reports copied bytes without advancing the original.
- `zfs_uioskip()` advances the uio by temporarily using `UIO_NOCOPY`.
- `zfs_uio_fault_move()` wraps fault-aware movement.
- `zfs_uio_page_aligned()` verifies each iovec base and length is page-aligned.
- Direct-I/O page lifecycle is handled by `zfs_uio_get_dio_pages_alloc()` and `zfs_uio_free_dio_pages()`.

## State And Control Flow

For direct I/O, the code allocates `uio->uio_dio.pages`, walks each nonempty iovec, and pins pages with `vm_fault_quick_hold_pages()`. It requires the number of pages obtained to match the expected page count and returns `EFAULT` on short holds. For write operations, pinned pages are made stable by acquiring shared busy state and removing write mappings with `pmap_remove_write()`. Release reverses this with `vm_page_sunbusy()`, `vm_page_unhold_pages()`, and frees the page array.

## Dependencies

Uses FreeBSD VM map/page APIs, `vn_io_fault_uiomove()`, SPL `zfs_uio_t` accessors, `kmem`, and FreeBSD-version-specific uio clone freeing.

## Correctness Notes

The direct-I/O path assumes aligned, page-granular iovecs: `zfs_uio_iov_step()` asserts `len == res * PAGE_SIZE`. Write-side stabilization is important because ZFS may checksum, compress, encrypt, deduplicate, or compute parity from user pages after they are pinned. Read-side direct I/O pages are not made immutable; later ABD/ZIO checksum verification must detect user modifications.
