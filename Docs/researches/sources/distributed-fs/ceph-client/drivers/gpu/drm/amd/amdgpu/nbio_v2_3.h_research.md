# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v2_3.h

## Purpose
`nbio_v2_3.h` declares the NBIO 2.3 register flush table and callback table.

## Important APIs, Types, And Functions
It includes `soc15_common.h` and declares `nbio_v2_3_hdp_flush_reg` plus `nbio_v2_3_funcs`.

## Control Flow
There is no executable flow; ASIC-common code includes this header to bind NBIO 2.3 operations into `adev->nbio`.

## State And Persistence
No local state exists. The declarations refer to constant global tables in `nbio_v2_3.c`.

## Dependencies And Integration Points
The header is used by `nv.c`, which includes it directly and relies on the generic NBIO function contract.

## Risks
The minimal declaration surface is stable, but any callback added in the C file remains invisible unless it is reachable through `struct amdgpu_nbio_funcs`.

## Test Signals
Build/link success and successful Navi common early init are the relevant signals.
