# sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_disp.h

## Purpose

`zynqmp_disp.h` declares the ZynqMP display-controller API shared by the platform, DP bridge, and DRM/KMS layers.

## Important APIs, Types, And Functions

It defines maximum display dimensions, 44-bit DMA limit, layer IDs `VID` and `GFX`, and declarations for display enable/disable, clock setup, global alpha, format-list queries, layer format/update/enable/disable, probe, and remove.

## Control Flow

No runtime flow exists in the header.

## State And Persistence Behavior

No state is owned, but the declarations operate on opaque `struct zynqmp_disp` and `struct zynqmp_disp_layer` instances maintained by `zynqmp_disp.c`.

## Dependencies And Integration Points

It forward declares DRM format/plane state, platform device, and DPSUB types to keep dependencies small. `zynqmp_dpsub.h`, `zynqmp_dp.c`, and `zynqmp_kms.c` consume this interface.

## Risks And Test Signals

Risks are API drift and mismatch between max dimensions/DMA limit and hardware/KMS constraints. Build coverage and mode validation around the advertised limits are test signals.
