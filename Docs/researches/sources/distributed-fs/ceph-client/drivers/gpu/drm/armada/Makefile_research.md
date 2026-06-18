# sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/Makefile

## Purpose

`armada/Makefile` defines how the Armada DRM driver objects are built and linked into `armada.o`.

## Important APIs, Types, And Functions

The base `armada-y` object list includes `armada_crtc.o`, `armada_drv.o`, `armada_fb.o`, `armada_gem.o`, `armada_overlay.o`, `armada_plane.o`, `armada_trace.o`, and `armada_510.o`. Conditional additions are `armada_debugfs.o` for `CONFIG_DEBUG_FS` and `armada_fbdev.o` for `CONFIG_DRM_FBDEV_EMULATION`. `obj-$(CONFIG_DRM_ARMADA) := armada.o` connects the aggregate to Kconfig.

## Control Flow

There is no runtime control flow. The build system concatenates the object list into one module/built-in object according to the selected kernel configuration.

## State And Persistence Behavior

No runtime state is stored. Build-time state controls whether debugfs and fbdev support are present in the final driver.

## Dependencies And Integration Points

The Makefile integrates with `Kconfig`, the DRM subsystem build, and local Armada source files. The inclusion of `armada_trace.o` ensures tracepoints are linked when the driver is built.

## Risks And Edge Cases

Object ordering can matter for init/exit references and tracepoint definitions. Conditional object omissions must match preprocessor guards in headers and driver ops. Adding a new local file without updating `armada-y` silently excludes it from the driver.

## Test Signals

Build tests with debugfs and fbdev combinations, module link checks, unresolved symbol scans, and verifying `modinfo`/module contents for expected objects are useful validation signals.
