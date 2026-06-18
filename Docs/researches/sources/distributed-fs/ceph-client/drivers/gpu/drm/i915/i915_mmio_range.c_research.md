# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_mmio_range.c

## Purpose
Implements a simple lookup helper for sentinel-terminated MMIO address range tables.

## Important APIs, types, and functions
Exports `i915_mmio_range_table_contains(u32 addr, const struct i915_mmio_range *table)`.

## Control flow
Iterates entries until both `start` and `end` are zero, returning true if `addr` falls inclusively between an entry's start and end.

## State and persistence
No state.

## Dependencies and integration points
Depends on `struct i915_mmio_range` from the header. Used by register-filtering code such as shadow/MCR/table checks.

## Risks
Tables cannot represent a valid range starting and ending at zero because that is the sentinel. Inclusive end semantics must match table authors' expectations.

## Test signals
Unit-style tests for first, middle, boundary, absent, and sentinel entries; build coverage for all table users.
