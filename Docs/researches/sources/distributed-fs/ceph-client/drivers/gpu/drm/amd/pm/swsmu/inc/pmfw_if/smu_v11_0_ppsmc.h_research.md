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
