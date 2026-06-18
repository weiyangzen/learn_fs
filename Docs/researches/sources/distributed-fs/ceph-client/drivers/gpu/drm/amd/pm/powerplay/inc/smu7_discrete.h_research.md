# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu7_discrete.h

## Purpose
`smu7_discrete.h` is the base SMU7 discrete-board packed ABI header. It defines DPM, soft-register, voltage, fan, memory-controller, and fuse table layouts for the original SMU7 discrete powerplay implementation.

## Important APIs, Types, And Constants
- DTE dimensions are discrete-specific: 5 iterations, 3 sources, 1 sink, no CPU TEs, 1 GPU TE, and 2 non-TEs.
- `SMU7_SoftRegisters` exposes ref clock, timers, feature enables, display PHY configs, enabled DPM masks, log-buffer addresses, and ULV counters.
- Level structs cover voltage, graphics, ACPI, ULV, memory, PCIe link, MCARB timing, UVD, external clocks, and compact state info.
- `SMU7_Discrete_DpmTable` is the main table. It includes PID controllers, SMIO masks, voltage arrays, DPM arrays for graphics/memory/link/UVD/VCE/ACP/SAMU, ULV, SCLK step size, boot levels, intervals, thermal/power limits, BAPM matrices, SVI2 and GPIO selectors, TDP values, and low-SCLK interrupt threshold.
- `SMU7_Discrete_MCRegisters`, `SMU7_Discrete_FanTable`, and `SMU7_Discrete_PmFuses` define companion programming tables.

## Control Flow And Data Flow
Host code converts board data and policy into these tables, uploads them to firmware-visible memory, and firmware performs local DPM control. DPM selection is driven by activity thresholds, PID settings, enabled-level masks, boot levels, hysteresis, voltage-response timing, and thermal/power clamps.

## State And Persistence
The structs describe volatile shared memory. Fuse values come from persistent board calibration but are copied into `SMU7_Discrete_PmFuses`. Log buffer addresses are runtime allocations. Packing is unconditional in this file.

## Dependencies And Integration Points
- Includes `smu7.h` for common SMU7 counts and `SMU7_PIDController`.
- Integrated by discrete SMU7 powerplay backend and SMC message interface.
- Memory controller register sets integrate with MCLK switching and display watermark selection.

## Risks
- Unconditional `#pragma pack(push, 1)` makes include order and matching `pop` important.
- Field names are older (`UpH`, `DownT`, `FpsHighT`) and can obscure semantics compared with later `Hyst`/`Threshold` names.
- DPM table and MC register table dimensions are firmware ABI; changing arrays breaks compatibility.
- Fuse dword comments must stay aligned with actual packed fields.

## Test Signals
- Static offset/size checks against firmware symbols.
- Runtime DPM table upload, graphics/memory/link/media level transitions, fan response, MC register switching, and fuse-based power readings.
