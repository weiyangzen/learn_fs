# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/Makefile

## Purpose

`shmobile/Makefile` defines the object composition for the legacy SH Mobile DRM module.

## Important APIs, Types, and Functions

`shmob-drm-y` links `shmob_drm_crtc.o`, `shmob_drm_drv.o`, `shmob_drm_kms.o`, and `shmob_drm_plane.o`. `obj-$(CONFIG_DRM_SHMOBILE)` adds the aggregate object to the build.

## Control Flow

Kbuild includes the module when `DRM_SHMOBILE` is enabled.

## State and Persistence Behavior

No runtime state exists.

## Dependencies and Integration Points

It integrates with the local Kconfig and Kbuild.

## Risks and Edge Cases

The plane implementation is outside this work item but is required for link completeness.

## Test Signals

Full module link tests confirm all listed objects and symbols resolve.
