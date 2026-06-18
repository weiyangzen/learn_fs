<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn316/dcn316_smu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn316/dcn316_smu.c

## Purpose
Implements DCN316 PMFW mailbox communication for display clock and table operations.

## Important APIs, Types, And Functions
- `dcn316_smu_send_msg_with_param` serializes PMFW transactions through MP1 response, argument, and message registers.
- `dcn316_smu_wait_for_response` polls `MP1_SMN_C2PMSG_91`.
- Public wrappers program DISPCLK, DPPCLK, DCFCLK hard-mins, deep-sleep DCFCLK, display idle optimization, PHY refclk powerdown, DRAM table addresses, DPM/watermark transfers, PME workaround, DTBCLK, DPREF query, and FCLK query.

## Control Flow
The send helper waits for not-busy, clears the response, writes the parameter to C2PMSG_83, writes the message ID to C2PMSG_67, then waits for completion. Wrappers skip when SMU is absent; pstate-dependent requests also require `debug.pstate_enabled`.

## State And Persistence
No memory is owned here. PMFW and MP1 mailbox registers hold the externally persistent state. Return values are converted from MHz to kHz by clock query/set wrappers.

## Dependencies And Integration Points
Uses MP 13.0.8 offsets/masks, common register helpers, DC logging, and `dm_helpers_smu_timeout`. It is the low-level backend for `dcn316_clk_mgr.c`.

## Risks And Edge Cases
The helper asserts on busy timeout but otherwise does not distinguish failed/unknown/rejected responses from successful parameter reads. `dcn316_smu_set_dtbclk` uses `VBIOSSMC_MSG_SetDtbclkFreq`, whose semantics are on/off despite a frequency-like name. Pstate-disabled paths intentionally skip DCF/idle messages.

## Test Signals
PMFW version query, DISP/DPP/DCF programming, DTBCLK toggle, DPREF/FCLK reads, timeout path, pstate-disabled no-op behavior, and table-transfer messages are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn316/dcn316_smu.c -->
