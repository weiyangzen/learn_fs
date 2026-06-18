# subset-b-003533 Research

Grouped research for AMD SMU PM firmware interface headers. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu14_driver_if_v14_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu14_driver_if_v14_0.h

## Purpose
Defines the SMU 14.0 power-play table and driver/shared-memory ABI for AMDGPU SW SMU. It is the full v14.0 PMFW driver interface: feature bits, DPM level counts, throttler and dstate masks, voltage/fuse/AVFS descriptors, PP table layout, board layout, driver config, metrics, watermark, I2C, ECC, overdrive, activity-monitor, table IDs, and firmware-to-driver interrupt context IDs.

## Important APIs, Types, And Constants
The ABI version is `PPTABLE_VERSION 0x1B`; changing `SkuTable_t` or `BoardTable_t` requires bumping it. Clock topology is exposed through `PPCLK_e` plus DPM array sizes such as 16 GFXCLK levels, 8 SOC/FCLK/display levels, 6 UCLK levels, and 3 PCIe link levels. Feature control uses 64 `FEATURE_*_BIT` positions and masks such as `ALLOWED_FEATURE_CTRL_DEFAULT` and `ALLOWED_FEATURE_CTRL_SCPM`. Major exported tables are `PPTable_t`, `PFE_Settings_t`, `SkuTable_t`, `CustomSkuTable_t`, `BoardTable_t`, `OverDriveTable_t`, `OverDriveLimits_t`, `DriverSmuConfigExternal_t`, `DriverInfoTable_t`, `SmuMetricsExternal_t`, `WatermarksExternal_t`, `SwI2cRequestExternal_t`, `EccInfoTable_t`, `AvfsDebugTableExternal_t`, and `DpmActivityMonitorCoeffIntExternal_t`.

## Control Flow
There are no functions, but the constants define firmware command flow. The host writes table contents into driver DRAM, points PMFW at that memory through PPSMC address messages, and transfers by `TABLE_*` IDs. Firmware consumes PP/board/driver config tables to initialize DPM, voltage, fan, power, GFXOFF/DCS, BACO, I2C, and AVFS behavior, then publishes telemetry through the SMU metrics table and asynchronous IH interrupt context IDs.

## State And Persistence
Most fields are persistent firmware policy state loaded from VBIOS or driver-supplied tables: SKU limits, board GPIO/I2C wiring, SVI3 regulator settings, DPM frequency tables, AVFS fuse overrides, overdrive limits, fan settings, and workload masks. Runtime state is exported in metrics counters, temperatures, voltages/currents, fan PWM/RPM, throttling percentages, energy accumulators, D3hot counters, ECC info, and table-transfer status codes. Padding and `MmHubPadding` fields are part of the binary ABI and must stay stable.

## Dependencies And Integration
This header is included by ASIC-specific SMU code and paired with v14 PPSMC message headers. It depends on fixed-width integer types supplied by the include chain and on firmware, VBIOS, DAL/display, RLC, MMHUB, power-management, overdrive, and I2C tooling agreeing on byte layout and enum values. Table IDs integrate directly with `SMC_MSG_TransferTableDram2Smu` and `SMC_MSG_TransferTableSmu2Dram`.

## Risks And Test Signals
The main risk is silent ABI drift: array size, enum order, packing, or padding changes can corrupt firmware interpretation. Feature bit mismatches can enable/disable the wrong power domain, and bad voltage/fan/thermal limits can cause throttling or safety issues. Test signals include driver-if version checks, table transfer return codes, SMU metrics sanity, overdrive validation errors, fan/thermal interrupt contexts, BACO/AC/DC IH events, I2C command success, and GPU suspend/resume/D3hot coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu14_driver_if_v14_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu14_driver_if_v14_0_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu14_driver_if_v14_0_0.h

## Purpose
Defines the lighter SMU 14.0.0 driver-interface table set used for display clocks, watermarks, custom DPM settings, DPM clocks, SMU metrics, workload bits, ISP tile selection, and table identifiers. This is a compact shared table ABI rather than a full PP table definition.

## Important APIs, Types, And Constants
Exports `FloatInIntFormat_t`, `DSPCLK_e`, `DisplayClockTable_t`, `WatermarkRowGeneric_t`, `Watermarks_t`, `WM_CLOCK_e`, `CUSTOM_DPM_SETTING_e`, `DpmActivityMonitorCoeffExt_t`, `CustomDpmSettings_t`, `MemPstateTable_t`, `DpmClocks_t`, `DpmClocks_t_v14_0_1`, `SmuMetrics_t`, and `TILE_NUM_e`. It fixes eight DPM levels for DCFCLK, DISPCLK, DPPCLK, SOCCLK, VCN, SOC voltage, VPE, and FCLK, with four memory p-states and four watermark ranges. Table IDs run from `TABLE_BIOS_IF` through `TABLE_SMU_METRICS`, with `TABLE_COUNT 8`.

## Control Flow
The driver and display stack use table transfer messages to exchange watermarks, custom DPM coefficients, DPM clock tables, and metrics. BIOS/VBIOS owns BIOS-facing tables, DAL uses watermarks through VBIOS, and tools can read momentary PM or modern standby logs.

## State And Persistence
DPM clock arrays and watermark rows are the firmware-visible state. `SmuMetrics_t` carries live telemetry such as average frequencies, activities, power, voltage/current, throttling percentage, temperatures, fan data, energy accumulator, and residency/counter fields. No local persistence exists outside the shared memory tables.

## Dependencies And Integration
Integrates with SMU 14 APU/display code, DAL/VBIOS watermark programming, SMF/PMF readers, and any code that selects ISP tiles via `ISP_TILE_SEL()` or workload masks. The `DpmClocks_t_v14_0_1` variant signals layout evolution that consumers must select by firmware/ASIC generation.

## Risks And Test Signals
Risks are off-by-one DPM arrays, using the wrong DPM clocks struct for the firmware generation, stale table IDs, and metrics consumers assuming fields that a firmware does not populate. Test signals include successful table transfers, correct display watermark behavior, sane DPM clock dumps, SMU metrics reads, and modern standby telemetry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu14_driver_if_v14_0_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu15_driver_if_v15_0_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu15_driver_if_v15_0_0.h

## Purpose
Defines the compact SMU 15.0.0 driver interface for display/power tables, DPM clocks, metrics, workload bits, ISP tile selection, and table IDs. It is very close to the SMU 14.0.0 compact interface but marks some table slots as unused for this generation.

## Important APIs, Types, And Constants
Exports the same core shared-memory types as the v14.0.0 compact interface: `FloatInIntFormat_t`, `DSPCLK_e`, `DisplayClockTable_t`, `Watermarks_t`, `CustomDpmSettings_t`, `MemPstateTable_t`, `DpmClocks_t`, `SmuMetrics_t`, and `TILE_NUM_e`. It fixes eight DPM levels for display/SOC/VCN/VPE/FCLK domains and four memory p-states. `TABLE_WATERMARKS` is retained but noted as no longer used for Medusa generation, while `TABLE_SPARE0` and `TABLE_SPARE1` reserve slots 5 and 6.

## Control Flow
Host-side SMU code transfers table IDs to firmware for BIOS information, custom DPM, GPIO config, DPM clocks, and SMU metrics. Metrics are read back by the driver and SMF/PMF, while DPM clocks are used by driver and VBIOS paths.

## State And Persistence
Persistent policy is limited to table content passed through the SMU shared-memory protocol. Runtime state appears in `SmuMetrics_t` fields for frequencies, activities, power, voltage/current, throttling, temperatures, fan state, energy, residency, and public serial data.

## Dependencies And Integration
Integrated with SMU 15 PMFW, VBIOS/BIOS table handoff, DAL/display clock code, SMF/PMF metrics readers, and ISP tile power messages. Consumers must not assume the v14.0.0 table slots retain identical semantics where the comments mark deprecation/spares.

## Risks And Test Signals
The main risks are generation mixups with SMU 14 headers, consumers still relying on deprecated watermark use, and telemetry layout drift. Test signals are table transfer success, DPM level dumps, metrics reads through debugfs/sysfs, VCN/VPE/display clock behavior, and suspend/resume stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu15_driver_if_v15_0_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu15_driver_if_v15_0_8.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu15_driver_if_v15_0_8.h

## Purpose
Defines auxiliary SMU 15.0.8 PMFW driver-interface structures for I2C command submission, MCA bank dump offsets, error-code decoding, AVFS debug tables, interrupt identifiers, throttler bits, and clear-on-read masks. It complements the main SMU 15 table and message headers.

## Important APIs, Types, And Constants
Exports I2C types `I2cControllerPort_e`, `I2cSpeed_e`, `I2cCmdType_e`, `SwI2cCmd_t`, `SwI2cRequest_t`, and `SwI2cRequestExternal_t` with `MAX_SW_I2C_COMMANDS 24`. Error-related APIs include `MCA_BANK_OFFSET_e`, `ERR_CODE_e`, and `GC_ERROR_CODE_e`. Clock/setting enums include `PPCLK_e`, `GpioIntPolarity_e`, and `UCLK_DPM_MODE_e`. Debug payloads are split into `AvfsDebugTableMid_t`, `AvfsDebugTableAid_t`, and `AvfsDebugTableXcd_t`.

## Control Flow
The driver submits an external I2C request table, firmware executes read/write command sequences, and response bytes are returned in the same table. MCA dump messages use `MCA_BANK_OFFSET_e` to select 64-bit registers. Interrupt context IDs identify thermal throttling and VFFLR events routed from PMFW to the driver.

## State And Persistence
The header carries transient command buffers and diagnostic state, not long-lived policy. AVFS debug structures expose per-block values, and clear-on-read masks control whether uncorrected/corrected/memory-hub poll state is consumed during dumps.

## Dependencies And Integration
Depends on SMU 15.0.8 PMFW messages that transfer driver tables and dump MCA/AVFS data. It integrates with kernel error handling/RAS paths, thermal throttling notification paths, SW I2C tooling, and AVFS diagnostics.

## Risks And Test Signals
Risks include malformed I2C command counts, incorrect MCA offset selection, and mismatched error-code interpretation between driver and firmware. Test signals are successful SW I2C transactions, expected MCA dump words, decoded GC/MCA errors, VFFLR interrupt handling, thermal throttling notifications, and AVFS debug table size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu15_driver_if_v15_0_8.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_0_7_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_0_7_ppsmc.h

## Purpose
Defines the SMU v11.0.7 PPSMC mailbox command ABI. It maps driver-visible message names to numeric PMFW command IDs and standard result codes.

## Important APIs, Types, And Constants
`PPSMC_VERSION` is `0x1`. Result constants are `OK`, `Failed`, `UnknownCmd`, `CmdRejectedPrereq`, and `CmdRejectedBusy`. Messages cover SMU/driver-if versioning, feature mask control, DRAM/tool table address setup, table transfer, PP table selection, BACO/D3/audio D3, clock soft/hard min/max, DPM queries, PCIe override, DRAM logging, workload masks, UCLK fast switch, voltage/video/DC max queries, GFXOFF, VCN/JPEG power, unload/reset, PPT limits, power-source notification, DC BTC, memory channel/width, Gemini, temperature/throttler masks, out-of-band monitor testing, MGPU fan boost, bad HBM page retirement, GPO/SMBUS, USB, and driver mode2 reset. `PPSMC_Message_Count` is `0x5E`.

## Control Flow
The driver writes a command ID plus argument to the SMU mailbox and waits for a result code. Some commands are paired setup/execute flows, especially setting high/low DRAM addresses before `TransferTable*`, and setting log address/size before logging.

## State And Persistence
Commands mutate PMFW runtime state: allowed/running feature masks, DPM bounds, power-gating state, BACO/D3 arming, table addresses, workload selection, PPT limits, memory configuration, retired page state, and fan boost limits. The header itself persists no state.

## Dependencies And Integration
Integrated with v11.0.7 ASIC SMU code, driver interface table headers, VCN/JPEG power-management code, BACO suspend/resume paths, RAS bad page handling, and overdrive/power limit interfaces.

## Risks And Test Signals
Numeric command drift is the key risk; a wrong ID can execute a different firmware action. High/low address ordering, busy retry handling, and unsupported command handling are also critical. Test signals include `GetSmuVersion`, `GetDriverIfVersion`, table-transfer status, feature-mask reads, GFXOFF/VCN/JPEG power tests, BACO resume, RAS page-retirement paths, and busy/prerequisite return coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_0_7_ppsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_0_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_0_ppsmc.h

## Purpose
Defines the original SMU v11.0 PPSMC command map and standard result codes for the driver-to-PMFW mailbox.

## Important APIs, Types, And Constants
Messages cover version queries, feature masks, table address/transfer, default/backup PP tables, system virtual DRAM addresses, BACO, D3 arming, clock min/max programming, DPM queries, PCIe override, deep-sleep DCEFCLK, workload/video controls, GFXOFF, VCN/JPEG power, MP1 unload/reset/shutdown preparation, PPT limits, AC/DC notification, BTC, DRAM logging, debug data, GFX DIDT, display count, memory channel and Gemini config, overdrive voltage curve queries, audio D3 PME, dummy pstate toggles, MGPU fan boost, dummy table addresses, and UMC firmware workaround query. `PPSMC_Message_Count` is `0x51`; `PPSMC_Result` is a `uint32_t`.

## Control Flow
All entries are mailbox IDs. The host sequences setup messages for tables/logging and then invokes transfer or start/stop actions. Query commands return values in the SMU response register, while mutating commands update firmware policy.

## State And Persistence
Runtime state includes allowed/enabled features, PP table selection, virtual address pointers, clock limits, workload mask, media power state, reset/shutdown preparation, power-source state, logging buffers, display/memory configuration, and overdrive query mode. Persistent state is only the ABI contract in firmware and driver.

## Dependencies And Integration
Used by SMU v11 dGPU support and paired with SMU v11 driver interface table definitions. It integrates with display, BACO, reset, VCN/JPEG, power limit, overdrive, debug, and UMC workaround paths.

## Risks And Test Signals
Risks include message holes and non-monotonic IDs such as `ArmD3`, confusing enabled versus running feature queries, and argument mismatch for overdrive curve selection. Test signals include version negotiation, feature readback, table transfer, power-gating smoke tests, reset/unload paths, and overdrive curve queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_0_ppsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_5_pmfw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_5_pmfw.h

## Purpose
Defines SMU v11.5 PMFW feature bit positions and the firmware status layout used by driver feature control and telemetry paths.

## Important APIs, Types, And Constants
Exports 60 `FEATURE_*_BIT` positions covering CCLK/FCLK/SOC/GFX/DCEFCLK/VCN/ISP/A55/CVIP DPM, fan/PPT/TDC/thermal/FIT/EDC, PLL power down, ULV/VDDOFF, C-state/CC6, deep sleep clocks, GFX temperature VMIN, S0i2/S0i3, low-power blocks, PSI/PROCHOT/STAPM, CPPC, OS C-states, ATHUB power gating, ECO deep C-state, and GFX EDC. `FwStatus_t` reports enabled features and key clock/voltage/power/temperature/activity fields.

## Control Flow
This header does not execute code. SMU messages enable features by bit position, and firmware updates `FwStatus_t` for driver reads.

## State And Persistence
Feature masks represent firmware runtime policy. `FwStatus_t` is runtime telemetry/state exported from PMFW, including clock frequencies, power/thermal values, activity, and status flags. No disk persistence is involved.

## Dependencies And Integration
Included by SMU v11.5 ASIC support and paired with `smu_v11_5_ppsmc.h` messages. Integrates with CPU/APU power management, graphics/media power gating, CPPC, fan/thermal control, and metrics readers.

## Risks And Test Signals
Feature-bit order must match firmware exactly. Adding or removing bits without updating `NUM_FEATURES` and feature masks can toggle the wrong feature. Test signals include enabled-feature readback, GFX/VCN/ISP/CVIP power transitions, CPPC and C-state behavior, thermal/fan telemetry, and SMU status table sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_5_pmfw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_5_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_5_ppsmc.h

## Purpose
Defines SMU v11.5 PPSMC command IDs for APU-oriented power, media, telemetry, and clock control.

## Important APIs, Types, And Constants
The command set includes GFXOFF enable/disable/allow/disallow, ISP tile power, VCN/JPEG/CVIP power, RLC notifications, clock soft/hard min/max for GFX/SOC/FCLK/VCN/ISP/CCLK, table address/transfer, mode2 reset, enabled feature query, post code, frequency queries, PPT/thermal/power/current/voltage/activity metrics, time constants, mitigation hysteresis, DRAM logging, DF pstate control, active WGP request/query, fast/slow PPT limits, and GFXOFF residency/status counters. `PPSMC_Message_Count` is `0x53`.

## Control Flow
The driver sends one mailbox command at a time; table transfers require address setup first, and logging requires address/buffer-size setup plus start/stop messages. Frequency and metrics getters read the response register.

## State And Persistence
Commands modify firmware runtime state such as media power gates, clock bounds, CCLK policy, DF pstate, PPT limits, logging configuration, active WGP request, and GFXOFF residency logging. Persistent state is limited to firmware-side policy until reset.

## Dependencies And Integration
Pairs with `smu_v11_5_pmfw.h`, display/media code, reset/TDR handling, PM metrics, CCLK/DF pstate management, and GFXOFF residency diagnostics.

## Risks And Test Signals
Risks include sending unsupported media-tile commands on the wrong ASIC, failing to retry busy results, and misinterpreting units for frequency and PPT percentages. Test signals include version checks, table transfer, media power up/down, mode2 reset, GFXOFF counters, DRAM logging, and fast/slow PPT limit readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_5_ppsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_8_pmfw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_8_pmfw.h

## Purpose
Defines SMU v11.8 PMFW feature bits, generated feature masks, and firmware status layout for a CPU/GFX-focused SMU generation.

## Important APIs, Types, And Constants
Exports 64 feature bits covering CCLK controller, GFX effective frequency, data calculation, thermal, PLL power down, FCLK/GFX/SOC DPM, deep-sleep clocks, core C-states, G6 SSC, STAPM, PROCHOT/CPUOFF, GFX CKS, UMC/DF throttling, SOC DPM, and related low-power controls. It also defines `FEATURE_*_MASK` helpers and `FwStatus_t`.

## Control Flow
The header is declarative. SMU message handlers use the bit positions to enable/query features, while the driver reads `FwStatus_t` to observe current firmware state.

## State And Persistence
Feature masks are runtime PMFW state. `FwStatus_t` contains firmware telemetry and control state such as enabled features, clock/frequency values, power/thermal information, and status counters. The state resets with firmware/device reset.

## Dependencies And Integration
Used by SMU v11.8 support and paired with `smu_v11_8_ppsmc.h`. Integrates with core pstate, GFXCLK, telemetry reporting, WGP control, CAC weight handling, GFX frequency/VID forcing, and feature readback paths.

## Risks And Test Signals
Risks are feature-bit ABI mismatch and mask width mistakes across 64 bits. Test signals include enabled-feature masks, telemetry reporting start/stop, pstate query/request results, GFX frequency/VID force/unforce, and thermal/prochot behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_8_pmfw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_8_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_8_ppsmc.h

## Purpose
Defines SMU v11.8 PPSMC mailbox commands for core pstate, GFXCLK, telemetry, WGP, CAC weights, soft CCLK bounds, and GFX frequency/VID control.

## Important APIs, Types, And Constants
Standard result constants are present. Command IDs include driver table address high/low, table transfers, core pstate request/query, GFXCLK request/query, VDDCR_SOC clock query, DF pstate query, S3 power-off register configuration, active WGP request/query, telemetry reporting start/stop/clear max, core enable mask, GC RSMU soft reset, GFX/L3 CAC weight operations, driver table VMID, CCLK soft min/max, GFX frequency and VID get/force/unforce, and enabled feature query. `PPSMC_Message_Count` is `0x3E`.

## Control Flow
Commands are mailbox operations. Table and S3 register commands require address high/low ordering; telemetry commands toggle ongoing firmware reporting; force/unforce commands alter GFX frequency/VID state until released.

## State And Persistence
Runtime state includes driver table pointer/VMID, requested pstates, telemetry reporting state, active WGP/core masks, CAC weights, CCLK bounds, and forced GFX frequency/VID. State is firmware-resident and volatile.

## Dependencies And Integration
Pairs with `smu_v11_8_pmfw.h` and integrates with CPU core pstate control, graphics frequency management, telemetry consumers, soft reset paths, and CAC/power tuning code.

## Risks And Test Signals
Risks include leaving forced GFX frequency/VID active, wrong VMID/table address programming, and command ID gaps marked reserved. Test signals include version checks, table transfer, telemetry report lifecycle, pstate query, active WGP query, force/unforce round trips, and soft reset handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v11_8_ppsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v12_0_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v12_0_ppsmc.h

## Purpose
Defines SMU v12.0 PPSMC command IDs for power-gating, clocks, display/video policy, table transfer, reset, overdrive, and diagnostics.

## Important APIs, Types, And Constants
Messages cover GFX/ISP/VCN/SDMA power, GFXOFF enable/disable, hard-min clocks for ISP/VCN/DCFCLK/other domains, FCLK switch policy, video FPS, display count, power-limit query, driver DRAM address and table transfer, GFX reset, GFXCLK overdrive by frequency/VID, workload/custom policy, metrics and thermal/power/voltage/current queries, logging, and clock bounds. `PPSMC_Message_Count` is `0x40`.

## Control Flow
The driver sends numeric mailbox commands and interprets standard result codes. Address setup precedes transfers; query commands use the response register; power-up/down commands gate media or graphics blocks.

## State And Persistence
The commands update runtime PMFW policy: clock minimums, media/GFX power state, custom policy/workload state, overdrive settings, logging buffers, and reset preparation. State is not persisted outside firmware lifetime.

## Dependencies And Integration
Integrated with SMU v12 ASIC power management, display/video policy, media power-gating, overdrive, and reset/TDR paths.

## Risks And Test Signals
Risks include using obsolete display-count semantics, incorrect units for frequency/VID, and mismatched table transfer IDs. Test signals include media/GFX power transitions, FCLK switch behavior, table transfer status, reset path execution, and overdrive readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v12_0_ppsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_0_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_0_ppsmc.h

## Purpose
Defines SMU v13.0.0 PPSMC command IDs for a broad dGPU PMFW mailbox ABI.

## Important APIs, Types, And Constants
`PPSMC_VERSION` is `0x1`. Commands include version and driver-if checks, feature masks, driver/tool DRAM addresses, table transfer/default PP table, BACO/D3/audio, clock soft/hard bounds and DPM queries, PCIe override, DRAM logging, workload mask, voltage/video/DC max queries, GFXOFF, VCN/JPEG power, unload/mode1 reset, PPT limits, AC/DC notification, DC BTC, virtual DRAM addresses, temperature/throttler/FW dstate masks, external DF cstate allow, MGPU fan boost, STB dump/logging, GPO/DCS/audio stutter, UMSCH power, DCS arch, VFFLR, bad memory page retirement, IH interrupt allow, and UCLK shadow enable. `PPSMC_Message_Count` is `0x52`.

## Control Flow
Mailbox control is sequential. Multi-step flows include address setup plus transfer, STB/DRAM log setup plus dump, and feature-mask programming plus readback. Reset, VFFLR, and power-gating commands have prerequisites enforced by PMFW result codes.

## State And Persistence
Runtime state includes feature masks, power states, DPM bounds, workload, logging buffers, PPT/power-source policy, dstate/throttler masks, DCS configuration, bad-page counts, and interrupt allowance. It is volatile firmware state.

## Dependencies And Integration
Pairs with SMU v13 driver interfaces and PMFW feature definitions. Integrates with BACO, RAS bad memory retirement, UMSCH/media power, dynamic clock switching, VFFLR, STB tracing, and IH interrupt routing.

## Risks And Test Signals
Risks are ABI drift in command numbers, missing high/low address setup, and enabling reset/VFFLR/DCS commands on unsupported firmware. Test signals include version negotiation, table/STB transfers, feature mask readback, BACO and mode1 reset tests, VCN/JPEG/UMSCH power tests, RAS page retirement, and IH interrupt delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_0_ppsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_12_pmfw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_12_pmfw.h

## Purpose
Defines PMFW metrics and static-info structures for SMU v13.0.12, including packed system, VF, FRU, and static metrics layouts used by host tools and drivers.

## Important APIs, Types, And Constants
The file exports DPM and link-count constants, `FEATURE_LIST_e`, `PCIE_LINK_SPEED_INDEX_TABLE_e`, `GFX_GUARDBAND_OFFSET_e`, `GFX_DVM_MARGIN_e`, temperature and power enums, `MetricsTable_t`, `SystemMetricsTable_t`, `VfMetricsTable_t`, `FRUProductInfo_t`, and `StaticMetricsTable_t`. `SMU_METRICS_TABLE_VERSION` is `0x15`, `SMU_SYSTEM_METRICS_TABLE_VERSION` is `0x1`, and `SMU_VF_METRICS_TABLE_VERSION` is `0x6` ORed with the VF mask bit.

## Control Flow
The driver requests metrics tables from PMFW and decodes the packed/aligned structures. Static tables describe capabilities and topology, while metrics tables report live clocks, temperatures, powers, activity, throttling, link states, XGMI/CXL/PCIe information, and partition/VF data.

## State And Persistence
Metrics are live firmware snapshots. Static metrics and FRU info are stable for the boot/device, while live fields change on each transfer. The packed layout is persistent as an ABI contract even though values are volatile.

## Dependencies And Integration
Integrated with SMU v13.0.12 server/datacenter GPU code, SR-IOV/VF metrics readers, FRU inventory paths, performance monitoring, hwmon, debugfs, and link/partition management.

## Risks And Test Signals
Risks include structure packing/alignment drift, version mismatch, interpreting VF tables as physical-function metrics, and stale enum order for temperature/power arrays. Test signals include metrics table version checks, struct size checks, plausible power/thermal/clock values, VF metrics reads, FRU field decoding, and PCIe/XGMI/CXL link telemetry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_12_pmfw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_12_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_12_ppsmc.h

## Purpose
Defines SMU v13.0.12 PPSMC mailbox commands for modern dGPU/datacenter PMFW control.

## Important APIs, Types, And Constants
Messages include versioning, feature masks, driver/tool DRAM address setup, table transfer/default PP table, BACO/D3/audio, DPM min/max queries, PCIe override, DRAM logging, workload/video/DC max queries, GFXOFF, VCN/JPEG power, unload/mode resets, PPT/power-source, DC BTC, virtual DRAM addresses, temperature/throttler/dstate masks, DF cstate, MGPU fan boost, STB dump/logging, profiling, DCS, audio stutter, UMSCH power, VFFLR, bad memory page retirement, priority delta gain, IH interrupt allow, shadow DPM, 64-bit address transfer variants, all-feature query, SVI3 voltage, policy update, external power connector support, and UCLK overdrive preload. `PPSMC_Message_Count` is `0x61`.

## Control Flow
Classic high/low address messages and newer single-address/with-address transfer messages both exist, so the driver must choose the flow expected by firmware. Commands return standard PPSMC result codes and may require retry on busy.

## State And Persistence
Commands manipulate volatile firmware policy: feature masks, table pointers, power gates, DPM bounds, tracing buffers, policy updates, retired-page flags, interrupt permissions, and external power connector state.

## Dependencies And Integration
Pairs with `smu_v13_0_12_pmfw.h` metrics, RAS, STB tracing, VFFLR, power connector support, UMSCH/media control, DCS, and policy-management code.

## Risks And Test Signals
Risks include choosing the wrong table-address protocol, unsupported policy/update commands, and incorrect bad-page flag packing. Test signals include driver-if version, table transfer, all-running-feature readback, SVI3 voltage query, STB dump, VFFLR handling, RAS retirement updates, and external power connector reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_12_ppsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_1_pmfw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_1_pmfw.h

## Purpose
Defines SMU v13.0.1 PMFW feature bits and `FwStatus_t` for feature control and status reporting.

## Important APIs, Types, And Constants
Exports 61 feature bit positions covering CCLK/fan/data/PPT/TDC/thermal/FIT/EDC, PLL/ULV/VDDOFF, VCN/FCLK/SOC/MP0/LCLK/SHUB/DCF/GFX DPM, deep sleep, GFX temp VMIN, zstates/whisper, low-power blocks, PSI/PROCHOT/STAPM/S0i3, DF light/cstates, CPPC preferred cores, SmartShift, voltage monitor, ATHUB PG, VDDOFF/Zstates ECO, CC6, and UMCCLK/HSPCLK deep sleep. `FwStatus_t` carries enabled features and live firmware status.

## Control Flow
Feature bit positions are consumed by PPSMC feature-mask messages; status is read through firmware table transfer or status queries. There are no functions.

## State And Persistence
Feature masks are runtime PMFW state. `FwStatus_t` is a volatile status snapshot that reflects enabled features and current PM telemetry/control state.

## Dependencies And Integration
Used by SMU v13.0.1 ASIC support and paired with its PPSMC message map. It integrates with APU low-power states, CPPC/SmartShift, media power management, GFX/SOC clock management, and thermal/power status consumers.

## Risks And Test Signals
Risks are feature-bit reorder, stale `NUM_FEATURES`, and incorrect assumptions across v13 variants. Test signals include enabled-feature readback, zstate/S0i3 behavior, SmartShift reporting, VCN/GFX DPM operation, and status table sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_1_pmfw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_1_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_1_ppsmc.h

## Purpose
Defines SMU v13.0.1 PPSMC command IDs for a compact PMFW command ABI.

## Important APIs, Types, And Constants
`PPS_PMFW_IF_VER` is `1.0`. Commands cover PMFW and driver-if version reads, VCN power, GFX soft min, unload preparation, table transfer, mode2 reset, enabled-feature query, FCLK/VCN/SOC clock bounds, GFX IMU, GFXOFF allow/disallow, JPEG power, zstates, SmartShift status, and related media controls. `PPSMC_Message_Count` is `0x29`. `Mode_Reset_e` defines the reset argument for `PPSMC_MSG_GfxDeviceDriverReset`.

## Control Flow
The host submits a mailbox ID and optional argument; table transfer uses PMFW-managed table address conventions for this generation. Mode reset commands use the enum argument to select reset type.

## State And Persistence
Runtime state includes media power-gate state, clock min/max requests, GFXOFF permission, zstate permission, SmartShift status query, and table transfer state. It resets with PMFW/device reset.

## Dependencies And Integration
Pairs with `smu_v13_0_1_pmfw.h`, media power management, GFX reset/TDR handling, SmartShift, and clock limit paths.

## Risks And Test Signals
Risks include treating this compact command set like the larger dGPU v13 maps and sending absent feature/table-address commands. Test signals include version reads, VCN/JPEG power tests, mode2 reset, enabled feature query, GFXOFF allow/disallow, and zstate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_1_ppsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_4_pmfw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_4_pmfw.h

## Purpose
Defines SMU v13.0.4 PMFW feature bits and `FwStatus_t`, adding ISP/IPU-related DPM and v13.0.4-specific low-power controls.

## Important APIs, Types, And Constants
Exports 59 feature bits for fan/data/PPT/TDC/thermal/FIT/EDC, VDDOFF, VCN/FCLK/SOC/MP0/LCLK/SHUB/DCF/ISP/IPU/GFX DPM, deep-sleep clocks, zstates/whisper, SMU/fuse/GFX DEM, PSI/PROCHOT/STAPM/S0i3, DF light/cstates, DVO, CPPC, FASTBYPASS CLDO, ATHUB PG, VDDOFF/Zstates ECO, CC6, UMCCLK/ISPCLK/HSPCLK/IPUCLK deep sleep, and MPCCX whisper mode.

## Control Flow
The file supplies bit positions for feature-mask commands and a firmware status structure for reads. It has no functions.

## State And Persistence
Feature masks control volatile firmware policy. `FwStatus_t` is live PMFW state and telemetry. The bit order is a persistent ABI contract for this ASIC generation.

## Dependencies And Integration
Used by SMU v13.0.4 support and paired with its PPSMC commands. It integrates with ISP/IPU power/clock management, DVO, CPPC, GFX/media power, and low-power state handling.

## Risks And Test Signals
Risks include cross-using v13.0.1/v13.0.5 feature maps, especially where bit 44 semantics differ, and stale `NUM_FEATURES`. Test signals include feature-mask readback, ISP/IPU DPM behavior, VCN/GFX DPM, DVO/CPPC paths, zstate/S0i3, and status telemetry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_4_pmfw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_4_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_4_ppsmc.h

## Purpose
Defines SMU v13.0.4 PPSMC command IDs for media, clocks, ISP tile power, zstates, VPE/LSDMA, and MALL power control.

## Important APIs, Types, And Constants
`PPS_PMFW_IF_VER` is `1.0`. Commands cover PMFW/driver-if version, VCN power, GFX soft min/max/hard min, table address/transfer, mode2 reset, enabled-feature query, SOC/FCLK/VCN bounds, GFX IMU, GFXOFF allow/disallow, JPEG power, zstate allow, ISP tile power and hard-min clocks, UMSCH power, ISP stutter/MMHUB PG toggles, VPE power/DPM table/clock bounds, LSDMA enable/disable, and MALL power controller/state. `PPSMC_Message_Count` is `0x31`; argument enums include `Mode_Reset_e` and `ZStates_e`.

## Control Flow
Mailbox commands mutate PMFW state or return values. ISP tile arguments use tile masks, reset commands use `Mode_Reset_e`, and zstate commands use `ZStates_e`.

## State And Persistence
Runtime state includes VCN/JPEG/ISP/VPE/UMSCH power gates, clock bounds, GFXOFF/zstate permissions, MALL power state, LSDMA enablement, and table contents. State is volatile.

## Dependencies And Integration
Pairs with `smu_v13_0_4_pmfw.h`, ISP/IPU/display code, VPE/LSDMA support, media scheduler power, GFX reset, and MALL power management.

## Risks And Test Signals
Risks include incorrect tile masks, using v14/v15 VCN instance commands on this map, and missing reset/zstate argument validation. Test signals include table transfer, ISP tile power transitions, VPE DPM table reads, LSDMA toggles, MALL state changes, GFX reset, and GFXOFF/zstate smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_4_ppsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_5_pmfw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_5_pmfw.h

## Purpose
Defines SMU v13.0.5 PMFW feature bits and `FwStatus_t` for another v13 APU/server variant with a distinct feature ordering.

## Important APIs, Types, And Constants
Exports 50 feature bits covering data/PPT/TDC/thermal/FIT/EDC, C-state boost, PROCHOT, CCLK/FCLK/LCLK/GFX/SOC/SHUB/MP0/DCF/VCN DPM, PSI7/DLDO, deep sleep, DVO, CC6/PC6/per-CCX PC6, DF cstates/light cstate, clock gating, fan controller, CPPC/preferred cores, GMI/XGMI controls, PCIe speed controller, PCC, S0i3, VDDOFF, ATHUB PG, and GFXOFF. `FwStatus_t` reports enabled features and live status.

## Control Flow
Feature masks are programmed or queried by PPSMC commands; status is read from firmware. There are no functions.

## State And Persistence
Feature bitmasks and status fields are volatile PMFW state. The enum order and `NUM_FEATURES 50` are persistent ABI definitions shared by driver and firmware.

## Dependencies And Integration
Pairs with `smu_v13_0_5_ppsmc.h` and integrates with CCLK/FCLK/LCLK/GFX/SOC clock control, PCIe speed control, CPPC, fan/thermal, and GFXOFF policy.

## Risks And Test Signals
Risks are variant confusion with other v13 feature maps and assumptions that low-numbered bits match older APUs. Test signals include enabled-feature readback, CCLK/FCLK/GFX DPM behavior, PCIe speed control, GFXOFF state, fan/thermal readings, and CPPC operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_5_pmfw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_5_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_5_ppsmc.h

## Purpose
Defines the compact SMU v13.0.5 PPSMC command map.

## Important APIs, Types, And Constants
Commands cover SMU/PMFW versioning, driver-if version, table transfer, GFX reset, enabled-feature query, soft min/max GFX/FCLK/SOC/VCN clocks, GFX IMU, GFXOFF allow/disallow, VCN/JPEG power, SmartShift status, and VPE/UMSCH-related control. `PPSMC_Message_Count` is decimal `27`, and `Mode_Reset_e` supplies the reset argument.

## Control Flow
Each entry is a mailbox command. Reset commands require an enum argument; query commands return the mailbox response value; media power commands toggle firmware-managed gates.

## State And Persistence
Runtime state includes table contents, clock bounds, GFXOFF permission, media power gates, SmartShift query state, and reset requests. It is volatile firmware state.

## Dependencies And Integration
Pairs with `smu_v13_0_5_pmfw.h`, media power, GFX reset/TDR, SmartShift, and clock policy code.

## Risks And Test Signals
Risks include the decimal message count, compact command coverage compared with other v13 files, and missing table-address setup assumptions. Test signals include version checks, table transfer, GFX reset, enabled features, VCN/JPEG power, and clock min/max readback through behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_5_ppsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_6_pmfw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_6_pmfw.h

## Purpose
Defines SMU v13.0.6 PMFW metrics structures and static metrics for a datacenter/server GPU generation.

## Important APIs, Types, And Constants
Exports DPM/link-count constants, `FEATURE_LIST_e`, `PCIE_LINK_SPEED_INDEX_TABLE_e`, `GFX_GUARDBAND_e`, packed `MetricsTableV0_t`, `MetricsTableV1_t`, `MetricsTableV2_t`, `VfMetricsTable_t`, and `StaticMetricsTable_t`. `SMU_METRICS_TABLE_VERSION` is `0x11` and `SMU_VF_METRICS_TABLE_VERSION` is `0x5`.

## Control Flow
Driver code transfers metrics tables from PMFW and chooses the expected layout/version. The metrics versions capture live clocks, temperatures, power, utilization, link state, throttling, and partition/VF information, while static metrics describe immutable hardware/topology information.

## State And Persistence
Metrics values are live snapshots; static metrics are boot/device-stable. Packed and aligned structure layout is the persistent ABI and must match firmware exactly.

## Dependencies And Integration
Integrates with SMU v13.0.6 monitoring, hwmon, debugfs, RAS/performance tooling, SR-IOV VF reporting, PCIe/XGMI/CXL link telemetry, and management utilities.

## Risks And Test Signals
Risks include selecting the wrong metrics version, struct packing drift, and interpreting VF tables as PF tables. Test signals include version checks, expected struct sizes, plausible telemetry values under load/idle, VF metrics reads, and link telemetry consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_6_pmfw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_6_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_6_ppsmc.h

## Purpose
Defines SMU v13.0.6 PPSMC commands for datacenter/server GPU control, table transfer, resets, tracing, RAS, and policy.

## Important APIs, Types, And Constants
The command map includes versioning, feature masks, table addresses/transfers, default PP table, BACO/D3/audio, clock min/max and DPM queries, PCIe override, DRAM logging, workload/video/DC max, GFXOFF, VCN/JPEG, unload/mode1 reset, PPT/power-source, DC BTC, virtual DRAM addresses, dstate/throttler masks, external DF cstate, MGPU fan boost, STB dump/log setup, GPO/DCS/audio stutter, UMSCH power, DCS arch, VFFLR, bad memory page retirement, priority delta gain, IH interrupt allow, and additional datacenter-oriented controls. `PPSMC_Message_Count` is `0x5C`.

## Control Flow
Mailbox control is sequential and result-code based. Table/logging/STB flows have address and size setup before transfer/dump; reset/VFFLR/RAS commands require firmware prerequisites.

## State And Persistence
Firmware runtime state includes feature masks, table pointers, DPM bounds, tracing buffers, power gates, reset state, bad-page retirement state, policy knobs, and interrupt routing.

## Dependencies And Integration
Pairs with `smu_v13_0_6_pmfw.h` metrics, RAS, STB tracing, VFFLR, media/UMSCH power, DCS, IH interrupt routing, and datacenter GPU management paths.

## Risks And Test Signals
Risks include command-ID differences from v13.0.0/v13.0.7, mishandled STB/log buffers, and unsupported reset/RAS commands. Test signals include driver-if version, table transfer, metrics availability, STB dump, VFFLR, bad page retirement, feature readback, and media power transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_6_ppsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_7_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_7_ppsmc.h

## Purpose
Defines SMU v13.0.7 PPSMC command IDs for another v13 dGPU mailbox ABI.

## Important APIs, Types, And Constants
`PPSMC_VERSION` is `0x1`. Commands closely follow the v13 dGPU family: versioning, feature masks, DRAM/tool addresses, table transfers/default PP table, BACO/D3/audio, clock soft/hard bounds and queries, PCIe override, DRAM logging, workload/video/DC max, GFXOFF, VCN/JPEG, unload/mode1 reset, PPT/power source, DC BTC, virtual DRAM, temperature/throttler/dstate masks, DF cstate, MGPU fan boost, STB dump/logging, GPO/DCS/audio stutter, UMSCH, VFFLR, bad memory page retirement, priority delta gain, IH interrupt allow, and UCLK shadow. `PPSMC_Message_Count` is `0x52`.

## Control Flow
Commands are sent through the PMFW mailbox with standard result handling. Address setup and transfer commands must be ordered, while power/reset/RAS commands depend on current firmware state.

## State And Persistence
Runtime firmware state includes feature masks, table/logging pointers, DPM and power limits, media/GFX power state, dstate/throttler masks, STB tracing buffers, RAS retirement fields, and interrupt permissions.

## Dependencies And Integration
Integrates with v13.0.7 ASIC SMU code, PP table/metrics headers, BACO, DCS, VCN/JPEG/UMSCH power, RAS, VFFLR, STB tracing, and IH interrupt paths.

## Risks And Test Signals
Risks are subtle ID differences from neighboring v13 variants and failure to handle busy/prerequisite result codes. Test signals include version and feature readback, table transfer, mode1 reset, BACO, STB dump, media power, RAS bad-page update, and IH interrupt delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v13_0_7_ppsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v14_0_0_pmfw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v14_0_0_pmfw.h

## Purpose
Defines SMU v14.0.0 PMFW feature bits, firmware image header/footer types, and firmware status layouts for v14.0.0 and v14.0.1.

## Important APIs, Types, And Constants
Exports 63 feature bits covering CCLK/fan/data/PPT/TDC/thermal/FIT/EDC, VDDOFF, VCN0/1, MPM/MPIO, FCLK/SOC/LCLK/SHUB/DCF/ISP/IPU/GFX/VPE DPM, low-power DCN clocks, zstates/IOMMUL2 PG, deep-sleep clocks, whisper/SMU low power, GFX DEM, PSI/PROCHOT/STAPM/S0i3, DF light/cstates, DVO, CPPC/preferred cores, CLDO, ATHUB PG, VDDOFF/Zstates ECO, CC6, DS_UMCCLK/ISPCLK/HSPCLK/IPU/VPE, Smart L3, and PCC. `SMU_Firmware_Header`, `SMU14_Firmware_Footer`, `FwStatus_t`, and `FwStatus_t_v14_0_1` define packed firmware/status metadata.

## Control Flow
The feature bits drive PPSMC feature queries and controls. Firmware header/footer structs are parsed when validating or loading PMFW images, while status structs are read back from PMFW shared state.

## State And Persistence
Feature masks and status fields are runtime state. Firmware header/footer fields are persistent image metadata. Distinct status variants preserve ABI compatibility across v14.0.0 and v14.0.1.

## Dependencies And Integration
Includes `smu14_driver_if_v14_0_0.h` and pairs with v14 PPSMC headers. Integrates with firmware loading/validation, feature enablement, status reporting, media/display/IPU/VPE power, CPPC, and low-power state handling.

## Risks And Test Signals
Risks include using the wrong status struct for v14.0.1, feature bit comments that differ by subgeneration, and firmware image metadata mismatch. Test signals include firmware header parsing, enabled-feature readback, status table sanity, VCN/IPU/VPE power tests, CPPC/zstate/S0i3 behavior, and driver-if version negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v14_0_0_pmfw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v14_0_0_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v14_0_0_ppsmc.h

## Purpose
Defines SMU v14.0.0 PPSMC command IDs and argument enums for the v14 PMFW mailbox.

## Important APIs, Types, And Constants
`PPS_PMFW_IF_VER` is `1.0`. Commands include PMFW/driver-if version, separate VCN0/VCN1 and JPEG0/JPEG1 power, VCN hard/soft clock bounds, GFX/SOC/FCLK min/max, unload preparation, driver DRAM address high/low, table transfers, GFX mode2 reset, enabled-feature query, GFX IMU, GFXOFF allow/disallow, zstate allow, ISP tile power and hard mins, UMSCH power, ISP stutter/MMHUB PG toggles, VPE power/DPM table/clock bounds, LSDMA, and MALL power controller/state. `PPSMC_Message_Count` is `0x3A`; `Mode_Reset_e` and `ZStates_e` define command arguments.

## Control Flow
The driver sends mailbox IDs with optional arguments. VCN/JPEG commands are instance-specific, table transfers require DRAM address setup, and reset/zstate commands require enum arguments.

## State And Persistence
Commands mutate volatile PMFW state: media/ISP/VPE/UMSCH/LSDMA/MALL power, clock bounds, GFXOFF/zstate permissions, table pointers, and reset state.

## Dependencies And Integration
Pairs with `smu_v14_0_0_pmfw.h` and compact v14 driver interface tables. Integrates with display/ISP/VPE/media scheduler power, MALL, GFX reset, firmware feature readback, and table transfer code.

## Risks And Test Signals
Risks include confusing instance-specific VCN/JPEG commands with single-instance generations, wrong tile masks, and stale table-address handling. Test signals include PMFW/driver-if version, table transfer, VCN0/1 and JPEG0/1 power, VPE DPM table, MALL state, LSDMA toggle, GFX reset, and zstate/GFXOFF behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v14_0_0_ppsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v14_0_2_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v14_0_2_ppsmc.h

## Purpose
Defines SMU v14.0.2 PPSMC commands, extending the v13-style dGPU command map with newer address-transfer, policy, SVI3, and external power connector controls.

## Important APIs, Types, And Constants
`PPSMC_VERSION` is `0x1`. Commands include versioning, feature masks, driver/tool addresses, table transfer/default PP table, BACO/D3/audio, clock soft/hard limits and DPM queries, PCIe override, DRAM logging, workload/video/DC max, GFXOFF, VCN/JPEG, unload, virtual DRAM, PPT/power-source, DC BTC, temperature/throttler/dstate masks, external DF cstate, MGPU fan boost, STB dump/logging, OBM trace logging, profiling mode, DCS, audio stutter, UMSCH, VFFLR, bad memory page retirement, priority delta gain, IH interrupt allow, shadow DPM, mode3 reset, direct driver/tool DRAM address messages, with-address table transfers, all-running-feature query, SVI3 voltage, policy update, external power connector support, and UCLK overdrive preload. `PPSMC_Message_Count` is `0x59`.

## Control Flow
Both legacy high/low address setup and newer direct/with-address transfers are available. Firmware returns standard result codes and may reject commands when prerequisites are not met.

## State And Persistence
Runtime PMFW state includes feature masks, table pointers, DPM bounds, power limits/source, trace buffers, DCS/profiling/OBM modes, RAS page state, interrupt permissions, SVI3 voltage query state, and external power connector support.

## Dependencies And Integration
Pairs with v14 driver interface and PMFW headers, RAS, STB/OBM tracing, DCS, VFFLR, UMSCH/media power, SVI3 regulator telemetry, external power connector support, and policy-management code.

## Risks And Test Signals
Risks include selecting the wrong address transfer flow, commands marked removable lingering in callers, and reset/DCS/RAS support differences by firmware. Test signals include driver-if version, table transfers both legacy and with-address, all-running-feature readback, STB/OBM traces, SVI3 voltage reads, external connector reports, VFFLR, and RAS retirement updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v14_0_2_ppsmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v15_0_0_pmfw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v15_0_0_pmfw.h

## Purpose
Defines SMU v15.0.0 PMFW feature bits, firmware image metadata, and firmware status layout.

## Important APIs, Types, And Constants
Includes `smu15_driver_if_v15_0_0.h` and exports 64 feature bits. Domains include CCLK/fan/data/PPT/TDC/thermal/FIT/EDC, VDDOFF, VCN, MPM/MPIO, FCLK/SOC/LCLK/SHUB/DCF/ISP/NPU/GFX/VPE/DACCCLK DPM, deep-sleep clocks, low-power DCN clocks, VRHOT/Z8/PCC/SPM, PSI/PROCHOT/STAPM/S0i3, DF light/cstates, CPPC/preferred cores, ATHUB/MMHUB PG, VDDOFF ECO, SC/FP DIDT, CC6, P3T, DS_NPUCLK/DS_VPECLK, and `NUM_FEATURES 64`. `SMU_Firmware_Header`, `SMU_Firmware_Footer`, and `FwStatus_t` define firmware/status metadata.

## Control Flow
Feature bits are consumed by PPSMC feature queries and controls. Firmware image metadata is parsed during PMFW load/validation, and `FwStatus_t` is read as a runtime firmware status table.

## State And Persistence
Feature masks and status fields are volatile firmware state. Firmware header/footer values are persistent image metadata and part of the loader contract.

## Dependencies And Integration
Pairs with `smu15_driver_if_v15_0_0.h` and `smu_v15_0_0_ppsmc.h`. Integrates with NPU/VPE/DACCCLK/ISP/media/display power management, CPPC, low-power states, firmware loading, and SMU status/feature reporting.

## Risks And Test Signals
Risks include feature-bit mismatch with v14/v13, firmware metadata parsing mismatch, and incomplete handling of new NPU/VPE/DACCCLK bits. Test signals include firmware load/header checks, driver-if version, enabled-feature readback, NPU/VPE/VCN/JPEG power transitions, status table sanity, and low-power-state testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v15_0_0_pmfw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v15_0_0_ppsmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v15_0_0_ppsmc.h

## Purpose
Defines SMU v15.0.0 PPSMC mailbox command IDs and argument enums for a compact v15 PMFW ABI.

## Important APIs, Types, And Constants
`PPS_PMFW_IF_VER` is `1.0`. Commands include PMFW and driver-if version reads, VCN/JPEG/VPE power, GFX soft min/max, FCLK/SOC/VCN/VPE bounds, unload preparation, table transfers, GFX mode2 reset, enabled-feature query, GFX IMU, GFXOFF allow/disallow, zstate allow, SmartShift status, UMSCH power, and LSDMA enable/disable. `PPSMC_Message_Count` is `0x22`; `Mode_Reset_e` and `ZStates_e` define reset/zstate arguments.

## Control Flow
The host sends a mailbox command with optional argument and checks the standard PPSMC result. Table transfer commands move PMFW driver-interface tables, while reset and zstate commands require enum arguments.

## State And Persistence
Commands affect volatile PMFW state: media/VPE/UMSCH/LSDMA power, clock bounds, GFXOFF/zstate permission, SmartShift query state, table contents, and reset state.

## Dependencies And Integration
Pairs with `smu_v15_0_0_pmfw.h` and the compact SMU 15 driver-interface table. Integrates with media/VPE power management, GFX reset/TDR, SmartShift, clock policy, and table-transfer code.

## Risks And Test Signals
Risks include assuming larger dGPU command maps, missing explicit driver-address messages, and not validating reset/zstate arguments. Test signals include PMFW/driver-if version, table transfer, VCN/JPEG/VPE power transitions, UMSCH/LSDMA toggles, GFX reset, enabled-feature query, SmartShift status, and zstate/GFXOFF behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/inc/pmfw_if/smu_v15_0_0_ppsmc.h -->
