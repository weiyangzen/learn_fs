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
