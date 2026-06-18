<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ttm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ttm.h

## Purpose
`radeon_ttm.h` is the private header for Radeon TTM initialization and teardown. It keeps the public surface of `radeon_ttm.c` small for other driver components.

## Important APIs, types, and functions
The header forward-declares `struct radeon_device` and declares `radeon_ttm_init(struct radeon_device *rdev)` and `radeon_ttm_fini(struct radeon_device *rdev)`.

## Control flow
There is no runtime control flow. The declarations are consumed by device initialization and teardown paths so ASIC bring-up code can initialize BO/TTM memory management and later finalize it in reverse order.

## State, dependencies, and integration points
The header owns no state. The declared functions manage `rdev->mman`, TTM resource managers, stolen VGA memory, debugfs files, and GART cleanup from the implementation file. It is integrated with Radeon ASIC init/fini paths such as RS400/RS600 and later chips through the broader BO initialization layer.

## Risks and test signals
Risks are minimal but include prototype drift or missing includes causing build failures. Runtime signals come indirectly from successful Radeon memory-manager initialization, BO creation, GART operation, and clean teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ttm.h -->
