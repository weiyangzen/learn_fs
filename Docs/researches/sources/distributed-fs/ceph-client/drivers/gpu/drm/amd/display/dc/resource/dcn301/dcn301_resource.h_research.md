# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.h

## Purpose
This header exposes the DCN301 resource-pool constructor and the minimal DCN301-specific pool wrapper used by the implementation file. It is the public include boundary for other Display Core initialization code that needs to create a Vangogh/DCN3.0.1 resource pool.

## Important APIs, Types, And Functions
The header forward-declares `struct dc`, `struct resource_pool`, and DML pipe parameter structures. It declares external DML globals `dcn3_01_ip` and `dcn3_01_soc`, which the C file patches during initialization. `struct dcn301_resource_pool` embeds `struct resource_pool base`, allowing DC core code to treat it polymorphically. `dcn301_create_resource_pool(const struct dc_init_data *init_data, struct dc *dc)` is the only exported constructor.

## Control Flow
Consumers include this header, call `dcn301_create_resource_pool()`, and receive a `struct resource_pool *`. The actual allocation, capability setup, object construction, and cleanup are hidden in `dcn301_resource.c`; the header provides no inline logic.

## State And Persistence
The header itself stores no state. It defines the structural relationship between the DCN301-specific allocation and generic `resource_pool` lifetime, and exposes mutable DML globals owned elsewhere in the DCN301/DML code.

## Dependencies And Integration Points
The dependency on `core_types.h` brings in `struct dc_init_data` and DC type definitions. Integration is with ASIC-family resource selection code that chooses the DCN301 constructor based on detected hardware, and with DML/FPU code that provides `dcn3_01_ip` and `dcn3_01_soc`.

## Risks
Because no `TO_DCN301_RES_POOL` macro is exported here, only the C file's private macro should downcast the base pointer. Changes to the embedded `base` layout or constructor signature would ripple into DC creation code. The extern DML globals are mutable and must remain aligned with the C file's initialization assumptions.

## Test Signals
Compile coverage is the primary signal: the selected ASIC init path must include the header and link against `dcn301_create_resource_pool()`. Runtime probe should return a non-null pool and later destroy it through the installed `resource_funcs.destroy` callback.
