# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce110/dce110_resource.h

## Purpose
This header declares the DCE 11.0 resource-pool wrapper and the small set of DCE 11.0 helpers reused by other resource implementations.

## Important APIs, Types, And Functions
- `struct dce110_resource_pool` embeds `struct resource_pool`.
- `TO_DCE110_RES_POOL(pool)` converts a base `resource_pool` pointer back to its containing DCE 11.0 pool.
- `dce110_resource_build_pipe_hw_param()` exposes DCE 11.0 pipe clock and stream parameter construction to later DCE variants.
- `dce110_create_resource_pool()` is the generation factory for DCE 11.0.
- `dce110_find_first_free_match_stream_enc_for_link()` exposes the common stream encoder selection policy.

## Control Flow
The header has no runtime control flow. It is consumed by DC resource initialization code and by DCE 11.2, DCE 12.0, DCE 6/8, and DCN code that reuse the container, helper, or stream-encoder selection APIs.

## State And Persistence
The only state shape introduced here is the wrapper around `struct resource_pool`; all owned state is allocated and persisted by the implementation.

## Dependencies And Integration Points
It includes `core_types.h` for `struct pipe_ctx`, `struct resource_context`, `struct dc_stream_state`, `struct hw_asic_id`, and related DC types. The exported helpers are integration points between generation-specific resource files and generic DC resource mapping.

## Risks
The container macro assumes callers pass a valid embedded `resource_pool`. Because this header is reused by multiple generations, signature changes can break several resource backends at once.

## Test Signals
Compile coverage across DCE 11.0, DCE 11.2, DCE 12.0, older DCE, and DCN resource files is the primary signal. Runtime signals come from successful pool creation and stream encoder selection in those implementations.
