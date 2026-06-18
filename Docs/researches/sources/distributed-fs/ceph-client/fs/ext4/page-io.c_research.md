# sources/distributed-fs/ceph-client/fs/ext4/page-io.c

## Purpose

`sources/distributed-fs/ceph-client/fs/ext4/page-io.c` implements ext4 buffered writeback bio submission and write I/O completion. It manages `ext4_io_end` lifetime, encrypted bounce-page writes, buffer-head completion, deferred conversion of unwritten extents, and journal abort behavior on data write errors. The source was read as a complete 613-line file.

## Important APIs, Types, and Functions

Initialization and teardown are `ext4_init_pageio()` and `ext4_exit_pageio()`, which create caches for `struct ext4_io_end` and `struct ext4_io_end_vec`. I/O end helpers include `ext4_init_io_end()`, `ext4_get_io_end()`, `ext4_put_io_end()`, `ext4_put_io_end_defer()`, `ext4_alloc_io_end_vec()`, and `ext4_last_io_end_vec()`. Completion helpers are `ext4_end_bio()`, `ext4_finish_bio()`, `ext4_end_io_end()`, `ext4_add_complete_io()`, `ext4_do_flush_completed_IO()`, and workqueue entry `ext4_end_io_rsv_work()`. Submission APIs are `ext4_io_submit_init()`, `ext4_io_submit()`, and `ext4_bio_write_folio()`.

## Control Flow

`ext4_bio_write_folio()` is called with a locked, non-writeback folio. It zeroes bytes past the requested length, walks buffer_heads to decide which buffers can be submitted, clears dirty bits, marks async-write buffers, and redirties or preserves the TOWRITE tag when buffers cannot yet be written. If nothing can be submitted, it cycles writeback state to update xarray tags. For encrypted files, it encrypts the relevant page-cache blocks into a bounce folio, using nonblocking allocation when appending to an existing bio and retrying safely for sync writeback.

The second loop starts folio writeback and sends each async-write buffer to `io_submit_add_bh()`. That helper starts a new bio when physical blocks are non-contiguous or fscrypt contexts cannot merge, attaches an `ext4_io_end` reference, and accounts cgroup ownership. `ext4_io_submit()` sets `REQ_SYNC` for `WB_SYNC_ALL` and submits through `blk_crypto_submit_bio()`.

`ext4_end_bio()` records write errors, sets `EXT4_IO_END_FAILED`, and either chains the bio onto a deferred `io_end` list or finishes the bio immediately. Deferred completion is required for unwritten extent conversion or data-error journal abort handling. `ext4_end_io_end()` converts unwritten extents via `ext4_convert_unwritten_io_end_vec()` on success; on failure it frees a reserved handle and may abort the journal when `DATA_ERR_ABORT` is enabled. `ext4_finish_bio()` clears buffer async-write state, marks buffer write I/O errors, frees encryption bounce pages, and ends folio writeback once no buffers in the folio remain under I/O.

## State and Persistence Behavior

Persistent effects are data writes and, after successful I/O to unwritten extents, metadata conversion from unwritten to written extents. I/O errors are persisted indirectly through mapping error state and optionally journal aborts. The file maintains transient `ext4_io_end` objects with reference counts, bio chains, conversion vectors, flags, reserved journal handles, and inode completion-list links. Per-inode deferred completions live on `i_rsv_conversion_list` and are drained by `rsv_conversion_wq`.

## Dependencies and Integration Points

The code depends on Linux bio, writeback control, buffer_heads, folios, blk-crypto, fscrypt pagecache bounce pages, cgroup writeback accounting, JBD2 reserved handles, ext4 unwritten extent conversion, per-inode completed I/O lists, and mount option `DATA_ERR_ABORT`. It is used by ext4 writepage/writepages paths that prepare mapped buffers and `ext4_io_submit` state.

## Risks and Edge Cases

Completion ordering is subtle. All buffers in a folio must be marked async before any bio can complete, otherwise writeback could end early. Deferred bios can complete concurrently and are atomically chained through `xchg(&io_end->bio, bio)`. Bounce-page lifetime depends on detecting fscrypt bounce folios and freeing them only when folio writeback finishes. Failed writes to unwritten extents must not convert extents, or stale data could be exposed. Encryption allocation can deadlock if blocking mempool allocation is used for non-first bio pages, so the retry logic submits existing bios or uses nofail only when safe.

## Test Signals

Test coverage should include buffered writeback to mapped, delayed, hole, and unwritten buffers; encrypted file writeback; multi-buffer folios; writeback with block discontinuities; sync and async writeback; I/O error injection; `DATA_ERR_ABORT`; unwritten extent conversion; and concurrent bio completion races. Signals include mapping errors, buffer write I/O error logs, journal aborts, delayed conversion workqueue activity, and absence of stuck folio writeback.
