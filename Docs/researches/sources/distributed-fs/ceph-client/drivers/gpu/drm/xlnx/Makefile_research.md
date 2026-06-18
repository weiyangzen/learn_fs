# sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/Makefile

## Purpose

The Makefile builds the ZynqMP DisplayPort Subsystem DRM module.

## Important APIs, Types, And Functions

`zynqmp-dpsub-y` includes `zynqmp_disp.o`, `zynqmp_dpsub.o`, `zynqmp_dp.o`, and `zynqmp_kms.o`; `zynqmp_dp_audio.o` is added when audio support is enabled.

## Control Flow

No runtime flow. Kbuild links the module when `CONFIG_DRM_ZYNQMP_DPSUB` is selected.

## State And Persistence Behavior

No runtime state.

## Dependencies And Integration Points

The object list maps to display-controller register programming, platform lifecycle, DP bridge/link handling, DRM/KMS integration, and optional ASoC audio.

## Risks And Test Signals

Risk is missing optional object linkage. Build with audio enabled and disabled validates the Makefile.
