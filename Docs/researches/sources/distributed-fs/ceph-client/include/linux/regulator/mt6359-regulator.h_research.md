# sources/distributed-fs/ceph-client/include/linux/regulator/mt6359-regulator.h

## Purpose

This header enumerates regulator IDs for the MediaTek MT6359 PMIC.

## Important APIs, Types, and Functions

The enum covers system bucks (`VS1`, GPU, modem, VPU, core, VPA, processors), LDO rails for audio, SIM, vibrator, RF, USB, SRAM, IO, camera, connectivity, eFuse, XO, UFS, VM, battery backup, and sensor-hub aliases. It ends with `MT6359_ID_RG_MAX`; `MT6359_MAX_REGULATOR` aliases that count.

## Control Flow

The driver indexes descriptor arrays with these IDs and uses aliases such as `MT6359_ID_VGPU11_SSHUB = MT6359_ID_VCORE_SSHUB` where hardware shares control.

## State and Persistence Behavior

No state is defined here. Runtime behavior is in PMIC registers and regulator core.

## Dependencies and Integration Points

It is standalone and integrates with MT6359 bindings, descriptor tables, and consumer supply names.

## Risks

Aliased IDs and explicit numbering can break array assumptions. Connectivity BT/WIFI rails and SRAM processor rails require accurate mapping to avoid powering the wrong domain.

## Test Signals

Tests should validate descriptor coverage, alias handling, DT supply resolution, and per-rail capabilities.
