# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn10/dcn10_resource.h

## Purpose
This header declares the DCN 1.0 resource-pool wrapper, constructor, and helper exports used by DCN/DC resource code.

## Important APIs, Types, And Functions
- `struct dcn10_resource_pool` embeds `struct resource_pool`.
- `TO_DCN10_RES_POOL(pool)` converts a base pool pointer to the DCN 1.0 containing type.
- `dcn10_create_resource_pool()` creates the DCN 1.0/1.01 pool from `struct dc_init_data`.
- `dcn10_find_first_free_match_stream_enc_for_link()` exposes DCN stream encoder matching.
- `dcn10_get_vstartup_for_pipe()` returns the pipe DLG vstartup value.
- `dcn10_get_default_tiling_info()` publishes the default DCN tiling metadata.
- `dcn1_0_ip` and `dcn1_0_soc` are declared as external DML IP/SOC bounding-box inputs.

## Control Flow
The header has no runtime control flow. Its declarations are consumed by DCN initialization, validation, and helper code.

## State And Persistence
The wrapper shape identifies a DCN 1.0 pool while storing state in the embedded generic `resource_pool`. The extern DML structures represent shared immutable model inputs defined elsewhere.

## Dependencies And Integration Points
It includes `core_types.h` and `dml/dcn10/dcn10_fpu.h`, tying the resource backend to DC core types and DML model structures. The exported helpers bridge DCN resource allocation with stream encoder selection, timing, and tiling code.

## Risks
The header exposes DML/FPU types, so build configurations around floating-point code must remain compatible. The container macro has the usual embedded-struct validity requirement.

## Test Signals
Build coverage for DCN 1.0/1.01 resource users, DML symbol linkage, and runtime calls to stream encoder selection, vstartup, and default tiling helpers are the main signals.
