# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_bo_types.h

## Purpose
This header defines `struct xe_bo`, the Xe-specific wrapper around `struct ttm_buffer_object`. It is the central data model for buffer placement, VM association, GGTT mappings, pin tracking, CPU mappings, purgeable accounting, CCS metadata, and SVM device-memory links.

## Important APIs, Types, and Functions
The main type is `struct xe_bo`. Important fields include `ttm`, `backup_obj`, `parent_obj`, `flags`, `vm`, `tile`, placement arrays, `ggtt_node`, `vmap`, `kmap`, `pinned_link`, process-client tracking under `CONFIG_PROC_FS`, `attr.atomic_access`, `pxp_key_instance`, `devmem_allocation`, `vram_userfault_link`, `min_align`, `purgeable`, and SR-IOV VF `bb_ccs` pointers.

## Control Flow
The header has no executable flow. Its fields are mutated by BO creation, TTM move callbacks, VM bind/unbind, mmap fault handling, PM eviction, shrinker reclaim, PXP setup, and SR-IOV CCS attach/detach paths.

## State and Persistence Behavior
`backup_obj`/`parent_obj` preserve pinned VRAM contents across suspend. `placement` records allowed TTM locations while `ttm.resource` records current location. `purgeable` tracks terminal purge state plus VMA and WILLNEED holder counts. `vram_userfault_link` persists runtime PM mmap-release tracking. `created` distinguishes initialized BOs from partially constructed objects.

## Dependencies and Integration Points
The type embeds DRM/TTM objects and references Xe device, tile, VM, GGTT, memory-pool, DRM SVM pagemap, and client accounting types. Because it is included widely, it is part of the ABI between memory management, VM, PM, debug, and display subsystems inside the driver.

## Risks
Field ownership is spread across subsystems, so lock discipline is essential. Reservation lock protects purgeable counters and atomic attributes, while `xe->pinned.lock` protects pinned-list membership. Incorrect lifetime handling of `backup_obj`, VM refs, or client links can leak objects or use freed memory.

## Test Signals
Tests should stress BO create/destroy, VM close, client fdinfo accounting, suspend backup lifetime, purgeable VMA transitions, SVM device-memory teardown, SR-IOV CCS attach/detach, and debug object dumps.
