# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_sa_media.c

## Purpose
`intel_sa_media.c` sets up a standalone media GT instance that shares the primary GT MMIO mapping while using its own uncore object and physical address metadata.

## Important APIs, Types, And Functions
The single public function is `intel_sa_mediagt_setup(struct intel_gt *gt, phys_addr_t phys_addr, u32 gsi_offset)`. It allocates an `intel_uncore`, seeds `gsi_offset`, reuses the primary GT IRQ lock, calls common GT and uncore early init, reuses primary uncore registers, stores `gt->uncore` and `gt->phys_addr`, and caches the media GT at `i915->media_gt`.

## Control Flow
Setup allocates managed memory through DRM managed allocation. It initializes shared lock and early GT state before attaching the uncore register mapping. It validates that the primary uncore register mapping exists and warns if a media GT is already cached.

## State, Persistence, And Dependencies
State persists in the lifetime of the DRM device through managed allocation and `i915->media_gt`. The uncore shares register memory with the primary GT but carries a separate GSI offset. Dependencies include DRM managed allocation, GT common init, uncore early init, i915 device state, and the primary GT lock.

## Integration Points
Platform discovery code for standalone media calls this before normal GT initialization. Later GT paths use `i915->media_gt` for quick lookup and use the initialized uncore for media register access.

## Risks
Sharing the primary MMIO mapping means offset handling must be correct. The code assumes current platforms have only one media GT. A missing primary mapping returns `-EIO`; allocation failure returns `-ENOMEM`.

## Test Signals
Probe tests on media-GT platforms, MMIO access using GSI offsets, interrupt lock sharing, duplicate setup warnings, and boot logs around `i915->media_gt` initialization are useful signals.
