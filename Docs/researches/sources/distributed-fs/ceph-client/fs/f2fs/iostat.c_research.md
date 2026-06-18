# sources/distributed-fs/ceph-client/fs/f2fs/iostat.c

## Purpose

`iostat.c` implements optional F2FS I/O accounting and latency tracing for a mounted filesystem. It maintains per-superblock counters in `struct f2fs_sb_info`, exposes the current aggregate view through a seq-file show function, periodically emits tracepoints with deltas, and wraps bios with a small private context so completion paths can attribute latency to read, synchronous write, or asynchronous write traffic.

The file is compiled only when `CONFIG_F2FS_IOSTAT` is enabled through declarations in `iostat.h`; without that option, callers get static inline no-ops.

## Important APIs and functions

- `iostat_info_seq_show()` prints current cumulative byte/count/average counters for write, read, folio-order read, discard, flush, and zone reset classes. It relies on `sbi->iostat_enable` and is suitable for debugfs/proc style reporting.
- `f2fs_update_iostat()` is the main accounting entry point for byte-count updates. It records the explicit `enum iostat_type`, derives aggregate app read/write counters, and conditionally mirrors compressed file traffic into compressed data categories.
- `f2fs_update_read_folio_count()` records folio-order read distribution and clamps oversize folio orders into the last bucket.
- `f2fs_reset_iostat()` clears byte, count, previous-delta, read-folio, and latency accumulators under the appropriate spinlocks.
- `iostat_alloc_and_bind_ctx()`, `iostat_update_submit_ctx()` from the header, and `iostat_update_and_unbind_ctx()` form the bio lifecycle. Allocation stores the original post-read context, submit stores jiffies/type, completion records latency and restores `bio->bi_private`.
- `f2fs_init_iostat_processing()` and `f2fs_destroy_iostat_processing()` create and destroy the global slab-backed mempool for `struct bio_iostat_ctx`.
- `f2fs_init_iostat()` and `f2fs_destroy_iostat()` initialize/destroy per-mount locks, defaults, and `sbi->iostat_io_lat`.

## Control flow and state

Counter updates first test `sbi->iostat_enable`, then mutate `sbi->iostat_bytes`, `sbi->iostat_count`, or `sbi->iostat_read_folio_count` under `sbi->iostat_lock`. After each update, `f2fs_record_iostat()` checks whether `sbi->iostat_next_period` has elapsed. It double-checks under lock, advances the next deadline by `sbi->iostat_period_ms`, computes deltas from `prev_iostat_bytes` and `prev_iostat_read_folio_count`, emits `trace_f2fs_iostat()`, then calls `__record_iostat_latency()`.

Latency state is separate in `struct iostat_lat_info`, guarded by `sbi->iostat_lat_lock`. Bio completion computes `jiffies - submit_ts`, normalizes `META_FLUSH` to `META`, validates the page type, and updates sum, count, and peak arrays. Periodic recording copies all latency buckets into a stack array, converts jiffies to milliseconds, resets the live buckets, and emits `trace_f2fs_iostat_latency()`.

The bio private pointer is multiplexed carefully. For write bios, unbind restores `bio->bi_private` to `iostat_ctx->sbi`; for read bios, it restores the saved `post_read_ctx`. This is an integration-sensitive contract with the surrounding F2FS bio submission/completion paths.

## Persistence behavior

This file does not write persistent filesystem state. All counters and latency buckets are in-memory telemetry. The only storage-like resources are kernel memory allocations: the global `bio_iostat_ctx_cache` slab, `bio_iostat_ctx_pool` mempool, and per-mount `sbi->iostat_io_lat`.

## Dependencies and integration points

The implementation depends on core kernel folio, bio, mempool, seq-file, time, and spinlock primitives. F2FS-specific dependencies include `struct f2fs_sb_info`, `enum iostat_type`, `enum page_type`, compressed-file detection, `f2fs_kzalloc()`, warnings, and tracepoints from `<trace/events/f2fs.h>`. It is called from F2FS read/write paths, including node I/O in `node.c`, where `f2fs_update_iostat(..., FS_NODE_READ_IO, F2FS_BLKSIZE)` records node-page reads.

## Risks and edge cases

- `iostat_update_and_unbind_ctx()` assumes `bio->bi_private` is a valid `struct bio_iostat_ctx`; callers must bind only once and unbind exactly once.
- A missing `iostat_update_submit_ctx()` before completion yields a near-boot-time latency, because `submit_ts` starts at zero.
- Page type validation protects against out-of-range latency indexing, but invalid page types are dropped after warning.
- Counter arrays are protected by spinlocks for mutation and reset, but printed cumulative counters are read without taking `iostat_lock`; debug output can be slightly inconsistent under concurrent updates.
- Mempool allocation is treated as never failing after global initialization; mount/module init ordering must ensure the pool exists before bio binding.

## Test signals

Useful validation signals include enabling/disabling F2FS iostat at runtime, verifying seq output remains empty when disabled, checking tracepoint deltas over the configured period, issuing buffered/direct/mmap reads and writes, exercising compressed files, reading with larger folio orders, and forcing read/write bios through completion to confirm `bio->bi_private` restoration and latency bucket updates. Fault tests should cover allocation init failure, reset while I/O is active, and invalid page-type warnings.
