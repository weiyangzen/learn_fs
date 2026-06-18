# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu74.h

## Purpose
`smu74.h` defines the common SMU74 discrete GPU firmware interface. It extends the SMU7-family interface with explicit dGPU-only configuration, exponential coefficients, AVFS table pointers in the firmware header, and additional clock-gating and graphics light-sleep masks.

## Important APIs, Types, And Constants
- `SMU__DGPU_ONLY` selects discrete-only layout behavior.
- Exponential coefficient macros `EXP_M1*`, `EXP_M2*`, and `EXP_B*` support firmware power/leakage calculations.
- Common DPM maxima use `SMU74_MAX_LEVELS_*`.
- `SMU74_PIDController`, `SMU7_LocalDpmScoreboard`, packed `SMU_VoltageLevel`, voltage/power/thermal/PCIe scoreboards, and `SMU74_SoftRegisters` define runtime control state.
- `SMU74_Firmware_Header` adds AVFS-related pointers: `VftTable`, `AvfsTable`, `AvfsCksOffGbvTable`, `AvfsMeanNSigma`, and `AvfsSclkOffsetTable`.
- AVFS types include `AgmAvfsData_t`, `VFT_TABLE_t`, `AVFS_Margin_t`, `GB_VDROOP_TABLE_t`, `AVFS_CksOff_Gbv_t`, `AVFS_meanNsigma_t`, and `AVFS_Sclk_Offset_t`.

## Control Flow And Data Flow
Host firmware discovery uses the firmware header at `SMU7_FIRMWARE_HEADER_LOCATION`. The driver writes soft registers, DPM policy, CG masks, VR encodings, clock-stretcher tables, and AVFS calibration tables. Firmware uses these plus scoreboards to choose DPM levels, track FPS clamps, apply thermal/voltage limits, and adjust voltage/frequency margins.

## State And Persistence
The file defines packed volatile firmware-memory state. AVFS and fuse-derived tables carry calibration data copied from persistent sources, but the runtime representation is in firmware-visible memory and must align exactly.

## Dependencies And Integration Points
- Included by `smu74_discrete.h`.
- Integrated by SMU74 discrete powerplay logic and mailbox commands for AVFS, DPM, clock gating, and telemetry.
- Shares many `SMU7_*` compatibility names with earlier generations while using SMU74-specific structures and counts.

## Risks
- AVFS header pointer additions reduce `Reserved` size; using an older header layout with SMU74 firmware would misplace signature/offsets.
- `FEATURE_*` and CG masks are not self-validating; unsupported bits can produce hangs or ineffective power gating.
- Packed `SMU_VoltageLevel` and VFT/GBV tables require exact units and dimensions.
- Soft-register field `AllowMvddSwitch` changes memory-voltage behavior and should be policy-validated.

## Test Signals
- Static layout checks for `SMU74_Firmware_Header`, `SMU74_SoftRegisters`, and AVFS table types.
- Runtime: firmware reports valid VFT/AVFS tables, DPM levels transition, CG masks apply, Mvdd switching behaves correctly, and telemetry matches expected power rails.
