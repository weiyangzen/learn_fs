# sources/distributed-fs/ceph-client/tools/include/linux/gfp.h

## Purpose

This header provides minimal GFP flag helpers for tools code that shares kernel allocation-style APIs.

## APIs, State, and Dependencies

It includes Linux types and `gfp_types.h`, defines `default_gfp` helper macros to supply `GFP_KERNEL` when no flag is passed, and implements `gfpflags_allow_blocking(gfp_t)` by testing `__GFP_DIRECT_RECLAIM`. It has no state.

## Risks and Test Signals

The helper reflects kernel GFP semantics only at a shallow flag level; userspace allocation behavior is not controlled by GFP flags. Tests should compile allocation wrappers and verify blocking classification for `GFP_KERNEL`, atomic/no-reclaim-style flags, and explicit default macro expansion.
