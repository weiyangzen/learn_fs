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
