# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_gem.h

## Purpose
This header defines Panfrost GEM object and mapping structures plus the public GEM subsystem API.

## Important APIs, Types, and Functions
It defines `PANFROST_BO_LABEL_MAXLEN`, debugfs GEM state flags, `struct panfrost_gem_debugfs`, `struct panfrost_gem_object`, and `struct panfrost_gem_mapping`. It declares GEM create/import/open/close, mapping refcount helpers, shrinker hooks, label helpers, cache sync, and debugfs printing.

## Control Flow
The header has inline casts from `drm_gem_object` to `panfrost_gem_object` and from `drm_mm_node` to `panfrost_gem_mapping`. Other behavior is implemented in `.c` files.

## State and Persistence Behavior
The structs describe persistent BO state, including shmem base, sg tables, per-MMU mappings, GPU usecount, heap RSS, labels, flags, and debugfs metadata. Mapping structs persist while a BO is open in an MMU context or referenced by jobs.

## Dependencies and Integration Points
It integrates DRM shmem GEM, drm_mm, Panfrost MMU, Panfrost device/file state, shrinker, debugfs, and UAPI-visible BO labels/cache sync behaviors.

## Risks
Fields such as `gpu_usecount`, `heap_rss_size`, and `active` are consumed by shrinker, MMU, and job code; changing semantics can corrupt memory reclamation or GPU VA teardown. Locking around `mappings` and labels must be respected by callers.

## Test Signals
Build and runtime coverage across GEM creation, mapping, shrinker purge, MMU faults, job BO references, labels, debugfs, and PRIME paths validates the interface.
