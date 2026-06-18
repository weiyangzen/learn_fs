<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/Kbuild

## Purpose
This build fragment lists the NV50-and-newer Nouveau display implementation objects and their debugfs-conditional CRC components.

## Important APIs, Types, and Functions
It adds display core, LUT, core channel classes, CRC, DAC/PIOR/SOR output classes, head classes, WIMM/window/base/cursor/overlay/OIMM objects, and generation-specific class files to `nouveau-y` or `nouveau-$(CONFIG_DEBUG_FS)`.

## Control Flow
There is no runtime flow. Kbuild composes the driver objects according to unconditional Nouveau display support and debugfs configuration.

## State and Persistence Behavior
No runtime state is stored. The file determines which class implementations are linked for runtime class selection by `nvif_mclass`.

## Dependencies and Integration Points
It integrates with the parent Nouveau build and class-selection code in `core.c`, `base.c`, and related display modules.

## Risks
Missing an object breaks class selection or unresolved symbols for generation-specific function tables. Debugfs CRC objects must stay conditional with CRC references guarded by `CONFIG_DEBUG_FS`.

## Test Signals
Build with debugfs enabled and disabled, across module and built-in configs. Runtime class selection on NV50 through modern GPUs validates that all required class files are linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/Kbuild -->
