# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_mmio_range.h

## Purpose
Defines the MMIO range table entry type and containment API.

## Important APIs, types, and functions
Defines `struct i915_mmio_range { u32 start; u32 end; }` and declares `i915_mmio_range_table_contains()`.

## Control flow
No runtime flow in the header.

## State and persistence
No state; callers provide static or dynamic sentinel-terminated tables.

## Dependencies and integration points
Included by MMIO validation/filtering code.

## Risks
Callers must terminate tables with `{ 0, 0 }` and use inclusive end addresses consistently.

## Test signals
Compile table users and test containment boundaries.
