# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/fiji_baco.h

## Purpose
`fiji_baco.h` declares the Fiji-specific BACO transition entry point for PowerPlay SMU7 hardware-manager integration.

## Important API
`fiji_baco_set_state(struct pp_hwmgr *hwmgr, enum BACO_STATE state)` is the only exported declaration. The generic hwmgr callback table can use it to route `BACO_STATE_IN` and `BACO_STATE_OUT` requests to Fiji register sequences.

## Dependencies And Integration
The header includes `smu7_baco.h` for the BACO enum and shared SMU7 BACO support. It is included by `fiji_baco.c` and participates in function-pointer wiring from the SMU7 backend to `amd_powerplay.c` BACO callbacks.

## Risks And Test Signals
Risks are limited to prototype drift and incorrect inclusion in ASIC-specific wiring. Test signals are compile/link success, symbol availability for Fiji hwmgr setup, and correct dispatch when `get_asic_baco_capability`, `get_asic_baco_state`, and `set_asic_baco_state` are exercised on Fiji hardware.
