# File Research: sources/block-storage/parted/libparted/cs/geom.c

This file implements `PedGeometry`, libparted’s representation of a contiguous sector range on a `PedDevice`.

Core invariants:
- `start + length - 1 == end`
- `length > 0`
- `start >= 0`
- `end < dev->length` is documented as an API invariant, though `ped_geometry_set()` itself mainly enforces positive length and nonnegative start.

Construction and mutation:
- `ped_geometry_init()` initializes caller-provided storage.
- `ped_geometry_new()` allocates a geometry.
- `ped_geometry_duplicate()` copies a geometry.
- `ped_geometry_intersect()` returns the shared region between two geometries on the same device.
- `ped_geometry_destroy()` frees an allocated geometry.
- `ped_geometry_set()`, `ped_geometry_set_start()`, and `ped_geometry_set_end()` update range fields.

Predicates:
- `ped_geometry_test_overlap()` checks overlap on the same device.
- `ped_geometry_test_inside()` checks full containment.
- `ped_geometry_test_equal()` checks same device/start/end.
- `ped_geometry_test_sector_inside()` checks sector membership.

I/O wrappers:
- `ped_geometry_read()` reads device sectors relative to the geometry start and rejects reads beyond the geometry end.
- `ped_geometry_read_alloc()` allocates a buffer sized by `count * sector_size`, reads into it, and returns ownership through `buffer`.
- `ped_geometry_write()` writes relative to the geometry start and throws an exception if the write crosses the geometry boundary.
- `ped_geometry_sync()` calls full device sync.
- `ped_geometry_sync_fast()` calls fast device sync.

Checking and mapping:
- `ped_geometry_check()` scans a region for unreadable sectors, using a timer and exception suppression while narrowing failures to granularity-sized reads.
- `ped_geometry_map()` maps a sector from one overlapping geometry’s coordinate system to another.

Research notes:
- This is the thin safety layer between partition/filesystem logic and `ped_device_*` I/O.
- Boundary checks are expressed in geometry-relative offsets, which is critical for filesystem code operating inside a partition region.
