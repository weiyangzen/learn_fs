# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_2.h

## Purpose
`nbio_v7_2.h` exposes NBIO 7.2 flush and function tables.

## Important APIs, Types, And Functions
It declares `nbio_v7_2_hdp_flush_reg` and `nbio_v7_2_funcs`.

## Control Flow
No runtime behavior exists. ASIC selection uses the declarations to install the NBIO 7.2 implementation.

## State And Persistence
The header has no state. The actual constant tables are in `nbio_v7_2.c`.

## Dependencies And Integration Points
It depends on `soc15_common.h` and the shared NBIO callback ABI.

## Risks
The header does not communicate the IP-version-specific behavior inside the C file; consumers must select it only for compatible hardware.

## Test Signals
Compile/link success and matching hardware reaching common init with `nbio_v7_2_funcs`.
