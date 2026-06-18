# sources/distributed-fs/ceph-client/drivers/gpu/drm/nova/file.rs

## Purpose
Implements Nova per-file state and ioctl handlers for parameter queries and GEM object management.

## Important APIs, Types, And Functions
`File` implements `drm::file::DriverFile`. Ioctl handlers are `get_param()`, `gem_create()`, and `gem_info()`.

## Control Flow
Open allocates an empty `File`. `get_param` converts the auxiliary parent to a PCI device and returns BAR1 size for `NOVA_GETPARAM_VRAM_BAR_SIZE`. `gem_create` creates a page-aligned `NovaObject` and returns a handle. `gem_info` looks up a handle and reports object size.

## State, Persistence, And Dependencies
Per-open state is currently empty. GEM handles and objects are managed by DRM core; returned ioctl fields persist only to userspace.

## Integration Points
Depends on Rust DRM file/GEM traits, PCI resource access, uapi constants, and `NovaObject` helpers.

## Risks
Unsupported params return `EINVAL`. Parent device conversion assumes the auxiliary parent is PCI. Object sizes are converted with checked conversions.

## Test Signals
Signals include successful DRM open, BAR size query, GEM create with nonzero size, GEM info returning aligned size, and invalid handle/param errors.
