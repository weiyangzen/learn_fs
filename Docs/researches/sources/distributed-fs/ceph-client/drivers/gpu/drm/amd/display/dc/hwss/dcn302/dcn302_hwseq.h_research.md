# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn302/dcn302_hwseq.h

## Purpose
Declares DCN302 power-gating overrides.

## Important APIs, Types, and Functions
Includes `hw_sequencer_private.h` and declares DPP, HUBP, and DSC PG control functions.

## Control Flow
No executable flow.

## State and Persistence Behavior
No direct state; declared functions mutate PG registers.

## Dependencies and Integration Points
Used by `dcn302_init.c` to override inherited DCN30 private HWSS hooks.

## Risks and Test Signals
Compile coverage plus runtime PG tests for all declared hooks.
