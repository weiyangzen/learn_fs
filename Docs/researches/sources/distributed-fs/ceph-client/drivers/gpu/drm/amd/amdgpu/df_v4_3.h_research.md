# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v4_3.h

## Purpose

This header declares the DF 4.3 callback table for AMDGPU Data Fabric dispatch.

## Important APIs and Types

- `extern const struct amdgpu_df_funcs df_v4_3_funcs`

## Control Flow and State

No runtime state is stored here. ASIC setup code uses the declaration to bind DF 4.3 RAS poison-mode behavior.

## Dependencies and Integration Points

It includes `soc15_common.h`, matching the SOC15 register-access style used in `df_v4_3.c`. Integration is through `adev->df.funcs`.

## Risks and Test Signals

Risks are declaration mismatch or missing selection in ASIC setup. Build coverage and a RAS poison-mode query smoke test are useful signals.
