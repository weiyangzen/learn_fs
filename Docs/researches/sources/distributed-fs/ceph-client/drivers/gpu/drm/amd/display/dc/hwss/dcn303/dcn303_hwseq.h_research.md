# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn303/dcn303_hwseq.h

## Purpose
Declares DCN303 no-op power-gating functions.

## Important APIs, Types, and Functions
Includes `hw_sequencer_private.h` and declares DPP, HUBP, DSC, and plane PG-control hooks.

## Control Flow
No executable flow.

## State and Persistence Behavior
No direct state.

## Dependencies and Integration Points
Consumed by `dcn303_init.c` when patching the inherited DCN30 table.

## Risks and Test Signals
Compile coverage and runtime confirmation that PG paths do not access removed registers.
