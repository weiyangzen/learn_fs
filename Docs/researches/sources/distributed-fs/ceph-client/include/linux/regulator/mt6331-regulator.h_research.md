# sources/distributed-fs/ceph-client/include/linux/regulator/mt6331-regulator.h

## Purpose

This header enumerates regulator IDs for the MediaTek MT6331 PMIC.

## Important APIs, Types, and Functions

The enum groups buck rails (`VDVFS11` through `VCORE2`, `VIO18`) and LDO rails including TCXO, audio, auxiliary, camera, memory, SIM, MIPI, vibrator, USB, SRAM, RTC, and digital rails, ending with `MT6331_ID_VREG_MAX`.

## Control Flow

The regulator driver uses IDs to index descriptors and register rails.

## State and Persistence Behavior

No runtime state is defined. Rail state is managed through PMIC registers and regulator core.

## Dependencies and Integration Points

The header is standalone and integrates with MT6331 regulator driver tables and DT supply names.

## Risks

Enum order is an ABI-like contract with driver arrays and bindings. Mislabeling buck vs LDO rails can expose wrong capabilities.

## Test Signals

Tests should validate descriptor coverage, supply lookup, and operation capabilities for each ID.
