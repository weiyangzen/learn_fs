# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/df_v4_3.c

## Purpose

This file implements the DF 4.3 RAS poison-mode query callback. It determines whether Data Fabric poison handling is enabled by checking selected hardware assert mask fields.

## Important APIs and Functions

- `df_v4_3_query_ras_poison_mode()` reads `regDF_CS_UMC_AON0_HardwareAssertMaskLow` and `regDF_NCS_PG0_HardwareAssertMaskHigh`, extracts `HWAssertMsk0`, `HWAssertMsk1`, `HWAssertMsk28`, and `HWAssertMsk31`, and returns true only if all four are set.
- It returns false when all four are clear.
- It warns and returns false when the fields are inconsistent.
- `df_v4_3_funcs` exposes `.query_ras_poison_mode`.

## Control Flow and State

The callback is a read-only hardware query. It maintains no software state and persists nothing. Its only side effect is `dev_warn()` on inconsistent hardware configuration.

## Dependencies and Integration Points

The file depends on generated DF 4.3 register headers and AMDGPU SOC15 register macros. It integrates with AMDGPU RAS paths through the DF callback table.

## Risks and Test Signals

Risks include interpreting mixed hardware assert masks incorrectly, stale register names/fields, and treating inaccessible or transient fields as disabled poison mode. Tests should cover all-set, all-clear, and mixed mask states, plus RAS behavior that depends on poison-mode reporting.
