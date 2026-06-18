# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce112/dce112_resource.h

## Purpose
This header exposes the DCE 11.2 resource-pool constructor and selected validation/mapping routines for use by DC core and nearby generations.

## Important APIs, Types, And Functions
- `dce112_create_resource_pool()` creates a DCE 11.2 pool.
- `dce112_validate_with_context()` is declared as an external validation API, though its implementation is not in this file.
- `dce112_validate_bandwidth()` exports the DCE bandwidth validation wrapper.
- `dce112_add_stream_to_ctx()` exports the DCE 11.2 stream resource mapping sequence.

## Control Flow
The header itself has no runtime behavior. It defines call boundaries used by DCE 11.2 and by DCE 12.0, which reuses the bandwidth and add-stream implementations.

## State And Persistence
No state is declared beyond function interfaces. The functions operate on `struct dc`, `struct dc_state`, `struct dc_stream_state`, and resource-pool state owned by implementation files.

## Dependencies And Integration Points
It includes `core_types.h` and forward-declares `struct dc` and `struct resource_pool`. It is an integration seam between generation resource construction and generic DC validation/modeset code.

## Risks
Because DCE 12.0 includes this header to reuse functions, ABI/signature changes here can break multiple resource backends. The declared `dce112_validate_with_context()` requires definition elsewhere; missing linkage would show up at build time.

## Test Signals
Build tests should verify both DCE 11.2 and DCE 12.0 users link successfully. Runtime tests should cover bandwidth validation and add-stream behavior through both generations.
