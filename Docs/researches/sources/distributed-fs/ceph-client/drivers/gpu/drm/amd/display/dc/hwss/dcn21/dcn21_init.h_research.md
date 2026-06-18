# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn21/dcn21_init.h

## Purpose
Declares the DCN21 HWSS constructor.

## Important APIs, Types, and Functions
Forward-declares `struct dc` and exports `void dcn21_hw_sequencer_construct(struct dc *dc);`.

## Control Flow
No executable flow. Included by code that chooses DCN21 behavior during DC construction.

## State and Persistence Behavior
No state. The implementation writes HWSS function tables.

## Dependencies and Integration Points
Header guard is `__DC_DCN21_INIT_H__`; the closing comment references DCN20, which is cosmetic but potentially confusing.

## Risks and Test Signals
Build coverage catches declaration drift. Runtime signal is correct selection of the DCN21 constructor.
