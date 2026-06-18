# File Research: sources/cow-pools/openzfs/module/zfs/vdev_indirect_births.c

## Purpose

Manages the vdev-indirect births object, an on-disk array describing the physical birth TXG for contiguous ranges copied during vdev removal. Consumers use it to determine the physical birth of a non-split remapped range.

## Main APIs And Entry Points

- Accessors: `vdev_indirect_births_count()`, `vdev_indirect_births_object()`, and `vdev_indirect_births_last_entry_txg()`.
- Lifecycle: `vdev_indirect_births_alloc()`, `vdev_indirect_births_open()`, `vdev_indirect_births_close()`, and `vdev_indirect_births_free()`.
- Mutation/query: `vdev_indirect_births_add_entry()` appends a `(max_offset, txg)` entry; `vdev_indirect_births_physbirth()` binary-searches entries to find the TXG covering a specified contiguously mapped range.

## Control Flow And Data Model

The object stores a bonus `vdev_indirect_birth_phys_t` with entry count plus a data payload array of `vdev_indirect_birth_entry_phys_t`. Open reads the whole entry array into memory if count is nonzero. Appending writes the new entry to the end of the object, increments the bonus count, and rebuilds the in-memory array. The lookup algorithm treats each entry as applying from the previous entry's offset up to this entry's `vibe_offset`, with entries sorted by increasing physical birth and offset.

## Dependencies And Integration

The file uses DMU object allocation/free, bonus buffers, `dmu_read()`/`dmu_write()`, syncing DMU transactions, and DSL pool sync-context assertions. Kernel builds export all public helpers for removal/remap code.

## Risks And Invariants

- `vdev_indirect_births_physbirth()` assumes the queried range is contiguously mapped and lies below the last entry offset.
- Entry ordering is semantic, not just storage convenience; binary search depends on monotonic offsets and the previous-entry boundary rule.
- Append reallocates and copies the full in-memory table, which is simple but assumes the entry count is manageable for this metadata path.

## Summary

This file is a compact DMU-backed table abstraction for mapping indirect-vdev source offsets to physical birth TXGs.
