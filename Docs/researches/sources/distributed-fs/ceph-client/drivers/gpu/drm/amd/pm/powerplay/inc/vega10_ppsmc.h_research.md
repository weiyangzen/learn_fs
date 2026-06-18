# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/vega10_ppsmc.h

## Purpose

`vega10_ppsmc.h` defines the SMU message ABI for Vega10 PowerPlay. It maps driver-visible `PPSMC_MSG_*` names to firmware command IDs, defines response codes, and records the expected SMU microcode version `0x001c0800`.

## Important APIs, types, and constants

`PPSMC_Result` is `uint16_t`; `PPSMC_Msg` is `int`. Response codes include OK, failed, unknown command, rejected prerequisite, and rejected busy. Message IDs cover SMU version/interface queries, feature enable/disable, workload and PPT limits, driver/tools DRAM address programming, table transfers, default/backup PP table selection, BTC, I2C bus arbitration, telemetry, ULV masks, VID offsets, floor SOC voltage, soft reset, BACO, low-GFX interrupt thresholds, soft min/max DPM indices, current DPM indices, average frequencies/activity, temperature sensors, overdrive, deep-sleep DCEF, AC switching, UCLK fast switch, fan targets, MP1 unload, display clock requests, DRAM logging, DIDT configuration, serial number reads, virtual DRAM addresses, ACG, current package power, PCC throttle, and package power PID alpha.

`PPSMC_Message_Count` is `0x69`, making it a useful upper bound for sanity checks in consumers.

## Control flow

No functions are present. Callers use the IDs through the SMU message transport: set argument if needed, write the message, wait for a nonzero response, and handle the response. Table-related messages pair with table IDs from `smu9_driver_if.h`.

## State and persistence behavior

The messages alter SMU firmware state such as feature masks, workload policy, power limits, PP table contents, voltage offsets, DPM bounds, fan thresholds, logging buffers, ACG state, and BACO monitoring. Some messages are queries that return values through the firmware response/argument registers rather than modifying persistent state.

## Dependencies and integration points

This header integrates with Vega10 SMU manager code, `smu9_driver_if.h` table definitions, PowerPlay profile and thermal code, and firmware that implements the listed command IDs. It must match the Vega10 firmware branch; Vega12/Vega20 headers have similar names but different numbering, extra split feature-mask commands, and sometimes different typedef widths.

## Risks

The central risk is command-number drift across SMU9 ASICs. Reusing a Vega10 ID on Vega12/Vega20 can call the wrong firmware operation. Another risk is result-width assumptions: this header uses a 16-bit result while Vega20 uses 32-bit result/message typedefs.

The header does not declare argument units. Callers must know when parameters are DPM indices, MHz, RPM, percentages, VID offsets, table IDs, or DRAM address halves. Incorrect units can be accepted by firmware but produce wrong policy.

## Test signals

Test signals include `GetSmuVersion` and `GetDriverIfVersion` success, PP table transfer success, feature-mask transitions, clock bound updates, temperature/fan queries, DRAM logging setup, display clock requests, and BACO monitor behavior on Vega10 hardware. Firmware-response logging should not show unknown or busy/rejected messages in valid sequences.
