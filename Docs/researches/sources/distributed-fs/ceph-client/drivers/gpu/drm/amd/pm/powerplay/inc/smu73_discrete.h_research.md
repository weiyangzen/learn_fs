# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu73_discrete.h

## Purpose
`smu73_discrete.h` defines the discrete-board SMU73 table ABI. It maps graphics, memory, PCIe, media clocks, ULV, fan, fuse, CAC, PM status, and AVFS-related data into packed structures for firmware.

## Important APIs, Types, And Constants
- SMIO pattern/table definitions control rail VID/phase output patterns.
- `SMU73_Discrete_GraphicsLevel`, `MemoryLevel`, `LinkLevel`, `UvdLevel`, `ExtClkLevel`, `ACPILevel`, and `Ulv` define each performance-state category.
- `SMU73_Discrete_DpmTable` is the central programming object, using `SMU73_PIDController` and `SMU73_MAX_LEVELS_*` arrays. It includes VR config, DPM counts, boot levels, intervals, SVI2/GPIO selectors, BAPM/DTE tables, thermal/power limits, display CAC, low-SCLK interrupt threshold, and VddGfx wait controls.
- Diagnostic/runtime structures include MCLK/ULV/VddGfx/TDC/pkg-power/BAPM/ACPI scoreboards, log tables, CAC collection and verification tables, and `SMU7_Discrete_Pm_Status_Table`.
- Constants define CAC coefficients, VDDCI/VDDR1 power constants, area coefficients, and thermal output modes.

## Control Flow And Data Flow
The driver provides populated tables, then firmware uses thresholds and counts to run local DPM loops. State flows from policy/VBIOS/fuse inputs into DPM/fan/fuse tables, then firmware writes live telemetry and status into scoreboards and PM status tables for driver inspection.

## State And Persistence
The DPM, fan, MC, log, CAC, and PM status tables are volatile firmware-shared memory. Fuse fields mirror nonvolatile board calibration but are copied into runtime tables. Scoreboard fields persist only while SMU firmware is active.

## Dependencies And Integration Points
- Includes `smu73.h` for common constants, PID controller, voltage encoding, AVFS support, and soft-register/header layouts.
- Used by discrete SMU73 powerplay backend and SMC message flow.
- Integrates with memory controller timing programming and power/thermal telemetry paths.

## Risks
- CAC signal count is fixed at 87 for this discrete generation; mismatches with firmware collection layout corrupt telemetry interpretation.
- Many fields are hardware register images (`CgSpll*`, `Mpll*`, spread spectrum registers); stale register programming can break clocks.
- Shared SMU7 names in status tables may mask SMU73-specific semantics.
- Firmware probably assumes the exact order of PM fuse dwords.

## Test Signals
- Validate DPM table upload and `SMU7_Discrete_Pm_Status_Table` reads.
- Exercise SCLK/MCLK, UVD/VCE/ACP/SAMU, PCIe, fan, ULV, VddGfx, CAC, and thermal-output modes.
- Confirm firmware accepts VFT/AVFS support inherited from `smu73.h`.
