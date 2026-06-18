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
