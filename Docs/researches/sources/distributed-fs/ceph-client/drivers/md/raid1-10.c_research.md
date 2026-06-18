# sources/distributed-fs/ceph-client/drivers/md/raid1-10.c

## Purpose
`raid1-10.c` is a shared implementation include used by RAID1 and RAID10 personalities for common mirrored-I/O helpers. In this subset it is included by `raid1.c` after defining `RAID_1_10_NAME` as `raid1`. It provides resync page management, write submission and plug batching, bitmap-unplug ordering, read-error thresholding, bad-block read-range selection, clustered resync read policy, and a common error-handling predicate.

## Important APIs, Types, And Functions
The file defines `RESYNC_BLOCK_SIZE`, `RESYNC_PAGES`, `IO_BLOCKED`, `IO_MADE_GOOD`, `BIO_SPECIAL()`, and `MAX_PLUG_BIO`. `struct resync_pages` ties a resync bio to its allocated page array and parent raid bio. `struct raid1_plug_cb` stores plugged pending write bios. Resync helpers include `resync_alloc_pages`, `resync_free_pages`, `resync_get_all_pages`, `resync_fetch_page`, `get_resync_pages`, and `md_bio_reset_resync_pages`. Write helpers include `raid1_submit_write`, `raid1_add_bio_to_plug`, and `raid1_prepare_flush_writes`. Error/read-selection helpers include `check_decay_read_errors`, `exceed_read_errors`, `raid1_check_read_range`, `raid1_should_read_first`, and `raid1_should_handle_error`.

## Control Flow
Resync buffer allocation allocates `RESYNC_PAGES` pages per `struct resync_pages`; additional bios can share the first page set by incrementing page refs. Bio reset rebuilds the bvec table after `bio_reset()` by re-adding each page. Normal mirrored writes either submit immediately when no bitmap is enabled or enter a block plug callback so bitmap I/O can be issued before data I/O without per-bio synchronous stalls. If a plug accumulates enough bios relative to copy count, it flushes early.

Read-error handling decays per-rdev read error counters based on elapsed hours, increments the counter on new errors, and calls `md_error()` when the threshold is exceeded. Bad-block range selection returns the length of the first readable sector range, updates the requested length when the good range starts after an initial bad range, and lets RAID1 split/retry reads around bad blocks. `raid1_should_read_first()` avoids balanced reads while a resync or clustered resync window covers the request. `raid1_should_handle_error()` suppresses repair/retry side effects for readahead, nowait, and invalid-user-request failures.

## State And Persistence
The helpers manipulate in-memory bio, page, rdev, and bitmap state. Bad-block decisions integrate with each `md_rdev`'s bad-block log, which may be metadata-backed elsewhere in MD. Read-error counters and timestamps are in-memory device health state. `IO_BLOCKED` and `IO_MADE_GOOD` are sentinel bio pointer values stored in RAID1/10 per-request arrays, so callers must always guard with `BIO_SPECIAL()` or equivalent before treating a slot as a real bio.

## Dependencies And Integration Points
This file is not a standalone translation unit. It depends on the including RAID personality to define `RAID_1_10_NAME` and to provide MD, bio, bitmap, and rdev context. In `raid1.c`, its helpers feed `r1buf_pool` allocation/freeing, write request submission, pending-bio flushing, read balancing, read-error repair, sync write completion, and retry handling.

## Risks
Because it is included C rather than a normal module, symbol names and macros share the including file's namespace. The `IO_BLOCKED`/`IO_MADE_GOOD` sentinel values are intentionally invalid low pointers; any code path that forgets to treat them specially can dereference garbage. Plug/bitmap ordering avoids deadlock around `current->bio_list`, so changes to `raid1_prepare_flush_writes()` or direct submission rules can reintroduce submit recursion stalls. Resync page reference sharing is subtle: allocation, reset, and freeing must stay symmetric across all bios.

## Test Signals
Useful coverage comes from RAID1 and RAID10 resync/recovery tests, bitmap-enabled write workloads, write-mostly/write-behind tests, bad-block injection, read error threshold tests, readahead and nowait read failures, discard to devices without discard support, and lockdep/KASAN runs during resync buffer allocation/free.
