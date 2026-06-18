# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h

## Purpose

This header aggregates SMU10-related register include files for the hwmgr layer and defines one display PHY status index not provided by the generated register headers.

## Important APIs, Types, and Functions

There are no functions or types. The file includes MP 10.0, NBIO 7.0, and THM 10.0 default/offset/mask headers and defines `ixDDI_PHY_GEN_STATUS` as `0x3FCE8`.

## Control Flow and State

There is no control flow or runtime state. Its effect is compile-time availability of register offsets and masks.

## Dependencies and Integration

It is included by `smu10_hwmgr.h`, which makes SOC register definitions available to SMU10 hwmgr code. The included generated headers back direct register reads such as temperature and GFXOFF status paths in `smu10_hwmgr.c`.

## Risks and Test Signals

The main risk is register-generation drift or a stale manually defined index. Compile failures catch missing generated headers. Runtime signals are successful register reads for thermal and power-state functions on SMU10 hardware.
