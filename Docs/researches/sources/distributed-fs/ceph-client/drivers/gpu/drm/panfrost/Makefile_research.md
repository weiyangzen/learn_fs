# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/Makefile

## Purpose
This Makefile defines the object composition for the Panfrost DRM driver.

## Important APIs, Types, and Functions
It builds `panfrost.o` from driver, device, devfreq, GEM, shrinker, GPU, job manager, MMU, performance counter, and dump objects. `obj-$(CONFIG_DRM_PANFROST)` links the aggregate when the Kconfig option is enabled.

## Control Flow
There is no runtime control flow. The link order places the platform/DRM driver and subsystem implementations into one module or built-in object.

## State and Persistence Behavior
The file controls build artifacts only. Any source omitted here is not part of the final Panfrost driver, and any added object becomes part of the module ABI surface indirectly through internal symbols.

## Dependencies and Integration Points
It integrates the Panfrost submodules with Kbuild and the `CONFIG_DRM_PANFROST` selection path from Kconfig.

## Risks
Forgetting to list a new implementation file causes unresolved references or missing functionality. Removing an object can disable required initialization stages such as MMU, scheduler, shrinker, perfcnt, or devcoredump.

## Test Signals
Signals are clean module and built-in builds, modpost without unresolved symbols, and runtime probe confirming all subsystem init functions linked from this object list are present.
