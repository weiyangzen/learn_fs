# sources/distributed-fs/ceph-client/include/linux/regulator/mt6397-regulator.h

## Purpose

This header enumerates regulator IDs and chip ID constants for the MediaTek MT6397 PMIC.

## Important APIs, Types, and Functions

The enum lists CPU/SRAM/core/GPU/DRAM/IO/TCXO/camera/USB/memory-card/general-purpose/vibrator rails, ending with `MT6397_ID_RG_MAX`. `MT6397_MAX_REGULATOR` aliases the max. Chip ID constants are `MT6397_REGULATOR_ID97` and `MT6397_REGULATOR_ID91`.

## Control Flow

The driver indexes descriptor tables by enum ID and may use chip ID constants to select variant behavior.

## State and Persistence Behavior

No state is defined in the header. Hardware and regulator core manage runtime rail state.

## Dependencies and Integration Points

It is standalone and integrates with MT6397 PMIC regulator descriptors and board/DT supply mappings.

## Risks

Explicit `MT6397_ID_VIO18 = 7` and subsequent ordering must match descriptor arrays. Chip ID selection must not confuse MT6397 variants.

## Test Signals

Tests should cover chip ID detection, descriptor count, rail registration, and supply mapping.
