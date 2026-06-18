# subset-b-007032 EOS MGM group balancer, group drainer, and gRPC namespace research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/BalancerEngineUtils.hh -->
# sources/distributed-fs/eos/mgm/groupbalancer/BalancerEngineUtils.hh

## Purpose
Provides small header-only helpers shared by the group balancer engines for average calculation, typed configuration extraction, percent parsing, comma-list parsing, and threshold validation.

## Important APIs, types, and functions
`calculateAvg()` averages `GroupSizeInfo::filled()` over a `group_size_map`. `extract_value()` is a generic map lookup plus extractor wrapper that invokes the extractor on an empty string when a key is missing. `extract_double_value()` uses `common::StringToNumeric()` with a default and optional error string. `extract_percent_value()` converts configured percent values to fractions. `extract_commalist_value()` returns an unordered set from a comma/space-delimited string. `is_valid_threshold()` validates one or more positive numeric strings.

## Control flow
Engines call these helpers during `configure()` and `recalculate()`. Missing config keys flow through defaults, while invalid numeric strings are reported through the shared error string and logged by callers.

## State and persistence
This file stores no state and performs no persistence. Its outputs become in-memory engine thresholds and blocklists.

## Dependencies and integration points
Depends on `common/StringUtils.hh`, `common/StringSplit.hh`, and `BalancerEngine.hh` types. It is used by `MinMaxBalancerEngine`, `StdDevBalancerEngine`, `StdDrainerEngine`, and `FreeSpaceBalancerEngine`.

## Risks and test signals
`std::stod()` accepts partial numeric strings, so threshold validation may allow values with suffixes. Default values passed to `extract_percent_value()` are treated as percent values, which makes callers sensitive to whether they pass `2` or `0.02`. Tests should cover missing keys, malformed strings, zero/negative thresholds, comma-list whitespace, and multi-threshold validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/BalancerEngineUtils.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/ConverterUtils.cc -->
# sources/distributed-fs/eos/mgm/groupbalancer/ConverterUtils.cc

## Purpose
Implements conversion-tag construction for balancer and drainer transfers by resolving file metadata, optionally filtering paths, returning file size, and formatting a proc conversion path.

## Important APIs, types, and functions
`PrefixFilter::operator()` rejects paths with a configured prefix using `common::startsWith()`. `getFileProcTransferNameAndSize()` prefetches file metadata, retrieves the file from `gOFS->eosFileService`, resolves the namespace URI, locks the file metadata for reading, checks container membership, applies the optional skip filter, writes the file size, and formats `<MgmProcConversionPath>/<fid>:<target_group>#<layoutid>`.

## Control flow
The caller supplies an FID and target group. The helper returns an empty string for metadata lookup failures, files without container ownership, and filtered paths. Successful calls return the proc conversion file name and optionally fill `size`.

## State and persistence
No durable state is written here. It reads namespace metadata under a metadata lock and exposes enough data for later converter scheduling.

## Dependencies and integration points
Uses `gOFS`, `Prefetcher`, `IView`, `IFileMD`, `LayoutId`, `MDLocking`, and EOS logging. `GroupBalancer` uses a prefix filter to avoid moving proc files; `GroupDrainer` uses `NullFilter`.

## Risks and test signals
The fixed 1024-byte buffer may truncate very long proc paths or group names. It returns empty strings for several different failure classes, so callers cannot distinguish filter skips from metadata failures. Tests should cover missing FIDs, container id zero, prefix filtering, size output, layout id formatting, and long target group names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/ConverterUtils.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/ConverterUtils.hh -->
# sources/distributed-fs/eos/mgm/groupbalancer/ConverterUtils.hh

## Purpose
Declares transfer-name helpers and file skip filters used by both group balancing and group draining code paths.

## Important APIs, types, and functions
`SkipFileFn` is a `std::function<bool(std::string_view)>` predicate. `NullFilter` is an empty function meaning no filtering. `PrefixFilter` stores a prefix and implements path-prefix rejection. `getFileProcTransferNameAndSize()` is the exported helper that maps an EOS file id and target group to a converter proc-file name while returning the source file size.

## Control flow
Callers construct a filter appropriate to the workflow, invoke the helper, check for an empty result, then append workflow-specific tags such as `^groupbalancer^` or `^groupdrainer^` before scheduling a converter job.

## State and persistence
The header defines no persistent state. `PrefixFilter::prefix` is per-instance transient state.

## Dependencies and integration points
Includes `common/FileId.hh` and is consumed by `GroupBalancer.hh`, `GroupDrainer.cc`, and the implementation file. It is part of the converter scheduling boundary.

## Risks and test signals
Because `NullFilter` is an empty `std::function`, implementation code must guard it before invocation. Tests should validate filter construction from string views, empty filters, target group propagation, and compatibility with converter tag parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/ConverterUtils.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/FreeSpaceBalancerEngine.cc -->
# sources/distributed-fs/eos/mgm/groupbalancer/FreeSpaceBalancerEngine.cc

## Purpose
Implements a balancer engine that classifies groups by absolute free space rather than used-percentage deviation.

## Important APIs, types, and functions
`configure()` reads `min_threshold`, `max_threshold`, and `blocklisted_groups`. `recalculate()` sums capacity and used bytes across non-blocklisted ON groups, then computes expected free space per participating group. `getFreeSpaceULimit()` and `getFreeSpaceLLimit()` derive deviation bounds. `updateGroup()` classifies groups with too much free space as targets and groups with too little free space as sources. `get_status_str()` reports engine state and blocklisted groups.

## Control flow
After `populateGroupsInfo()`, the base engine calls `recalculate()` and `updateGroup()` per group. Blocklisted groups are excluded from totals and classification. Balancer scheduling then picks one source from `mGroupsOverThreshold` and one target from `mGroupsUnderThreshold`.

## State and persistence
Stores total free space, computed per-group free space, min/max deviation fractions, and an in-memory blocklist protected by `mtx`. No persistent storage is modified.

## Dependencies and integration points
Uses `BalancerEngineUtils.hh` for config parsing and `common/Logging.hh` for errors. `GroupBalancer` selects this engine via `groupbalancer.engine=freespace` and disables average mode in `eosGroupsInfoFetcher`.

## Risks and test signals
`mTotalFreeSpace` and `mGroupFreeSpace` are not explicitly initialized in the header, so status before first recalculation can expose indeterminate values. `mGroupFreeSpace` is not reset when all groups are filtered out. Tests should cover blocklist exclusion, zero participating groups, integer division, threshold boundaries, and thread-safe concurrent status/config/update calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/FreeSpaceBalancerEngine.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/FreeSpaceBalancerEngine.hh -->
# sources/distributed-fs/eos/mgm/groupbalancer/FreeSpaceBalancerEngine.hh

## Purpose
Declares the free-space based `BalancerEngine` implementation for balancing groups toward equal free bytes.

## Important APIs, types, and functions
`FreeSpaceBalancerEngine` overrides `recalculate()`, `updateGroup()`, `configure()`, and `get_status_str()`. Test-facing getters expose expected per-group free space and computed lower/upper limits. `group_set_t` holds blocklisted group names.

## Control flow
The base `BalancerEngine` owns group maps and calls this subclass to compute aggregate free space and classify each group. Calls are synchronized by a private mutex in methods that mutate configuration or computed state.

## State and persistence
Members include `mTotalFreeSpace`, `mGroupFreeSpace`, `mMinDeviation`, `mMaxDeviation`, `mtx`, and `mBlocklistedGroups`. All state is in memory and recomputed from `FsView` snapshots supplied by `GroupsInfoFetcher`.

## Dependencies and integration points
Inherits from `mgm/groupbalancer/BalancerEngine.hh` and participates in `BalancerEngineFactory.hh`. The blocklist is populated from space configuration `groupbalancer.blocklist`.

## Risks and test signals
The header comments state that the getters are not thread-safe on their own and depend on callers holding locks. Tests should instantiate the class through the factory, validate defaults, and verify the monitoring/status strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/FreeSpaceBalancerEngine.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/GroupBalancer.cc -->
# sources/distributed-fs/eos/mgm/groupbalancer/GroupBalancer.cc

## Purpose
Implements the per-space group balancer service thread that periodically classifies groups, picks source/target groups, selects eligible files, and schedules converter jobs to move data between groups.

## Important APIs, types, and functions
The constructor creates the default stddev engine and starts the assisted thread. `Configure()` reads space config (`groupbalancer`, `groupbalancer.ntx`, min/max file sizes, engine, attempts, thresholds, blocklist) and checks converter availability. `GroupBalance()` is the main loop. `chooseFidFromGroup()` picks random filesystems and random FIDs. `chooseFileFromGroup()` filters by converter metadata and size bounds. `prepareTransfer()` selects groups via the engine. `scheduleTransfer()` builds a converter tag and calls `ConverterEngine::ScheduleJob()`. `UpdateTransferList()` prunes finished jobs through `mFidTracker`.

## Control flow
The thread waits for namespace boot, runs only on the master MGM, refreshes config when `mDoConfigUpdate` is set, cleans converter tracker state, recreates the engine when the configured type changes, refreshes group-size caches every 60 seconds or after engine changes, and schedules up to `groupbalancer.ntx` transfers when the engine can pick source and target groups.

## State and persistence
In-memory state includes current config, engine instance, engine config map, transfer map, last cache refresh, and proc-path filter. Persistent effects are indirect: converter jobs are scheduled and can cause files to be converted/moved; no config is written by this file.

## Dependencies and integration points
Integrates `FsView`, `FsSpace`, `FsGroup`, namespace services, `ConverterEngine`, `FidTracker`, `BalancerEngineFactory`, `GroupsInfoFetcher`, and `ConverterUtils`. The proc conversion tag includes `^groupbalancer^`.

## Risks and test signals
`mEngine.reset()` in the main loop is not guarded by `mEngineMtx`, while `Status()` can read the engine under that lock. File selection is random and may fail silently after many attempts. Tests should cover disabled converter, invalid thresholds per engine, engine switching, cache expiry, transfer pruning, size filtering, duplicate transfer suppression, and non-master behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/GroupBalancer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/GroupBalancer.hh -->
# sources/distributed-fs/eos/mgm/groupbalancer/GroupBalancer.hh

## Purpose
Declares the public and private contract for the per-space group balancing service.

## Important APIs, types, and functions
`GroupBalancer` exposes construction, destruction, `Stop()`, `GroupBalance()`, `Configure()`, `Status()`, `is_valid_engine()`, and `reconfigure()`. `Config` holds enable flags, converter status, transfer limit, min/max file sizes, attempt count, and engine type. `FileInfo` carries selected FID, proc filename, and size with a boolean validity operator.

## Control flow
The class owns an `AssistedThread` that runs `GroupBalance()`. Private helpers split the workflow into file selection, transfer preparation, converter scheduling, cache-expiry checks, and transfer-list cleanup.

## State and persistence
Members track the space name, current configuration, reconfiguration flag, engine mutex and engine pointer, last group-size refresh, scheduled transfers, engine config, and proc-path filter. There is no direct persistence, but scheduled converter jobs produce storage movement.

## Dependencies and integration points
Uses EOS namespace, filesystem view, file IDs, assisted threading, `BalancerEngineTypes`, and `ConverterUtils`. It is instantiated per MGM space and depends on `gOFS` services at runtime.

## Risks and test signals
Defaults are large-file oriented: 1 GiB to 16 GiB and 50 attempts. Tests should validate `Config` defaults, `FileInfo` truthiness, engine-name validation, `reconfigure()` atomic semantics, and lifecycle behavior when `Stop()` is called during waits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/GroupBalancer.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/GroupsInfoFetcher.cc -->
# sources/distributed-fs/eos/mgm/groupbalancer/GroupsInfoFetcher.cc

## Purpose
Fetches current group capacity and usage data from `FsView` for a configured space, applying group-status filters and averaging or summing filesystem counters.

## Important APIs, types, and functions
`eosGroupsInfoFetcher::fetch()` locks `FsView::gFsView.ViewMutex`, verifies the space exists in `mSpaceGroupView`, iterates each `FsGroup`, converts its `status` config to `GroupStatus`, applies `is_valid_status()`, computes used bytes and capacity through either `AverageDouble()` or `SumLongLong()`, skips zero-capacity groups, and returns a `group_size_map`.

## Control flow
Balancer and drainer loops call `fetch()` before populating engine state. The `do_average` flag determines whether per-filesystem statistics are averaged or summed, with freespace balancing explicitly using summed values.

## State and persistence
No durable state is modified. The method reads live filesystem view state and returns a new map.

## Dependencies and integration points
Uses `FsView`, `FsGroup` config members, `GroupStatus` helpers, and `GroupSizeInfo`. It is the data source for all engines in this subset.

## Risks and test signals
The method logs and returns an empty map for unknown spaces, which disables picking but may mask configuration mistakes. Tests should cover missing spaces, status filtering, average versus sum mode, zero capacity, and multiple statuses including drain states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/GroupsInfoFetcher.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/GroupsInfoFetcher.hh -->
# sources/distributed-fs/eos/mgm/groupbalancer/GroupsInfoFetcher.hh

## Purpose
Declares the injectable interface and EOS implementation for building `group_size_map` snapshots consumed by balancer engines.

## Important APIs, types, and functions
`IGroupsInfoFetcher` exposes `fetch()`. `OnGroupStatusFilter` accepts only `GroupStatus::ON`. `eosGroupsInfoFetcher` stores a space name, type-erased callable status filter, and `do_average` flag. Templated constructors accept any callable taking `GroupStatus`; `should_average()` controls aggregation mode.

## Control flow
Production code instantiates the fetcher with a space name and optional status predicate. Tests can replace the fetcher through the interface or use custom predicates to include drain groups.

## State and persistence
Only transient configuration is stored: `spaceName`, `status_filter_fn`, and `do_average`.

## Dependencies and integration points
Depends on `BalancerEngineTypes.hh`, C++ memory utilities, and `FsView` in the implementation. `GroupBalancer` uses the default ON filter; `GroupDrainer` supplies a DRAIN-or-ON predicate.

## Risks and test signals
The type-erased filter owns arbitrary callable state, so move-only/lifetime cases deserve coverage. Tests should verify default filtering, lambda filtering, toggling `should_average()`, and interface substitution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/GroupsInfoFetcher.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/MinMaxBalancerEngine.cc -->
# sources/distributed-fs/eos/mgm/groupbalancer/MinMaxBalancerEngine.cc

## Purpose
Implements a threshold engine that classifies groups solely by configured minimum and maximum fill percentages.

## Important APIs, types, and functions
`configure()` reads `min_threshold` and `max_threshold`, defaulting to 60% and 90%. `updateGroup()` clears previous classification, marks groups above max as sources, and groups below min as targets. `get_status_str()` reports thresholds and base engine state.

## Control flow
Unlike stddev/freespace engines, `recalculate()` is a no-op because classification does not depend on global aggregates. `updateGroup()` operates on each group's `filled()` value from `data.mGroupSizes`.

## State and persistence
Stores two in-memory threshold fractions. No persistence or external state changes occur.

## Dependencies and integration points
Uses `BalancerEngineUtils.hh` and `common/Logging.hh`. Selected by `groupbalancer.engine=minmax`.

## Risks and test signals
Invalid config is rejected earlier by `GroupBalancer::Configure()` for minmax, but this class still logs conversion errors and keeps defaulted values. Tests should cover exact boundary behavior, missing config defaults, min greater than max, and groups absent from the map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/MinMaxBalancerEngine.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/MinMaxBalancerEngine.hh -->
# sources/distributed-fs/eos/mgm/groupbalancer/MinMaxBalancerEngine.hh

## Purpose
Declares the configured min/max fill-percentage balancer engine.

## Important APIs, types, and functions
`MinMaxBalancerEngine` overrides `updateGroup()`, `configure()`, and `get_status_str()`, while `recalculate()` is intentionally empty. `get_min_threshold()` and `get_max_threshold()` are test-facing accessors.

## Control flow
The base engine populates group information and invokes `updateGroup()` for each group. Groups are classified independently from all other groups.

## State and persistence
The class stores `mMinThreshold` and `mMaxThreshold` as doubles. There is no direct persistent state.

## Dependencies and integration points
Inherits `BalancerEngine` and is constructed by the factory for `minmax`.

## Risks and test signals
The thresholds have no in-class initializers, so tests should call `configure()` before using the instance. Header-level tests should assert no aggregate recalculation is required and accessors reflect parsed config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/MinMaxBalancerEngine.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/StdDevBalancerEngine.cc -->
# sources/distributed-fs/eos/mgm/groupbalancer/StdDevBalancerEngine.cc

## Purpose
Implements the default percentage-deviation balancer engine, classifying groups relative to average fill level.

## Important APIs, types, and functions
`configure()` reads `min_threshold` and `max_threshold` as percent deviations. `recalculate()` sets `mAvgUsedSize` from `calculateAvg()`. `updateGroup()` compares a group's fill ratio to the average, clears old state, marks high positive deviation as source and low negative deviation as target. `get_status_str()` reports average and deviations.

## Control flow
On each group snapshot refresh, the base engine recalculates the average and updates each group. Later `pickGroupsforTransfer()` pairs groups from the classified sets.

## State and persistence
Stores average fill and deviation thresholds in memory only.

## Dependencies and integration points
Uses `BalancerEngineUtils.hh` and EOS logging. It is the default engine created by `GroupBalancer`.

## Risks and test signals
Defaults are passed as `0.05` to `extract_percent_value()`, which divides by 100 and therefore yields `0.0005`, unless this is intentional to represent 0.05 percent. Tests should verify expected default threshold semantics, average calculation on empty maps, boundary equality, and status output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/StdDevBalancerEngine.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/StdDevBalancerEngine.hh -->
# sources/distributed-fs/eos/mgm/groupbalancer/StdDevBalancerEngine.hh

## Purpose
Declares the standard deviation-from-average balancer engine used as the default group balancer.

## Important APIs, types, and functions
The class overrides `recalculate()`, `updateGroup()`, `configure()`, and `get_status_str()`. Accessors expose min and max deviation thresholds to unit tests.

## Control flow
The base class owns group data; this subclass supplies the average and classification policy. Groups over the average by more than max deviation become sources, and groups under the average by more than min deviation become targets.

## State and persistence
In-memory fields are `mAvgUsedSize`, `mMinDeviation`, and `mMaxDeviation`.

## Dependencies and integration points
Depends on `BalancerEngine.hh` and participates in `BalancerEngineFactory` as the fallback/default engine.

## Risks and test signals
The header does not initialize its doubles, so `configure()`/`recalculate()` ordering matters. Tests should verify constructor plus configure behavior and that status before population is either avoided or deterministic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/StdDevBalancerEngine.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/StdDrainerEngine.cc -->
# sources/distributed-fs/eos/mgm/groupbalancer/StdDrainerEngine.cc

## Purpose
Implements the engine used by group draining: draining groups are sources, and underfilled ON groups are targets.

## Important APIs, types, and functions
`configure()` reads `threshold`. `recalculate()` computes average fill. `updateGroup()` marks `GroupStatus::DRAIN` groups as over-threshold sources and marks ON groups under average by more than the threshold as under-threshold targets; a zero threshold allows any ON group below average to be a target.

## Control flow
`GroupDrainer` fetches both DRAIN and ON groups, populates this engine, and then repeatedly asks for transfer pairs. The source set is therefore the set of groups explicitly marked for drain.

## State and persistence
Stores average fill and threshold in memory. Persistent changes happen in `GroupDrainer`, not this engine.

## Dependencies and integration points
Uses `BalancerEngineUtils.hh`, EOS logging, and `GroupSizeInfo::draining()/on()`. Owned by `GroupDrainer`.

## Risks and test signals
The method does not explicitly clear a non-draining group's prior source/target entries before classification, relying on base refresh behavior. Tests should cover draining groups, ON groups above/below average, zero threshold, and empty maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/StdDrainerEngine.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/StdDrainerEngine.hh -->
# sources/distributed-fs/eos/mgm/groupbalancer/StdDrainerEngine.hh

## Purpose
Declares the balancer-engine variant used by the group drainer workflow.

## Important APIs, types, and functions
`StdDrainerEngine` overrides `recalculate()`, `updateGroup()`, and `configure()`. `get_threshold()` exposes configured threshold for validation.

## Control flow
The engine follows the common `BalancerEngine` populate/update/pick contract but interprets over-threshold groups as drain sources and under-threshold groups as acceptable destinations.

## State and persistence
Fields are `mAvgUsedSize` and `mThreshold`, both transient.

## Dependencies and integration points
Inherits `BalancerEngine`. `GroupDrainer` constructs it directly rather than via the standard factory.

## Risks and test signals
As with other engines, uninitialized doubles require configuration before use. Tests should verify construction in `GroupDrainer`, threshold parsing, and interactions with `GroupStatus` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupbalancer/StdDrainerEngine.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupdrainer/DrainProgressTracker.cc -->
# sources/distributed-fs/eos/mgm/groupdrainer/DrainProgressTracker.cc

## Purpose
Implements a thread-safe per-filesystem progress counter for group drain scheduling.

## Important APIs, types, and functions
`setTotalFiles()` records the largest known total file count for an FSID. `increment()` increases scheduled/drained count. `getDrainStatus()` returns scheduled count divided by total as a percent. `dropFsid()` and `clear()` remove tracked entries. `getTotalFiles()` and `getFileCounter()` expose counters.

## Control flow
`GroupDrainer` calls `setTotalFiles()` when populating file lists and `increment()` after successfully scheduling a converter job. Status reporting reads the counters to format per-FSID progress.

## State and persistence
Two maps hold total files and scheduled counters. They are protected by separate mutexes and are not persisted.

## Dependencies and integration points
Uses `common/FileSystem.hh` FSID type. Integrated into `GroupDrainer::getStatus()`.

## Risks and test signals
`getDrainStatus()` can exceed 100 percent because failed/retried schedules may increment more than the original total. Tests should cover concurrent increments, increasing totals, zero totals, dropped FSIDs, and lock ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupdrainer/DrainProgressTracker.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupdrainer/DrainProgressTracker.hh -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupdrainer/DrainProgressTracker.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupdrainer/GroupDrainer.cc -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupdrainer/GroupDrainer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupdrainer/GroupDrainer.hh -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupdrainer/GroupDrainer.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupdrainer/RetryTracker.hh -->
# sources/distributed-fs/eos/mgm/groupdrainer/RetryTracker.hh

## Purpose
Provides a small retry backoff tracker for filesystem drain retry attempts.

## Important APIs, types, and functions
`DEFAULT_RETRY_INTERVAL` is four hours. `RetryTracker` stores `count` and `last_run_time`. `need_update()` returns true before the first run or after the configured interval has elapsed. `update()` increments the count and records the current steady-clock time. Both methods accept an optional `SteadyClock` test hook.

## Control flow
`GroupDrainer::populateFids()` and `handleRetries()` use this tracker to suppress repeated retries for failed FIDs on the same FSID until the interval passes.

## State and persistence
State is in memory per FSID inside `GroupDrainer::mFsidRetryCtr`.

## Dependencies and integration points
Depends on `common/SteadyClock.hh` for testable time.

## Risks and test signals
The comparison uses `>` rather than `>=`, so exactly equal elapsed intervals do not retry. Count is `uint16_t`; long-running services should avoid overflow assumptions. Tests should cover first run, before/after interval, exact boundary, injected clock, and update count progression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/groupdrainer/RetryTracker.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/grpc/GrpcNsInterface.cc -->
# sources/distributed-fs/eos/mgm/grpc/GrpcNsInterface.cc

## Purpose
Implements the gRPC namespace bridge for EOS MGM, translating RPC metadata, find, insert, namespace-stat, and namespace command requests into existing MGM namespace, proc command, ACL, recycle, quota, token, and filesystem APIs.

## Important APIs, types, and functions
`Filter()` applies `MDSelection` predicates to file and container metadata. `GetMD()` streams file or container metadata responses and fills protobuf fields, checksums, xattrs, paths, etags, locations, and timestamps. `Stat()`, `StreamMD()`, and `Find()` implement metadata lookup, listing, and breadth-by-depth traversal. `Access()` applies UNIX permissions and EOS ACL checks. `NsStat()` reports namespace and process health. `FileInsert()` and `ContainerInsert()` create metadata as sudo-only operations. `Exec()` dispatches namespace commands to `Mkdir`, `Rmdir`, `Touch`, `Unlink`, `Rm`, `Rename`, `Symlink`, `SetXAttr`, `Version`, recycle commands, `Chown`, `Chmod`, `Acl`, `Token`, and `Quota`.

## Control flow
Requests optionally remap the caller identity if the authenticated identity is sudo-capable. Metadata paths prefetch namespace records, take read locks when needed, check parent or self access, filter, then stream protobuf responses. Mutation commands resolve path or id inputs, delegate to `gOFS` or command objects, and encode return codes/messages into the RPC reply while usually returning `grpc::Status::OK`.

## State and persistence
This file can create and update namespace file/container metadata, set xattrs, mutate ACLs, create/purge/grab versions, remove or recycle files, chown/chmod paths, create tokens, and set/remove quota entries. It also reads process memory/fd stats. Locks are taken around namespace view reads/writes.

## Dependencies and integration points
Compiled under `EOS_GRPC`. Depends on generated RPC protobufs, gRPC server writer/status, `gOFS`, namespace services, `Prefetcher`, `Acl`, proc command wrappers, recycle/quota/token command classes, Linux process-stat helpers, checksum/layout helpers, etag helpers, regex, and XRootD error structures.

## Risks and test signals
Several command handlers return application errors in reply payloads rather than gRPC error statuses, so clients must inspect both. File filtering appears to check `mtime` twice and uses `mtime` for `locations()` range filtering, which may be unintended. Mutation coverage is broad and security-sensitive; tests should cover sudo remapping, ACL/immutable behavior, path-vs-id resolution, filter edge cases, recursive xattr, version operations, recycle list/restore/purge, quota parsing, insert conflict detection, and lock behavior during streamed listings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/grpc/GrpcNsInterface.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/grpc/GrpcNsInterface.hh -->
# sources/distributed-fs/eos/mgm/grpc/GrpcNsInterface.hh

## Purpose
Declares the static gRPC namespace interface class used by the MGM gRPC server to expose namespace metadata and command operations.

## Important APIs, types, and functions
`GrpcNsInterface` declares filtering for files and containers, metadata methods (`GetMD`, `Stat`, `StreamMD`, `Find`, `NsStat`), sudo-only insert APIs, generic command dispatch (`Exec`), individual namespace command handlers, recycle handlers, ACL/token/quota handlers, and `Access()` for permission checks.

## Control flow
The class is a stateless static facade. Server handlers pass a `VirtualIdentity`, request protobuf, and response/writer object. The implementation performs identity remapping, permission checks, namespace locking, and command delegation.

## State and persistence
The header stores no state. It declares methods that can read and mutate namespace state, quota state, ACL/xattr metadata, recycle state, and process stats through the implementation.

## Dependencies and integration points
Guarded by `EOS_GRPC`, it includes identity mapping, logging, MGM namespace macros, namespace metadata interfaces, `GrpcServer.hh`, generated `Rpc.grpc.pb.h`, and gRPC C++ headers.

## Risks and test signals
Because every method is static, test isolation depends on controlling global `gOFS` and namespace services. Tests should validate method dispatch, compile guards, protobuf compatibility, and permission behavior at the public API boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/grpc/GrpcNsInterface.hh -->
