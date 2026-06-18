# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsPages.h

## Purpose
`FhgfsOpsPages.h` declares BeeGFS page-cache/address-space operations and provides the fast inline inode-size correction wrapper used after paged reads. It defines the maximum page-vector list size shared with the page batching implementation.

## Important APIs, Types, And Functions
- `BEEGFS_MAX_PAGE_LIST_SIZE` caps chunk page-vector sizes and must remain larger than the implementation's initial search size.
- Cache lifecycle: `FhgfsOpsPages_initPageListVecCache()` and `FhgfsOpsPages_destroyPageListVecCache()`.
- Read callbacks: `FhgfsOps_readpagesVec()`, `FhgfsOpsPages_readpageSync()`, `FhgfsOps_read_folio()` or `FhgfsOpsPages_readpage()`, and `FhgfsOpsPages_readahead()` or `FhgfsOpsPages_readpages()`.
- Write callbacks: `FhgfsOpsPages_writepage()`, `FhgfsOpsPages_writepages()`, and `FhgfsOpsPages_writeBackPage()`.
- Completion and size helpers: `FhgfsOpsPages_incInodeFileSizeOnPagedRead()`, `__FhgfsOpsPages_incInodeFileSizeOnPagedRead()`, `FhgfsOpsPages_isShortRead()`, `FhgfsOpsPages_endReadPage()`, and `FhgfsOpsPages_endWritePage()`.

## Control Flow
The header selects folio-aware or page-based callback declarations depending on kernel feature macros. The inline `FhgfsOpsPages_incInodeFileSizeOnPagedRead()` reads current `i_size`, returns immediately for non-positive reads, and calls the slower non-inline helper only when `offset + readRes` exceeds local size.

## State And Persistence Behavior
The header itself holds no state. The inline helper can trigger local inode-size correction through the implementation function, which may refresh metadata and increase local `i_size`.

## Dependencies And Integration Points
The header depends on `toolkit/FhgfsPage.h` and Linux page-cache types. It is included by BeeGFS page-cache implementation and address-space operation table declarations used by inode setup.

## Risks
- The documented maximum page-list size comment appears to state `65536` pages and `262144 MiB` for 4K pages, while the macro is `65535`; consumers should rely on the macro and implementation assertions.
- If the inline size check is removed or bypassed, reads beyond stale local `i_size` can be discarded incorrectly by callers.
- Kernel feature macro mismatches can produce incorrect address-space operation signatures.

## Test Signals
Compile coverage for folio and non-folio kernels, read-completion tests where remote reads extend beyond local `i_size`, and static checks that `BEEGFS_MAX_PAGE_LIST_SIZE` remains above implementation thresholds validate this header.
