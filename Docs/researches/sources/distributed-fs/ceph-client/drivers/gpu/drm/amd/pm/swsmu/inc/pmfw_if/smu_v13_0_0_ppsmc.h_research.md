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
