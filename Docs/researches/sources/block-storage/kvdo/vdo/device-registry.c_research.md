# File Research: sources/block-storage/kvdo/vdo/device-registry.c

## Purpose
Implements a simple global registry of live VDO instances so target creation/reload paths can find existing devices by pointer, name, or backing device.

## Main Behavior
- `vdo_initialize_device_registry_once()` initializes a global list and rwlock.
- `vdo_register()` asserts the VDO is not already registered, initializes its list node, and appends it.
- `vdo_unregister()` removes the VDO if present.
- `vdo_find_matching()` scans under read lock using caller-supplied `vdo_filter_t`.

## Dependencies
Uses Linux list/rwlock primitives, VDO object `registration` field, UDS assertions, and VDO status codes.

## Invariants
Registry scans are linear; comments explicitly accept this because the set should be small. Write-side operations hold the write lock, and lookup holds the read lock.
