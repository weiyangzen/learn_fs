# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu75.h

## Purpose
`smu75.h` is the shared SMU75 firmware interface. It carries the SMU7-family DPM, soft-register, firmware-header, voltage, power, clock-gating, clock-stretcher, and AVFS table contracts for a later discrete generation.

## Important APIs, Types, And Constants
- It defines common level counts and `SMU75_MAX_LEVELS_*`, plus DPM direction constants and scratch-register index bitfields.
- Power/CAC types include polynomial coefficient data, `PowerCalculatorData_t`, CAC weights, and 64/128-bit helper structs.
- Runtime state includes `SMU75_PIDController`, `SMU7_LocalDpmScoreboard`, packed voltage bitfield type `SMU_VoltageLevel`, PCIe and power scoreboards, and `SMU75_SoftRegisters`.
- `SMU75_Firmware_Header` points to common tables plus AVFS-specific tables.
- Clock-gating masks add BIF MGCG and expanded graphics 3D/RLC/CP light-sleep masks.
- AVFS support includes VFT columns, optional SCKS cells, VFT table, GB droop tables, quadratic coefficients, margins, CKS-off tables, mean/sigma, SCLK offsets, and power sharing data.

## Control Flow And Data Flow
The driver interprets the firmware header, writes soft registers and table pointers, then firmware applies DPM/voltage/thermal/AVFS policy. Scoreboards track firmware-local control loop state, while masks encode host-requested feature enablement, clock gating, voltage regulator routing, and clock stretcher behavior.

## State And Persistence
The header describes volatile packed memory shared with firmware. AVFS and droop data may be derived from persistent calibration, but the C structures are runtime table images. Optional conditional fields such as SCKS data must match the firmware build configuration.

## Dependencies And Integration Points
- Included by `smu75_discrete.h`.
- Integrates with mailbox command definitions in `smu7_ppsmc.h`, especially AVFS, VFT, fan, DPM, and secure register messages.
- The surrounding powerplay code must use the same `SMU__DGPU_ONLY` and optional firmware feature macros as firmware.

## Risks
- Several feature mask macros near FAST_PPT/GFX_EDC/ACG appear to use names without the `FEATURE_` prefix in the shift expression; this is sensitive to surrounding macro definitions and build coverage.
- Conditional `SMU__DGPU_ONLY` changes `SMU75_SoftRegisters`.
- Optional `SMU__FIRMWARE_SCKS_PRESENT__1` changes `VFT_TABLE_t` layout.
- AVFS table dimensions and voltage units are hardware-critical.

## Test Signals
- Compile in the exact kernel configuration used by consumers to catch conditional macro issues.
- Firmware table-offset and signature validation.
- Runtime checks for AVFS/VFT validity, clock-gating masks, DPM transitions, fan control, and telemetry correlation.
