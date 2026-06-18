# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn301/dcn301_hwseq.h

## Purpose
Placeholder header for DCN 3.0.1 HWSS-specific declarations.

## Important APIs, Types, and Functions
Includes `hw_sequencer_private.h` but declares no DCN301-specific functions.

## Control Flow
No executable flow.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Included by `dcn301_init.c` and `dcn301_hwseq.c`; it reserves a generation-specific extension point while DCN301 uses inherited behavior.

## Risks and Test Signals
Low risk. Test signal is successful compilation and absence of unresolved DCN301 symbols.
