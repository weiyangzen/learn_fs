# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/tonga_ppsmc.h

## Purpose

`tonga_ppsmc.h` is a Tonga/SMU7-era SMC message and flag dictionary. It defines firmware response codes, system/state flags, thermal/fan constants, DPM flags, event bits, and a large set of `PPSMC_MSG_*` command IDs used by PowerPlay managers when controlling SMC firmware.

## Important APIs, types, and constants

The file uses `#pragma pack(push, 1)` but defines no structs. `PPSMC_Result` and `PPSMC_Msg` are `uint16_t` typedefs. `PPSMC_Result_OK`, `NoMore`, `NotNow`, `Failed`, `UnknownCmd`, and `UnknownVT` encode firmware responses; `PPSMC_isERROR(x)` treats bit 7 as the error marker.

System and state flags describe DC/AC, UVD, VCE, PCIe x1, GPIO DC detection, step VDDC, GDDR5, baby-step disable, regulator-hot signals, 12-channel memory, PowerTune/DPM2 features, watermark levels, deep sleep, power boost, and power shift.

The message list spans core SMC control (`Halt`, `Resume`, forced levels), power features (CAC, TDP clamping, PowerShift, OCP), multimedia power (`UVDPowerON/OFF`, `VCEPowerON/OFF`, ACP/SAMU/SDMA/IOMMU), DPM masks and forced levels, AC/DC and VR-hot interrupts, status logging, package power limits, overdrive, fan targets, BACO, microcode load addresses/status, VBIOS load, metadata loading, telemetry calibration, and display power messages.

Event status bits identify thermal, regulator-hot, DC, and GPIO17 events.

## Control flow

The header defines command IDs only. Runtime control flow is in callers such as SMU7/Tonga/CI managers: write an optional argument, write a message ID to the SMC message register, poll the response register, then interpret the result. Higher-level flows combine messages, for example freezing DPM levels before direct table edits and unfreezing them afterward.

## State and persistence behavior

Messages change firmware and hardware state: DPM enable masks, forced levels, power-gated IP state, clock sources, fan targets, voltage overrides, logging buffers, microcode load state, and BACO monitoring state. The flags are embedded in SMC DPM tables or interpreted as status/event bits.

The header itself persists no state, but the numeric command IDs are persistent ABI. Firmware and driver must agree on these values for every boot.

## Dependencies and integration points

The header depends on integer typedefs from the including environment. It integrates with SMU7 table structures, manager implementations in `smumgr/`, and hardware managers that translate user/profile/power events into SMC commands.

It is specifically relevant to Tonga-like SMU7 firmware, but many command names are shared with other SMU7-family chips. The values must not be mixed blindly with Vega SMU9 headers, where command numbering and result widths differ.

## Risks

This header contains a dense, hand-maintained command namespace with repeated or overlapping legacy IDs in the Trinity-specific section. Sending a command ID intended for a different firmware branch can be ignored, rejected, or interpreted as a different operation.

Several commands directly affect voltage, power limits, thermal throttling, microcode loading, and power-gated blocks. A wrong argument or command sequence can hang engines or destabilize power management. Since the header does not encode argument semantics, all validation must live in callers and firmware.

## Test signals

Validation requires runtime SMC message tests on supported ASICs: DPM enable/disable, UVD/VCE power transitions, forced clock levels, fan target updates, package power limit updates, PM status logging, BACO monitor paths, and microcode load status. Kernel logs should show no `UnknownCmd`, rejected-prerequisite, or failed message responses for supported flows.
