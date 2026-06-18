<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn301/dcn301_smu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn301/dcn301_smu.h

## Purpose

`dcn301_smu.h` defines Van Gogh/DCN3.0.1 PMFW table layouts, DPM clock structures, watermark structures, display idle bitfields, and SMU helper prototypes.

## Important APIs, Types, And Functions

It defines `SMU13_DRIVER_IF_VERSION`, `df_pstate_t`, `vcn_clk_t`, `DSPCLK_e`, `DisplayClockTable_t`, `WatermarkRowGeneric_t`, watermark enums, `Watermarks_t`, table IDs `TABLE_WATERMARKS` and `TABLE_DPMCLOCKS`, VG DPM level counts, `struct vg_dpm_clocks`, `struct smu_dpm_clks`, `struct watermarks`, `struct display_idle_optimization`, `union display_idle_optimization_u`, and all `dcn301_smu_*` prototypes.

## Control Flow

The header has no runtime control flow. Its structs are allocated by `vg_clk_mgr.c`, filled by SMU table transfers or watermark builders, then passed back to PMFW through mailbox commands.

## State And Persistence Behavior

It defines binary shared-memory state: DPM clocks copied from SMU, watermark rows copied to SMU, and display idle optimization bitfields sent as message parameters. Runtime ownership is in the clock manager and PMFW.

## Dependencies And Integration Points

It is the ABI boundary between Van Gogh display clock management and PMFW. `vg_clk_mgr.c` uses its types for framebuffer-backed SMU tables; `dcn301_smu.c` uses its prototypes and table IDs.

## Risks

The header comments say some definitions are copied from PMFW headers; layout drift is a firmware compatibility risk. Counts must match PMFW array sizes. The display idle bitfield is packed into a `uint32_t`, so bit ordering is ABI-sensitive.

## Test Signals

Static layout/version checks against PMFW headers, DPM table transfer validation, watermark upload acceptance, idle optimization behavior, and build coverage of all SMU helper prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn301/dcn301_smu.h -->
