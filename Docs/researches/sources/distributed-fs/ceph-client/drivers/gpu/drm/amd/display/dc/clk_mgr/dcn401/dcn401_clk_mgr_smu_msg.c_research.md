# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_clk_mgr_smu_msg.c

## Purpose
This file implements the DCN 4.01 SMU/DAL message transport and typed wrappers used by the DCN 4.01 clock manager. It owns register-level message submission, response polling, optional delay accounting, and all PMFW command encodings.

## Important APIs, Types, And Functions
Core helpers are `dcn401_smu_wait_for_response`, `dcn401_smu_send_msg_with_param`, `dcn401_smu_wait_for_response_delay`, and `dcn401_smu_send_msg_with_param_delay`. Public wrappers include version checks, p-state messages, CAB for UCLK, DRAM address setters, watermark transfer, PME workaround, hardmin programming, DMCUB wait control, DRR status, idle/active/SubVP UCLK/FCLK hardmins, deep-sleep DCEF clock, display count, UMC channel query, DPM frequency query, and DC-mode max DPM query.

## Control Flow And Integration
The transport waits until `DAL_RESP_REG` is nonzero, clears it, writes `DAL_ARG_REG`, writes the message ID to `DAL_MSG_REG`, then waits for `DALSMC_Result_OK`. For hardmin requests, it sends `DALSMC_MSG_SetHardMinByFreq` and then polls `DALSMC_MSG_ReturnHardMinStatus` until the bit for the requested PPCLK is set or a one-second software limit is reached. Idle, active, and SubVP UCLK/FCLK hardmins pack FCLK in bits 31:16 and UCLK in bits 15:0.

## State And Persistence
No heap state is owned. Persistent effects are firmware-side settings: clock hardmins, p-state allow policies, display count, watermark table contents, DMCUB wait policy, DRR state, and CAB ways. Delay-accounting helpers only accumulate local timing for hardmin polling.

## Dependencies
It includes `dalsmc.h` for message IDs and `dcn401_smu14_driver_if.h` for table/version constants. It depends on register helpers, Display Core trace macros, and `clk_mgr_internal` for context and logging.

## Risks
The first wait result before sending is ignored, so a stuck or invalid response register may still lead to a new message attempt. Generic failures return `false` but many higher-level callers do not fully recover cached state. Hardmin status polling uses bit positions based on `PPCLK_e`, so enum drift would break acknowledgement detection. Temporary defines for missing message IDs suggest header synchronization risk.

## Test Signals
Tracepoints `TRACE_SMU_MSG_ENTER` and `TRACE_SMU_MSG_EXIT` should show every transaction. Tests should cover version mismatch, hardmin timeout, non-OK transfer response, DPM query levels including fine-grained mode, and packed UCLK/FCLK parameter correctness.
