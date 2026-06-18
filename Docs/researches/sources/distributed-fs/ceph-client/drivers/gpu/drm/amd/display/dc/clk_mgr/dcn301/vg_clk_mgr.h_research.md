<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn301/vg_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn301/vg_clk_mgr.h

## Purpose

`vg_clk_mgr.h` declares the Van Gogh clock-manager wrapper type and constructor/destructor.

## Important APIs, Types, And Functions

It forward-declares `struct watermarks`, declares external `ddr4_wm_table` and `lpddr5_wm_table`, defines `struct smu_watermark_set` with a watermark pointer and MC address, defines `struct clk_mgr_vgh` embedding `clk_mgr_internal`, and declares `vg_clk_mgr_construct()` and `vg_clk_mgr_destroy()`.

## Control Flow

There is no runtime flow in the header. It defines the object layout that lets implementation code recover `clk_mgr_vgh` from the embedded base and manage SMU watermark memory.

## State And Persistence Behavior

The declared wrapper persists watermark table memory and its GPU/MC address alongside the base clock manager. The header itself owns no state.

## Dependencies And Integration Points

It includes `clk_mgr_internal.h` and integrates Van Gogh-specific watermark memory with generic DC clock-manager callbacks.

## Risks

The embedded-struct layout is relied on by `container_of()` in `vg_clk_mgr.c`; changing field order breaks that conversion. External watermark table declarations must be defined elsewhere.

## Test Signals

Build/link coverage, constructor/destructor memory lifecycle tests, and runtime watermark notification on Van Gogh systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn301/vg_clk_mgr.h -->
