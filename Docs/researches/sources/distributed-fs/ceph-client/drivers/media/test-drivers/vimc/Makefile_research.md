# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/Makefile

## Purpose
`vimc/Makefile` defines the object composition for the VIMC kernel module.

## Important APIs, Types, and Functions
`vimc-y` aggregates `vimc-core.o`, `vimc-common.o`, `vimc-streamer.o`, `vimc-capture.o`, `vimc-debayer.o`, `vimc-scaler.o`, `vimc-sensor.o`, and `vimc-lens.o`. `obj-$(CONFIG_VIDEO_VIMC) += vimc.o` connects the aggregate to the Kconfig option.

## Control Flow
When `CONFIG_VIDEO_VIMC` is enabled, kbuild links the listed objects into one `vimc` module or built-in object. `vimc-core.o` owns module init/exit; the remaining objects supply entity type callbacks and shared helpers referenced by the core topology.

## State and Persistence
The file has no runtime state. Build state is derived from Kconfig.

## Dependencies and Integration Points
The object list must stay synchronized with declarations in `vimc-common.h` and entity references in `vimc-core.c`. Removing one entity object without changing topology would leave unresolved symbols such as `vimc_sensor_type`.

## Risks and Edge Cases
Adding a new entity type requires updating this file, the topology config, and common declarations together. Object ordering is generally not semantically important after linking, but missing objects break module linkage.

## Test Signals
Build VIMC as module and built-in to catch missing object references. `modinfo` and load tests should show one `vimc` module containing all entity implementations.
