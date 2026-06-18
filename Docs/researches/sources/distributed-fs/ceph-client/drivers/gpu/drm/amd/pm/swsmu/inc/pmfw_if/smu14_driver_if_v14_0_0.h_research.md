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
