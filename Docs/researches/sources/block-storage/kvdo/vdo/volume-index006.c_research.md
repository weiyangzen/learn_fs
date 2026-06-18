# File Research: sources/block-storage/kvdo/vdo/volume-index006.c

## Purpose
Implements volume index format/version 006 as a sparse+dense wrapper over two 005 indexes:
- non-hook index for ordinary dense entries,
- hook index for sampled sparse entries.

It routes operations to the proper subindex based on chunk-name sampling, persists a 006 header plus both subindexes, and adds per-zone synchronization for sparse sampled lookups.

## Core Data Structures
- `struct volume_index_zone`: holds a per-zone `hook_mutex` protecting sampled hook-index access.
- `struct volume_index6`: embeds common vtable, stores sparse sample rate, zone count, non-hook and hook `volume_index` pointers, and zone mutex array.
- `struct vi006_data`: persisted header with magic `MI6-0001` and sparse sample rate.
- `struct split_config`: local pair of derived configurations/geometries for hook and non-hook 005 indexes.

## Routing Model
`is_volume_index_sample_006()` treats a chunk name as sampled when `extract_sampling_bytes(name) % sparse_sample_rate == 0`.

`get_sub_index()` returns `vi_hook` for sampled names and `vi_non_hook` otherwise.

Operations route as follows:
- `get_volume_index_zone_006()` delegates to the selected subindex.
- `get_volume_index_record_006()` delegates to hook or non-hook. Hook records are looked up under the per-zone mutex, and the mutex pointer is saved into `record->mutex` for later mutation operations implemented by 005.
- `lookup_volume_index_name_006()` only checks sampled names. It locks the relevant hook mutex, delegates to `lookup_volume_index_sampled_name()` on the hook subindex, and returns `UINT64_MAX` for non-sampled names.
- `lookup_volume_index_sampled_name_006()` is a defensive stub returning `UINT64_MAX` with a FIXME saying it should never be called.
- Chapter movement updates non-hook first, then hook under the zone mutex.

## Persistence
`start_saving_volume_index_006()` writes the 006 header, then starts saving the non-hook 005 index followed by the hook 005 index to the same buffered writer.

`finish_saving_volume_index_006()` finishes non-hook first, then hook if non-hook succeeded.

`start_restoring_volume_index_006()` reads and validates the 006 header from each reader, enforces consistent sparse sample rate, then starts restore for non-hook and hook indexes.

`finish_restoring_volume_index_006()` finishes both subindexes in order. `abort_restoring_volume_index_006()` aborts both subindexes.

## Configuration Splitting
`split_configuration006()` requires:
- `sparse_chapters_per_volume != 0`,
- `sparse_sample_rate != 0`.

It copies the original config and geometry twice, then:
- hook geometry indexes only sampled records per chapter and no sparse chapters,
- non-hook geometry removes sampled records and only indexes dense chapters,
- both derived geometries use dense 005 indexes internally.

`compute_volume_index_save_bytes006()` returns `sizeof(vi006_data) + non_hook_005_bytes + hook_005_bytes`.

## Construction and Cleanup
`make_volume_index006()`:
1. splits the configuration,
2. allocates `volume_index6`,
3. initializes vtable methods,
4. allocates zone mutexes,
5. creates non-hook 005 index tagged `'d'`,
6. creates hook 005 index tagged `'s'`.

`free_volume_index_006()` destroys per-zone mutexes, frees both subindexes, and frees the wrapper.

## Dependencies
Uses `buffer.h`, `errors.h`, `hash-utils.h`, `logger.h`, `memory-alloc.h`, `permassert.h`, `uds-threads.h`, and `volume-index005.h`.

## Invariants and Risks
- Hook lookup is the only multithreaded sparse operation explicitly supported; zone mutexes protect it from hook-index mutations and open-chapter changes.
- 006 relies on 005 for actual delta-index storage and most record mutation.
- The sampled lookup path returns sparse virtual chapters only for sampled names.
- Save/restore stream layout is nested: 006 header, non-hook 005 payload, hook 005 payload.
