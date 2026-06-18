# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_baco.c

## Purpose

This file implements Vega12 BACO state transitions for the PowerPlay hwmgr using SOC15 BACO command tables and an SMC fallback for entering BACO.

## Important APIs, Types, and Functions

The exported function is `vega12_baco_set_state(struct pp_hwmgr *hwmgr, enum BACO_STATE state)`. Static `soc15_baco_cmd_entry` arrays describe the hardware sequences: `pre_baco_tbl` disables doorbell monitoring/framebuffer and masks reset interrupts, `enter_baco_tbl` waits for SOC idle and powers/islands the BACO domain down, `exit_baco_tbl` reverses power/isolation/reset/clock controls and waits for exit, and `clean_baco_tbl` clears BIOS scratch registers.

## Control Flow, State, and Persistence

The function reads current state through `smu9_baco_get_state` and returns immediately if already at the requested target. For `BACO_STATE_IN`, it runs the pre-BACO table, sends `PPSMC_MSG_EnterBaco` only if that table reports success, then runs the hardware enter table and returns success if it reports success. For `BACO_STATE_OUT`, it sleeps 20 ms to satisfy regulator off/on timing, runs the exit table, then clears scratch registers. Failed or unsupported paths return `-EINVAL`.

## Dependencies and Integration Points

The file depends on Vega12 SOC15 register offsets and masks, `soc15_baco_program_registers`, SMU9 BACO state helpers, Vega12 PPSMC message IDs, and the shared hwmgr device context. It is used by the Vega12 power-management path that exposes BACO entry/exit.

## Risks and Test Signals

The command table interpreter's return convention is crucial: this code treats nonzero returns from `soc15_baco_program_registers` as success. Any convention mismatch in the shared helper would invert behavior. Hardware waits use masks and expected values that must match Vega12 register semantics. Tests should cover already-in-state returns, enter fallback failure, enter table wait timeout, exit timing, scratch cleanup, invalid target states, and full suspend/resume or runtime power-cycle sequences on BACO-capable Vega12 hardware.
