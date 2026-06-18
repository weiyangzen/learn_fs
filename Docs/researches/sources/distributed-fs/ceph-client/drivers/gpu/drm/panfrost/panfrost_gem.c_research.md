# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_gem.c

## Purpose
This file implements Panfrost GEM buffer objects, per-file GPU virtual mappings, PRIME dma-buf integration, cache synchronization, labels, debugfs reporting, and optional transparent hugepage backing.

## Important APIs, Types, and Functions
Key entry points are `panfrost_gem_init`, `panfrost_gem_create_object`, `panfrost_gem_create`, `panfrost_gem_open`, `panfrost_gem_close`, `panfrost_gem_mapping_get/put`, `panfrost_gem_teardown_mappings_locked`, PRIME import/export callbacks, `panfrost_gem_sync`, label helpers, and debugfs BO printing.

## Control Flow
Object creation allocates shmem GEM, initializes mapping lists and labels, sets default cacheability, and tags heap/noexec/WB flags. GEM open allocates a `panfrost_gem_mapping`, assigns a VA range in the file MMU with executable alignment/color constraints, maps non-heap objects immediately, and links the mapping. Close unlinks and drops the mapping, which unmaps and removes the VA node at final ref. PRIME callbacks synchronize sg tables and vmap ranges for CPU/device access. Cache sync walks DMA sg entries over the requested range.

## State and Persistence Behavior
BO state includes shmem backing, optional per-2 MiB sg tables for heap faults, mapping list, GPU usecount, heap resident size, label string, cacheability flags, debugfs metadata, and madvise state inherited from shmem GEM. Mapping state includes VA node, MMU context, refcount, and active bit.

## Dependencies and Integration Points
It depends on DRM GEM shmem helpers, drm_mm, dma-buf, DMA mapping/cache APIs, Panfrost MMU, per-file private state, shrinker, debugfs, and the driver-wide transparent hugepage parameter.

## Risks
Mapping refcounts must stay balanced across handles, jobs, and close. Executable buffers must not cross 16 MiB and 4 GiB-sensitive boundaries. Heap BOs are fault-mapped lazily and cannot be CPU mmapped. Cache sync rejects imported buffers and must avoid stale data on coherent versus noncoherent devices. Label lifetime is protected by a mutex and const-free semantics.

## Test Signals
Test create/open/close, mmap restrictions for heap BOs, per-file VA reuse, job submission with shared BOs, PRIME import/export CPU access, cache flush/invalidate ranges, shrinker interaction, label ioctl/debugfs output, and transparent hugepage mount behavior.
