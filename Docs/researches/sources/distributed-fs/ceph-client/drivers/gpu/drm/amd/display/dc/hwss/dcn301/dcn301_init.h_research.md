# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn301/dcn301_init.h

## Purpose
Declares the DCN301 HWSS constructor.

## Important APIs, Types, and Functions
Forward-declares `struct dc` and exports `void dcn301_hw_sequencer_construct(struct dc *dc);`.

## Control Flow
No executable flow.

## State and Persistence Behavior
No direct state.

## Dependencies and Integration Points
Used by DCN301 resource initialization. The closing comment references DCN30, which is cosmetic.

## Risks and Test Signals
Build coverage catches signature problems.
