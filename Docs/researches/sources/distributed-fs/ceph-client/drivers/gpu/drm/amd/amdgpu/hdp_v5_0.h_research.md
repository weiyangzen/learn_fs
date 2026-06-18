# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v5_0.h

## Purpose
`hdp_v5_0.h` declares the HDP 5.0 function table for AMDGPU IP setup.

## Important APIs, Types, And Functions
It includes `soc15_common.h` and exports `extern const struct amdgpu_hdp_funcs hdp_v5_0_funcs;`.

## Control Flow, State, Dependencies, And Risks
The header has no code or state. It depends on the HDP function-table type being visible through included headers. Build/link coverage catches declaration drift, and runtime coverage is successful assignment and use of the HDP 5.0 callbacks.
