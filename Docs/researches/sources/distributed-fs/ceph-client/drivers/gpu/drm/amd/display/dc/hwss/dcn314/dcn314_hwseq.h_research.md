# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn314/dcn314_hwseq.h

## Purpose
Declares DCN314 HWSS-specific ODM, DSC, power, clock-divider, FIFO resync, root-clock, link-disable, and DPP PG functions.

## Important APIs, Types, and Functions
Includes `hw_sequencer_private.h`, forward-declares `struct dc`, and declares all exported functions from `dcn314_hwseq.c`.

## Control Flow
No executable flow.

## State and Persistence Behavior
No local state; declared functions mutate DC pipe, link, clock, DSC/ODM, and register state.

## Dependencies and Integration Points
Consumed by `dcn314_init.c` and any shared code calling DCN314 helpers through private HWSS hooks.

## Risks and Test Signals
Compile/link coverage plus runtime coverage for every hook assigned in `dcn314_init.c`, especially pixel divider and FIFO resync.
