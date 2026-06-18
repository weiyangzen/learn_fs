
# sources/distributed-fs/ceph-client/drivers/md/dm-log-userspace-base.c

## Purpose
Implements the `userspace` dirty-log type for dm mirror-style targets. It delegates dirty-region-log policy and persistence to a userspace daemon over the dm-log-userspace connector protocol while preserving the kernel `dm_dirty_log_type` interface expected by device-mapper mirror code.

## Important APIs, Types, And Functions
`struct log_c` stores target/device references, UUID/LUID identity, cached constructor string, region size/count, pending mark/clear lists, flush mempool, reconnect metadata, optional integrated-flush workqueue, and `in_sync_hint`. `userspace_ctr()` validates `<UUID> [integrated_flush] <daemon args>`, sends `DM_ULOG_CTR`, fetches region size, optionally opens a returned log device, and initializes flush batching. `userspace_do_request()` wraps `dm_consult_userspace()` and reconnects on `-ESRCH`. Log operations implement clean/sync queries, mark/clear queues, grouped `userspace_flush()`, resync work, sync count, remote recovery, suspend/resume, status, and destructor. `_userspace_type` registers with `dm_dirty_log_type_register()`.

## Control Flow
Constructor strips the UUID and optional `integrated_flush`, builds a daemon constructor string prefixed with target length, initializes pending-request lists, sends create and region-size requests, then saves context. Mark and clear operations enqueue `dm_dirty_log_flush_entry` objects under `flush_lock` rather than always contacting userspace. Flush drains mark/clear lists, sends grouped requests up to `MAX_FLUSH_GROUP_COUNT`, commits with `DM_ULOG_FLUSH`, and optionally combines mark payloads with integrated flush. Query paths call userspace synchronously and return conservative answers on failure.

## State And Persistence
The kernel stores runtime queues and identity only; actual log state and durable metadata live in userspace or its chosen log device. Pending mark/clear entries are volatile until flushed. `in_sync_hint` caches a lower bound for optimization and resets on resume. Integrated flush schedules delayed work for clear-only batches.

## Dependencies And Integration Points
Depends on `dm-log-userspace-transfer.c`, `linux/dm-log-userspace.h` request codes, dirty-log registration in `dm-log.c`, mempools/slab caches, workqueues, dm target events, and optional lower log devices returned by the userspace daemon.

## Risks
Userspace daemon loss can stall reconnect loops. Conservative failure behavior can force resync or table events but avoids falsely clean/in-sync results. `userspace_clear_region()` uses GFP_ATOMIC and may skip clearing, intentionally causing later resync. Grouped flush failure falls back only for non-integrated grouped mark/clear traffic. Correctness depends on daemon protocol compatibility, NUL-terminated returned device names, and flushing pending delayed work during suspend/destruction.

## Test Signals
Test module init/exit, missing daemon, daemon restart/reconnect, constructor argument validation, long UUID rejection, returned device open/close, integrated and non-integrated flush paths, mark/clear batching, clear allocation failure behavior, suspend/resume ordering, remote recovery throttling, status fallback on communication failure, and mirror resync behavior after daemon errors.
