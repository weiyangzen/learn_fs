# sources/distributed-fs/ceph-client/include/linux/regulator/mt6357-regulator.h

## Purpose

This header enumerates regulator IDs for the MediaTek MT6357 PMIC.

## Important APIs, Types, and Functions

The enum lists buck rails (`VCORE`, `VMODEM`, `VPA`, `VPROC`, `VS1`) and many LDO rails for audio, camera, connectivity, DRAM, eFuse, eMMC, front-end, vibrator, IO, memory card, RF, SIM, SRAM, USB, and XO domains, ending with `MT6357_ID_RG_MAX`. `MT6357_MAX_REGULATOR` aliases the max.

## Control Flow

The driver uses these IDs to index descriptors and register all PMIC rails.

## State and Persistence Behavior

No state is defined here. Runtime state is in PMIC registers and core regulator objects.

## Dependencies and Integration Points

The header is standalone and integrates with MT6357 PMIC regulator tables and DT bindings.

## Risks

ID ordering and max value must stay aligned with descriptors. Similar connectivity rails (`VCN33_BT` vs `VCN33_WIFI`) must not be swapped.

## Test Signals

Tests should verify descriptor coverage, supply names, and capabilities for every ID.
