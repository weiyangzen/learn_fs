# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu74_discrete.h

## Purpose
`smu74_discrete.h` provides the SMU74 discrete-board table layouts. It binds the common SMU74 firmware interface to board-specific DPM levels, register images, fan policy, fuses, logging, CAC verification, PM status, and graphics CU power-gating state.

## Important APIs, Types, And Constants
- `SMU74_Discrete_GraphicsLevel`, `MemoryLevel`, `LinkLevel`, `UvdLevel`, `ExtClkLevel`, `ACPILevel`, and `Ulv` describe programmable performance levels.
- `SMU74_Discrete_DpmTable` aggregates SMU74 PID controllers, rail level arrays, DPM level arrays, VRConfig, UVD/VCE/ACP/SAMU/graphics/memory/link boot and interval fields, SVI2/GPIO selectors, DTE/BAPM matrices, thermal/power limits, display CAC, low-SCLK interrupt threshold, VddGfx wait, and TDP controls.
- Memory programming uses `SMU74_Discrete_MCRegisters` and `SMU74_Discrete_MCArbDramTimingTable`.
- Diagnostics and runtime state include fan table, MCLK/ULV/VddGfx/TDC/pkg-power/BAPM/ACPI scoreboards, PM fuse layout, log control/header, CAC collection/verification, PM status, AutoWattMan status, and `SMU7_GfxCuPgScoreboard`.
- DIDT/EDC-style masks for SQ/TCP/TD/DB blocks and PM fuse AVFS constants define additional hardware controls.

## Control Flow And Data Flow
The host builds this table set from policy, atom/VBIOS tables, and fuse data, then firmware executes DPM and throttling locally. The data path includes register images for PLLs and memory timing, threshold/hysteresis fields for control loops, and status tables for host telemetry and AutoWattMan/PM feedback.

## State And Persistence
Most fields are runtime firmware state. PM fuse and AVFS-related fields are runtime copies of persistent board calibration. Log buffers reference host/firmware-visible memory and persist only as long as allocated.

## Dependencies And Integration Points
- Includes `smu74.h` for common AVFS, soft register, scoreboard, and firmware header definitions.
- Works with SMC mailbox commands for DPM enablement, AVFS, fan, telemetry, CU power gating, and secure register access.
- Integrates with memory-controller programming, display watermarks, PCIe link management, and thermal GPIO/VRHOT handling.

## Risks
- SMU74 adds more table families than earlier headers; forgetting to fill AVFS or CU PG-related regions can cause firmware feature failures.
- Status/log buffer address fields require correct 32/64-bit splitting and DMA visibility.
- DIDT/EDC block masks are dense and block-specific; bad values can over-throttle or under-protect hardware.
- AutoWattMan status structure is a policy interface and should remain synchronized with userspace expectations if exposed.

## Test Signals
- Validate table offsets against the SMU74 firmware header and run DPM table upload smoke tests.
- Exercise fan, AutoWattMan status reads, CAC verification, CU power gating, AVFS enable/disable, VddGfx transitions, memory level changes, and PCIe link DPM.
