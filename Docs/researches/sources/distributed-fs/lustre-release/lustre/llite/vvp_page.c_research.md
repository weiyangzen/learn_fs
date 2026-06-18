<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/vvp_page.c -->
# sources/distributed-fs/lustre-release/lustre/llite/vvp_page.c

## Purpose
`vvp_page.c` implements the VVP `cl_page` slice for Linux page-cache pages. It connects `struct page` private pointers to `struct cl_page`, handles read/write completion, tracks discarded readahead, clears stale uptodate state on deletion, and reports VM-level writeback errors.

## Important APIs, Types, And Functions
Important functions are `vvp_page_init()`, `vvp_page_delete()`, `vvp_page_discard()`, `vvp_vmpage_error()`, `vvp_page_complete_read()`, and `vvp_page_complete_write()`. Operation tables are `vvp_page_ops` for cacheable pages and `vvp_transient_page_ops` for direct-I/O/transient pages.

## Control Flow
Cacheable page init takes a page reference, increments cl-page refcount, sets `PagePrivate`, stores the cl-page pointer in `page->private`, and installs VVP page ops. Delete reverses the page-private mapping, drops the cache-held cl-page refcount, and clears `PageUptodate` under `lli_page_inv_lock` so racing reads/faults can detect invalidation. Read completion sets `PageUptodate` unless readahead deferred it, handles `-EAGAIN` mirror retry by removing the folio, and unlocks async pages. Write completion marks mapping errors for async writes and ends writeback.

## State And Persistence
State is mostly in Linux page flags and `page->private`. `vvp_object::vob_discard_page_warned` suppresses repeated discard warnings. Readahead accounting is decremented for deferred uptodate pages. Mapping error state persists in `address_space` for later fsync/writeback reporting.

## Dependencies And Integration Points
The file depends on cl-page ownership and completion APIs, Linux page flags/writeback, llite readahead stats, inode page invalidation seqlock, `cl_inode2vvp()`, and dirty-page discard warning helpers.

## Risks And Edge Cases
Transient pages intentionally do not take user page references. Clearing uptodate on delete is required to avoid stale data and SIGBUS races. Async write errors need mapping-level propagation because applications may not wait on individual I/O. Mirror read retry must destroy wrong-subpage cache state.

## Test Signals
Cover cacheable and transient page init, read completion success and error, deferred readahead accounting, mirror retry `-EAGAIN`, async writeback error propagation, page deletion during fault/read, and repeated eviction/discard warning suppression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/vvp_page.c -->
