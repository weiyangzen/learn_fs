# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_11.h

## Purpose
`nbio_v7_11.h` declares NBIO 7.11 exported tables.

## Important APIs, Types, And Functions
It declares `nbio_v7_11_hdp_flush_reg`, `nbio_v7_11_funcs`, and `nbio_v7_11_ras_funcs`.

## Control Flow
The header has no runtime flow. ASIC code includes it to access NBIO 7.11 callbacks.

## State And Persistence
No state is defined here; all objects are external.

## Dependencies And Integration Points
It depends on `soc15_common.h` and the common NBIO/RAS type definitions.

## Risks
The declaration of `nbio_v7_11_ras_funcs` is not matched by a visible definition in `nbio_v7_11.c` in this snapshot. That may be an unused stale declaration or a cross-file symbol expectation that needs link-time verification.

## Test Signals
Compile/link is the primary signal, especially with configs that reference NBIO 7.11 RAS functionality.
