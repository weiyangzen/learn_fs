# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v4_3.h

## Purpose
`nbio_v4_3.h` declares the NBIO 4.3 normal and SR-IOV operation tables plus RAS integration object.

## Important APIs, Types, And Functions
It declares `nbio_v4_3_hdp_flush_reg`, `nbio_v4_3_funcs`, `nbio_v4_3_sriov_funcs`, and `nbio_v4_3_ras`.

## Control Flow
The header has no code path. Device setup selects either the normal or SR-IOV function table according to virtualization mode, and RAS setup consumes `nbio_v4_3_ras` when supported.

## State And Persistence
No state is owned by the header; it exposes global objects defined in the C file.

## Dependencies And Integration Points
It depends on the common SOC15 NBIO/RAS types and is integrated by ASIC-specific common init logic.

## Risks
Normal and SR-IOV tables must remain distinct. If a caller only includes this header and chooses the wrong table, host/guest doorbell ownership can break.

## Test Signals
Compile/link coverage plus runtime selection of `nbio_v4_3_sriov_funcs` in VF mode are the key signals.
