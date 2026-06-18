# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn30/dcn30_init.h

## Purpose
Declares the DCN30 HWSS constructor.

## Important APIs, Types, and Functions
Forward-declares `struct dc` and exports `void dcn30_hw_sequencer_construct(struct dc *dc);`.

## Control Flow
No executable flow. Used by ASIC init and by smaller derivative constructors.

## State and Persistence Behavior
No direct state. Constructor implementation installs function tables.

## Dependencies and Integration Points
DCN302 and DCN303 constructors include and call this constructor before applying overrides.

## Risks and Test Signals
Build and constructor selection coverage are sufficient for this header.
