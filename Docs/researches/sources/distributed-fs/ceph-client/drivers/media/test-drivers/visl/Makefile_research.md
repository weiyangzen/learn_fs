# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/Makefile

## Purpose
`visl/Makefile` defines the object composition for the VISL virtual stateless decoder module.

## Important APIs, Types, and Functions
`visl-y` includes `visl-core.o`, `visl-video.o`, `visl-dec.o`, and `visl-trace-points.o`. When `CONFIG_VISL_DEBUGFS=y`, it adds `visl-debugfs.o`. `obj-$(CONFIG_VIDEO_VISL) += visl.o` connects the aggregate to Kconfig.

## Control Flow
Kbuild links the listed objects into `visl.o` when `VIDEO_VISL` is enabled, conditionally including debugfs support. Runtime module entry points are provided by the VISL core object.

## State and Persistence
The file has no runtime state. It controls build-time inclusion only.

## Dependencies and Integration Points
The object list must match VISL implementation symbol dependencies. Trace points are always included; debugfs is conditional on Kconfig.

## Risks and Edge Cases
Adding codec support or diagnostics requires updating this Makefile with new objects. A mismatch between `CONFIG_VISL_DEBUGFS` and debugfs code references would cause link failures.

## Test Signals
Build matrix coverage for debugfs enabled and disabled should catch missing objects. Module load tests should confirm tracepoints are present and debugfs support appears only under the configured option.
