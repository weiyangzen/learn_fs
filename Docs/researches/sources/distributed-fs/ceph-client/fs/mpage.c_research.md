<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/mpage.c -->
# sources/distributed-fs/ceph-client/fs/mpage.c

## Purpose
`mpage.c` provides generic multipage BIO assembly for block-mapped filesystems. It batches contiguous page-cache folios into larger block I/O requests for readahead, read-folio, and writepages, while falling back to buffer-head based helpers when a folio has holes, non-contiguous blocks, existing buffers, or filesystem-specific complexity.

## Important APIs, Types, and Functions
Exported entry points are `mpage_readahead()`, `mpage_read_folio()`, and `__mpage_writepages()`. Read-side internals include `struct mpage_readpage_args`, `do_mpage_readpage()`, `map_buffer_to_folio()`, `mpage_bio_submit_read()`, and `mpage_read_end_io()`. Write-side internals include `struct mpage_data`, `mpage_write_folio()`, `clean_buffers()`, `mpage_bio_submit_write()`, and `mpage_write_end_io()`. Filesystems provide a `get_block_t` mapper.

## Control Flow
Read readahead iterates folios from `readahead_folio()`, maps logical blocks with `get_block()`, reuses previous extent information when possible, and accumulates contiguous blocks into a BIO. Holes at EOF are zeroed; all-hole folios are marked uptodate and unlocked. If an existing buffer, uptodate mapped buffer, hole-then-data pattern, non-contiguous mapping, allocation failure, or mapping error is encountered, outstanding BIOs are submitted and the folio falls back to `block_read_full_folio()`.

Writeback iterates dirty folios via `writeback_iter()` inside a block plug. `mpage_write_folio()` either validates existing buffers or maps a bufferless uptodate folio with `get_block(create=1)`. Fully contiguous dirty mapped ranges are added to a write BIO, buffers are cleaned only after the folio is accepted by the BIO, writeback is started, and the folio is unlocked. EOF-straddling folios are zeroed past `i_size`. Non-contiguous or otherwise complex folios fall back to `block_write_full_folio()`.

## State and Persistence Behavior
`mpage.c` does not own filesystem metadata; it drives page-cache folio state, buffer-head state, BIO submission, and writeback error propagation. Read completions call `folio_end_read()`. Write completions set mapping errors and call `folio_end_writeback()`. BIOs are guarded with `guard_bio_eod()` before submission. The write path accounts cgroup ownership and initializes writeback flags from `writeback_control`.

## Dependencies and Integration Points
It depends on block layer BIO APIs, buffer-head block mapping, page cache folios, readahead/writeback infrastructure, backing-dev flags, and filesystem `get_block()` callbacks. Minix uses `mpage_writepages()` from its address-space operations. Other simple block filesystems can use the same helpers when their mappings are block-contiguous enough for batching.

## Risks
The fallback boundaries are critical: submitting partial folios with complex buffer dependencies would make completion accounting incorrect. Cleaning buffers before successful BIO attachment could lose dirty state on allocation failure, which the code explicitly avoids. EOF handling must avoid allocating or writing beyond `i_size` and must zero mapped tail bytes. BIO contiguity, `BH_Boundary`, and block-device changes must be handled to preserve ordering and correctness.

## Test Signals
Use filesystems with `get_block()` to test contiguous reads/writes, sparse holes, hole-then-data fallback, non-contiguous extents, EOF partial folios, mmap-dirtied bufferless pages, BIO allocation pressure, device removal/read mapping errors, writeback error propagation through `mapping_set_error()`, `BH_Boundary` ordering, and high buffer-head pressure triggering `try_to_free_buffers()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/mpage.c -->
