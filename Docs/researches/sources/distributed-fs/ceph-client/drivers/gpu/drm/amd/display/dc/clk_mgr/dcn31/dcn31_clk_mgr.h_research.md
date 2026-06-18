<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn31/dcn31_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn31/dcn31_clk_mgr.h

## Purpose

`dcn31_clk_mgr.h` declares the DCN31 clock-manager wrapper type, watermark-set container, public callbacks, constructor, DTB reference query, and destructor.

## Important APIs, Types, And Functions

It forward-declares `struct dcn31_watermarks`, defines `struct dcn31_smu_watermark_set`, defines `struct clk_mgr_dcn31` embedding `clk_mgr_internal`, and declares `dcn31_are_clock_states_equal()`, `dcn31_init_clocks()`, `dcn31_update_clocks()`, `dcn31_clk_mgr_construct()`, `dcn31_get_dtb_ref_freq_khz()`, and `dcn31_clk_mgr_destroy()`.

## Control Flow

The header has no runtime flow. It exposes functions used by resource construction and by related DCN31 variants while keeping helper internals private.

## State And Persistence Behavior

The wrapper state persists framebuffer-backed watermark memory and its MC address beside the base clock manager. The header itself owns no state.

## Dependencies And Integration Points

It includes `clk_mgr_internal.h` and integrates DCN31-specific SMU watermark storage with the generic clock-manager callback interface.

## Risks

The embedded layout is used with `container_of()`; changing it requires implementation updates. Public declarations for update/init/equality mean derived managers may depend on DCN31 semantics, increasing compatibility pressure.

## Test Signals

Build coverage, DCN31 construction/destruction, DTB reference query, and derived-manager callback reuse tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn31/dcn31_clk_mgr.h -->
