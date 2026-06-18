# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn302/dcn302_fpu.h

## Purpose
This header declares the two DCN302 FPU bandwidth-bounding-box entry points used by DCN302 resource and initialization code.

## Important APIs, Types, And Functions
- `dcn302_fpu_init_soc_bounding_box(struct bp_soc_bb_info bb_info)` loads BIOS latency overrides into the DCN302 SoC model.
- `dcn302_fpu_update_bw_bounding_box(struct dc *dc, struct clk_bw_params *bw_params)` rebuilds DCN302 DML clock limits from runtime clock-manager data.

## Control Flow
No runtime control flow exists in the header. It provides compile-time linkage to the DCN302 FPU implementation.

## State And Persistence
The header stores no state. The implementation mutates global DCN302 SoC/IP descriptors and DML contexts.

## Dependencies And Integration Points
The declarations reference `struct bp_soc_bb_info`, `struct dc`, and `struct clk_bw_params`. Callers are expected to include this from resource/clock-management code with those types already visible and to call under the display-core FPU guard.

## Risks And Edge Cases
The interface is intentionally small, so any required DCN302 behavior beyond initialization and clock-table update must be wired elsewhere. Incorrect FPU call context or missing type declarations are the main integration hazards.

## Test Signals
Build coverage should catch prototype/definition mismatch. Functional coverage should exercise both declarations through the DCN302 resource path and verify the DML instance is reinitialized after clock-table updates.
