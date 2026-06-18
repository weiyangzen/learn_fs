# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v8_7.h

## Purpose

This header defines UMC v8.7 geometry, counter constants, per-channel offset, and public declarations for the v8.7 RAS object and channel index table.

## Important APIs, Types, and Functions

Important constants are `UMC_V8_7_HBM_MEMORY_CHANNEL_WIDTH`, `UMC_V8_7_CHANNEL_INSTANCE_NUM`, `UMC_V8_7_UMC_INSTANCE_NUM`, `UMC_V8_7_TOTAL_CHANNEL_NUM`, `UMC_V8_7_PER_CHANNEL_OFFSET_SIENNA`, and `UMC_V8_7_CE_CNT_INIT`.

## Control Flow

No executable flow is present. The constants feed v8.7 channel iteration, offset calculation, counter setup, and channel-index conversion in `umc_v8_7.c`.

## State and Persistence Behavior

The header stores no state. It exposes topology constants used to interpret hardware state.

## Dependencies and Integration Points

It includes SOC15 and AMDGPU headers and is consumed by generation setup and the v8.7 RAS implementation.

## Risks

The total channel count and Sienna offset must match platform setup. Wrong table dimensions would break flattened channel-index lookups.

## Test Signals

Signals include compile-time table dimension checks, successful v8.7 RAS binding, correct channel count, and stable Gecc counter queries.
