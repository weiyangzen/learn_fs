# File Research: sources/cow-pools/openzfs/module/zfs/mmp.c

## Scope

OpenZFS Multi-Modifier Protection implementation. This file maintains MMP heartbeat uberblock writes while a multihost pool is imported, records delay/config data in MMP-reserved uberblock slots, supports claim writes during import, suspends pools when configured heartbeat deadlines are missed, and exposes tunables for MMP timing.

## Main Interfaces

- Lifecycle: `mmp_init()`, `mmp_fini()`, `mmp_thread_start()`, `mmp_thread_stop()`.
- Uberblock state: `mmp_update_uberblock()`.
- Import claim: `mmp_claim_uberblock()`.
- Thread signaling: `mmp_signal_all_threads()`.
- Internal write path: `mmp_next_leaf()`, `mmp_delay_update()`, `mmp_write_uberblock()`, `mmp_write_done()`.
- Tunables: `zfs_multihost_interval`, `zfs_multihost_import_intervals`, `zfs_multihost_fail_intervals`.

## State And Control Flow

`spa->spa_mmp` contains the MMP thread, condition variable, I/O lock, last selected leaf, latest synced uberblock copy, sequence number, delay estimate, last successful write time, skip error state, kstat IDs, and outstanding root zio.

When a pool is writable, `mmp_thread_start()` creates `mmp_thread()`. The thread tracks multihost state, suspension state, interval/fail-interval tunables, and leaf count. If multihost is enabled and the pool is not suspended, it writes heartbeat uberblocks roughly once per configured interval per leaf. Tunable changes cause accelerated writes so peers can see the new configuration quickly.

`mmp_write_uberblock()` enters `SCL_STATE`, chooses a writable leaf without a pending MMP write, fills the cached uberblock with `MMP_MAGIC`, delay, interval/fail-interval config, timestamp, and sequence, then writes it to a random label and MMP-reserved uberblock slot. Completion updates delay, clears leaf pending state, exits the config lock, records history, and frees the ABD.

`mmp_delay_update()` stores a conservative write-delay estimate: spikes are recorded immediately, successful shorter delays decay slowly, and the minimum stays at the expected per-leaf write cadence. If multihost is off, delay is cleared so later import can skip activity checks.

`mmp_claim_uberblock()` is used during import claiming. It writes the candidate MMP uberblock to label 0 of all writable leaves under `SCL_ALL`, flushes, and requires enough successful writes for topology visibility: one for singletons, two for mirrors, and parity plus one for raidz/draid.

If no successful MMP write lands for `fail_intervals * interval`, `mmp_thread()` suspends the pool with `ZIO_SUSPEND_MMP`. Fail interval 0 disables suspension but still records failures.

## Dependencies

Depends on SPA/vdev config locking, vdev leaf lists and writeability, uberblock layout macros, ABD and ZIO label writes/flushes, spa MMP history/kstats, pool multihost property state, callb CPR thread hooks, and module parameter callbacks.

## Correctness Notes

MMP writes use uberblock slots reserved away from normal txg-sync uberblocks, preserving historical txg slots. Leaf selection skips offline, detached, unwritable, dRAID spare, and pending-write leaves. `mmp_write_done()` holds enough state to clear pending writes and exit `SCL_STATE` exactly once. Import claim requires topology-specific write quorum to reduce false ownership claims. The timestamp/sequence handling resets sequence on timestamp change to preserve `uberblock_compare()` ordering.
