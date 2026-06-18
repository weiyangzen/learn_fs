# File Research: sources/cow-pools/openzfs/module/zfs/ddt_log.c

## Scope

Fast-dedup log implementation. It keeps recently modified DDT entries in two in-memory AVL trees backed by two append-only DMU log objects, reloads them at import, swaps active/flushing roles, checkpoints partial flush progress, truncates emptied logs, and maintains log memory/object stats.

## Main Interfaces

- Global lifecycle: `ddt_log_init()`, `ddt_log_fini()`.
- Per-DDT lifecycle: `ddt_log_alloc()`, `ddt_log_free()`, `ddt_log_load()`, `ddt_log_destroy()`.
- Append path: `ddt_log_begin()`, `ddt_log_entry()`, `ddt_log_commit()`.
- Lookup/removal: `ddt_log_find_key()`, `ddt_log_take_first()`, `ddt_log_remove_key()`.
- Flush management: `ddt_log_checkpoint()`, `ddt_log_truncate()`, `ddt_log_swap()`.
- Tunables: `zfs_dedup_log_txg_max`, `zfs_dedup_log_mem_max`, `zfs_dedup_log_mem_max_percent`.

## State And Control Flow

Each `ddt_t` owns two `ddt_log_t` slots. One is active for appends, the other is flushing. Both have an AVL tree keyed by `ddt_key_t`, an on-disk object ID, flags, byte length, first txg, and optional checkpoint key. Allocation initializes both AVL trees and marks the second as flushing.

`ddt_log_begin()` creates log objects on first use, computes a fixed record length for the current DDT phys format, holds the active log dnode, sets storage type to `DMU_OT_DDT_ZAP`, and holds enough DMU buffers to append the requested number of entries. `ddt_log_entry()` updates the active AVL and writes a `DLR_ENTRY` record directly into the current DMU buffer, zero-filling unused block tail space so import can detect `DLR_INVALID`. `ddt_log_commit()` completes the last buffer, releases the array, advances object length, writes the bonus header, and refreshes stats.

`ddt_log_swap()` starts a new flush epoch when the active tree exceeds half the configured memory limit, is older than `zfs_dedup_log_txg_max`, or has been force-requested by DDT walking. It requires the old flushing tree to be empty, truncates leftover on-disk data if needed, swaps active/flushing pointers, updates flags and headers, and returns whether a swap occurred.

`ddt_log_checkpoint()` records the last flushed key in the flushing log header. `ddt_log_truncate()` frees the entire flushing object range, clears checkpoint state, and resets length. `ddt_log_take_first()` pops the first in-memory flushing entry for conversion into the regular store object.

Import uses `ddt_log_load_one()` for each object. It reads the bonus header, validates version 1, optionally skips records up to a checkpoint, prefetches the log stream, parses records block by block, and rebuilds the target AVL. `ddt_log_load()` skips work during tryimport, loads both logs, validates exactly one active and one flushing log, removes duplicate keys from flushing when active has a newer copy, rebuilds the log histogram, and updates stats.

## Dependencies

Uses DMU object allocation/free/range-free, dnode holds, DMU buffer fill APIs, ZAP directory links, DDT lightweight entry conversion macros, DDT histograms, `ddt_key_compare()`, SPA load state, and config locks for histogram/stat regeneration.

## Correctness Notes

The log is append-only on disk but canonical in memory. Multiple records for a key collapse to one AVL entry. Checkpoints let import skip already-flushed records in a still-nonempty flushing log. Active entries override flushing entries at import. Memory accounting is based on AVL entries, not raw object length, because user-visible log size should reflect logical entries. The code deliberately uses two logs so appends can continue while another batch drains to the store backend.
