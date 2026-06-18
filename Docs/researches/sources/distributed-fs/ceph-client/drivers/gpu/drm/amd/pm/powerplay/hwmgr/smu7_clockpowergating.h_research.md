# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_clockpowergating.h

## Purpose

This header declares SMU7 clock and power gating functions for use by SMU7 hwmgr code.

## Important APIs, Types, and Functions

It declares `smu7_powergate_vce()`, `smu7_powergate_uvd()`, `smu7_powergate_acp()`, `smu7_powergate_gfx()`, `smu7_disable_clock_power_gating()`, and `smu7_update_clock_gatings()`. The ACP declaration is not implemented in the paired `smu7_clockpowergating.c`, so its definition must come from another SMU7 translation unit or the build would fail when referenced.

## Control Flow and State

The header has no control flow or state. The functions it declares mutate `struct smu7_hwmgr` backend booleans and hardware/SMU state in the implementation.

## Dependencies and Integration

It includes `smu7_hwmgr.h`, which supplies `struct pp_hwmgr`, backend definitions, and required SMU7 context. The declarations are consumed by SMU7 hwmgr function-table setup and clock-gating update paths.

## Risks and Test Signals

The public API mixes void powergate functions with int-returning ACP, disable, update, and GFX functions, so UVD/VCE media powergate errors are not propagated to callers. The unpaired ACP declaration is a linkage risk if no other object supplies it. Compile coverage catches signature and symbol drift; runtime test signals are UVD/VCE/GFX/ACP power-gating transitions and clock-gating SMU message success.
