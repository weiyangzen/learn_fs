<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn315/dcn315_smu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn315/dcn315_smu.c

## Purpose
Provides DCN315 PMFW mailbox operations for display clock programming, watermark/DPM table transfer, DPREF/DTB clock queries, idle optimization, and PME workaround messages.

## Important APIs, Types, And Functions
- `dcn315_smu_send_msg_with_param` performs the mailbox transaction using MP1 C2P response/argument registers and an indexed write/readback path for the message ID.
- `dcn315_smu_wait_for_response` polls `MP1_SMN_C2PMSG_38` until PMFW leaves busy state.
- Public wrappers set DISPCLK, DPPCLK, hard-min DCFCLK, minimum deep-sleep DCFCLK, display idle optimization, PHY refclk powerdown, DRAM table addresses, table transfers, DPREF/DTB queries, DTBCLK enablement, and PME workaround.

## Control Flow
The transaction helper waits for ready, clears the response, writes the argument, retries the message-ID write up to five times until readback matches, then waits for completion. Wrappers short-circuit when SMU is not present; DCFCLK and idle optimization also short-circuit when pstate is disabled.

## State And Persistence
The file owns no heap state. It changes PMFW state and reads/writes MP1 mailbox registers. Returned clock frequencies are converted from MHz to kHz by wrappers before returning to callers.

## Dependencies And Integration Points
Uses MP 13.0.5 register offsets, `IX_REG_SET_SYNC`/`IX_REG_GET_SYNC` for the special C2PMSG_3 path, DC logging, and timeout reporting. It is the SMU backend for `dcn315_clk_mgr.c`.

## Risks And Edge Cases
Message-ID write failures are retried but not fatal unless PMFW later times out. Unlike DCN314, this helper does not special-case `Result_Failed`, so failed responses can still produce register return values. Frequency precision is MHz-based. A stale or missing SMU presence flag turns programming calls into no-ops.

## Test Signals
Observe successful readback of message IDs, timeout handling, DPREF/DTB query values, pstate-disabled DCFCLK short-circuiting, display-off idle optimization, and table transfers with valid GPU addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn315/dcn315_smu.c -->
