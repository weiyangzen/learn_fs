# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_hw_sequencer_debug.h

## Purpose
Declares public DCN1 hardware-state debug helpers.

## Important APIs, Types, And Functions
Exports `dcn10_clear_status_bits()` and `dcn10_get_hw_state()`. It also declares `dcn10_log_hw_state()`, which is not implemented in the paired source file in this subset and may be implemented conditionally or in another snapshot. It forward-declares `struct dc` and includes `core_types.h`.

## Control Flow
No executable flow. Consumers call the declared functions from debug or hardware-sequencer code paths.

## State And Persistence
No state in the header. Implementations read diagnostic state and may clear hardware underflow flags.

## Dependencies And Integration Points
This header is the interface between debugfs/logging callers and DCN10 debug implementation.

## Risks
Prototype drift, especially for `dcn10_log_hw_state()`, can cause link failures if a caller references a declaration that is not built. Mask semantics are documented only in implementation comments, not in typed enums.

## Test Signals
Build/link coverage for all declared functions and smoke tests of debug state collection through the user-facing diagnostic interface.
