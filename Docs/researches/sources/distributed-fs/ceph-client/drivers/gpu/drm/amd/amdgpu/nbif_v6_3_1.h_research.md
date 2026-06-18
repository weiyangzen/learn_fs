# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbif_v6_3_1.h

## Purpose
`nbif_v6_3_1.h` is the public declaration point for the NBIF 6.3.1 implementation.

## Important APIs, Types, And Functions
It includes `soc15_common.h` for `struct nbio_hdp_flush_reg`, `struct amdgpu_nbio_funcs`, and `struct amdgpu_nbio_ras`, then declares `nbif_v6_3_1_hdp_flush_reg`, `nbif_v6_3_1_funcs`, and `nbif_v6_3_1_ras`.

## Control Flow
The header has no runtime control flow. ASIC selection code includes it and assigns the exported tables to `adev->nbio` when NBIF 6.3.1 support is needed.

## State And Persistence
It owns no state; the declared objects live in the C file and are process-lifetime kernel data.

## Dependencies And Integration Points
The integration point is the SOC15/NBIO common abstraction used by `nv.c`, SOC21 common setup, and RAS initialization.

## Risks
Because the header exposes the RAS object as mutable `struct amdgpu_nbio_ras`, changes to the struct layout or object name must stay synchronized with the implementation and ASIC dispatch tables.

## Test Signals
Compile/link success confirms symbol names and types match. Runtime confirmation comes indirectly from selecting `nbif_v6_3_1_funcs` and observing working NBIO/RAS callbacks.
