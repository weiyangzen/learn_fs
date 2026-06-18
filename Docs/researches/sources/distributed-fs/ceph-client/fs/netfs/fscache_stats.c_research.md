<!-- Source: sources/distributed-fs/ceph-client/fs/netfs/fscache_stats.c -->
# sources/distributed-fs/ceph-client/fs/netfs/fscache_stats.c

## Purpose
Owns FS-Cache statistic counters and renders them through seq_file output, normally as the FS-Cache tail of `/proc/fs/netfs/stats`.

## Important APIs, Types, And Functions
Defines counters for volumes, cookies, LRU, acquisitions, invalidations, updates, relinquishes, resizes, IO, no-space events, culling, and DIO misfits. Several backend-facing counters are exported: `fscache_n_updates`, `fscache_n_read`, `fscache_n_write`, `fscache_n_no_write_space`, `fscache_n_no_create_space`, `fscache_n_culled`, and `fscache_n_dio_misfit`. `fscache_stats_show()` prints grouped counts.

## Control Flow
There is no state machine. Callers increment/decrement atomic counters through `fscache_stat()` helpers from `internal.h`; proc display atomically snapshots them and includes LRU timer remaining time when pending.

## State And Persistence
All state is in `atomic_t` counters and the externally declared cookie LRU timer. Counters reset at module load and are not persistent.

## Dependencies And Integration Points
Depends on `CONFIG_FSCACHE_STATS`, seq_file, procfs, and `internal.h`. Called by `netfs_stats_show()` after netfs statistics so users can inspect netfs and FS-Cache behavior together.

## Risks
Counters are diagnostic only and may be approximate under concurrency. Miscounted increments/decrements can mislead troubleshooting, particularly active cookie/volume counts and LRU depth.

## Test Signals
Run cache acquisition/use/relinquish, invalidation, no-space/cull, read/write, and resize paths and confirm expected counter movement. Check `LRU at=` changes when the LRU timer is armed.
