<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr_smu_msg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr_smu_msg.c

## Purpose

`dcn30_clk_mgr_smu_msg.c` implements the DCN30 DALSMC mailbox transport and typed wrappers for PMFW clock, DPM, watermark, display, MALL, DF C-state, and PME messages.

## Important APIs, Types, And Functions

Exports include `dcn30_smu_test_message()`, `dcn30_smu_get_smu_version()`, interface/header version checks, DRAM address setters, watermark table transfers, hard-min/max by frequency, DPM frequency queries, DC-mode max DPM query, minimum deep-sleep DCEFCLK, number-of-displays, display-refresh-from-MALL, external-client DF C-state allow, and PME workaround. Internal helpers are `dcn30_smu_wait_for_response()` and `dcn30_smu_send_msg_with_param()`.

## Control Flow

The send helper waits for a nonzero response register, clears it, writes DAL argument and message registers, traces the message, waits again, reports timeouts, and returns true only for `DALSMC_Result_OK`, optionally reading the argument register as output. Frequency messages pack clock ID in bits 23:16 and MHz or DPM level in the low bits. Watermark transfers first require the caller to set DRAM high/low address, then send table-transfer messages with `TABLE_WATERMARKS`.

## State And Persistence Behavior

The file holds no heap/static mutable state. It changes PMFW state through SMU messages and uses DAL response/argument/message registers as transient mailbox state. Trace macros record message latency.

## Dependencies And Integration Points

It depends on `dalsmc.h`, `dcn30_smu11_driver_if.h`, `reg_helper`, DC logging, SMU timeout helpers, and DCN30 clock-manager callers. `dcn30_clk_mgr.c` uses it for all PMFW interactions.

## Risks

`CmdRejectedBusy` is noted but not specially retried. Most void wrappers ignore failed sends. Interface/header version checks return booleans but current init does not fail hard on mismatch. Parameter packing assumes frequencies fit in 16 bits. The mailbox register offsets are hard-coded DAL register numbers.

## Test Signals

SMU test message, version/interface/header checks, timeout handling, DPM feature query with `0xFF`, hard-min/max readbacks, watermark upload/download, display-count changes, MALL refresh parameters, DF C-state toggles, and PME message tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr_smu_msg.c -->
