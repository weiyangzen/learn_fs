<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sysfs_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sysfs_types.h

## Purpose

`xe_tile_sysfs_types.h` defines the kobject wrapper used by tile sysfs.

## Important APIs, Types, and Functions

`struct kobj_tile` contains the base kobject and a backpointer to the associated `struct xe_tile`.

## Control Flow

`xe_tile_sysfs_init()` allocates and initializes this wrapper. Sysfs callbacks recover the tile through `kobj_to_tile()`.

## State and Persistence Behavior

The wrapper persists for the lifetime of the tile sysfs kobject and is freed by its release callback.

## Dependencies and Integration Points

The header depends on Linux kobject and forward-declares `xe_tile`. It supports tile sysfs and child attribute modules.

## Risks and Test Signals

Kobject lifetime bugs can cause use-after-free in child sysfs callbacks. Tests should cover teardown while attributes exist and verify release frees the wrapper once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sysfs_types.h -->
