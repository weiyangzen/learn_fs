# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v3_6.h

## Purpose

This header declares the DF 3.6 callback table and MGCG register encodings used by the implementation. It also declares `df_v3_6_attr_groups`, although the implementation in this source set creates a device attribute directly.

## Important APIs and Types

- `enum DF_V3_6_MGCG` defines disabled mode and enable delays of 0, 1, 15, 31, and 63 cycles.
- `extern const struct attribute_group *df_v3_6_attr_groups[]`
- `extern const struct amdgpu_df_funcs df_v3_6_funcs`

## Control Flow and State

The header carries no mutable state. Its constants are consumed by DF 3.6 clock-gating programming, and its function table declaration lets ASIC setup select DF 3.6 operations.

## Dependencies and Integration Points

It includes `soc15_common.h` and participates in the AMDGPU DF dispatch interface. Consumers must also see Linux sysfs attribute types if they use the attr-group declaration.

## Risks and Test Signals

Risks include stale `df_v3_6_attr_groups` declarations if no matching definition exists in a build configuration, enum encoding drift, and callback table declaration mismatch. Build/link coverage and MGCG register readback are the primary signals.
