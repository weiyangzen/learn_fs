<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/Makefile

## Purpose

`bridge/Makefile` maps DRM bridge Kconfig symbols to bridge driver objects and descends into bridge-family subdirectories.

## Important APIs, Types, And Targets

- Direct object mappings for many bridge drivers such as `aux-bridge.o`, `chipone-icn6211.o`, `display-connector.o`, `inno-hdmi.o`, `lontium-*`, `sii902x.o`, `tc358*`, TI bridge drivers, and others.
- Composite `tda998x-y := tda998x_drv.o`.
- Subdirectory descent: `adv7511/` under `CONFIG_DRM_I2C_ADV7511`, and unconditional `analogix/`, `cadence/`, `imx/`, and `synopsys/` directories.

## Control Flow

There is no runtime flow. Kbuild uses `obj-$(CONFIG_*)` variables to include objects and subdirectories in the kernel build.

## State And Persistence Behavior

The Makefile only affects build outputs. It stores no runtime state.

## Dependencies And Integration Points

It integrates with the Kconfig symbols in `bridge/Kconfig` and family Kconfig files. The unconditional `obj-y` subdirectories rely on their internal Makefiles to gate individual objects.

## Risks And Edge Cases

Kconfig/Makefile symbol mismatches lead to enabled drivers not building or dead objects that never build. Composite module variables must match the target object name. Unconditional subdir traversal increases the need for correct gating inside subdirectories.

## Test Signals

Build tests for each bridge symbol, `make drivers/gpu/drm/bridge/`, allmodconfig, and checking that Kconfig help/module names match produced objects validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/Makefile -->
