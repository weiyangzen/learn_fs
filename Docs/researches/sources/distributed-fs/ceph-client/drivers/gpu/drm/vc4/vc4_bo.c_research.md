# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_bo.c

## Purpose

`vc4_bo.c` implements VC4 GEM buffer-object management for the pre-VC5 VC4 driver. It allocates contiguous DMA-backed GEM objects, caches recently freed kernel BOs, tracks BO labels/statistics, supports userspace purgeable BOs, exposes create/mmap/shader/tiling/label ioctls, and defines GEM object operations.

## Important APIs, Types, and Functions

- BO stats/labels: `bo_type_names`, `vc4_bo_stats_print`, `vc4_get_user_label`, `vc4_bo_set_label`, and `vc4_label_bo_ioctl`.
- Kernel BO cache: `vc4_get_cache_list_for_size`, `vc4_bo_get_from_cache`, `vc4_free_object`, `vc4_bo_cache_free_old`, `vc4_bo_cache_purge`, timer/work callbacks, and `vc4_bo_cache_init/destroy`.
- Purgeable userspace cache: `vc4_bo_add_to_purgeable_pool`, `vc4_bo_remove_from_purgeable_pool`, `vc4_bo_userspace_cache_purge`, `vc4_bo_purge`, `vc4_bo_inc_usecnt`, and `vc4_bo_dec_usecnt`.
- Creation paths: `vc4_create_object`, `vc4_bo_create`, `vc4_bo_dumb_create`, `vc4_create_bo_ioctl`, and `vc4_create_shader_bo_ioctl`.
- Mapping/export operations: `vc4_prime_export`, `vc4_gem_object_mmap`, `vc4_fault`, and `vc4_gem_object_funcs`.
- User ioctls: mmap offset query, tiling set/get, shader BO creation, dumb create, generic BO create, and label assignment.

## Control Flow

Initialization creates label slots, initializes `bo_lock`, BO cache lists, timer/work, and managed destroy action. Allocation first rounds size to pages and tries a same-size cached BO; otherwise it allocates via `drm_gem_dma_create`, purging kernel then userspace caches on DMA allocation failure. User-visible BO ioctls set `madv = VC4_MADV_WILLNEED` and create GEM handles. Shader BO creation copies user code, zeroes padding, validates the shader before handle exposure, and disallows writable mmap/export of validated shader BOs.

On final GEM unref, `vc4_free_object` removes purgeable entries if needed, refuses to cache imported/named/purged objects, frees validated shader metadata, resets BO state, puts reusable DMA BOs into size/time cache, relabels them as kernel cache, and expires old cache entries. Purgeable logic moves `DONTNEED` BOs into a separate list when not in use and can free their DMA memory under pressure; later mmap faults on purged BOs return SIGBUS.

## State and Persistence Behavior

Persistent driver state includes dynamic `bo_labels`, allocation counters, kernel BO cache lists indexed by page count, cache timer/work, purgeable list counters, and per-BO `madv`, `usecnt`, `validated_shader`, tiling flag, label, free time, and DMA mapping. Exporting a BO increments use count and effectively makes it unpurgeable.

## Dependencies and Integration Points

The file depends on DRM GEM DMA helpers, dma-buf export, DRM vma mmap helpers, debugfs, VC4 shader validation, VC4 V3D bin BO acquisition, VC4 UAPI structs, DMA allocation, timers/workqueues, and driver generation checks. It is used by VC4 ioctl dispatch and KMS framebuffer paths.

## Risks and Edge Cases

- This code explicitly rejects `vc4->gen > VC4_GEN_4`; VC5 uses different memory management assumptions.
- Purgeable list removal deliberately drops/reacquires locks; races are mitigated with `list_del_init`, `madv_lock`, and `usecnt`, but changes here are high risk.
- Kernel BO cache can retain sensitive data; user BO creation avoids unzeroed cache reuse, while shader BO creation zeroes padding after copying.
- `bo_page_index(size)` assumes nonzero page-rounded size.
- Label slot management is linear and user labels are freed when counts drop to zero; stats updates require `bo_lock`.
- Purged BO mmap faults intentionally SIGBUS, so userspace must honor MADV results.

## Test Signals

Run VC4 GEM ioctl tests for BO create/mmap/dumb/shader/tiling/label, shader validation race tests, dma-buf export rejection for shader BOs, purgeable MADV pressure tests, SIGBUS on purged mmap access, BO cache reuse/expiry tests, debugfs `bo_stats`, fault injection for DMA allocation failure, and lockdep/KCSAN around `bo_lock`, `purgeable.lock`, and `madv_lock`.
