<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ggtt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ggtt.c

## Purpose
`xe_ggtt.c` implements Xe Global Graphics Translation Table management. It allocates usable GGTT ranges, maps BOs and transformed display layouts, clears mappings to scratch, invalidates GT TLBs, supports SR-IOV VF assignment/save/load, and exposes debug hole/dump helpers.

## Important APIs, types, and functions
Internal types include `xe_ggtt_node`, platform `xe_ggtt_pt_ops`, and `xe_ggtt`. Public operations include `xe_ggtt_alloc()`, `xe_ggtt_init_early()`, `xe_ggtt_init()`, `xe_ggtt_insert_node()`, `xe_ggtt_insert_node_transform()`, `xe_ggtt_node_remove()`, `xe_ggtt_insert_bo_at()`, `xe_ggtt_insert_bo()`, `xe_ggtt_remove_bo()`, `xe_ggtt_largest_hole()`, SR-IOV `assign/save/load`, dump/print helpers, PTE flag encoding, PTE read, and node address/size helpers.

## Control flow and integration points
Early init computes usable GGTT from WOPCM and GSM size, or VF-provisioned base/size, clamps to `GUC_GGTT_TOP`, maps GSM, selects PTE ops including WA `22019338487`, allocates a removal workqueue, initializes `drm_mm`, and marks online. Regular init creates a scratch BO and clears all holes. BO insertion validates placement, takes runtime PM, allocates a node, translates requested ranges relative to `ggtt->start`, inserts into `drm_mm`, writes PTEs from TT SG pages or VRAM resources, and invalidates if requested. Removal clears to scratch if online, removes the node, optionally invalidates, and may defer through a workqueue if runtime PM is inactive.

## State and persistence behavior
Each tile has a persistent GGTT with start/size, online flag, scratch BO, GSM pointer, `drm_mm`, access counter, and removal workqueue. BOs store per-tile `ggtt_node` pointers. VF recovery can shift the base with `WRITE_ONCE` while node offsets remain stable. SR-IOV assignment persists VFID bits in PTEs.

## Dependencies, risks, and test signals
Dependencies include DRM MM, MMIO/GSM mapping, PAT/MOCS cache indices, TTM resources, BO validation, runtime PM, TLB invalidation, WOPCM, SR-IOV VF provisioning, display transform callbacks, and generated workarounds. Risks include off-by-one loops using `end = start + size - 1`, scratch clearing before scratch allocation, access-counter WA thresholds, deferred removal after device offline, 64K VRAM alignment, VF base shifts, and PTE VFID validation. Test signals include KUnit GGTT init, GuC boot allocations, display inherited framebuffer mapping, BO insert/remove stress, suspend/resume remap, GGTT TLB invalidation, SR-IOV save/load/assign, hole reporting, and error-injection on init/insert paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ggtt.c -->
