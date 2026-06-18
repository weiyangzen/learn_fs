# sources/distributed-fs/ceph-client/rust/helpers/drm.c

## Purpose
Exposes DRM GEM and shmem-GEM helper functions to Rust graphics drivers when DRM configs are enabled.

## APIs, Types, and Functions
Under `CONFIG_DRM`, exports GEM object get/put and VMA node offset helpers; under `CONFIG_DRM_GEM_SHMEM_HELPER`, exports shmem object free, print-info, pin/unpin, sg-table retrieval, vmap/vunmap, and mmap helpers.

## Control Flow, State, and Persistence
State is in GEM object refcounts, shmem backing storage, mapping state, and VMA manager nodes. The wrappers keep no local state.

## Dependencies and Integration
Depends on DRM GEM, DRM shmem helper, VMA manager headers, and Rust DRM abstractions.

## Risks and Test Signals
Risks include config-dependent symbols, unbalanced object references, pin/vmap lifecycle bugs, and mmap offset misuse. Test signals are Rust DRM driver tests, GEM object refcount leak checks, mmap/pin/vmap stress, and builds with DRM helpers disabled.
