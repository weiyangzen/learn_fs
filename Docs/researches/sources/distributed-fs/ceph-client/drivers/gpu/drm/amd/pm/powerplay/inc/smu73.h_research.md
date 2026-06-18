# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu73.h

## Purpose
`smu73.h` defines the shared SMU73 firmware ABI. Compared with SMU72, it keeps the same broad DPM and firmware-header model but adds richer FPS/LED fields in the local DPM scoreboard and AVFS VFT table support.

## Important APIs, Types, And Constants
- Common DPM constants and maxima mirror SMU72 with `SMU73_MAX_LEVELS_*` names.
- Thermal/DTE constants add `SMU73_THERMAL_INPUT_LOOP_COUNT` and `SMU73_THERMAL_CLAMP_MODE_COUNT`.
- `SMU73_PIDController`, `SMU7_LocalDpmScoreboard`, packed `SMU_VoltageLevel` bitfields (`VDDC_MASK`, `VDDCI_MASK`, `PHASES_MASK`), PCIe/power scoreboards, and soft registers define firmware runtime state.
- `SMU73_Firmware_Header` points to RTOS, soft registers, DPM/fan/CAC/MC/fuse/global/clock-stretcher tables.
- AVFS-related types include `AgmAvfsData_t`, `VFT_COLUMNS`, `VFT_CELL_t`, and `VFT_TABLE_t`.

## Control Flow And Data Flow
The host uses these definitions to discover and populate firmware tables. Firmware reads `FeatureEnables`, handshake masks, DPM enabled-level bitmasks, and scratch index bitfields, then updates scoreboards as it applies DPM, voltage, FPS clamp, LED, telemetry, and thermal policy decisions.

## State And Persistence
Everything in this file is volatile shared firmware state except calibration values sourced externally. `#pragma pack(push, 1)` makes it a byte-level ABI. The AVFS VFT table is a calibration/runtime policy table keyed by temperature steps and SCLK columns.

## Dependencies And Integration Points
- Included by `smu73_discrete.h`.
- Consumed by SMU73 powerplay code that parses firmware headers and uses the common scoreboards.
- Clock-gating, VR configuration, clock stretcher, and display config constants integrate with CG, voltage, and display policy programming.

## Risks
- The file uses shared `SMU7_*` names for SMU73-specific layouts; consumers must include the correct header generation.
- The compressed `SMU_VoltageLevel` changes the representation from the struct form seen in some earlier headers.
- AVFS tables introduce matrix dimensions (`TEMP_RANGE_MAXSTEPS` by `NUM_VFT_COLUMNS`) that must match firmware expectations.
- `#pragma pack(pop)` is inside a `!SMC_MICROCODE` conditional at the end while the push is unconditional, so build-context assumptions matter.

## Test Signals
- Compile and static layout checks for voltage bitfield packing, soft-register offsets, and firmware header offsets.
- Runtime evidence: AVFS VFT validity, FPS clamp updates, DPM residency counters, telemetry power readings, and clock-stretcher settings accepted by firmware.
