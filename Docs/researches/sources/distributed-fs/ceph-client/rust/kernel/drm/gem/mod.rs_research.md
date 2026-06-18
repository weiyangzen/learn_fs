# sources/distributed-fs/ceph-client/rust/kernel/drm/gem/mod.rs

## Purpose
`drm/gem/mod.rs` implements the base Rust DRM GEM object abstraction. It defines driver object traits, raw GEM conversion, handle lookup/creation helpers, object lifetime callbacks, and DRM file operations for GEM-capable drivers.

## Important APIs, Types, and Functions
`DriverObject` defines `Driver`, `Args`, `new`, `open`, and `close`. `IntoGEMObject` converts typed objects to and from raw `drm_gem_object`. `BaseObject` provides `size`, `create_handle`, `lookup_handle`, and `create_mmap_offset`. `BaseObjectPrivate` exposes `raw_dma_resv`. `Object<T>` embeds `drm_gem_object` and pinned driver data. `impl_aref_for_gem_obj!` implements GEM refcounting. `create_fops` creates DRM GEM file operations.

## Control Flow
`Object::new` allocates a pinned Rust object, installs object funcs, calls `drm_gem_object_init`, and transfers the initial GEM reference into `ARef<Self>`. GEM open/close callbacks convert raw object and file pointers back to typed wrappers and invoke driver hooks. `free_callback` releases GEM base state and drops the `KBox` when the final GEM reference is gone. Handle lookup takes ownership of the reference returned by `drm_gem_object_lookup`.

## State and Persistence
GEM state is in-memory DRM object state plus typed driver data. Object references are managed by DRM GEM refcounting. Handles and mmap offsets are per-DRM-file/core state, not durable across process or driver lifetime.

## Dependencies and Integration Points
This module integrates with `drm::Driver`, `drm::File`, `drm::driver::AllocImpl`, DRM GEM C helpers, `ARef`, and optional shmem GEM support. `drm/device.rs` installs `create_fops` and allocation ops into the DRM driver vtable.

## Risks
Raw pointer conversion relies on object type coherence: a raw GEM object must actually be embedded in the expected Rust type. The code comments note a typo-level risk around proof assumptions for `lookup_handle`; practically the file and object driver associations must stay aligned. Object initialization failure requires the correct private cleanup path.

## Test Signals
Create and drop GEM objects, open/close handles, look up valid and invalid handles, create mmap offsets, unload with live handles, exercise free callbacks, and run PRIME/dumb-buffer tests for memory managers that fill `AllocOps`.
