# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v1_7.h

## Purpose

This header declares the DF 1.7 callback table and defines the MGCG mode enumeration used when programming `DfGlobalClkGater.MGCGMode`.

## Important APIs and Types

- `enum DF_V1_7_MGCG` defines disabled mode and enable delays of 0, 1, 15, 31, and 63 cycles.
- `extern const struct amdgpu_df_funcs df_v1_7_funcs` exposes the implementation table from `df_v1_7.c`.

## Control Flow and State

The header has no runtime state. Its enum constants are written into hardware by `df_v1_7_update_medium_grain_clock_gating()`, and the exported callback table is selected by ASIC setup code.

## Dependencies and Integration Points

It includes `soc15_common.h` for SOC15-oriented types/macros expected by the implementation. Integration is through AMDGPU DF function dispatch.

## Risks and Test Signals

Risks are limited to enum/register encoding mismatch and callback declaration drift. Build coverage plus clock-gating register readback on DF 1.7 hardware are the key signals.
