# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.h

## Purpose

`dcn351_resource.h` is the public declaration header for the DCN 3.5.1 resource pool implementation. It exposes the DCN351 DML IP/SOC bounding boxes, the typed resource-pool wrapper, and the factory used by DC initialization to create the generation-specific resource pool.

## Important APIs, Types, And Functions

- `extern struct _vcs_dpi_ip_params_st dcn3_51_ip` and `extern struct _vcs_dpi_soc_bounding_box_st dcn3_51_soc`: DCN351 DML tuning inputs supplied by the FPU/DML side.
- `TO_DCN351_RES_POOL(pool)`: container macro converting a generic `struct resource_pool *` to `struct dcn351_resource_pool *`.
- `struct dcn351_resource_pool`: thin wrapper containing only `struct resource_pool base`.
- `dcn351_create_resource_pool(init_data, dc)`: exported constructor implemented in `dcn351_resource.c`.

## Control Flow

The header has no runtime control flow. It is included by the DCN351 implementation and by DC initialization code that needs to call `dcn351_create_resource_pool()`. The container macro is used by teardown to recover the outer allocation from the embedded base pool.

## State And Persistence Behavior

The header defines no storage. It declares external DML data and a resource-pool type whose state is owned and populated by the C file.

## Dependencies And Integration Points

It depends on `core_types.h` for DC core structures and on Linux `container_of` semantics through the included headers. Its exported factory is the integration point between ASIC selection and the generic display-core resource model.

## Risks And Edge Cases

- The wrapper currently has no extra generation-specific fields. Any future per-ASIC state must be added here and initialized/destructed in the C file.
- The `TO_DCN351_RES_POOL` macro assumes the incoming pointer is a valid `base` member of a `struct dcn351_resource_pool`; misuse will produce invalid memory access.
- The external DML symbols must be linked whenever DCN351 support is built.

## Test Signals

- Compile/link tests catch missing DML symbols and signature drift for `dcn351_create_resource_pool()`.
- Resource-pool creation/destruction tests indirectly validate the container macro by exercising `dcn351_destroy_resource_pool()`.
