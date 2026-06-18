# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.h

## Purpose

`dcn21_resource.h` declares the public DCN 2.1 resource-pool entry points and DML bounding-box globals for Renoir-class display hardware.

## Important APIs, Types, And Functions

- `TO_DCN21_RES_POOL()` casts a generic `resource_pool` to `struct dcn21_resource_pool`.
- Extern globals `dcn2_1_ip` and `dcn2_1_soc` expose the DCN21 DML IP parameters and SoC bounding box.
- `struct dcn21_resource_pool` embeds `struct resource_pool base`.
- `dcn21_create_resource_pool()` constructs the DCN21 pool.
- `dcn21_fast_validate_bw()` exposes DCN21's fast validation path, adding the `allow_self_refresh_only` parameter on top of the DCN20-style bandwidth API.

## Control Flow

The header has no runtime control flow. DC initialization uses the constructor, and bandwidth code can call the declared fast validator with already populated DML pipe storage and output pointers for pipe count, split provenance, and selected voltage level.

## State And Persistence Behavior

The header stores no state. The extern DML globals are mutable implementation data, and the declared functions mutate `dc`, `dc_state`, DML validation state, pipe topology, and resource acquisition state.

## Dependencies And Integration Points

The header includes `core_types.h` and forward-declares DC/resource/DML pipe types. It sits beside `dcn21_resource.c` and also depends conceptually on `dcn20_resource.h` because DCN21 reuses many DCN20 helper APIs internally.

## Risks And Edge Cases

- `dcn21_fast_validate_bw()` has more parameters than the DCN20 fast validator; callers must pass valid storage for all output pointers.
- The mutable extern DML data can be patched based on fused pipe count and clock tables, so tests should not assume static defaults after initialization.
- Header declarations must stay consistent with resource function callbacks and FPU wrapper functions in the implementation.

## Test Signals

Compile coverage catches prototype drift. Runtime coverage should verify that DCN21 construction installs the expected validator and that direct fast-validator callers handle both full mclk-switch and self-refresh-only validation modes.
