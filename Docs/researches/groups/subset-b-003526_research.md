# Research: subset-b-003526 SMU powerplay interface headers

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu71_discrete.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu71_discrete.h

## Purpose
`smu71_discrete.h` is a packed host/SMC ABI header for SMU71 discrete GPUs. It specializes the generic `smu71.h` definitions into discrete-board voltage, clock, DPM, fan, fuse, logging, CAC, and scoreboard layouts that the powerplay driver can populate in memory for SMU firmware consumption.

## Important APIs, Types, And Constants
- Voltage routing flags `VDDC_ON_SVI2`, `VDDCI_ON_SVI2`, and `MVDD_ON_SVI2` identify SVI2-controlled rails.
- DPM level types include `SMU71_Discrete_VoltageLevel`, `GraphicsLevel`, `MemoryLevel`, `LinkLevel`, `ACPILevel`, `Ulv`, `UvdLevel`, and `ExtClkLevel`.
- `SMU71_Discrete_DpmTable` is the central table: it embeds PID controllers from `smu71.h`, voltage-level arrays, graphics/memory/link DPM arrays, SMIO masks, boot levels, intervals, DTE/BAPM coefficients, GPIO selectors, SVI2 enablement, power limits, TDP values, and thermal limits.
- Memory-controller programming is represented by `SMU71_Discrete_MCRegisters` and optional `SMU71_Discrete_MCArbDramTimingTable` under `SMU__DYNAMIC_MCARB_SETTINGS`.
- Runtime/telemetry state is modeled by scoreboards such as `SMU71_MclkDpmScoreboard`, `SMU71_UlvScoreboard`, `SMU71_VddGfxScoreboard`, and `SMU71_AcpiScoreboard`.
- `SMU71_Discrete_PmFuses` captures board calibration fuses for SIDD VIDs, load-line trims, TDC limits, LPML scaling, fuzzy fan deltas, and leakage bases.

## Control Flow And Data Flow
This header does not implement executable control flow. Its structures define the data flow between the host driver, VBIOS-derived tables, and SMU firmware. The expected sequence is: host discovers board capabilities, fills voltage/DPM/fan/MC/fuse tables, writes them to firmware-visible memory, then firmware interprets counts and boot indices to run local DPM, voltage, thermal, PCIe, ULV, and ACPI transitions.

## State And Persistence
All state is transient runtime state in SMU-visible RAM or firmware scratch space. Persistent inputs originate from VBIOS/fuse data but this header only defines their in-memory representation. `#pragma pack(push, 1)` is guarded by `SMC_MICROCODE`, making exact byte layout a contract between host C code and firmware.

## Dependencies And Integration Points
- Includes `smu71.h` for maximum counts, PID controller layout, and DTE dimensions.
- Integrates with AMD powerplay code that uploads DPM, fan, MC, CAC, and fuse tables.
- The scoreboard structs contain firmware-oriented function-pointer fields and must not be treated as normal host-callable callbacks unless compiled in the matching firmware context.

## Risks
- Any field insertion, type-size change, or pack mismatch breaks firmware offsets.
- Arrays depend on `SMU71_MAX_LEVELS_*`; count fields must be validated before firmware uses them.
- Conditional MCARB support changes exported type availability.
- Voltage rail/fuse values are hardware-sensitive; wrong units or rail routing can cause unstable clocks, throttling, or board damage.

## Test Signals
- Build both host and SMC contexts when available to catch packing and conditional-definition errors.
- Validate `sizeof` and key offsets against firmware/VBIOS expectations.
- Runtime signals include successful DPM table upload, stable SCLK/MCLK/PCIe transitions, fan response, ULV entry/exit counters, and CAC/power telemetry consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu71_discrete.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu72.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu72.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu72_discrete.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu72_discrete.h

## Purpose
`smu72_discrete.h` specializes `smu72.h` for discrete boards. It defines the packed DPM table and companion tables used to program SMU72 discrete SCLK, MCLK, PCIe, UVD/VCE/ACP/SAMU, ULV, fan, fuse, CAC, logging, and power status behavior.

## Important APIs, Types, And Constants
- SMIO definitions `SMIO_Pattern` and `SMIO_Table` map voltage phases and VID patterns.
- Level structs include `SMU72_Discrete_GraphicsLevel`, `ACPILevel`, `Ulv`, `MemoryLevel`, `LinkLevel`, `UvdLevel`, and `ExtClkLevel`.
- `SMU72_Discrete_DpmTable` combines PID controllers, rail-level arrays, DPM level arrays, VR config, boot levels, intervals, SVI2/GPIO selectors, DTE/BAPM fields, TDP/power limits, ULV config, and display CAC.
- MC programming is represented by `SMU72_Discrete_MCRegisters`; MCARB timing is represented by `SMU72_Discrete_MCArbDramTimingTable`.
- Runtime and diagnostics include `SMU7_MclkDpmScoreboard`, `SMU7_UlvScoreboard`, `VddgfxSavedRegisters`, `SMU7_VddGfxScoreboard`, TDC/pkg power/BAPM/ACPI scoreboards, log header/control tables, CAC collection/verification tables, and PM status tables.

## Control Flow And Data Flow
Host code populates this file's tables from VBIOS, fuse data, and policy settings, then points the firmware to them through the SMU72 firmware header. Firmware consumes count fields and boot indices to move between DPM states, using hysteresis, activity thresholds, thermal clamps, voltage requests, and PCIe thresholds to choose target levels.

## State And Persistence
The structures are firmware-resident state. Fan tables and fuses derive from board-persistent sources, but once copied they are mutable runtime inputs. Scoreboards track live state such as current/target levels, clamp modes, residency counters, ULV/VddGfx transitions, and power-limit status.

## Dependencies And Integration Points
- Includes `smu72.h`; relies on its `SMU72_MAX_LEVELS_*`, `SMU72_PIDController`, voltage encodings, clock-gating masks, and firmware header.
- Integrated by SMU72/Tonga-family powerplay setup paths that upload discrete DPM and fan tables.
- Interacts with mailbox messages from `smu7_ppsmc.h` for feature enablement, table upload, fan control, and telemetry.

## Risks
- This is a packed binary ABI. Even renaming is harmless, but reordering or changing widths is not.
- DPM count fields and array dimensions must remain consistent; firmware likely trusts counts.
- Several shared structs are named `SMU7_*`, which can hide version-specific layout differences from casual readers.
- Log/CAC/PM status buffers include host/firmware addresses; wrong address programming can corrupt memory or produce bogus telemetry.

## Test Signals
- `sizeof(SMU72_Discrete_DpmTable)` and offsets should match firmware symbols.
- Runtime tests should exercise boot levels, SCLK/MCLK/PCIe transitions, fan table programming, CAC collection, VddGfx save/restore, and AC/DC GPIO clamp behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu72_discrete.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu73.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu73.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu73_discrete.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu73_discrete.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu74.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu74.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu74_discrete.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu74_discrete.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu75.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu75.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu75_discrete.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu75_discrete.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu7_common.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu7_common.h

## Purpose
`smu7_common.h` is a small shared constants header for SMU7-family power management. It centralizes feature bit positions and masks used by the host driver and firmware-facing code to enable DPM, thermal, voltage, media, PCIe, display, and memory power-management features.

## Important APIs, Types, And Constants
- Defines feature bit positions such as `SMU7_SCLK_DPM_CONFIG_ID`, `SMU7_MCLK_DPM_CONFIG_ID`, `SMU7_UVD_DPM_CONFIG_ID`, `SMU7_VCE_DPM_CONFIG_ID`, `SMU7_ACP_DPM_CONFIG_ID`, `SMU7_SAMU_DPM_CONFIG_ID`, `SMU7_PCIEGEN_DPM_CONFIG_ID`, and other SMU7 feature selectors.
- Provides matching `SMU7_*_CONFIG_MASK` macros via bit shifts.
- The header is guarded by `SMU7_COMMON_H`.

## Control Flow And Data Flow
There is no executable control flow. Driver policy code uses these masks to compose feature-enable fields sent to SMU soft registers or SMC messages. Firmware reads the resulting bitmask to determine which controllers should run.

## State And Persistence
The header defines constants only. It has no storage, persistence, or runtime ownership.

## Dependencies And Integration Points
- Shared by SMU7-family implementation files that need feature-enable bitmasks.
- Integrates indirectly with `FeatureEnables` fields in SMU soft registers and DPM table programming.

## Risks
- Bit position changes are ABI changes for every firmware consumer.
- Duplicated mask names in generation-specific headers can diverge; consumers should include the intended generation header consistently.

## Test Signals
- Compile coverage for all SMU7-family users.
- Runtime feature enablement should match requested policy: enabling one mask must not toggle unrelated DPM blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu7_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu7_discrete.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu7_discrete.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu7_fusion.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu7_fusion.h

## Purpose
`smu7_fusion.h` defines SMU7 APU/fusion packed table layouts. It differs from discrete layouts by modeling shared CPU/GPU thermal entities, NB voltage, GIO/LCLK DPM, and fusion-specific clock breakdown rather than discrete memory voltage rails.

## Important APIs, Types, And Constants
- DTE dimensions are fusion-specific: 5 iterations, 5 sources, 3 sinks, 2 CPU TEs, 1 GPU TE, and 2 non-TEs.
- `SMU7_SoftRegisters` provides ref clock, PM timer, feature enables, handshake disables, display PHY configs, enabled DPM masks, log addresses, and ULV counters.
- Fusion level types include `SMU7_Fusion_GraphicsLevel`, `SMU7_Fusion_GIOLevel`, `SMU7_Fusion_UvdLevel`, `SMU7_Fusion_ExtClkLevel`, `SMU7_Fusion_ACPILevel`, `SMU7_Fusion_NbDpm`, and `SMU7_Fusion_StateInfo`.
- `SMU7_Fusion_DpmTable` contains system flags, graphics/GIO PID controllers, counts and arrays for graphics/media clocks, boot levels, intervals, graphics clock slow controls, display CAC, low-SCLK interrupt threshold, and DRAM log buffer addresses.
- `SMU7_Fusion_GIODpmTable` separately models LCLK/GIO levels, voltage changes, target/current state, thermal throttle status, and high/low temperature limits.

## Control Flow And Data Flow
Host code fills fusion DPM tables for integrated graphics and GIO, then firmware uses enabled level counts, NB voltage requirements, clock divider/bypass controls, and thermal throttle settings to select states. GIO has a separate target/current state path from graphics/media clocks.

## State And Persistence
Tables are volatile packed firmware state. There are no discrete rail fuse tables here; voltage policy centers on NB voltage and VID fields. DRAM log fields describe runtime buffers.

## Dependencies And Integration Points
- Includes `smu7.h`.
- Integrates with APU-specific powerplay code, display PHY configuration, UVD/VCE/ACP/SAMU media clock management, and NB/GIO DPM.
- Shares `SMU7_SoftRegisters` name with the discrete header but with a different layout, so the include path determines ABI.

## Risks
- Name reuse with `smu7_discrete.h` can cause accidental layout confusion.
- GIO/LCLK and NB fields have platform-specific semantics and should not be copied into discrete flows.
- Packed layout and count fields must match firmware; no runtime bounds protection is expressed here.

## Test Signals
- Compile fusion/APU configurations that include this header alone.
- Runtime: graphics and GIO DPM transitions, NB voltage changes, media clock levels, thermal throttle status, and display watermark behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu7_fusion.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu7_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu7_ppsmc.h

## Purpose
`smu7_ppsmc.h` defines the SMU7 powerplay SMC mailbox command and event ID namespace. It is the command contract used by the host driver to ask SMU firmware to initialize, upload tables, enable/disable features, adjust DPM and fan policy, query telemetry, and access secure register operations.

## Important APIs, Types, And Constants
- Defines response/status values such as success/failure/unknown-command style mailbox responses.
- The core `PPSMC_MSG_*` range includes initialization, DPM table loading, fan control, voltage and clock DPM enable/disable, UVD/VCE/ACP/SAMU/PCIe DPM controls, thermal controls, power limits, CAC/telemetry queries, and overdrive/fan target controls.
- Later ranges include BACO, VddGfx, microcode/VBIOS loading, DRAM address handoff, DMCU PSR, clock-gating, metadata, telemetry calibration, AVFS, AGM/PSM/VFT, CU power gating, DIDT/EDC/FFC/zero RPM, secure SRBM read/write, and generic address/data access.
- `typedef uint16_t PPSMC_Msg` establishes command ID width.
- Event status masks include thermal, regulator-hot, and DC events.

## Control Flow And Data Flow
Host control flow writes a `PPSMC_Msg` plus any argument to the SMC mailbox registers, waits for a response, and interprets firmware status. Data paths frequently require setup through table-memory addresses or prior soft-register writes before issuing commands such as table load, DPM enable, AVFS enable, or telemetry query.

## State And Persistence
The header stores no state. The message IDs mutate firmware runtime state when sent: enabling controllers, changing fan limits, loading tables, toggling AVFS/clock gating, updating power limits, or reading status. Persistence is firmware/session scoped unless command effects are backed by board policy elsewhere.

## Dependencies And Integration Points
- Used by all SMU7-family discrete/fusion implementation files that send SMC messages.
- Integrates with the table layouts in `smu7*.h`, `smu7*_discrete.h`, and later SMU72-SMU75 headers.
- Secure SRBM and address/data messages bridge powerplay with protected register access.

## Risks
- Command IDs are firmware ABI. Reusing an ID for a different semantic breaks every firmware version expecting the old command.
- Some commands are only valid on specific ASIC/firmware generations; callers must gate by firmware capability.
- Address high/low handoff commands must match DMA address width and ordering.
- Misspelled names such as calibration variants should not be "fixed" without checking external users and firmware symbols.

## Test Signals
- Build-time references should resolve to the intended IDs.
- Runtime mailbox tests: command accepted response, table load succeeds, telemetry commands return sane values, unsupported commands are handled gracefully, and feature toggles produce expected firmware state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu7_ppsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu8.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu8.h

## Purpose
`smu8.h` is a compact SMU8 firmware interface header. It defines the packed firmware header, multimedia power-log data, and key firmware/SRAM address constants for SMU8 platforms.

## Important APIs, Types, And Constants
- `ENABLE_DEBUG_FEATURES` enables debug-feature conditionals in consumers.
- `SMU8_Firmware_Header` contains digest, version, header size, flags, entry point, code/image sizes, and table pointers.
- `SMU8_MultimediaPowerLogData` captures multimedia block power/clock/activity logging fields.
- Address constants include `SMU8_FIRMWARE_HEADER_LOCATION`, `SMU8_UNBCSR_START_ADDR`, and `SMN_MP1_SRAM_START_ADDR`.

## Control Flow And Data Flow
Host code uses the firmware header location to locate metadata and table pointers in firmware memory. Power logging data flows from firmware instrumentation to host-readable buffers for multimedia blocks.

## State And Persistence
The header defines packed in-memory firmware metadata and log data only. No persistent state is owned here; firmware images and SRAM regions are discovered or addressed through constants.

## Dependencies And Integration Points
- Included by `smu8_fusion.h`.
- Integrated by SMU8 platform initialization, firmware loading, and multimedia power logging.
- Address constants couple this code to SMU8 memory maps.

## Risks
- Firmware header location and SRAM constants are platform ABI; wrong values break firmware discovery.
- The compact header leaves little self-description; consumers must know which table pointers are valid for their firmware.
- Packed layout must be preserved.

## Test Signals
- Firmware header read at `0x1FF80` returns expected signature/version fields.
- Runtime multimedia power logs are nonzero and correlated with UVD/VCE/ACP activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu8.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu8_fusion.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu8_fusion.h

## Purpose
`smu8_fusion.h` defines SMU8 fusion/APU-specific packed tables. It focuses on compute-unit power gating, port 80 monitoring, power-management separation settings, and clock breakdown tables for SCLK, LCLK, UVD, VCE/ECLK, ACP/ACLK, and related clocks.

## Important APIs, Types, And Constants
- CU constants: `SMU8_MAX_CUS`, `SMU8_PSMS_PER_CU`, and `SMU8_CACS_PER_CU`.
- `SMU8_GfxCuPgScoreboard` models graphics CU power-gating state.
- `SMU8_Port80MonitorTable` stores port 80 monitor values.
- `PWRMGT_*` shift/mask constants encode separation time and CPU C-state/P-state disable flags.
- Clock level counts include `NUM_SCLK_LEVELS`, `NUM_LCLK_LEVELS`, `NUM_UVD_LEVELS`, `NUM_ECLK_LEVELS`, and `NUM_ACLK_LEVELS`.
- `SMU8_Fusion_ClkLevel` and the SCLK/LCLK/ECLK/VCLK/DCLK/ACLK breakdown table structs are grouped by `SMU8_Fusion_ClkTable`.

## Control Flow And Data Flow
The driver or firmware fills clock breakdown arrays with frequency/divider data. Firmware uses the clock tables to select operating points for graphics, memory/GIO, and multimedia blocks. Power-management mask fields influence CPU state separation behavior on the APU.

## State And Persistence
Tables are volatile packed firmware-memory structures. Clock data may be derived from firmware/VBIOS policy but is represented here as runtime tables. Port 80 and CU PG scoreboards are runtime status/control structures.

## Dependencies And Integration Points
- Includes `smu8.h` for firmware header and address constants.
- Integrates with SMU8 APU powerplay setup, CU power gating, multimedia clock selection, and CPU power-state coordination.

## Risks
- Fixed level counts require producers to avoid overflow and fill unused entries deterministically.
- CPU P-state/C-state disable masks affect platform-wide power behavior.
- CU PG constants are small and platform-specific; using them for larger GPU configurations would be wrong.

## Test Signals
- Runtime clock table reads match expected frequencies for SCLK/LCLK/UVD/VCE/ACP.
- CU power-gating scoreboard changes with workload/idleness.
- CPU power-state coordination does not regress suspend/resume or multimedia playback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu8_fusion.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu9.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu9.h

## Purpose
`smu9.h` defines a compact SMU9 feature/workload/ULV interface. It enumerates the 32 firmware feature bits and masks for DPM, deep sleep, AVFS, PPT/TDC/thermal, display, fan, EDC, ACG, PCC limit control, plus workload and ULV client masks.

## Important APIs, Types, And Constants
- `ENABLE_DEBUG_FEATURES` is defined for debug feature paths.
- Feature bit macros run from `FEATURE_DPM_PREFETCHER_BIT` through spare bits, with `NUM_FEATURES` set to 32.
- Matching feature masks include `FFEATURE_*` names for most features and several `FEATURE_*_MASK` names for later features.
- Workload bits include VR, FRTC, video, and compute with `NUM_WORKLOADS`.
- ULV client masks cover RLC, UVD, VCE, SDMA0/1, JPEG, and DPM clients for GFXCLK, UVD, VCE, MP0CLK, UCLK, SOCCLK, and DCEFCLK.
- A packed anonymous typedef near the end defines a firmware-visible feature/status style table with bitmaps and enabled/running state fields.

## Control Flow And Data Flow
Host policy code composes feature masks and workload selections, sends them to firmware through SMU9 messaging paths, and firmware uses ULV client masks to decide when low-voltage states are blocked. The file itself has no functions; control is expressed through bitmask protocol.

## State And Persistence
Constants are stateless. The packed struct represents volatile firmware-visible state. Feature enablement survives only for the running firmware session unless re-applied at initialization/resume.

## Dependencies And Integration Points
- Used by SMU9 powerplay and firmware-management code.
- Integrates with later-generation SMU message interfaces, feature enable/disable commands, workload policy selection, and ULV/deep-sleep gating.

## Risks
- The `FEATURE_FAST_PPT_MASK`, `FEATURE_GFX_EDC_MASK`, and `FEATURE_ACG_MASK` definitions reference shift names without the visible `FEATURE_` prefix in this header; compilation depends on whether those names exist elsewhere or this is dead code.
- `FFEATURE_` versus `FEATURE_` mask naming is inconsistent and easy to misuse.
- Feature bit order is firmware ABI; reordering breaks host/firmware negotiation.
- ULV client masks must match firmware blockers or the GPU may enter ULV during active work.

## Test Signals
- Compile all SMU9 users to catch undefined mask-shift names.
- Runtime feature table query should report expected enabled/running bits.
- Workload switching should affect DPM policy, and ULV should stay blocked while media/compute/display clients are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu9.h -->
