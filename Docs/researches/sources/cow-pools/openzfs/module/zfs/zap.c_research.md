# File Research: sources/cow-pools/openzfs/module/zfs/zap.c

## Purpose
Provides the public ZAP object API: create/destroy, lookup, add/update/remove, count, increment, value search, integer-key helpers, cursor iteration, prefetch, and stats. It dispatches between microzap and fatzap implementations.

## Main Responsibilities
- Allocates or claims DMU objects with ZAP-compatible byteswap type and initializes them as microzaps.
- Creates linked child ZAP objects by adding the new object ID into a parent ZAP.
- Looks up string and uint64-array keys, including normalization-aware matching and real-name return.
- Adds, updates, removes, counts, and increments entries.
- Upgrades microzaps to fatzaps when entry names/values or object size exceed microzap limits.
- Initializes and advances cursors for full or serialized iteration.
- Provides stats and object prefetch helpers.
- Exports the ZAP API symbols used by the wider OpenZFS kernel module.

## Key Data And State
- The file does not introduce global mutable state beyond exported functions.
- `zap_attribute_t` objects are allocated through helpers from `zap_impl.c`.
- Cursor state is carried in `zap_cursor_t`: held `zap_t`, optional held leaf, hash, collision differentiator, object set/object number, and prefetch preference.
- Microzap entries are managed through `mzap_*`; fatzap entries through `fzap_*`.

## Important Functions
- `zap_create_impl()` and wrappers: allocate/claim ZAP DMU objects with optional normalization, flags, block shifts, bonus type/length, and dnode size.
- `zap_lookup_norm_by_dnode()`: locks the ZAP, builds a normalized name, dispatches to `fzap_lookup()` or microzap btree lookup, and reports normalization conflicts.
- `zap_add_by_dnode()` / `zap_update_by_dnode()`: write string-keyed entries, upgrading to fatzap when microzap constraints are exceeded.
- `zap_add_uint64_by_dnode()` / `zap_update_uint64_by_dnode()`: uint64-keyed write paths that use fatzap semantics.
- `zap_remove_norm_by_dnode()` / `zap_remove_uint64_by_dnode()`: delete entries from microzap or fatzap.
- `zap_length_by_dnode()` and uint64 variant: report value integer size and count.
- `zap_count_by_dnode()`: returns microzap in-memory count or fatzap physical count.
- `zap_increment_by_dnode()`: lookup-add/remove helper for counters, removing zero-valued entries.
- `zap_value_search_impl()`: cursor-based scan for first entry whose first integer matches a masked value.
- `zap_cursor_init*()`, `zap_cursor_retrieve()`, `zap_cursor_advance()`, `zap_cursor_serialize()`, `zap_cursor_fini()`: iteration API.
- `zap_get_stats_by_dnode()`: fills microzap or fatzap stats.

## Control Flow Notes
- Most public object-number APIs hold the dnode, call the `_by_dnode` variant, then release the dnode.
- Microzap supports only one 8-byte integer value per short string key; larger or incompatible entries trigger fatzap upgrade.
- Cursor initialization takes and then drops the ZAP read lock while preserving underlying holds, letting retrieval reacquire locks per step.
- Serialized cursors pack hash bits and collision differentiator; corrupt serialized collision differentiators are reset to zero.

## Error Handling And Invariants
- Object creation asserts the DMU object type uses `DMU_BSWAP_ZAP`.
- Unsupported match types without normalization return `ENOTSUP`.
- Value reads return `EOVERFLOW` when caller buffers are too small and `EINVAL` for incompatible integer sizes.
- Add returns `EEXIST` when a key already exists; remove returns `ENOENT` when absent.
- Cursor retrieval returns `EIO` if initialized from a failed cursor and `ENOENT` at end.

## Dependencies
Depends on DMU object allocation/holding/freeing, dnode holds, microzap implementation, fatzap implementation, ZAP name normalization/hash helpers, btree cursor support, and module symbol export infrastructure.

## Research Notes
This file is the stable facade for ZAP consumers. Behavioral changes here affect directories, pool metadata ZAPs, feature state, vdev metadata, quotas, and any code storing structured key/value metadata in DMU objects.
