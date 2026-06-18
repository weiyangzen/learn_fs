# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_baco.c

## Purpose
This file implements the Vega10 BACO transition sequence for the PowerPlay hardware manager. BACO is driven through ordered register command tables for pre-entry, entry, exit, and cleanup. The exported function `vega10_baco_set_state()` compares the current BACO state with the requested state and then runs either the hardware register scripts or the SMC entry message needed to cross the boundary.

## Important APIs, Types, and Functions
- `vega10_baco_set_state(struct pp_hwmgr *hwmgr, enum BACO_STATE state)`: exported transition entry point used by `vega10_hwmgr.c` through `.set_asic_baco_state`.
- `pre_baco_tbl`: NBIF setup before entering BACO. It enables doorbell monitoring, disables framebuffer access, bypasses BACO D-state behavior, and masks reset interrupts.
- `enter_baco_tbl`: ordered THM/NBIF register operations to wait for SOC idleness, assert BACO enable and isolation bits, power off, delay, assert reset, and wait for BACO mode.
- `exit_baco_tbl`: reverse transition that powers on, clears isolation and reset controls, asserts and waits for BACO exit, clears fences and dummy/LCLK/BACO enable bits, then waits until BACO mode clears.
- `clean_baco_tbl`: zeroes BIOS scratch registers after successful exit.
- `soc15_baco_cmd_entry`: command-table type, used with `CMD_READMODIFYWRITE`, `CMD_WRITE`, `CMD_WAITFOR`, and `CMD_DELAY_MS`.

## Control Flow
`vega10_baco_set_state()` first calls `smu9_baco_get_state()` and returns success if the device is already in the requested state. For `BACO_STATE_IN`, it programs `pre_baco_tbl`; on success it sends `PPSMC_MSG_EnterBaco`; if the SMC message succeeds, it programs `enter_baco_tbl` and returns success only if that command table reports success. For `BACO_STATE_OUT`, it waits 20 ms to satisfy the hardware regulator off/on timing requirement, then programs `exit_baco_tbl` followed by `clean_baco_tbl`. All other paths return `-EINVAL`.

The register sequencing is deliberately table-driven so the shared SOC15 BACO executor owns polling, masking, delays, and RMW details. This keeps Vega10-specific logic limited to the ordering and bit definitions.

## State and Persistence
The function does not allocate persistent software state. Durable effects are hardware register state in NBIF/THM, BIOS scratch cleanup on exit, and SMC firmware state after `PPSMC_MSG_EnterBaco`. The current-state read is external through SMU9 BACO helpers.

## Dependencies and Integration Points
- Includes `amdgpu.h`, SOC15 register helpers, Vega10 register offsets/masks, `vega10_ppsmc.h`, and `vega10_baco.h`.
- Depends on `soc15_baco_program_registers()` for command-table execution and on `smum_send_msg_to_smc()` for firmware coordination.
- Integrated by `vega10_hwmgr.c` as `.set_asic_baco_state = vega10_baco_set_state`; passthrough initialization can expose BACO support via `vega10_baco_set_cap()`.

## Risks
- Register ordering is safety-critical. Changing the sequence, wait masks, or delays can leave the ASIC isolated, powered off, or not fully reset.
- The nested success checks are easy to misread because the command executor appears to return nonzero on successful table completion in this code path. Any refactor should confirm the helper's return contract before simplifying conditions.
- BACO exit depends on a fixed 20 ms regulator interval plus a 10 ms table delay. Hardware variants with different timing requirements would need validated updates.
- Failure returns are mostly `-EINVAL`, so callers get limited diagnostics without register tracing.

## Test Signals
- BACO state transition tests should cover in, out, no-op when already in target state, and SMC-message failure.
- Hardware validation should watch NBIF/THM BACO mode bits, doorbell/framebuffer behavior, and post-exit display/PCIe recovery.
- Suspend/resume, runtime power-management, GPU reset, and passthrough tests are high-value because they exercise the same BACO boundary.
