# sources/distributed-fs/ceph-client/drivers/md/dm-raid1.c

## Purpose
Implements the legacy `mirror` device-mapper target. It mirrors writes to multiple devices, chooses readable mirrors for reads, tracks dirty/no-sync regions through a dirty log and region hash, performs background recovery with kcopyd, and supports user-visible error handling features.

## Important APIs, Types, And Functions
`struct mirror_set` is the target context with bio queues, region hash, kcopyd and dm-io clients, recovery state, error flags, workqueue/timer, and mirror array. `struct mirror` stores device, offset, error count/type, and parent pointer. The target callbacks are `mirror_ctr()`, `mirror_dtr()`, `mirror_map()`, `mirror_end_io()`, suspend/resume hooks, `mirror_status()`, and `mirror_iterate_devices()`.

Core helpers include `fail_mirror()`, `mirror_flush()`, `recover()`, `do_recovery()`, `choose_mirror()`, `do_reads()`, `do_writes()`, `do_failures()`, and the worker `do_mirror()`. `create_dirty_log()` constructs a core or disk dirty log, and `parse_features()` handles `handle_errors` and `keep_log`.

## Control Flow
Writes are queued to the mirror worker. The worker updates region states, starts recovery work, dispatches reads, classifies writes by region state, flushes the dirty log, writes clean/dirty regions to all mirrors through dm-io, delays writes to recovering regions, and writes no-sync regions only to the default mirror when allowed. `mirror_end_io()` decrements pending region counts for writes.

Reads to in-sync regions can be remapped directly to a selected mirror; reads to not-yet-synced regions are queued. Failed reads restore the original bio and retry another mirror if possible. Recovery asks the region hash for quiesced regions, copies from the default mirror to all other mirrors with kcopyd, and marks regions recovered or failed. Error handling can hold bios and trigger DM table events so userspace can reconfigure.

## State And Persistence
Persistent synchronization state is owned by the dirty log implementation passed in the table; `dm-region-hash` caches dirty/no-sync/recovering regions in memory and writes state through the log. Volatile state includes queued bios, current default mirror, per-mirror error bits, in-sync/log-failure/leg-failure flags, suspend flag, timer state, and recovery-in-flight.

`keep_log` changes persistence/error semantics: with handled errors and kept logs, failed writes may be failed rather than allowing log state to be cleared. Without handled errors, some failures can be reported as success after marking regions no-sync, relying on later recovery.

## Dependencies And Integration Points
The target depends on dm-io for replicated I/O, dm-kcopyd for recovery copies, dm-dirty-log for persistent sync state, dm-region-hash for region state and delayed bios, dm-bio-record for read retry, and device-mapper target APIs. It registers as target `mirror` with atomic-write support and uses a global `dm_raid1_wq` for table-event work plus per-target `kmirrord` workqueues.

## Risks
The mirror target has intricate concurrency around worker queues, pending region counts, suspend, and recovery stopping. Misordered region-hash updates can mark data clean before all mirror writes are durable. Using `bio->bi_next` to stash a mirror pointer is delicate and valid only before lower-layer submission. Error handling semantics are subtle: the wrong combination of `handle_errors`, `keep_log`, and log failure can either hang bios awaiting userspace or acknowledge data that is not replicated.

## Test Signals
Test normal mirrored reads/writes, read retry after one leg fails, write failure with and without `handle_errors`, `keep_log` behavior, dirty-log flush failures, recovery after out-of-sync regions, suspend/resume during recovery, noflush suspend requeue, discard handling, and status characters `A/F/D/S/R`. Persistent tests should reload with disk logs and confirm dirty regions recover.
