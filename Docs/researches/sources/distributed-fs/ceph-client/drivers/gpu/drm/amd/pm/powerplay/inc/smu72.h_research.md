# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu72.h

## Purpose
`smu72.h` defines the common SMU72 firmware interface for a GCN powerplay generation. It supplies DPM level limits, shared power/CAC math types, firmware header layout, soft-register layout, scoreboards, clock-gating masks, voltage-regulator encodings, and clock-stretcher tables consumed by discrete and possibly fusion-specific headers.

## Important APIs, Types, And Constants
- Global DPM counts: `SMU__NUM_SCLK_DPM_STATE`, `SMU__NUM_MCLK_DPM_LEVELS`, `SMU__NUM_LCLK_DPM_LEVELS`, and `SMU__NUM_PCIE_DPM_LEVELS`.
- Version-specific maxima: `SMU72_MAX_LEVELS_VDDC`, `VDDGFX`, `VDDCI`, `MVDD`, graphics, memory, GIO, link, UVD, VCE, ACP, SAMU, and SMIO entries.
- Power modeling types include `SMU7_Poly3rdOrder_Data`, `PowerCalculatorData_t`, `GcCacWeight_Data`, `data_64_t`, and `data_128_t`.
- Runtime controllers and state include `SMU72_PIDController`, `SMU7_LocalDpmScoreboard`, `SMU7_VoltageScoreboard`, `SMU7_PCIeLinkSpeedScoreboard`, `SMU7_PowerScoreboard`, and `SMU7_ThermalScoreboard`.
- `SMU72_SoftRegisters` exposes host-programmed soft registers: ref clock, timer period, feature enables, display PHY configs, enabled DPM masks, DRAM log addresses, ULV counters, and microcode load status.
- `SMU72_Firmware_Header` points firmware consumers to RTOS, soft registers, DPM table, fan table, CAC tables, MC register table, MCARB table, fuse table, globals, and clock-stretcher table.

## Control Flow And Data Flow
The control path is data-driven. Host code uses the firmware header location `SMU72_FIRMWARE_HEADER_LOCATION` to discover table offsets, writes soft registers and tables, then sends SMC commands elsewhere. Firmware uses masks such as `SMU7_*_DPM_CONFIG_MASK`, scratch-register bitfields, and scoreboards to coordinate local DPM decisions, voltage changes, PCIe transitions, thermal clamp modes, and display/workload interactions.

## State And Persistence
Soft registers, scoreboards, and firmware header entries are volatile firmware-memory state. Fuse- and VBIOS-derived calibration values feed these structures but are not persisted here. The file conditionally packs only outside `SMC_MICROCODE`, so host and firmware builds must agree on layout.

## Dependencies And Integration Points
- Included by `smu72_discrete.h`.
- Depends on C fixed-width integer types provided by surrounding kernel includes.
- Interfaces with driver code that parses firmware headers, programs clock-gating bitmasks, selects VR modes via `VRCONF_*`, and configures clock stretcher data.

## Risks
- Some feature mask names are legacy SMU7 names even though the file is SMU72; callers must not infer a different ABI from naming alone.
- `VoltageChangeHandler_t` and pointer fields in scoreboards are not portable serialized data in normal host userspace terms.
- Incorrect `SMU72_Firmware_Header` offsets or signature handling can make the driver program the wrong firmware memory region.
- Clock-gating and VR bitfields are densely packed and easy to mis-mask.

## Test Signals
- Compile coverage for consumers such as `smu72_discrete.h`.
- Firmware header offset validation at `0x20000`.
- Runtime checks: enabled DPM masks match requested levels, scratch index fields update, voltage scoreboard reports expected rails, and clock-gating masks do not hang display or PCIe blocks.
