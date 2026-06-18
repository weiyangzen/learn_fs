# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu10_driver_if.h

## Purpose

`smu10_driver_if.h` defines the SMU10 driver table interface version and the packed table layouts exchanged between AMDGPU and SMU10 firmware for display clocks, watermarks, custom DPM activity coefficients, and DPM clock reporting.

## Important APIs, Types, And Functions

The interface version is `SMU10_DRIVER_IF_VERSION 0x6`. `FloatInIntFormat_t` stores fixed-point values. `DSPCLK_e` identifies DCEFCLK, DISPCLK, PIXCLK, and PHYCLK. `DisplayClockTable_t` maps a frequency to VID. `WatermarkRowGeneric_t` stores min/max clock and memory clock ranges plus watermark setting/type, while `Watermarks_t` contains rows for SOCCLK and DCFCLK over four ranges. `CUSTOM_DPM_SETTING_e`, `DpmActivityMonitorCoeffExt_t`, and `CustomDpmSettings_t` define custom DPM activity monitor tuning. `DpmClock_t` and `DpmClocks_t` report DCEF, SOC, FCLK, and memory clock/voltage pairs.

## Control Flow And Data Flow

There is no implementation. Driver code fills these structures in host memory, sends table-transfer messages to firmware, or reads firmware-populated DPM clock tables back. Display and memory watermark data flows from display mode decisions into `Watermarks_t`. Custom DPM coefficients flow from policy code into firmware activity monitors.

## State And Persistence Behavior

These structures become persistent SMU table state after transfer. Firmware can use them until the next table update, reset, or reload. The header itself has no mutable state.

## Dependencies And Integration Points

It depends on fixed-width integer types. It integrates with SMU10 message/table transfer code, display watermark programming, custom DPM tuning, DPM clock query paths, and hwmgr clock reporting APIs.

## Risks And Edge Cases

Changing any structure requires an interface-version bump and matching firmware support. Fixed array sizes are ABI. Units differ by field: some frequencies are MHz, voltages are millivolts with two fractional bits, and coefficients are fixed-point. Padding fields must remain deterministic for firmware compatibility.

## Test Signals

Validation should include structure size checks against firmware expectations, SMU10 table transfer smoke tests, display mode/watermark changes, custom DPM profile updates, DPM clock readback sanity, and version mismatch handling.
