# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dcn314/dcn314_fpu.h

## Purpose

`dcn314_fpu.h` declares the DCN 3.14 floating-point DML hooks and defines DCN 3.14 DET/compbuf/CRB sizing constants. It is the public interface used by DCN 3.14 resource and validation code to update the bandwidth bounding box and populate DML pipe parameters from a `dc_state`.

## Important APIs, Types, And Functions

- `DCN3_14_DEFAULT_DET_SIZE`: default DET buffer size in KB, `384`.
- `DCN3_14_MAX_DET_SIZE`: maximum DET buffer size in KB, `384`.
- `DCN3_14_MIN_COMPBUF_SIZE_KB`: minimum compressed buffer size in KB, `128`.
- `DCN3_14_CRB_SEGMENT_SIZE_KB`: CRB segment size in KB, `64`.
- `dcn314_update_bw_bounding_box_fpu(struct dc *dc, struct clk_bw_params *bw_params)`: updates the DCN 3.14 DML bounding box from runtime clock/bandwidth parameters.
- `dcn314_populate_dml_pipes_from_context_fpu(struct dc *dc, struct dc_state *context, display_e2e_pipe_params_st *pipes, enum dc_validate_mode validate_mode)`: fills and adjusts DML pipe parameters from a display context and returns the active pipe count.

The header references `struct dc`, `struct clk_bw_params`, `struct dc_state`, `display_e2e_pipe_params_st`, and `enum dc_validate_mode`, all of which must be defined by surrounding DC/DML includes.

## Control Flow

There is no runtime control flow in the header. It uses the include guard `__DCN314_FPU_H__` and exposes constants plus two function prototypes.

The implied integration flow is:

1. Validation setup calls `dcn314_update_bw_bounding_box_fpu` after clock/bandwidth data is available.
2. Mode validation calls `dcn314_populate_dml_pipes_from_context_fpu` to translate `dc_state` into DML pipe arrays using DCN 3.14 policy.
3. Later DML validation and register calculation consume the populated `display_e2e_pipe_params_st` data.

## State And Persistence Behavior

This header owns no mutable state. Its constants are compile-time sizing policy. The declared functions mutate `dc->dml`, static/global model data in the implementation, `context->bw_ctx`, and caller-provided pipe arrays, but those behaviors are implemented in `dcn314_fpu.c`.

## Dependencies And Integration Points

The file is part of AMD Display Core's DCN 3.14 DML/FPU layer. It integrates with:

- DCN 3.14 resource validation code.
- Clock manager bandwidth parameter flow.
- DML pipe arrays and validation modes.
- DET/compbuf/CRB sizing policy used by the implementation and neighboring DCN 3.14 code.

Because it is an FPU header, callers must follow the driver's FPU access rules before invoking the declared functions.

## Risks And Edge Cases

- The header does not include the type definitions it references. Include order must provide `struct dc`, `struct clk_bw_params`, `struct dc_state`, `display_e2e_pipe_params_st`, and `enum dc_validate_mode`.
- Constants here must remain synchronized with the implementation's `dcn3_14_ip` defaults and DET/CRB policy. Divergence can create confusing validation behavior.
- The functions require floating-point execution to be enabled by the caller/implementation path; calling them from a non-FPU-safe context would violate kernel display-driver rules.
- The pipe population function returns an `int` active pipe count, so callers must handle zero or failure-like counts according to the surrounding validation convention.

## Test Signals

- Compile coverage catches signature drift and missing include dependencies.
- DCN 3.14 validation tests should assert that the declared constants match expected DET and CRB policy.
- Integration tests should call the declared functions through the normal resource validation path and verify resulting DML project, bounding-box, and pipe-array behavior.
