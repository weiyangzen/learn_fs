<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_smu11_driver_if.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_smu11_driver_if.h

## Purpose

`dcn30_smu11_driver_if.h` defines the subset of the SMU11 driver interface used by DCN30 display clock management, especially PPCLK IDs and watermark table layouts.

## Important APIs, Types, And Functions

It defines `SMU11_DRIVER_IF_VERSION`, `PPCLK_e`, `WatermarkRowGeneric_t`, watermark constants/enums, `Watermarks_t`, `WatermarksExternal_t`, and table IDs such as `TABLE_WATERMARKS`.

## Control Flow

No runtime flow exists. The structures are filled by `dcn30_clk_mgr.c` and transferred to PMFW through `dcn30_clk_mgr_smu_msg.c`.

## State And Persistence Behavior

The header describes binary table state shared with PMFW. Runtime instances live in GPU memory allocated by the clock manager and are persisted in PMFW after table transfer.

## Dependencies And Integration Points

It integrates DC display clock code with PMFW's SMU11 table ABI. PPCLK IDs are used in hard-min/max and DPM query messages. `WatermarksExternal_t` is the memory layout passed by physical/GPU address to PMFW.

## Risks

Any layout, padding, enum, or version mismatch can make PMFW misinterpret watermark data or reject interface checks. The file lacks include guards in this snapshot, so duplicate inclusion safety depends on surrounding usage.

## Test Signals

SMU driver-interface version check, watermark table upload acceptance, DPM query correctness for each PPCLK ID, and ABI-size/layout checks against PMFW headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_smu11_driver_if.h -->
