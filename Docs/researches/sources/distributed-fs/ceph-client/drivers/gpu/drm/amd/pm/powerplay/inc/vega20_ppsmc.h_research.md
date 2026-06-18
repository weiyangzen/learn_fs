# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/vega20_ppsmc.h

## Purpose

`vega20_ppsmc.h` defines the Vega20 SMU message ABI. It is closely related to the Vega12 command set but uses 32-bit result/message typedefs and adds Vega20-specific commands for WAFL, FCLK/GFX clock ratio, debug data, XGMI mode, AFLL BTC, shutdown/reset preparation, multi-GPU fan boost, AVFS voltage query, BACO workaround, and DFC state control.

## Important APIs, types, and constants

Response codes are OK, failed, unknown command, rejected prerequisite, and busy. Both `PPSMC_Result` and `PPSMC_Msg` are `uint32_t`, which differs from Vega10/Vega12.

The command list includes version/interface queries, low/high feature masks, workload/PPT limits, DRAM address programming, table transfers, PP table selection, BTC, I2C bus arbitration, floor SOC voltage, reset/BACO, frequency min/max/hard/soft bound operations, DPM frequency queries, SS voltage by DPM, memory channel and Gemini settings, PCIe override, overdrive, AC/DC notification, UCLK switching, fan/thermal controls, MP1 unload/reset/shutdown preparation, DRAM logging, DIDT, display count, margin removal, serial reads, virtual DRAM address programming, GFXOFF allow/disallow, PPT-limit/debug/DC-frequency queries, XGMI mode, AFLL BTC, BACO workaround, and DFC state control.

`PPSMC_MSG_GfxDeviceDriverReset` is commented out at `0x3B`, documenting a reserved/removed command slot.

## Control flow

The file is a constant map only. Runtime code sends messages through the SMU transport and interprets 32-bit responses. Table-transfer commands pair with Vega20 table IDs from the corresponding SMU driver-interface header, not with the older Vega10/Vega12 definitions by assumption.

## State and persistence behavior

Messages mutate firmware-managed feature masks, clock limits, power limits, table contents, fan policy, logging, BACO/XGMI/GFXOFF state, MP1 reset/shutdown readiness, and debug/telemetry state. Some commands are query-only and return values through firmware argument registers.

## Dependencies and integration points

This header integrates with Vega20 PowerPlay/SMU manager code, high-level DPM policy, multi-GPU/XGMI handling, BACO/reset/shutdown flows, AVFS tooling, and fan/thermal management. Its 32-bit typedefs imply call sites must not assume 16-bit command/result widths.

## Risks

Cross-generation message reuse is the major risk. Vega20 removes or reserves some Vega12 commands and adds new IDs, so shared code must select the correct header through the ASIC-specific manager. The wider result/message types can also expose truncation bugs in helper functions typed for `uint16_t`.

Commands for reset/shutdown, XGMI, BACO workaround, and clock ratios are high-impact. Bad sequencing can affect multi-GPU links, low-power transitions, or firmware survivability during driver unload/reset.

## Test signals

Validation should cover version/interface queries, feature masks, PP table transfers, DPM frequency operations, debug data retrieval, XGMI mode changes, AFLL BTC, BACO entry/exit and workaround, MP1 reset/shutdown preparation, multi-GPU fan boost, AVFS voltage query, and DFC state control on Vega20 hardware.
