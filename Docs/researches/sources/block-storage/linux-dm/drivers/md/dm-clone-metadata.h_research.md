# File Research: sources/block-storage/linux-dm/drivers/md/dm-clone-metadata.h

## Purpose
Declares the public internal API used by `dm-clone-target.c` to manage clone metadata, region hydration state, commit/rollback behavior, read-only transitions, and metadata device accounting.

## Main Interfaces
- Constants: `DM_CLONE_METADATA_BLOCK_SIZE`, `DM_CLONE_METADATA_MAX_SECTORS`, warning threshold, and `SPACE_MAP_ROOT_SIZE`.
- Opaque metadata handle: `struct dm_clone_metadata`.
- Mutation APIs: `dm_clone_set_region_hydrated()`, `dm_clone_cond_set_range()`.
- Lifecycle APIs: `dm_clone_metadata_open()`, `dm_clone_metadata_close()`.
- Commit APIs: `dm_clone_metadata_pre_commit()`, `dm_clone_metadata_commit()`.
- Recovery/mode APIs: `dm_clone_reload_in_core_bitset()`, `dm_clone_metadata_abort()`, read-only/read-write setters.
- Query/accounting APIs for hydration completion, region/range state, hydrated counts, next unhydrated region, free metadata blocks, and metadata device size.

## Control Flow
The header documents the two-phase commit contract: first `pre_commit` freezes the current transaction’s dirty region set, then the clone target flushes destination data, then `commit` persists metadata. This ordering ensures a crash cannot expose metadata claiming a region is hydrated before its destination contents are durable.

## State And Synchronization
The comments specify context constraints. Single-region hydration is nonblocking and interrupt-safe. Range hydration is nonblocking but uses `spin_lock_irq()` and must not be called with interrupts disabled. Reloading the in-core bitset may block and must not race with hydration updates unless metadata has first been made read-only.

## Integration Points
This header is consumed by the clone target and backed by `dm-clone-metadata.c`. It also exposes persistent-data metadata limits to constructor code so target validation can warn about oversized metadata devices.

## Notable Behaviors
- Read-only mode causes commit, mutation, and abort operations to reject updates with `-EPERM`.
- Hydration completion can be queried globally, per region, or over a range.
- `find_next_unhydrated_region()` supports background hydration scanning.

## Risks And Review Focus
- Callers must honor the commit sequence and reload synchronization rules from the comments.
- Context-safety differences between single-region and range updates are easy to misuse.
