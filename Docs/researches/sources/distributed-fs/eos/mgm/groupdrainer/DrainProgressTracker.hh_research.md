# sources/distributed-fs/eos/mgm/groupdrainer/DrainProgressTracker.hh

## Purpose
Declares `DrainProgressTracker`, the in-memory counter used to expose group-drainer progress per filesystem.

## Important APIs, types, and functions
The class defines `fsid_t`, mutators for total file counts and scheduled counts, removal/reset methods, and read methods for percent, total files, and file counter.

## Control flow
The drainer updates the tracker while discovering files and scheduling transfer jobs. UI/status calls read it without modifying drainer state.

## State and persistence
`mFsTotalfiles` and `mFsScheduledCounter` are guarded by `mFsTotalFilesMtx` and `mFsScheduledCtrMtx`. State is cleared on reset or FSID drop and is not durable.

## Dependencies and integration points
Depends only on standard containers/mutex and EOS filesystem ID types, making it easy to unit test independently.

## Risks and test signals
Two-mutex design requires consistent multi-lock ordering, which the implementation uses via `std::scoped_lock`. Tests should assert zero behavior for unknown FSIDs and no deadlocks under parallel readers/writers.
