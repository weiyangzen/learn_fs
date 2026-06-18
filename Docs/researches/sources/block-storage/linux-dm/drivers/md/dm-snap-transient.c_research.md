# File Research: sources/block-storage/linux-dm/drivers/md/dm-snap-transient.c

## Purpose

`dm-snap-transient.c` implements the non-persistent snapshot exception store. It allocates COW chunks sequentially in memory-only state and does not preserve exception metadata across reloads or reboot.

## Behavior

`struct transient_c` contains only `next_free`, the next COW sector to allocate. Metadata reading is a no-op. Preparing an exception checks whether the COW device has enough space for another chunk, assigns `e->new_chunk` from `next_free`, and advances `next_free` by the store chunk size.

Committing an exception immediately invokes the callback with the supplied validity value; no metadata is written. Usage reports allocated sectors as `next_free`, total sectors from the COW device size, and zero metadata sectors.

The constructor initializes `next_free` to zero. The type is registered as both `transient` and compatibility alias `N`. Table status emits `N <chunk_size>`.

## Invariants And Risks

- All exception mappings are volatile and must be reconstructed by the snapshot target’s in-memory state only for the active lifetime.
- Allocation is strictly sequential with no metadata reservations.
- COW exhaustion is detected by comparing `next_free + chunk_size` with the COW device size.
- Commit cannot fail due to store metadata because there is no persistent metadata.

## Test Focus

Test constructor/destructor, no-op metadata read, sequential chunk allocation, COW full handling, commit callback propagation of valid/invalid state, usage accounting, compatibility alias `N`, and table/IMA status output.
