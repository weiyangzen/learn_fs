# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_spl_translate.h

## Purpose
`dc_spl_translate.h` declares the SPL/DC translation API used to map DC pipe context into SPL scaler input and SPL output back into DC scaler data.

## Important APIs
`translate_SPL_in_params_from_pipe_ctx` maps `struct pipe_ctx` into `struct spl_in`. `translate_SPL_out_params_to_pipe_ctx` maps `struct spl_out` into `pipe_ctx->plane_res.scl_data`.

## Control Flow And State
The header has no logic. Callers provide all storage; the implementation mutates the supplied `spl_in` or `pipe_ctx`.

## Dependencies And Integration Points
It includes `dc.h`, `resource.h`, and `dm_helpers.h`, tying it to internal pipe context/resource helpers and display manager HDR helpers. The scaler calculation path is the primary integration point.

## Risks
The API does not express nullability or required initialized subfields. It also exposes SPL types through DC headers, so SPL structure changes can require synchronized updates here.

## Test Signals
Compile coverage against SPL headers and scaler validation tests that exercise both translation directions are expected.
