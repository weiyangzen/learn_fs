# File Research: sources/block-storage/lvm2/libdm/mm/pool.c

## Summary
Top-level memory-pool module that defines global pool tracking, selects debug or fast pool implementation, adds convenience allocation helpers, checks unreleased pools, and implements pool lock/unlock wrappers.

## Main Responsibilities
- Owns the global `_dm_pools` list and `_dm_pools_mutex`.
- Includes `pool-debug.c` when `DEBUG_POOL` is set, otherwise `pool-fast.c`.
- Provides `dm_pool_strdup()`, `dm_pool_strndup()`, and `dm_pool_zalloc()`.
- Reports unreleased memory pools with `dm_pools_check_leaks()`.
- Exposes `dm_pool_locked()`, `dm_pool_lock()`, and `dm_pool_unlock()`.
- Defines page-alignment helpers for `DEBUG_ENFORCE_POOL_LOCKING`.

## Key APIs
- `dm_pool_strdup()`
- `dm_pool_strndup()`
- `dm_pool_zalloc()`
- `dm_pools_check_leaks()`
- `dm_pool_locked()`
- `dm_pool_lock()`
- `dm_pool_unlock()`

## Important Behavior
`DEBUG_POOL` and `DEBUG_ENFORCE_POOL_LOCKING` are mutually exclusive. `DEBUG_ENFORCE_POOL_LOCKING` uses page-aligned chunks and `mprotect()` in the fast implementation to catch writes to locked pools.

`dm_pool_lock()` optionally records a pool checksum, protects memory read-only, marks the pool locked, and logs debug memory state. `dm_pool_unlock()` restores write protection and optionally compares the checksum.

`dm_pools_check_leaks()` reports all pools still present in `_dm_pools`; debug builds include tracked byte counts, while fast builds report pool pointers and names.

## State and Lifetime
The file-level pool list is static and shared by whichever implementation is included. Pools add/remove themselves in implementation-specific create/destroy paths.

## Risks
The implementation is assembled by textual inclusion of either `pool-debug.c` or `pool-fast.c`, so static helper names and globals are shared in one translation unit. Locking support depends on implementation-specific `_pool_crc()` and `_pool_protect()` behavior.
