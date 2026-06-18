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
