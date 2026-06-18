# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_actlog.c

## Purpose

`drbd_actlog.c` implements DRBD metadata I/O helpers, the activity log transaction machinery, and the resync extent coordination layer. The activity log records recently active 4 MiB data extents in an on-disk ring so DRBD can recover after crashes without resyncing the entire device. The same file also updates the out-of-sync bitmap in response to application writes, successful resync, and failed resync, and it arbitrates write exclusion between application I/O and resync I/O.

## Important APIs, Types, and Data

- `struct al_transaction_on_disk` is the 4 KiB big-endian activity-log transaction block. It stores magic, transaction number, CRC32C, transaction type, update count, AL context size/start slot, update slot/extent arrays, and context snapshot entries.
- `drbd_md_get_buffer()` / `drbd_md_put_buffer()` serialize access to `device->md_io.page` with `md_io.in_use` and `misc_wait`.
- `drbd_md_sync_page_io()` and `_drbd_md_sync_page_io()` perform synchronous 4 KiB metadata reads/writes with optional flush/FUA, timeout handling, and fault injection.
- `drbd_al_begin_io_fastpath()`, `drbd_al_begin_io_prepare()`, `drbd_al_begin_io_commit()`, `drbd_al_begin_io()`, `drbd_al_begin_io_nonblock()`, and `drbd_al_complete_io()` manage activity-log extent references around application I/O.
- `__al_write_transaction()` and `al_write_transaction()` serialize dirty AL changes to the on-disk transaction ring, including hinted bitmap writeout.
- `drbd_al_initialize()` initializes the on-disk AL ring.
- `__drbd_change_sync()` plus `update_sync_bits()` update bitmap bits for `SET_IN_SYNC`, `SET_OUT_OF_SYNC`, and `RECORD_RS_FAILED`.
- `drbd_rs_begin_io()`, `drbd_try_rs_begin_io()`, `drbd_rs_complete_io()`, `drbd_rs_cancel_all()`, and `drbd_rs_del_all()` manage resync LRU extents and write exclusion flags.
- Shared state includes `device->act_log`, `device->resync`, `device->al_lock`, `device->al_wait`, `device->al_tr_number`, `device->al_tr_cycle`, `device->resync_locked`, `device->resync_wenr`, `device->rs_failed`, and resync progress marks.

## Control Flow

Application write admission starts by translating the request interval to AL extent numbers. The fast path can acquire one already-available extent nonblocking through `_al_get()`. The normal path waits for every required extent with `drbd_al_begin_io_prepare()`, notes whether any LRU cache entry changed, and commits if a transaction is needed.

`drbd_al_begin_io_commit()` serializes AL transactions with `lc_try_lock_for_transaction()`. If `pending_changes` remain and `disk_conf->al_updates` permits writes, `al_write_transaction()` writes them to disk. The LRU cache is then marked committed and waiters are woken. `drbd_al_complete_io()` later drops references on all AL extents touched by the request.

`__al_write_transaction()` constructs one transaction block from `act_log->to_be_changed`, marks bitmap pages associated with evicted AL extents for writeout, writes context entries from the AL LRU, advances `al_tr_cycle`, computes CRC32C over the block, writes hinted bitmap pages first, and then writes the AL block to the metadata area if configured. The on-disk sector is derived from transaction number, stripe count, stripe size, metadata offset, and AL offset.

Metadata I/O goes through `drbd_md_sync_page_io()`. It validates metadata sector ranges, prepares a one-page bio against `md_bdev`, gets an ldev reference for normal cases, sets completion fields, optionally injects faults, submits the bio, and waits until completion, force-detach, or disk timeout. Timeout calls `drbd_chk_io_error()` with force-detach semantics.

Bitmap sync updates enter `__drbd_change_sync()`. It validates request size, maps sector ranges to bitmap bit ranges, rounds differently for clearing in-sync bits versus setting out-of-sync/failure bits, gets a local disk reference, and calls `update_sync_bits()`. `update_sync_bits()` chunks by resync extent, modifies bitmap bits through `drbd_bm_*`, updates cached `bm_extent` counters under `al_lock`, advances resync progress marks, schedules lazy on-disk bitmap updates, and wakes AL waiters.

Resync I/O exclusion uses the resync LRU. `drbd_rs_begin_io()` sleeps until `_bme_get()` can lock a bitmap extent, waits for all corresponding AL extents to become inactive unless throttling gives priority to application I/O, then sets `BME_LOCKED`. `drbd_try_rs_begin_io()` performs a nonblocking version with a remembered half-locked extent in `resync_wenr`. `drbd_rs_complete_io()` drops the resync extent reference and clears `BME_LOCKED`, `BME_NO_WRITES`, and `BME_PRIORITY` when the last reference leaves.

## State and Persistence Behavior

The activity log persists to the DRBD metadata area as a ring of 4 KiB transaction blocks. Each transaction includes update deltas and a rolling context snapshot so the log can be reconstructed after crash. Transaction blocks are big endian and protected by CRC32C.

The out-of-sync bitmap is persistent but managed by `drbd_bitmap.c`; this file decides when bitmap pages must be written before AL updates and when lazy bitmap progress updates should be scheduled. Hinted bitmap writeout ties AL eviction to bitmap persistence so evicted extents do not lose dirty state.

Resync LRU state (`rs_left`, `rs_failed`, lock flags) is in-memory cache state. It can be recounted from the bitmap when a cache entry is reused or detected inconsistent.

## Dependencies and Integration Points

- `drbd_int.h` for core DRBD structs, state, wait queues, LRU cache, metadata layout, and logging helpers.
- `linux/crc32c.h` for AL transaction checksum.
- Block layer bios for metadata I/O.
- LRU cache helpers (`lc_get`, `lc_try_get`, `lc_committed`, `lc_put`, `lc_del`, `lc_reset`).
- Bitmap APIs from `drbd_bitmap.c`, especially `drbd_bm_mark_for_writeout()`, `drbd_bm_write_hinted()`, bit set/clear/count, and total weight.
- State and worker integration through `drbd_chk_io_error()`, `drbd_device_post_work()`, `RS_PROGRESS`, `RS_DONE`, and connection protocol version checks.
- Fault injection through `drbd_insert_fault()` when enabled.

## Risks and Edge Cases

- Metadata buffer serialization is strict: callers must hold the one `md_io` buffer exactly once, and completion also decrements `md_io.in_use` for submitted bios.
- AL transaction error handling has a FIXME around canceling failed LRU changes after write failure; committed state may need careful review when metadata I/O fails.
- Sector range checks log out-of-range metadata access but still rely on lower-level error handling.
- Resync and application writes contend through AL and resync LRU flags. Mistakes can allow writes into `BME_NO_WRITES` ranges or deadlock resync waiters.
- `update_rs_extent()` recounts when counters go inconsistent, but counter underflow or stale cache state is a sign of subtle concurrency races.
- Nonblocking AL begin can partially acquire extent references and stores continuation in `partially_in_al_next_enr`; callers must resume and complete correctly.
- Lazy bitmap update timing can defer persistence; crash behavior depends on the AL/bitmap ordering guarantees.

## Test Signals

- Metadata I/O tests for read/write success, timeout, force-detach, and injected metadata faults.
- AL transaction tests that cross one extent and multiple extents, including pending-change commit and `al_updates=0`.
- Crash/restart style tests verifying AL ring recovery after writes and bitmap hinted writeout.
- Resync/application write contention tests for `BME_NO_WRITES`, `BME_PRIORITY`, throttling, and nonblocking retry behavior.
- Sync bit update tests for aligned and unaligned sectors, full-device end-sector rounding, failed resync accounting, and lazy bitmap update scheduling.
- Lockdep/KCSAN stress around `al_lock`, `al_wait`, LRU cache refcounts, and disk detach while metadata I/O is pending.
