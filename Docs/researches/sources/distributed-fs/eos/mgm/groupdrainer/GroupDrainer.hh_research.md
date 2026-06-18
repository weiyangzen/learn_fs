# sources/distributed-fs/eos/mgm/groupdrainer/GroupDrainer.hh

## Purpose
Declares the per-space group drainer service and its scheduling, retry, status, and cache management APIs.

## Important APIs, types, and functions
Public methods include lifecycle (`GroupDrainer`, destructor, `Stop()`, `GroupDrain()`), configuration (`Configure()`, `reconfigure()`), transfer handling, retry handling, status reporting, resets, and static group-drain status helpers. Type aliases define FSID-to-FID caches and group-to-FSID drain maps. Constants set cache batch size, default transfer count, cache expiry, retry count, and threshold.

## Control flow
The class owns an `AssistedThread` and an engine. Public helper methods are used by the main loop and by UI/control code to query status, reset failures/caches, and force reconfiguration.

## State and persistence
State covers refresh flags, retry/round-robin counters, transfer limits, retry intervals, timestamps, space name, engine config, transfer and failed-transfer collections, tracked transfer history, drain FS maps, retry trackers, failed FSIDs, FID iterators, cached file lists, and `DrainProgressTracker`. Persistent effects are performed by the implementation when statuses or converter jobs are changed.

## Dependencies and integration points
Depends on assisted threading, file IDs, filesystem types, logging, `FsView`, group-balancer types, progress/retry trackers, filesystem status utilities, and namespace iterators.

## Risks and test signals
The class exposes several methods used by both the worker thread and UI paths; locking coverage should be tested around transfer sets and drain maps. Tests should cover `trackedTransferEntry()` allowing failed retries, `isTransfersFull()`, allowed transfer computation, reset semantics, and `checkGroupDrainStatus()` mapping.
