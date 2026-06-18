# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu9_driver_if.h

## Purpose

`smu9_driver_if.h` is the packed driver-to-SMU ABI for early SMU9/Vega power management. It defines the binary table layouts, table IDs, feature limits, and command arguments used when the Linux AMDGPU PowerPlay driver exchanges power, clock, voltage, fan, watermark, AVFS, and debug data with SMU firmware. The file has no executable functions; its primary responsibility is keeping the host-side C layout identical to the firmware layout.

The interface version is `SMU9_DRIVER_IF_VERSION 0xE`, with an explicit warning that any structure change must increment the version. That is a strong signal that compatibility is versioned at the byte-layout level rather than by named fields.

## Important APIs, types, and constants

The DPM limit macros define fixed array sizes for graphics, UVD, VCE, MP0, memory, SOC, DCEF, PCIe link, EVV voltage, and PSP level maps. These constants size the arrays embedded in `PPTable_t` and therefore define how much data the firmware expects for each clock domain.

`PllSetting_t` describes a PLL level with feedback multipliers, spread-spectrum state, and divider ID. It is used for graphics and memory clock levels. `GbVdroopTable_t` and `QuadraticInt_t` encode fixed-point droop/guardband equations. `DisplayClockTable_t` pairs display clock frequencies with voltage IDs. `DSPCLK_e` identifies DCEF, DISP, PIX, and PHY clock classes.

`PPTable_t` is the central packed table. It contains PowerTune limits, external I2C component addresses, Gemini board aperture data, ULV settings, SOC voltage IDs, graphics/SOC/UVD/VCE/MP0/memory DPM tables, display clock tables, voltage mode selectors, averaging alpha values, PCIe link settings, fan control parameters, GPIO assignments, LED pins, AVFS/guardband equations, ageing guardband parameters, boost/ACG settings, and firmware padding.

`Watermarks_t` contains four watermark ranges for SOC/DCEF clock classes. `AvfsTable_t`, `AvfsDebugTable_t`, and `AvfsFuseOverride_t` describe AVFS runtime tables, debug samples, and fuse/equation overrides. The `TABLE_*` constants map the table-transfer SMU messages to specific shared-memory table IDs.

The file also defines `UCLK_SWITCH_SLOW`/`FAST`, GFX DIDT bit masks and shifts for SQ/TCP/TD/DB blocks, and margin-removal bit indices.

## Control flow

There is no local runtime control flow. The effective flow is imposed by PowerPlay managers: allocate or fill a `PPTable_t`/related table in driver memory, program the driver DRAM address through SMU messages, and use `SMC_MSG_TransferTableDram2Smu` or `SMC_MSG_TransferTableSmu2Dram` with the `TABLE_*` IDs. Firmware then consumes the packed layout directly.

Call sites must populate dependent fields consistently. For example, voltage modes determine whether indexed voltage tables, AVFS interpolation, worst-case values, or static offsets are meaningful; link DPM fields must match PCIe capabilities; and fan fields only matter when firmware fan control is enabled.

## State and persistence behavior

The structures model firmware-owned runtime state and driver-provided policy, not persistent kernel state. Values persist in SMU RAM or DRAM-backed transfer buffers until the driver uploads a replacement table, the firmware overwrites a status/debug table, or the GPU resets. GPIO, fan, I2C, voltage, and DPM fields can affect live hardware behavior after transfer.

Because `PPTable_t` is packed, padding fields are also ABI state. The `MmHubPadding` arrays are reserved for firmware/internal use and must remain present to preserve offsets.

## Dependencies and integration points

The header includes `smu9.h` and depends on Linux fixed-width integer types being available through the include chain. It integrates with the PowerPlay SMU manager abstraction in `smumgr.h`, generation-specific SMC message headers such as `vega10_ppsmc.h`, and SMU9 manager implementations that transfer `TABLE_PPTABLE`, `TABLE_WATERMARKS`, `TABLE_AVFS`, and related IDs.

It also depends on VBIOS/PowerPlay table parsing code for actual values: thermal limits, fan parameters, DPM clocks, voltages, I2C addresses, and board-specific capabilities are typically derived from VBIOS tables before being encoded here.

## Risks

The main risk is ABI drift. Any field insertion, type-size change, array-size change, or packing change can cause firmware to interpret the wrong bytes as clocks, voltages, thermal limits, or fan settings. The file uses fixed-width types and `#pragma pack(push, 1)` to reduce that risk, but consumers still need version checks against firmware.

Unit mismatches are another risk: fields mix MHz, 10 KHz units, Celsius, watts, amps, SVI2 VID, mOhms, and fixed-point equation formats. Incorrect scaling can silently produce unstable DPM or thermal behavior. The AVFS and ageing-guardband equations are especially sensitive because they encode fixed-point coefficients and shifts.

## Test signals

Useful validation includes build coverage for SMU9 PowerPlay, firmware interface-version checks, table-size/offset assertions against firmware specifications, and runtime testing on Vega hardware. Runtime signals include successful PP table upload/download, correct DPM level enumeration, stable fan behavior, valid temperature/power telemetry, successful watermark updates, and no SMU table-transfer failures in kernel logs.
