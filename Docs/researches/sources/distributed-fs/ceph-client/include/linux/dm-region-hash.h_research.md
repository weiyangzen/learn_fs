<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dm-region-hash.h -->
# sources/distributed-fs/ceph-client/include/linux/dm-region-hash.h

## Purpose
Declares Device Mapper's dirty-region hash interface, used to coordinate write tracking and resynchronization by region.

## Important APIs, Types, And Functions
Opaque types are `struct dm_region_hash` and `struct dm_region`. Region states are `DM_RH_CLEAN`, `DM_RH_DIRTY`, `DM_RH_NOSYNC`, and `DM_RH_RECOVERING`. APIs create/destroy hashes, access the dirty log, convert bios to regions and regions to sectors, inspect context/key/size, get/set/update state, flush, increment/decrement pending counts, delay bios, mark nosync, and control recovery lifecycle.

## Control Flow
The target creates a region hash with dispatch and wakeup callbacks, increments pending state for writes, delays conflicting bios, updates states after I/O completion, flushes the log, and runs recovery by preparing regions, starting a quiesced region, and ending recovery with success or error.

## State And Persistence
The hash tracks per-region dirty/nosync/recovering state, pending I/O counts, delayed bios, recovery-in-flight count, and a pointer to the dirty log. Persistent sync state is delegated to the dirty log.

## Dependencies And Integration Points
Depends on `dm-dirty-log`, bios, bio lists, and DM mirror-style recovery workers. Integration callbacks wake workers and dispatch delayed bios when regions quiesce.

## Risks And Edge Cases
State transitions must keep dirty-log state consistent. Nonzero `errors_handled` leaves regions `NOSYNC`. Delayed bios must be released exactly once. Recovery must quiesce regions before copying to avoid concurrent writes.

## Test Signals
Tests should cover bio-to-region mapping, pending inc/dec, dirty/nosync transitions, delayed bio dispatch, flush errors, recovery prepare/start/end, remote recovery interaction through the log, and error handling that preserves NOSYNC state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dm-region-hash.h -->
