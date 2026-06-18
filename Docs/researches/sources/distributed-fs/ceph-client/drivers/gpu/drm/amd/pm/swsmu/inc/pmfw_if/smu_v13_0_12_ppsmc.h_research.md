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
