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
