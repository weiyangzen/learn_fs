# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-rt.c

## Purpose
Implements the real-time changelog dispatch mode, serializing change handling behind a simple lock.

## APIs, Types, and Functions
`changelog_rt_init()` allocates `changelog_rt_t`, initializes its lock, stores it in `changelog_dispatcher_t::cd_data`, and sets `dispatchfn` to `changelog_rt_enqueue()`. `changelog_rt_fini()` destroys and frees that state. `changelog_rt_enqueue()` locks, calls `changelog_handle_change()` for the primary record and optional second record, then unlocks.

## Control Flow, State, and Persistence
The runtime state is a single lock protecting writes and rollover/fync handling in the selected dispatch mode. Persistence is delegated to `changelog_handle_change()`, so this file enforces ordering rather than writing files directly.

## Dependencies and Integration
Depends on Gluster locks, logging, memory accounting, and changelog helper APIs. Selected by the changelog bootstrap table in the main xlator for `CHANGELOG_MODE_RT`.

## Risks and Test Signals
Risks include serialization bottlenecks, missing error handling if lock initialization fails, and no batching beyond the optional second record. Test signals include ordered two-record rename handling, concurrent FOP updates producing non-interleaved records, and clean init/fini under reconfigure.
