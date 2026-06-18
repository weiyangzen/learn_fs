# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_4.h

## Purpose
`nbio_v7_4.h` declares NBIO 7.4 operation, flush, and RAS objects.

## Important APIs, Types, And Functions
It exposes `nbio_v7_4_hdp_flush_reg`, `nbio_v7_4_funcs`, and mutable `nbio_v7_4_ras`.

## Control Flow
No executable logic exists. Common ASIC code uses this header to bind NBIO callbacks and RAS behavior for NBIO 7.4 hardware.

## State And Persistence
The header owns no state, but it exposes a mutable RAS object defined by the C file.

## Dependencies And Integration Points
It depends on `soc15_common.h` and integrates with common NBIO and RAS setup.

## Risks
Because RAS is mutable global state, object definition and initialization order matter. Any mismatch with the C file breaks link or runtime RAS registration.

## Test Signals
Build/link success, plus runtime registration of `pcie_bif` RAS block and NBIO 7.4 callbacks.
