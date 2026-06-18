# sources/distributed-fs/ceph-client/mm/vma_init.c

## Purpose

`vma_init.c` owns initialization, allocation, duplication, and freeing of `struct vm_area_struct` objects shared by MMU and NOMMU configurations. It sets up the VMA slab cache and centralizes field copying and cleanup for VMA lifetime management.

## Important APIs, Types, and Functions

- `vma_state_init()` creates the `vm_area_struct` kmem cache with a free pointer offset, sheaf capacity, cacheline alignment, panic-on-failure, RCU type safety, and accounting.
- `vm_area_alloc(struct mm_struct *mm)` allocates from the VMA cache and calls `vma_init()`.
- `vm_area_dup(struct vm_area_struct *orig)` allocates and initializes a copy of an existing VMA, including locks, anon-vma chain, NUMA balancing state, anon name, and optional PFNMAP tracking.
- `vm_area_free(struct vm_area_struct *vma)` asserts detachment and releases NUMA, anon-name, PFNMAP tracking, and slab storage.
- `vm_area_init_from()` is the internal field-by-field copier.
- Optional `vma_pfnmap_track_ctx_dup()` and `vma_pfnmap_track_ctx_release()` reference-count PFNMAP tracking contexts.

## Control Flow

The boot-time `vma_state_init()` configures the cache before VMA allocations are needed. `vm_area_alloc()` performs a plain allocation and initializes a fresh VMA for an mm. `vm_area_dup()` allocates raw storage, asserts exclusive writer access to key mutable fields in the original, copies structural fields, duplicates optional PFNMAP tracking with kref protection, initializes the VMA lock as already detached/new, initializes anon-vma chain and NUMA state, and duplicates anon-vma names. `vm_area_free()` asserts the VMA is detached from address-space structures before releasing auxiliary state and freeing the object.

## State and Persistence

The persistent allocator state is the static `vm_area_cachep`. Per-VMA copied state includes mm, ops, range, anon_vma pointer, pgoff, file pointer, private data, flags, page protection, shared interval-tree node contents, userfaultfd context, optional anon name, swap readahead, NOMMU region, NUMA policy, and PFNMAP tracking. Duplication does not itself take file or mempolicy references; callers in `vma.c` handle those as part of split/copy operations.

## Dependencies and Integration Points

This file depends on slab APIs, `vma_init()`, VMA lock initialization, anon-vma name helpers, NUMA balancing state helpers, optional swap/NOMMU/NUMA/PFNMAP features, RCU-safe VMA cache semantics, and all VMA mutation code that allocates, duplicates, or frees VMAs.

## Risks

- Field copying is intentionally selective; adding fields to `struct vm_area_struct` requires auditing this copier.
- `shared` is copied with `data_race()` because `dup_mmap()` may see concurrent modification, and consumers must reinitialize/link it appropriately before use.
- PFNMAP tracking duplication can fail on reference-count saturation, making VMA duplication fail.
- `vm_area_free()` assumes the VMA has already been detached; freeing attached VMAs would leave stale maple-tree or interval-tree references.
- File, mempolicy, and anon-vma chain lifetime adjustments are split between this file and callers, so misuse can leak or double-release references.

## Test Signals

Signals include boot/slab initialization checks, split/mremap/fork paths using `vm_area_dup()`, debug assertions for detached frees, PFNMAP tracking reference tests, NUMA/anon-name cleanup checks, and configuration matrix builds with swap, NOMMU, NUMA, and PFNMAP tracking toggled.
