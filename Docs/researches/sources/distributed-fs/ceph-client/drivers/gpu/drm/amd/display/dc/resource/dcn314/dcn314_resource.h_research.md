# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.h

## Purpose
This header declares the public DCN314 resource interfaces and wrapper type used by the DCN314 implementation and ASIC initialization code.

## Important APIs, Types, And Functions
It includes `core_types.h`, declares extern `dcn3_14_ip` and `dcn3_14_soc`, defines `TO_DCN314_RES_POOL()` for downcasting from `struct resource_pool`, defines `struct dcn314_resource_pool { struct resource_pool base; }`, declares `dcn314_validate_bandwidth()`, and declares `dcn314_create_resource_pool()`.

## Control Flow
ASIC resource selection calls `dcn314_create_resource_pool()`. The resource vtable installed by the C file can call back into `dcn314_validate_bandwidth()` for mode validation. No inline logic exists in the header.

## State And Persistence
The header does not allocate state. It exposes the DCN314 wrapper shape and mutable DML IP/SOC globals used during resource construction and validation.

## Dependencies And Integration Points
The header integrates DCN314 resource code with DC core initialization, validation callers, and DCN314 DML/FPU providers. The downcast macro is used by destruction and internal code that needs the wrapper allocation.

## Risks
The downcast macro assumes the pool pointer came from `dcn314_create_resource_pool()`. The validation declaration is generation-specific; wiring it into the wrong resource table would apply DCN314 validation semantics, including no self-refresh-only support, to another ASIC.

## Test Signals
Build/link signals should confirm the constructor and validation symbols resolve. Runtime probe should return a non-null pool, and validation callbacks should report `DC_OK` or `DC_FAIL_BANDWIDTH_VALIDATE` through the DCN314 path.
