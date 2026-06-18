# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce80/dce80_resource.h

## Purpose
This header declares resource-pool constructors for DCE 8.0, DCE 8.1, and DCE 8.3.

## Important APIs, Types, And Functions
- `dce80_create_resource_pool()` creates a DCE 8.0 pool.
- `dce81_create_resource_pool()` creates a DCE 8.1 pool.
- `dce83_create_resource_pool()` creates a DCE 8.3 pool.

## Control Flow
The header has no runtime flow; it provides constructor entry points for the DC version/ASIC selection layer.

## State And Persistence
No state is declared here. Each constructor returns an owned `struct resource_pool` that persists all DCE 8 resources in the implementation.

## Dependencies And Integration Points
It includes `core_types.h` and forward-declares `struct dc` and `struct resource_pool`. It integrates the DCE 8 resource backend with DC core initialization.

## Risks
The three variants share signatures but have different hardware caps. Incorrect call-site selection can overstate available pipes, clocks, or DDCs.

## Test Signals
Build coverage for all constructor declarations and runtime pool creation on DCE 8.0/8.1/8.3 ASICs are the primary signals.
