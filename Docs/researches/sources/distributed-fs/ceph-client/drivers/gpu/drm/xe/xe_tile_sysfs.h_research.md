<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sysfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sysfs.h

## Purpose

`xe_tile_sysfs.h` declares tile sysfs initialization and the kobject-to-tile helper.

## Important APIs, Types, and Functions

`xe_tile_sysfs_init()` creates per-tile sysfs state. `kobj_to_tile()` converts a tile kobject to its `struct xe_tile *` through `struct kobj_tile`.

## Control Flow

Tile init creates the kobject, and child sysfs callbacks use `kobj_to_tile()` to recover tile context.

## State and Persistence Behavior

The helper relies on a persistent `struct kobj_tile` wrapper allocated during init.

## Dependencies and Integration Points

It includes tile sysfs types and is consumed by tile setup and tile sysfs child modules.

## Risks and Test Signals

Using `kobj_to_tile()` on non-tile kobjects is invalid. Tests should read child attributes and verify the correct tile is selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sysfs.h -->
