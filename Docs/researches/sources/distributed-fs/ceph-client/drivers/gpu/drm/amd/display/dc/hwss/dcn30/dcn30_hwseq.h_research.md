# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn30/dcn30_hwseq.h

## Purpose
Declares DCN 3.0 HWSS operations for initialization, writeback, color, metadata, MALL, bandwidth, pattern generation, pending-update waits, and underflow debug.

## Important APIs, Types, and Functions
Includes `hw_sequencer_private.h`, forward-declares `struct dc` and `struct dc_underflow_debug_data`, and exposes the functions implemented in `dcn30_hwseq.c`. Notably declares `dcn30_set_hubp_blank`, which is not implemented in the read file and may be implemented elsewhere or stale.

## Control Flow
No executable flow. It provides prototypes consumed by init tables and later-generation implementations.

## State and Persistence Behavior
No local state. Declared functions operate on DC resource pools, streams, pipes, DMUB, clocks, DWB/MCIF, and hardware registers.

## Dependencies and Integration Points
Common dependency for DCN30, DCN301, DCN302, DCN303, DCN31, and DCN314 init code. The private HWSS include supplies shared DC type definitions.

## Risks and Test Signals
Prototype drift affects many generations. The `dcn30_set_hubp_blank` declaration should be checked during build/link. Runtime tests should cover every vtable hook assigned from this header.
