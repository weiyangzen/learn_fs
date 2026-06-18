# File Research: sources/cow-pools/openzfs/module/zfs/dbuf_stats.c

## Scope

This file implements the raw `/proc`/kstat-style diagnostic dump for the dbuf hash table. It exposes rows that combine dbuf identity/state, associated ARC buffer state, and dnode/object information.

The source was read completely, lines 1-232.

## Primary APIs And Entry Points

- `dbuf_stats_init()` initializes the raw dbuf hash table kstat for a supplied `dbuf_hash_table_t`.
- `dbuf_stats_destroy()` deletes the kstat and destroys its lock.
- `dbuf_stats_hash_table_headers()` emits the table header string.
- `dbuf_stats_hash_table_data()` emits rows for one hash bucket.
- `dbuf_stats_hash_table_addr()` maps a kstat logical offset to a hash bucket index.
- `__dbuf_stats_hash_table_data()` formats a single `dmu_buf_impl_t` row.
- Module parameter `zfs_dbuf_state_index` controls whether ARC header state index calculation is requested through `arc_buf_info()`.

## Data Model

- `dbuf_stats_t` stores the raw kstat lock, kstat pointer, hash table pointer, and current bucket index.
- The kstat is named `zfs:dbufs:misc`, type `KSTAT_TYPE_RAW`, virtual, and uses raw ops for headers/data/addressing.
- Each row includes:
  - dbuf fields: pool, objset, object, level, blkid, offset, dbsize, user size, metadata flag, state, holds, cache-list state;
  - ARC fields from `arc_buf_info_t`: state, flags, counts, size, access time, MRU/MFU/L2ARC hit stats, L2ARC details, ARC holds;
  - dnode fields from `dmu_object_info_t`: data/bonus types, block sizes, bonus size, indirection, dnode holds, fill count, and max offset.

## Control Flow

Initialization creates a private mutex, stores the dbuf hash pointer, creates the raw kstat, attaches the lock/private state, sets `ks_ndata` to `UINT32_MAX`, registers raw ops, and installs the kstat.

For each logical address `n`, `dbuf_stats_hash_table_addr()` sets the current bucket index if it is within `hash_table_mask`. The data callback locks the relevant hash bucket, walks `db_hash_next`, locks each dbuf, skips `DB_EVICTING` dbufs, formats one row, and unlocks. If the scratch buffer is too small, it returns `ENOMEM` so kstat will retry with a larger buffer.

Destroy deletes the kstat if present and destroys the private mutex.

## Dependencies

- Dbuf internals: `dbuf_hash_table_t`, `dmu_buf_impl_t`, dbuf state, cache link, holds, `DB_DNODE()`, `dbuf_is_metadata()`, and `DBUF_HASH_MUTEX()`.
- ARC diagnostics: `arc_buf_info()` and `arc_buf_info_t`.
- DMU/dnode object info: `__dmu_object_info_from_dnode()` and `dmu_object_info_t`.
- SPA and objset helpers: `spa_name()` and `dmu_objset_id()`.
- Kernel kstat raw APIs and mutex primitives.

## Notable Behavior

- The table snapshot is best-effort and bucket-by-bucket, not a globally consistent dbuf-cache snapshot.
- It intentionally skips dbufs in `DB_EVICTING` state.
- `arc_buf_info()` is called only when `db->db_buf` exists.
- The row format is fixed-width text, with a minimum scratch buffer expectation of 512 bytes.

## Risks And Correctness Notes

- This file reads many internal fields while holding only the hash bucket lock and per-dbuf mutex; values from related ARC/dnode structures can still be observational diagnostics rather than an atomic snapshot.
- Formatting changes must stay aligned with the header columns or downstream diagnostic tooling may break.
- If future dbuf fields are made invalid earlier during eviction, the skip condition and lock ordering here need to stay in sync with `dbuf_destroy()`.
- `zfs_dbuf_state_index` can make `arc_buf_info()` do extra ARC state-index work, so it is disabled by default.
