# sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_dpsub.h

## Purpose

`zynqmp_dpsub.h` defines the shared subsystem object and topology enums for the ZynqMP DP subsystem.

## Important APIs, Types, And Functions

It defines `ZYNQMP_DPSUB_NUM_LAYERS`, port enum entries for live video/gfx/audio and output video/audio/DP, output format enum values, `struct zynqmp_dpsub`, optional audio init/uninit prototypes or stubs, and `zynqmp_dpsub_release()`.

## Control Flow

No direct runtime flow. Audio stubs compile to no-ops when audio support is disabled.

## State And Persistence Behavior

`struct zynqmp_dpsub` persists for the platform device lifetime or DRM-managed lifetime and owns pointers to clocks, DRM bridge/display/DP/audio components, layer handles, connected-port flags, DMA mode flag, and DMA alignment.

## Dependencies And Integration Points

It is the central type shared by platform, display, DP, KMS, and audio files. It forward declares most component types to reduce include dependencies.

## Risks And Test Signals

Risks include inconsistent interpretation of `dma_enabled`, connected port bits, and layer indices across modules. Build coverage and probe tests in DMA vs live mode validate the contract.
