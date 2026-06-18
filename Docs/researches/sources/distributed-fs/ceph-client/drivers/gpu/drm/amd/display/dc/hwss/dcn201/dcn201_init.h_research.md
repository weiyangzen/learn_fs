# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn201/dcn201_init.h

## Purpose
Declares the DCN201 HWSS constructor.

## Important APIs, Types, and Functions
Forward-declares `struct dc` and declares `void dcn201_hw_sequencer_construct(struct dc *dc);`.

## Control Flow
No executable flow. It allows ASIC-specific construction code to install DCN201 tables.

## State and Persistence Behavior
No local state; the implementation mutates `struct dc` function tables.

## Dependencies and Integration Points
Used by DCN201 resource/init code and protected by `__DC_DCN201_INIT_H__`.

## Risks and Test Signals
Build failures catch signature drift. Runtime coverage is through successful constructor selection.
