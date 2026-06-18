# sources/distributed-fs/eos/mgm/groupdrainer/GroupDrainer.cc

## Purpose
Implements the group drainer service that moves files out of groups marked for drain into suitable target groups using the converter engine.

## Important APIs, types, and functions
`GroupDrain()` is the main thread loop. It configures the service, registers a converter observer, refreshes engine state, throttles transfers, and calls `prepareTransfers()`. `Configure()` reads `groupdrainer` settings, max transfers, retry interval/count, refresh interval, and threshold. `prepareTransfer()` chooses a drain source and target group, refreshes FSID maps, populates FID caches, and schedules one transfer. `populateFids()` streams up to `FID_CACHE_LIST_SZ` FIDs, handles ghost entries, separates failed retry candidates, and applies drained status when empty. `handleRetries()` enforces retry backoff and failure thresholds. Static helpers compute and persist drain-complete or drain-failed group status.

## Control flow
The loop runs only on the master. It waits if config/converter is invalid, registers converter callbacks once, stops scheduling when the transfer set is full, periodically refreshes group data, picks source/target groups from `StdDrainerEngine`, and schedules converter jobs. Converter callbacks remove completed transfers or move failed jobs into retry state.

## State and persistence
In-memory state includes transfer sets, failed transfer map, tracked transfer set, cached FID lists, streaming iterators, retry trackers, drain FS map, round-robin seeds, progress tracker, and refresh flags. Persistent side effects include converter jobs, FS drain status updates through `fsutils::ApplyDrainedStatus/ApplyFailedDrainStatus`, deletion of ghost FIDs from FS view, and group config `status` changes to drained/drainfailed.

## Dependencies and integration points
Integrates `ConverterEngine`, `ConversionInfo`, `StdDrainerEngine`, `ConverterUtils`, `GroupsInfoFetcher`, `FsView`, `FileSystemStatusUtils`, namespace file services, table formatting, and `BackOffInvoker`.

## Risks and test signals
`handleRetries()` copies `RetryTracker` before checking count, so log count can be stale and max-retry behavior needs careful testing. Observer lifetime is not explicitly removed in the visible code. Tests should cover converter DONE/FAILED callbacks, full queues, ghost file cleanup, empty/offline FS maps, retry interval/count, status transitions, reset methods, and non-master behavior.
