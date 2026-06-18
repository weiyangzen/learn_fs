# File Research: sources/cow-pools/openzfs/module/zfs/rrwlock.c

## Summary
Implements re-entrant read reader/writer locks (`rrwlock_t`) plus reader-mostly striped locks (`rrmlock_t`). Readers may reacquire read locks while a writer is waiting, avoiding self-deadlock while still preventing general writer starvation.

## Main Responsibilities
- Provides read/write enter, exit, held, init, and destroy operations.
- Tracks reader ownership through thread-specific data when needed.
- Gives waiting writers priority once anonymous readers drain.
- Rejects recursive writers and read-to-write recursion.
- Implements `rrmlock_t` as an array of `rrwlock_t` locks for lower read contention.

## Key APIs
- `rrw_init()`, `rrw_destroy()`.
- `rrw_enter_read()`, `rrw_enter_read_prio()`, `rrw_enter_write()`, `rrw_enter()`, `rrw_exit()`, `rrw_held()`.
- `rrw_tsd_destroy()`.
- `rrm_init()`, `rrm_destroy()`, `rrm_enter()`, `rrm_enter_read()`, `rrm_enter_write()`, `rrm_exit()`, `rrm_held()`.

## Important Behavior
Fast read acquisition can increment anonymous reader count without TSD when there is no writer pressure and full tracking is disabled. Once a writer is wanted, new readers are linked into per-thread TSD so re-entrant readers can be distinguished from unrelated readers.

`rrm_enter_read()` hashes the current thread to one shard. `rrm_enter_write()` acquires every shard for writing, making writes slower but reducing read-side lock contention.

## Risks
Read locks must be released by the same thread that acquired them, especially for `rrmlock_t` shard selection. `rrw_held(RW_READER)` is exact only when `track_all` is enabled; otherwise anonymous readers can make it report a reader hold without proving the current thread owns one.
