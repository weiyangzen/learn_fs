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
