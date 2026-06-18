# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/Makefile

## Purpose
Lists the object files linked into the etnaviv DRM driver and connects them to `CONFIG_DRM_ETNAVIV`.

## Important APIs, Types, and Functions
The `etnaviv-y` aggregate includes buffer, command parser, command buffer, driver, dump, GEM/PRIME/submit, GPU, hardware DB, IOMMU v1/v2/MMU, perfmon, flop reset, and scheduler objects. `obj-$(CONFIG_DRM_ETNAVIV) += etnaviv.o` emits the final built-in or module object.

## Control Flow
Kbuild compiles all listed objects into the aggregate driver when the Kconfig symbol is enabled.

## State and Persistence
No runtime state; this is build metadata. Ordering matters only insofar as Kbuild aggregates the listed objects into one module.

## Dependencies and Integration Points
Integrates this subset with adjacent etnaviv files not in this work item, including GPU, scheduler, MMU, submit, hardware DB, and perfmon implementations.

## Risks
Missing an object can produce unresolved symbols or disabled functionality. Adding generated headers alone is insufficient without corresponding object inclusion.

## Test Signals
Run kernel build targets for built-in and module configurations, and inspect `modinfo etnaviv`/link errors for aggregate consistency.
