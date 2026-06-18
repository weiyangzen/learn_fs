# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v7_0.h

## Purpose
`hdp_v7_0.h` declares the HDP 7.0 function table.

## Important APIs, Types, And Functions
It includes `soc15_common.h` and exports `extern const struct amdgpu_hdp_funcs hdp_v7_0_funcs;`.

## Control Flow, State, Integration, And Risks
There is no code or state. The header supports AMDGPU IP setup by exposing the HDP 7.0 callback table. Build/link coverage catches declaration mismatches; hardware probe and HDP flush/clock-gating callback dispatch validate integration.
