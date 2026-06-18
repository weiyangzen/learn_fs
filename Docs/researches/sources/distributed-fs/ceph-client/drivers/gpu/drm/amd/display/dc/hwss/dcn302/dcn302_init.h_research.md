# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn302/dcn302_init.h

## Purpose
Declares the DCN302 HWSS constructor.

## Important APIs, Types, and Functions
Forward-declares `struct dc` and exports `void dcn302_hw_sequencer_construct(struct dc *dc);`.

## Control Flow
No executable flow.

## State and Persistence Behavior
No local state.

## Dependencies and Integration Points
Used by resource code selecting DCN302 behavior.

## Risks and Test Signals
Build coverage and constructor selection tests.
