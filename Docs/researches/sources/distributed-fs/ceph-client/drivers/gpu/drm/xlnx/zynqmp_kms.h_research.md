# sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_kms.h

## Purpose

`zynqmp_kms.h` declares the DRM/KMS state and entry points for ZynqMP DPSUB DMA-mode display.

## Important APIs, Types, And Functions

It defines `struct zynqmp_dpsub_drm` with backpointer, DRM device, two planes, one CRTC, and one encoder. It declares `zynqmp_dpsub_drm_handle_vblank()`, `zynqmp_dpsub_drm_init()`, and `zynqmp_dpsub_drm_cleanup()`.

## Control Flow

No runtime flow. It is a shared declaration boundary.

## State And Persistence Behavior

The struct persists for the DRM device lifetime and owns DRM objects used by KMS.

## Dependencies And Integration Points

It includes DRM object headers and `zynqmp_dpsub.h`, and is consumed by platform, DP IRQ, and KMS implementation files.

## Risks And Test Signals

Risks are object lifetime mismatch and declaration drift. DRM init/cleanup and vblank IRQ paths validate it.
