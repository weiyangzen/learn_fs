# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v4_0.h

## Purpose
`hdp_v4_0.h` declares the HDP 4.x function table and RAS descriptor.

## Important APIs, Types, And Functions
It includes `soc15_common.h` and exports `hdp_v4_0_funcs` as `const struct amdgpu_hdp_funcs` plus `hdp_v4_0_ras` as `struct amdgpu_hdp_ras`.

## Control Flow, State, And Integration
There is no executable code. The declarations are consumed by GMC/IP setup, especially GMC v9 code, to assign HDP cache and RAS callbacks into `adev->hdp`.

## Risks And Test Signals
The risk is declaration mismatch with `hdp_v4_0.c` or missing includes for the function-table types. Build coverage and successful HDP function dispatch during GMC init are the relevant signals.
