# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/rv_ppsmc.h

## Purpose

`rv_ppsmc.h` defines the Raven PowerPlay-to-SMC message and result ABI. It gives driver code numeric command IDs for MP1/SMU firmware operations such as clock limits, power gating, table transfers, display notifications, GFXOFF, reset, and power-limit queries.

## Important APIs, Types, And Functions

The file exports result codes `PPSMC_Result_OK`, `Failed`, `UnknownCmd`, `CmdRejectedPrereq`, and `CmdRejectedBusy`. Message constants include version queries, GFX power up/down and GFXOFF control, ISP/VCN/SDMA power gating, hard-min clocks for ISP/VCN/FCLK/DCEFCLK/SOCCLK/GFXCLK, display count, video FPS, table transfer address setup, table transfer directions, driver reset, GFX overdrive, soft reset, MMHUB power gating, RCC/PFC/PME restore, GPU state changes, and GFX busy query. It typedefs `PPSMC_Result` as `uint16_t` and `PPSMC_Msg` as `int`.

## Control Flow And Data Flow

There is no code. Consumers pass a `PPSMC_MSG_*` value, usually with an optional parameter, to hwmgr/SMU message functions. Firmware returns a `PPSMC_Result` that controls retries, prerequisite handling, or error propagation. Table-transfer messages pair with DRAM address setup messages before moving tables between driver and SMU memory.

## State And Persistence Behavior

Messages can mutate persistent firmware and hardware state: power-gated blocks, DPM hard minimums, clock ceilings, display count, table content, GFXOFF state, and reset state. The header itself is stateless and packed for ABI consistency.

## Dependencies And Integration Points

It depends on fixed-width integer types and `#pragma pack`. It integrates with Raven hwmgr, SMU message send helpers, clock and power-gating APIs, display-manager notifications, VCN/ISP/SDMA paths, table upload/download, and reset handling.

## Risks And Edge Cases

Numeric message IDs are firmware ABI values; renumbering breaks communication. `PPSMC_Message_Count` is `0x42`, while not every value in the range is defined. Busy or prerequisite rejection needs caller-specific retry or ordering. Some messages require parameters in specific units not encoded here.

## Test Signals

Validation should include Raven firmware version query, table transfer round trips, GFXOFF enable/disable, VCN/ISP/SDMA power gating, display count changes, hard-min clock requests, reset messages, and handling of busy/prerequisite rejection results.
