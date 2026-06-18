# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce120/dce120_resource.h

## Purpose
This header declares the public constructor for the DCE 12.0 resource pool.

## Important APIs, Types, And Functions
- `dce120_create_resource_pool(uint8_t num_virtual_links, struct dc *dc)` creates and returns a DCE 12.0 `struct resource_pool`.

## Control Flow
The header has no runtime control flow. DC initialization code calls the constructor declared here when the ASIC/display version maps to DCE 12.

## State And Persistence
No state is declared in the header. The implementation uses the DCE 11.0 resource-pool wrapper internally and persists state in `struct resource_pool` and `struct dc`.

## Dependencies And Integration Points
It includes `core_types.h` and forward-declares `struct dc` and `struct resource_pool`. It is the compile-time boundary between DC version selection and DCE 12 resource construction.

## Risks
The API exposes only a constructor, so any future DCE 12 helper reuse would require header expansion. Signature drift must be coordinated with DC factory selection code.

## Test Signals
Build coverage of DCE 12 selection and runtime pool construction on Vega-family hardware are the relevant signals.
