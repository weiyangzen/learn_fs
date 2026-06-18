# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn303/dcn303_fpu.h

## Purpose
This header declares the DCN303 FPU functions for bounding-box update and BIOS latency initialization.

## Important APIs, Types, And Functions
- `dcn303_fpu_update_bw_bounding_box(struct dc *dc, struct clk_bw_params *bw_params)` updates the DCN303 DML SoC/IP model from runtime clock-manager data.
- `dcn303_fpu_init_soc_bounding_box(struct bp_soc_bb_info bb_info)` imports BIOS-provided latency values into the DCN303 SoC model.

## Control Flow
The header contains no runtime control flow and serves as the public compile-time contract for the DCN303 FPU implementation.

## State And Persistence
No data is stored here. State changes happen inside the implementation's global DML descriptors and caller-owned `dc` state.

## Dependencies And Integration Points
The prototypes reference display-core and clock-manager structures. The header is intended for DCN303 resource initialization and validation paths that already observe the DC FPU access discipline.

## Risks And Edge Cases
The same small public surface means all DCN303 DML behavior must be reached through these two hooks or common DCN code. Calling outside an FPU-enabled section would violate the implementation contract.

## Test Signals
Build tests should ensure the header stays in sync with the implementation. Integration tests should invoke both functions through the DCN303 resource path and verify the updated DML model reflects BIOS and SMU clock inputs.
