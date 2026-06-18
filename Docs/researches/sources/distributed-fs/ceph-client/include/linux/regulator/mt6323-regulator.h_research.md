# sources/distributed-fs/ceph-client/include/linux/regulator/mt6323-regulator.h

## Purpose

This header enumerates regulator IDs for the MediaTek MT6323 PMIC.

## Important APIs, Types, and Functions

The enum lists buck/LDO rails such as `VPROC`, `VSYS`, `VPA`, `VTCXO`, connectivity/camera/IO/USB/memory/SIM/vibrator/RF rails, ending with `MT6323_ID_RG_MAX`. `MT6323_MAX_REGULATOR` aliases that max value.

## Control Flow

The driver uses the enum values to index descriptor tables and expose named regulators to the core.

## State and Persistence Behavior

No state is defined. Runtime rail configuration is in PMIC registers and regulator core objects.

## Dependencies and Integration Points

The header is standalone and integrates with MT6323 PMIC regulator descriptors and consumer mappings.

## Risks

Changing enum order breaks descriptor and DT supply compatibility. Sparse explicit value `MT6323_ID_VIO28 = 9` must be preserved.

## Test Signals

Tests should ensure every ID maps to a descriptor, max count matches arrays, and all DT supplies resolve to expected rails.
