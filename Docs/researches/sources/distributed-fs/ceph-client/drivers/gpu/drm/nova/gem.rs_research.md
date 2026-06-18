# sources/distributed-fs/ceph-client/drivers/gpu/drm/nova/gem.rs

## Purpose
Defines the Nova GEM driver object wrapper and allocation/lookup helpers.

## Important APIs, Types, And Functions
`NovaObject` implements `gem::DriverObject` with no inner fields. `NovaObject::new()` validates size, page-aligns it, and calls `gem::Object::new()`. `lookup_handle()` wraps DRM GEM handle lookup.

## Control Flow
GEM creation rejects zero size, page-aligns with overflow checking, then delegates allocation to DRM GEM core. Lookup returns an owned reference to the GEM object for a file handle.

## State, Persistence, And Dependencies
State is held by DRM GEM core; the driver object currently has no extra fields.

## Integration Points
Depends on Rust DRM GEM abstractions, page alignment helpers, `ARef`, and Nova file/driver types.

## Risks
No placement, VRAM backing, mmap, or GPU binding state exists yet. Large sizes that fail page alignment return `EINVAL`.

## Test Signals
Signals include zero-size rejection, aligned size reporting through `gem_info`, handle lifetime correctness, and object cleanup through DRM core.
