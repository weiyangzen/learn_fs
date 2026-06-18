# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v6_1.h

## Purpose

This header defines UMC v6.1 geometry, ECC counter constants, per-channel offsets for Vega20 and Arcturus, and public declarations for the v6.1 RAS object and channel index table.

## Important APIs, Types, and Functions

Important constants are `UMC_V6_1_HBM_MEMORY_CHANNEL_WIDTH`, `UMC_V6_1_CHANNEL_INSTANCE_NUM`, `UMC_V6_1_UMC_INSTANCE_NUM`, `UMC_V6_1_TOTAL_CHANNEL_NUM`, `UMC_V6_1_PER_CHANNEL_OFFSET_VG20`, `UMC_V6_1_PER_CHANNEL_OFFSET_ARCT`, and `UMC_V6_1_CE_CNT_INIT`.

## Control Flow

There is no executable flow. The constants drive v6.1 channel loops, channel-index lookups, counter setup, and ASIC-specific offset selection in `umc_v6_1.c`.

## State and Persistence Behavior

The header stores no state. Its declarations expose static topology and threshold policy to runtime code that mutates hardware counters and RAS records.

## Dependencies and Integration Points

It includes SOC15 and AMDGPU common definitions. It integrates with ASIC initialization and common UMC/RAS dispatch through `umc_v6_1_ras`.

## Risks

Topology constants must match the selected channel table and hardware register map. An incorrect CE initial value or per-channel offset makes counter deltas wrong or causes invalid register access.

## Test Signals

Compile coverage, correct channel count reporting, valid CE counter initialization, and correct channel ordering in retired-page reports are the main signals.
