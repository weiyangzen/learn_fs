# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v6_7.h

## Purpose

This header defines UMC v6.7 RAS constants, channel geometry, bad-page expansion dimensions, PA bit positions, channel-hash helpers, channel index table exports, and the address conversion function prototype.

## Important APIs, Types, and Functions

Key definitions include `UMC_V6_7_INST_DIST`, `UMC_V6_7_UMC_INSTANCE_NUM`, `UMC_V6_7_CHANNEL_INSTANCE_NUM`, `UMC_V6_7_NA_MAP_PA_NUM`, `UMC_V6_7_BAD_PAGE_NUM_PER_CHANNEL`, `UMC_V6_7_PA_CH4_BIT`, `UMC_V6_7_PA_C2_BIT`, `UMC_V6_7_PA_R14_BIT`, `CHANNEL_HASH`, and `SET_CHANNEL_HASH`.

## Control Flow

There is no executable flow, but the `SET_CHANNEL_HASH` macro performs a small address rewrite sequence when used by the implementation.

## State and Persistence Behavior

The header stores no state. The hash macro reads `adev->df.hash_status` from the caller context and mutates the passed physical-address lvalue.

## Dependencies and Integration Points

It includes SOC15 and AMDGPU definitions and assumes callers have an `adev` identifier in scope for `CHANNEL_HASH`. It integrates with UMC RAS address conversion and channel-index setup.

## Risks

`CHANNEL_HASH` is not a pure function because it references `adev` implicitly. Incorrect bit constants or hash masks directly affect retired-page addresses.

## Test Signals

Signals are correct macro expansion at compile time, correct bad-page candidate count, channel hash behavior under 64K/2M/1G hash settings, and valid channel table selection.
