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
