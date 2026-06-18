# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn20/dcn20_init.h

## Purpose
Declares the DCN 2.0 HWSS constructor used by resource/ASIC initialization code.

## Important APIs, Types, and Functions
Forward-declares `struct dc` and exports `void dcn20_hw_sequencer_construct(struct dc *dc);`.

## Control Flow
The header has no executable flow. Including code calls the constructor after allocating and initializing `struct dc` and `dc->hwseq`.

## State and Persistence Behavior
No local state. The declared function persists HWSS behavior by installing function tables into `struct dc`.

## Dependencies and Integration Points
The guarded include prevents duplicate declarations. It intentionally avoids pulling in full DC definitions by using a forward declaration.

## Risks and Test Signals
Prototype drift between the header and implementation would break compilation. Test signal is successful build of DCN20 resource code using this constructor.
