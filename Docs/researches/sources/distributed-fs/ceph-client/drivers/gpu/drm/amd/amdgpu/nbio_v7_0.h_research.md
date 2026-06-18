# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_0.h

## Purpose
`nbio_v7_0.h` declares NBIO 7.0 HDP flush and function tables.

## Important APIs, Types, And Functions
It exposes `nbio_v7_0_hdp_flush_reg` and `nbio_v7_0_funcs`.

## Control Flow
No executable code exists. ASIC dispatch includes this header to select NBIO 7.0 behavior.

## State And Persistence
The header owns no state and only references constant implementation objects.

## Dependencies And Integration Points
It depends on `soc15_common.h` and integrates through the shared `amdgpu_nbio_funcs` contract.

## Risks
Consumers must not assume self-ring aperture support just because the function table contains a callback; in this version it is empty.

## Test Signals
Build success and runtime NBIO 7.0 table selection.
