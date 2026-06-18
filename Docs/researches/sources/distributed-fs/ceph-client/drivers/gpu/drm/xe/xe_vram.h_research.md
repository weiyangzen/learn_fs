# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vram.h

## Purpose

`xe_vram.h` declares the public VRAM probe and region accessor interface. It keeps callers independent of the concrete `struct xe_vram_region` layout in `xe_vram_types.h`.

## Important APIs, Types, and Functions

The header declares `xe_vram_probe()`, `xe_vram_region_alloc()`, and accessors for IO start, IO size, DPA base, usable size, and actual physical size. It forward-declares `struct xe_device` and `struct xe_vram_region`.

## Control Flow and State

There is no executable control flow in the header. The declared functions are used during device and tile memory initialization and by code that needs read-only VRAM region metadata.

## Dependencies and Integration Points

The header depends only on Linux fixed-width type definitions and is consumed by Xe device/tile setup, TTM VRAM manager setup, memory region reporting, migration, and tests.

## Risks and Edge Cases

The accessors intentionally return zero for NULL regions in the implementation, so callers must distinguish "missing region" from a valid zero-valued field when that matters. Future additions should preserve this low-dependency API boundary.

## Test Signals

Build coverage and probe tests should verify declarations stay synchronized with `xe_vram.c`. Unit tests can call accessors on NULL and initialized regions.
