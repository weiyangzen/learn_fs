# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn201/dcn201_hwseq.h

## Purpose
Declares the DCN 2.0.1 hardware sequencing functions used by the DCN201 dispatch tables.

## Important APIs, Types, and Functions
Includes `hw_sequencer_private.h` and declares the exported DCN201 helpers for DMData, hardware init, unblank, plane address update, atomic disconnect, MPCC update, cursor attributes, pipe control lock, and blank initialization.

## Control Flow
No executable control flow. It defines the compile-time contract between `dcn201_init.c` and `dcn201_hwseq.c`.

## State and Persistence Behavior
No direct state. Functions declared here mutate DC pipe/resource/hardware state in the implementation.

## Dependencies and Integration Points
The included private HWSS header supplies `struct dc`, `struct pipe_ctx`, `struct dc_state`, `struct timing_generator`, and related types used in prototypes.

## Risks and Test Signals
Header/implementation mismatch breaks builds or vtable assignment. Compile coverage from DCN201 initialization is the primary test signal.
