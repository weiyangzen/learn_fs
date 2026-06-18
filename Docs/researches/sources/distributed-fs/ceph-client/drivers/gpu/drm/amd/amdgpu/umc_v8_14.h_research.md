# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v8_14.h

## Purpose

This header defines UMC v8.14 channel geometry, register spacing, ECC counter constants, and the exported RAS object declaration.

## Important APIs, Types, and Functions

Important constants include `UMC_V8_14_CHANNEL_INSTANCE_NUM`, `UMC_V8_14_UMC_INSTANCE_NUM(adev)`, `UMC_V8_14_TOTAL_CHANNEL_NUM(adev)`, `UMC_V8_14_PER_CHANNEL_OFFSET`, `UMC_V8_14_INST_DIST`, `UMC_V8_14_CE_CNT_MAX`, `UMC_V8_14_CE_INT_THRESHOLD`, and `UMC_V8_14_CE_CNT_INIT`.

## Control Flow

There is no executable flow. The macros guide channel enumeration, offset computation, and counter baseline calculation in `umc_v8_14.c`.

## State and Persistence Behavior

No state is stored. Some macros read runtime topology from `adev`, so callers need initialized UMC/GMC fields.

## Dependencies and Integration Points

It includes SOC15 and AMDGPU headers and integrates with AMDGPU generation dispatch through `umc_v8_14_ras`.

## Risks

`UMC_V8_14_UMC_INSTANCE_NUM(adev)` maps to `adev->umc.node_inst_num`, which is unusual compared with several other generations and must match setup code. Wrong topology values lead to incomplete or invalid counter scans.

## Test Signals

Compile coverage, correct total-channel count, successful v8.14 RAS registration, and valid Gecc counter reads during RAS queries are the main signals.
