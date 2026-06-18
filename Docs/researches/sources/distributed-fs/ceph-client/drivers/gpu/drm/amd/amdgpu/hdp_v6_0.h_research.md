# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v6_0.h

## Purpose
`hdp_v6_0.h` declares the HDP 6.0 callback table.

## Important APIs, Types, And Functions
It includes `soc15_common.h` and exports `extern const struct amdgpu_hdp_funcs hdp_v6_0_funcs;`.

## Control Flow, State, Integration, And Risks
The file has no executable control flow or state. It participates in AMDGPU IP wiring by making the function table visible to ASIC setup. Build/link coverage catches declaration drift; runtime validation is callback use on HDP 6.x hardware.
