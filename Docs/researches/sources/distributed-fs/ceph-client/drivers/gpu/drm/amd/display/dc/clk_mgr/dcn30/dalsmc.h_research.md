<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dalsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dalsmc.h

## Purpose

`dalsmc.h` defines the DCN30 DAL-to-SMU message ABI constants used by DCN30 clock-manager SMU mailbox code.

## Important APIs, Types, And Functions

It defines `DALSMC_VERSION`, SMU response codes, message IDs from `DALSMC_MSG_TestMessage` through `DALSMC_MSG_SmartAccess`, and `DALSMC_Message_Count`. There are no functions or structs.

## Control Flow

No runtime flow exists. The constants drive message selection and response interpretation in `dcn30_clk_mgr_smu_msg.c` and `dcn30m_clk_mgr_smu_msg.c`.

## State And Persistence Behavior

The header owns no state. It describes a firmware ABI whose effects are persisted by PMFW when messages are sent.

## Dependencies And Integration Points

It is included by DCN30 SMU message implementations. `DALSMC_MSG_SmartAccess` is used by the mobile SmartMux path; watermark, DPM, display-count, MALL, DF C-state, and PME messages are used by the main DCN30 clock manager.

## Risks

The comment says this is temporary until definitions exist in the proper location, so ABI drift against PMFW headers is a risk. Numeric message IDs are firmware contracts; accidental renumbering would send the wrong command.

## Test Signals

Compile-time inclusion plus runtime SMU version/header checks, test message response, watermark transfers, DPM frequency queries, hard-min/max requests, and SmartAccess/SmartMux commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dalsmc.h -->
