# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu75_discrete.h

## Purpose
`smu75_discrete.h` is the SMU75 discrete-board packed table ABI. It adds SMU75-specific SCLK PLL/FCW data and richer AVFS/fuse/GFX block controls on top of the standard discrete DPM, fan, MC, CAC, log, and status tables.

## Important APIs, Types, And Constants
- SCLK PLL programming constants include `NUM_SCLK_RANGE`, `VCO_*`, `POSTDIV_*`, `sclkFcwRange_t`, and `SMU_SclkSetting`.
- Level types cover graphics, memory, PCIe link, ACPI, ULV, UVD, and external clocks.
- `SMU75_Discrete_DpmTable` carries SMU75 PID controllers, voltage and DPM arrays, VRConfig, boot levels, intervals, register images, BAPM/DTE data, GPIO/SVI2 controls, TDP/power limits, and SMU75-specific SCLK settings.
- Runtime tables include fan, scoreboards, PM fuses, log/CAC tables, PM status, AutoWattMan status, GFX CU PG scoreboard, DIDT/EDC masks, and AVFS fuse constants.
- CAC constants mirror earlier SMU7-family values with `CAC_ACC_NW_NUM_OF_SIGNALS` set for dGPU builds.

## Control Flow And Data Flow
The host fills DPM and calibration tables, including SCLK PLL ranges/settings, then firmware uses the counts, boot indices, hysteresis, thresholds, and register images to drive DPM transitions. Telemetry flows back through status, log, CAC, AutoWattMan, and scoreboard structures.

## State And Persistence
Runtime table memory is volatile and packed. SCLK, fuse, AVFS, and droop data are loaded from persistent calibration or firmware tables into this runtime ABI. Log buffers and status tables are live firmware outputs.

## Dependencies And Integration Points
- Includes `smu75.h` for common SMU75 constants, soft registers, firmware header, AVFS tables, and voltage encoding.
- Integrates with SMC commands for SCLK PLL DFS, AVFS, fan, EDC, FFC, zero RPM, CU power gating, and telemetry.
- The memory and PLL register-image fields integrate directly with hardware programming paths.

## Risks
- SCLK FCW/VCO/post-divider encoding is low-level; wrong ranges can make SCLK programming fail or hang.
- Many power/fuse constants are copied into firmware with implicit units.
- Dense block masks for SQ/TCP/TD/DB EDC and IR/PCC controls can create silent power-management misbehavior.
- Conditional `SMU__DGPU_ONLY` around CAC count and AVFS fuse size must align with including context.

## Test Signals
- Static checks for DPM table offsets, SCLK setting layout, and PM fuse size.
- Runtime: successful SCLK changes across ranges, stable memory/PCIe/media DPM, AVFS command success, zero-RPM/fan behavior, AutoWattMan status, CAC verification, and EDC controller toggles.
