# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v5_2.h

## Purpose
`hdp_v5_2.h` declares the HDP 5.2 function table.

## Important APIs, Types, And Functions
The only exported symbol is `extern const struct amdgpu_hdp_funcs hdp_v5_2_funcs;`, with `soc15_common.h` included for AMDGPU/SOC15 type context.

## Control Flow, State, Integration, And Risks
There is no control flow or local state. The header is consumed by ASIC/IP setup code that assigns HDP 5.2 callbacks. Build/link tests catch symbol mismatch; runtime signals are successful HDP flush and clock-gating callback dispatch.
