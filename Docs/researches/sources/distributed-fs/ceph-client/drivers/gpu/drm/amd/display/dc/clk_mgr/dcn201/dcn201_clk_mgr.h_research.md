<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn201/dcn201_clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn201/dcn201_clk_mgr.h

## Purpose

`dcn201_clk_mgr.h` declares the DCN2.0.1/Cyan Skillfish clock-manager constructor.

## Important APIs, Types, And Functions

It exports `dcn201_clk_mgr_construct(struct dc_context *ctx, struct clk_mgr_internal *clk_mgr, struct pp_smu_funcs *pp_smu, struct dccg *dccg)`.

## Control Flow

The header has no runtime flow. The implementation installs DCN201 callback tables and register metadata during resource construction.

## State And Persistence Behavior

No state is owned by the header. The constructed manager stores clock state in `clk_mgr_internal`, DCCG state, and hardware registers.

## Dependencies And Integration Points

It integrates with DC resource construction and shared DCN20 helper code. The `pp_smu` parameter is part of the common constructor shape even though DCN201's implementation does not use it heavily.

## Risks

Constructor signature drift breaks platform bring-up. The minimal header gives no access to private update helpers, which is intentional.

## Test Signals

Build coverage and DCN201 resource construction/runtime clock update tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn201/dcn201_clk_mgr.h -->
