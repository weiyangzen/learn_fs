# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu71.h

## Purpose

`smu71.h` is an SMU7.1/Iceland firmware ABI header. It specializes SMU7 constants and structures for a dGPU-only variant, defining DPM dimensions, scoreboards, soft registers, firmware header offsets, CAC table structures, and display configuration values used by PowerPlay hwmgr and SMC firmware.

## Important APIs, Types, And Functions

The header defines DPM dimensions, Iceland/dGPU feature macros, `SID_OPTION`, `data_64_t`, `data_128_t`, SMU7 context IDs, SMU71 maximum level counts, DPM action constants, GPIO clamp modes, scratch B bit masks, DTE dimensions, `SMU71_PIDController`, `SMU7_LocalDpmScoreboard`, `SMU7_VoltageScoreboard`, `SMU7_PCIeLinkSpeedScoreboard`, `SMU7_PowerScoreboard`, `SMU7_ThermalScoreboard`, feature masks, handshake disables, `SMU71_SoftRegisters`, `SMU71_Firmware_Header`, `SMU7_HystController_Data`, `enum DisplayConfig`, and local CAC table structures.

The scoreboards expose firmware runtime state for DPM PID control, voltage requests across clients, PCIe DPM, power calculation, and thermal control. `SMU71_SoftRegisters` carries reference clocks, timer period, feature enables, display PHY configs, activity averages, enabled DPM levels, DRAM log addresses, ULV counters, microcode status, freeze/forced flags, and activity weight. `SMU71_Firmware_Header` extends the SMU7 header with UVD, ACP, VCE, SAMU DPM table pointers and ULV settings.

## Control Flow And Data Flow

There is no C implementation. Driver code reads firmware headers and soft-register offsets, writes feature enables and enabled-level masks, interprets scoreboards for diagnostics or policy, and transfers SMC tables. Firmware updates scoreboards as PID loops, voltage arbitration, PCIe DPM, power, and thermal controllers run.

## State And Persistence Behavior

Most structures are layouts for persistent firmware memory. Soft registers and scoreboards retain runtime state until firmware reset. Function pointers inside `SMU7_LocalDpmScoreboard` are meaningful to SMC firmware builds, not host driver execution. CAC tables and firmware table offsets persist as part of firmware/SMC memory.

## Dependencies And Integration Points

The header conditionally packs structures when not building SMC microcode. It integrates with SMU7/SMU71 hwmgr code, firmware parsing, DPM/voltage/PCIe/thermal/power diagnostics, MC/CAC setup, display configuration policy, ULV handling, and local CAC programming.

## Risks And Edge Cases

Host code must not call firmware function pointers embedded in scoreboards. Conditional fields under `SMU__DGPU_ONLY` change structure layout and must match firmware. `SMU71_MAX_LEVELS_GIO` references `SMU__NUM_LCLK_DPM_LEVELS`, which must be defined by the build context. Packed ABI changes can break firmware table offsets. Several names retain SMU7 prefixes even in SMU71-specific structures.

## Test Signals

Validation should include structure size/offset checks, Iceland firmware header parsing, soft-register read/write, DPM and voltage scoreboard sanity during load changes, PCIe DPM transitions, thermal and power scoreboard updates, local CAC table programming, ULV counters, and suspend/resume firmware state restoration.
