# sources/distributed-fs/ceph-client/include/linux/regulator/mt6380-regulator.h

## Purpose

This header enumerates regulator IDs for the MediaTek MT6380 PMIC.

## Important APIs, Types, and Functions

The enum lists `MT6380_ID_VCPU`, `VCORE`, `VRF`, `VMLDO`, `VALDO`, `VPHYLDO`, `VDDRLDO`, `VTLDO`, ending with `MT6380_ID_RG_MAX`. `MT6380_MAX_REGULATOR` aliases the max value.

## Control Flow

The regulator driver uses IDs to index descriptors and register rails.

## State and Persistence Behavior

No state is declared. Runtime state resides in PMIC registers and regulator core.

## Dependencies and Integration Points

The header is standalone and integrates with MT6380 regulator driver tables.

## Risks

The include guard uses lowercase `mt6380` in the macro name; changing it can affect duplicate-include behavior. ID order must match descriptors and bindings.

## Test Signals

Tests should validate descriptor coverage, max count, and consumer supply mapping.
