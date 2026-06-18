<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pt.h

## Purpose

`xe_pt.h` declares the public page-table management API used by VM, migration, eviction, and SVM code.

## Important APIs

`MAX_HUGEPTE_LEVEL` currently allows huge PTEs up to level 2, or 1 GiB. `xe_pt_write()` writes a 64-bit page-table entry through `xe_map_wr()`. Creation/destruction helpers manage page-table metadata and BOs. Update operation functions prepare, run, finish, or abort staged VMA operations. `xe_pt_zap_ptes()` and `xe_pt_zap_ptes_range()` zero GPU mappings for VMA or SVM invalidation.

## Control Flow and State

The declared API follows a prepare/run/fini or prepare/abort pattern. Prepare mutates CPU-side staging state, run submits/commits GPU updates, fini releases temporary resources and deferred BO puts, and abort unwinds staged state after failures.

## Dependencies and Integration Points

The header includes `xe_pt_types.h` and forward-declares DMA fence, DRM exec, BO, device, exec queue, SVM range, sync entry, tile, VM, VMA, and VMA ops types. It is central to VM bind paths.

## Risks and Test Signals

Callers must hold the locks required by the implementation and must pair prepare with run/fini or abort. Test signals include lockdep coverage, fence lifetime checks, and no leaks after error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pt.h -->
