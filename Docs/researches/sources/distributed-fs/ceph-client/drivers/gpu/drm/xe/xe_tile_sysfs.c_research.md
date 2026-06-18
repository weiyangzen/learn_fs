<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sysfs.c

## Purpose

`xe_tile_sysfs.c` creates a per-tile kobject under the PCI device and initializes tile-specific sysfs children such as VRAM frequency attributes.

## Important APIs, Types, and Functions

`xe_tile_sysfs_init()` allocates `struct kobj_tile`, initializes a kobject with `kobj_sysfs_ops`, adds it as `tile%d`, stores it in `tile->sysfs`, initializes VRAM frequency sysfs, and registers devm cleanup. Internal release and cleanup helpers free the wrapper and put the kobject.

## Control Flow

Tile noalloc initialization calls this after VRAM manager/pagemap cache setup. Error paths put the kobject, triggering release.

## State and Persistence Behavior

`tile->sysfs` persists until device-managed teardown. The wrapper stores a backpointer to the tile for child sysfs callbacks.

## Dependencies and Integration Points

The file depends on Linux kobject/sysfs, DRM managed cleanup, Xe runtime-related headers, tile types, and VRAM frequency sysfs.

## Risks and Test Signals

Risks include partial sysfs setup if VRAM frequency initialization fails and ensuring kobject lifetime matches tile lifetime. Tests should cover allocation failure, kobject add failure, VRAM freq failure, and `kobj_to_tile()` users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sysfs.c -->
