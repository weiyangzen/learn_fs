<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fuse/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fuse/base.c

## Purpose
Provides the common NVKM fuse subdevice wrapper and dispatches fuse reads to generation-specific register accessors.

## Important APIs, Types, And Functions
Exports `nvkm_fuse_read` and `nvkm_fuse_new_`. Defines the subdev destructor and initializes a spinlock in each `struct nvkm_fuse`.

## Control Flow
Construction allocates the fuse object, initializes the NVKM subdev, stores the function table, and initializes the lock. `nvkm_fuse_read` calls `fuse->func->read`.

## State And Persistence
Persistent state is the fuse subdev object, function table, and spinlock. Fuses themselves are hardware-programmed nonvolatile state, but this file only reads through lower layers.

## Dependencies And Integration Points
Used by chipset-specific files and public fuse consumers that need strap, security, or configuration data.

## Risks And Edge Cases
No validation exists for missing `read` hooks. The lock only protects readers that use it; generation code must correctly preserve gate registers.

## Test Signals
Successful fuse reads and absence of register-gating races under concurrent calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fuse/base.c -->
