# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v6_1.h

## Purpose
`nbio_v6_1.h` declares the NBIO 6.1 callback table and HDP flush table.

## Important APIs, Types, And Functions
It exposes `nbio_v6_1_hdp_flush_reg` and `nbio_v6_1_funcs`.

## Control Flow
No runtime flow exists in the header. SOC15 common code includes it to install NBIO 6.1 callbacks for matching ASICs.

## State And Persistence
The header owns no mutable state. The declared objects are constant global tables in `nbio_v6_1.c`.

## Dependencies And Integration Points
The only dependency is `soc15_common.h`, which supplies the shared NBIO table structures.

## Risks
Any consumer needing RAS or VCN-specific NBIO 6.1 hooks will not find them here; the implementation only advertises the base function table.

## Test Signals
Compile/link success and a device selecting `nbio_v6_1_funcs` during common init.
