# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.h

## Purpose
This header declares the public DCN 3.2.1 resource-pool interface. It is intentionally small: DCN321 mostly reuses DCN32 infrastructure, so the header provides only the container type, conversion macro, external DML bounding-box inputs, and resource-pool creation entry point.

## Important APIs, Types, And Functions
- `TO_DCN321_RES_POOL(pool)` converts a generic `struct resource_pool *` to `struct dcn321_resource_pool *` with `container_of`.
- `extern struct _vcs_dpi_ip_params_st dcn3_21_ip` and `extern struct _vcs_dpi_soc_bounding_box_st dcn3_21_soc` provide DCN321 DML IP/SOC bounding boxes owned by the FPU/DML implementation.
- `struct dcn321_resource_pool` embeds the generic `struct resource_pool`.
- `dcn321_create_resource_pool(const struct dc_init_data *init_data, struct dc *dc)` is the ASIC-specific factory used by Display Core initialization.

## Control Flow
The header has no executable flow. Runtime flow enters through `dcn321_create_resource_pool`, which allocates a DCN321 pool, invokes the constructor in `dcn321_resource.c`, and returns the embedded generic pool on success. The DML externs are passed to DML initialization during construction and can be adjusted for pipe fusing before use.

## State And Persistence
No state is stored in the header. The embedded-pool layout is an ABI contract between generic resource cleanup, `TO_DCN321_RES_POOL`, and DCN321-specific destructors. The extern DML structures are persistent globals defined elsewhere; constructor code mutates fields such as maximum pipe counts after reading fuses.

## Dependencies And Integration Points
The header depends on `core_types.h` for Display Core resource and DC type definitions. It integrates with the DCN321 resource constructor, DML DCN321 bounding-box implementation, and generic Display Core resource-pool ownership model.

## Risks And Edge Cases
The main risk is layout coupling: `TO_DCN321_RES_POOL` assumes `base` remains a direct member of `struct dcn321_resource_pool`. If the create function signature or extern DML object names change, initialization code and ASIC selection tables must be updated together. Because this header exposes mutable global DML structures, cross-file users must avoid inconsistent assumptions about when fuse-adjusted fields are valid.

## Test Signals
Build tests should include every translation unit that includes this header. Runtime signals include ASIC selection choosing `dcn321_create_resource_pool`, successful construction/destruction through the generic `resource_pool` pointer, correct DML initialization using `dcn3_21_soc/ip`, and pipe-fuse tests showing adjusted DML pipe limits.
