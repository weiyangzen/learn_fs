# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce60/dce60_resource.h

## Purpose
This header declares resource-pool constructors for DCE 6.0, DCE 6.1, and DCE 6.4.

## Important APIs, Types, And Functions
- `dce60_create_resource_pool()` creates a DCE 6.0 pool.
- `dce61_create_resource_pool()` creates a DCE 6.1 pool.
- `dce64_create_resource_pool()` creates a DCE 6.4 pool.

## Control Flow
There is no runtime logic in the header. DC version selection calls one of the declared constructors based on the target ASIC.

## State And Persistence
The header declares no state. Each constructor returns a generic `struct resource_pool` whose ownership is transferred to DC core.

## Dependencies And Integration Points
It includes `core_types.h` and forward-declares `struct dc` and `struct resource_pool`. It is the boundary between DCE 6 ASIC selection and the resource implementation.

## Risks
The three constructor APIs are easy to confuse because they share the same signature but publish different caps. Call-site ASIC mapping is therefore the main correctness dependency.

## Test Signals
Build coverage for all three constructor references and runtime creation on DCE 6.0/6.1/6.4 ASIC IDs are the relevant signals.
