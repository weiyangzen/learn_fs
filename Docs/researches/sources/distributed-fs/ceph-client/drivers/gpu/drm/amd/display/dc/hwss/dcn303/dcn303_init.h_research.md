# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn303/dcn303_init.h

## Purpose
Declares the DCN303 HWSS constructor.

## Important APIs, Types, and Functions
Forward-declares `struct dc` and exports `void dcn303_hw_sequencer_construct(struct dc *dc);`.

## Control Flow
No executable flow.

## State and Persistence Behavior
No local state.

## Dependencies and Integration Points
Used by DCN303 ASIC/resource init code.

## Risks and Test Signals
Build coverage catches declaration drift.
