# subset-b-007029 Research

Grouped research for the listed EOS MGM filesystem-view, lock-tracking, and geobalancer files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/fsview/FsView.cc -->
# sources/distributed-fs/eos/mgm/fsview/FsView.cc

## Purpose
`FsView.cc` implements the MGM-side in-memory view of EOS filesystem topology. It keeps the same registered filesystem visible by filesystem id, FST node queue, scheduling group, space, and geotag tree, and it ties those views to shared-hash configuration, the persistent config engine, the scheduler, balancer/drainer services, and command/table output. It is the operational core behind filesystem registration, unregister, group moves, heartbeat-driven online/offline state, space defaults, capacity statistics, and view printing.

## Important APIs, Types, And Functions
The file defines the singleton `FsView::gFsView`, `FsSpace::gDisableDefaults`, `FsNode::sNumInstances`, and the node refresh tag `stat.refresh_fs`. `GeoTreeElement`, `GeoTree`, `DoubleAggregator`, and `LongLongAggregator` implement geotag-aware grouping and aggregation. `FsSpace` owns per-space service objects: `FsBalancer`, `GroupBalancer`, `GeoBalancer`, `GroupDrainer`, and `FileInspector`, except for the spare space. `FsNode` manages node shared-hash subscriptions and heartbeat updates.

The most important `FsView` methods are `Register`, `UnRegister`, `MoveGroup`, `RegisterNode`, `RegisterSpace`, `RegisterGroup`, `Reset`, `ApplyFsConfig`, `ApplyGlobalConfig`, `SetGlobalConfig`, `GetGlobalConfig`, `StoreFsConfig`, `HeartBeatCheck`, `ReapplyDrainStatus`, `Df`, `UnderNominalQuota`, `CollectEndpoints`, `GetUnbalancedGroups`, `GetFsToBalance`, and the print helpers. `BaseView` contributes the shared API for `GetMember`, config member access, statistics (`SumLongLong`, `AverageDouble`, deviations, sigma), and `Print`.

## Control Flow
Filesystem registration first rejects null inputs and queue-path collisions, then updates `mIdView`, creates or reuses the node view, group view, and space view, and registers the filesystem in `GeoTreeEngine`. If GeoTreeEngine insertion fails, it tries to roll back through `UnRegister`. After the view maps are consistent, it applies core parameters, stores filesystem config, and signals the owning node to refresh. Unregistration snapshots the filesystem, removes it from node/group/space views, removes it from GeoTreeEngine when requested, erases id and uuid mappings, deletes persistent config on masters, optionally deletes shared hashes and empty node objects, then deletes the `FileSystem`.

`MoveGroup` changes `schedgroup`, removes the filesystem from its previous space/group and GeoTreeEngine group, creates the target group or space when needed, reinserts into GeoTreeEngine, and attempts rollback if insertion fails. `ApplyFsConfig` is the config-load path: it parses serialized filesystem config, validates `queuepath`, `id`, and `uuid`, creates mappings and `FileSystem` objects as needed, applies durable key updates in a batch, handles `configstatus` outside the transaction to avoid drain deadlocks, and calls `Register`.

`HeartBeatCheck` runs every ten seconds. It warns when live `FsNode` instances differ from `mNodeView.size()`, marks nodes online only when their shared-hash heartbeat is recent, and updates each filesystem under the node based on node config, group status, boot status, active overload thresholds (`max.ropen`, `max.wopen`), and scheduler disk status. `Df` combines space nominal capacity, node network capacity, namespace tree size, file/container counts, and policy size factor into table or JSON output.

## State And Persistence
Primary in-memory state is protected by `FsView::ViewMutex` and includes `mSpaceGroupView`, `mSpaceView`, `mGroupView`, `mNodeView`, `mIdView`, `mFilesystemMapper`, and a short-lived nominal quota cache `mUsageOk` guarded by `mUsageMutex`. Individual `BaseView` status strings are guarded by a local mutex; heartbeat timestamps are atomic. `GeoTree` owns dynamically allocated branch nodes and tracks leaves by fsid.

Persistent and distributed state flows through `mq::SharedHashWrapper` and `IConfigEngine`. `BaseView::SetConfigMember` writes to the view shared hash and, on the master and for non-status values, to config storage under the global namespace. `StoreFsConfig` persists serialized filesystem config under the `fs` namespace. Global config is stored in the global MGM shared hash and config engine. `FsNode` subscribes to its node hash so FST heartbeat and traffic shaping updates affect MGM state.

## Dependencies And Integration Points
This file integrates with `FileSystem`, `FileSystemRegistry`, `FilesystemUuidMapper`, `GeoTreeEngine`, `FsScheduler`, `GroupBalancer`, `GeoBalancer`, `GroupDrainer`, `FsBalancer`, `FileInspector`, `ConverterEngine` indirectly through space services, QuarkDB/shared-hash wrappers, namespace metadata services, `Policy`, table formatting, JSON, token generation, FUSE server settings, traffic shaping, and the global `gOFS` MGM service object. It assumes callers hold `ViewMutex` for several operations noted in comments, especially config application and some view lookups.

## Risks
The file mixes raw pointer ownership, distributed config side effects, thread lifecycle, and rollback logic. Failed partial registration can leave inconsistent state if rollback paths also fail. Many methods rely on external locking discipline; missing `ViewMutex` locking around map access would be high risk. `UnRegisterNode`, `UnRegisterSpace`, and `UnRegisterGroup` use `retc |= UnRegister(fs)`, so an earlier failure can be obscured by later successes. `RemoveMapping(fsid, uuid)` uses bitwise OR intentionally or accidentally; this evaluates both removals but is easy to misread. `UnderNominalQuota` reads view maps under `mUsageMutex` but not `ViewMutex`, so callers must ensure broader view safety. `BaseView::Print` parses user format strings with minimal validation and assumes split key/value pairs exist. `GeoTree::erase` deliberately leaves some parent references during branch deletion, so ownership invariants are subtle.

## Test Signals
Useful signals include unit tests for `GeoTree` insert/erase/aggregation, registration/unregistration rollback tests with mocked `GeoTreeEngine`, config load tests for `ApplyFsConfig`, heartbeat tests covering node online/offline and overload transitions, shared filesystem de-duplication tests in `SumLongLong`, output golden tests for `Df` and `Print`, and leak checks around `Reset` verifying `FsNode::sNumInstances == mNodeView.size()`. Integration tests should cover master-only config persistence, failover reset, shared-hash heartbeat updates, group moves, drain reapplication, and balancer priority set selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/fsview/FsView.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/fsview/FsView.hh -->
# sources/distributed-fs/eos/mgm/fsview/FsView.hh

## Purpose
`FsView.hh` declares the MGM filesystem-view model used by EOS to represent cluster topology by space, group, node, filesystem id, and geotag. It exposes the contracts used by registration/configuration code, balancers, schedulers, drainers, inspectors, command output, and tests. The header is not a thin declaration file: it defines several inline helpers and constructors, names the public view maps, and documents locking expectations for statistics and quota-sensitive operations.

## Important APIs, Types, And Functions
`FsBalanceInfo` and `FsPrioritySets` model filesystem candidates for balancing. Priority sets divide filesystems around group average fill into low, normal-low, normal-high, and high-priority buckets.

`GeoTreeElement`, `GeoTreeNodeOrderHelper`, `GeoTreeAggregator`, and `GeoTree` define a reusable geotag tree. `GeoTree` supports `insert`, `erase`, `getGeoTagInTree`, `size`, `runAggregator`, and bidirectional leaf iteration. `GeoTreeAggregator` is the extension point for statistics over tree levels.

`BaseView` extends `GeoTree` with a shared-hash locator, heartbeat timestamp, status, config accessors, table printing, and statistics APIs. `FsSpace`, `FsGroup`, and `FsNode` specialize it for space, group, and node views. `FsSpace` owns per-space balancing/draining/inspection components and default-parameter logic. `FsGroup` stores a group index. `FsNode` tracks shared-hash subscriptions, node active status, heartbeat freshness, refresh signaling, and a static instance counter for leak detection.

`FsView` exposes the central singleton and its public view maps: `mSpaceGroupView`, `mSpaceView`, `mGroupView`, `mNodeView`, and `mIdView`. It declares lifecycle operations (`Register`, `UnRegister`, `Reset`), movement (`MoveGroup`, `MoveNode` declaration), config persistence/application, mapping functions, print/df methods, quota checks, endpoint collection, balancer helpers, and heartbeat management. `DoubleAggregator` and `LongLongAggregator` are concrete `GeoTreeAggregator` implementations for floating-point and integer statistics.

## Control Flow
The declared flow is centered on `ViewMutex`: callers update the global maps through `FsView` registration APIs and query them through print/statistics helpers. `BaseView` statistics can optionally take the view lock, which allows aggregate calls to be reused inside already locked geotag aggregation. `FsView::HeartBeatCheck` is launched by the constructor through `AssistedThread` and joined in the destructor. Space construction starts companion worker objects, while `FsSpace::Stop` is available so `FsView::Reset` can stop threads before deleting views.

Geotag aggregation flow is declared in three stages: `GeoTree::runAggregator` initializes an aggregator with geotag labels and depth boundaries, then calls leaf and node aggregation bottom-up. The aggregators call back into `BaseView` to compute sums, averages, deviations, standard deviation, and counts for filesystem subsets.

## State And Persistence
`FsView` state is mostly in-memory pointers and registries. `mConfigEngine` is a non-owning pointer used for durable config writes, while `mFilesystemMapper` preserves fsid-to-uuid associations. `mUsageOk` caches quota decisions. `BaseView` persists config members through shared hashes and the config engine in implementation. `FsNode` owns a `SharedHashSubscription`, and `FsSpace` owns or references long-running worker objects. The header shows ownership is mixed: some members use `std::unique_ptr`, while `mGroupBalancer`, `mGeoBalancer`, and view maps use raw pointers and require disciplined destruction.

## Dependencies And Integration Points
The header depends on EOS common threading, locks, instance names, locators, symmetric keys, namespace metadata interfaces, filesystem registries, UUID mapping, shared-hash subscriptions, and platform statfs headers. Forward declarations connect it to `Balancer`, `GroupBalancer`, `GroupDrainer`, `GeoBalancer`, `Converter`, `IConfigEngine`, `FsBalancer`, and `FileInspector`. External users can directly inspect several public maps, so the class is both an API and a shared data structure.

## Risks
The broad public surface makes invariants difficult to enforce. Public mutable maps allow integration code to bypass registration helpers unless it follows locking and ownership rules. Raw pointer ownership for views and some worker objects raises leak and double-delete risk during reset, failover, and partial registration failures. The constructor starts the heartbeat thread immediately, which can surprise tests unless global dependencies are initialized. Aggregators require `setView` before `runAggregator`; this is enforced by `assert`, not by type structure. The deprecated `std::iterator` base in `GeoTree::const_iterator` may create future build issues with newer C++ standards.

## Test Signals
Header-level behavior should be covered through compile tests and focused unit tests for type contracts: `FsPrioritySets` ordering, `GeoTree` iterator behavior, aggregator initialization requirements, `FsNode` instance counting, and `FsView` lifecycle with `start/stop/reset` under test harness globals. API-level tests should assert that public print format functions continue to include required keys for monitoring consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/fsview/FsView.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/fuse-locks/LockTracker.cc -->
# sources/distributed-fs/eos/mgm/fuse-locks/LockTracker.cc

## Purpose
`LockTracker.cc` implements the in-memory POSIX byte-range lock tracker declared in `LockTracker.hh`. It models read and write locks for a single tracked object, answers `F_GETLK`-style conflict queries, applies non-blocking and short blocking `F_SETLK`/`F_SETLKW`-style requests, removes locks by pid or owner, and exposes owner-based lock listings for FUSE-related cleanup.

## Important APIs, Types, And Functions
Stream operators print `ByteRange` as half-open ranges and `Lock` with its pid. `LockSet::add` merges overlapping or touching ranges for the same pid. `LockSet::conflict` and `LockSet::getconflict` detect overlapping ranges held by different pids. `LockSet::remove(const Lock&)` subtracts a range from all matching-pid locks and may split one lock into two. `LockSet::remove(pid_t)` and `remove(owner)` drop all matching locks. `lslocks(owner)` returns pids held by an owner.

`LockTracker::getlk` checks if a requested read or write lock would be granted and mutates the supplied `struct flock` to `F_UNLCK` or to the blocking lock details. `setlk` delegates to `addLock` for non-sleeping calls, or retries for up to roughly 10 ms with 1 ms sleeps for sleeping calls. `addLock` holds the mutex, handles unlock requests, enforces read/write conflict rules, adds the new lock to `rlocks` or `wlocks`, and removes converted locks from the opposite set. `removelk`, `inuse`, `getrlks`, and `getwlks` are all mutex-protected.

## Control Flow
All public tracker operations take a `std::lock_guard<std::mutex>` either directly or through `addLock`, except `setlk` only locks per retry through `addLock`. Conflict logic follows POSIX-style compatibility: unlock always succeeds; read locks conflict only with write locks from other pids; write locks conflict with read or write locks from other pids. Same-pid overlaps are not conflicts and are coalesced, allowing lock upgrade/downgrade by adding the requested lock and subtracting the same range from the opposite lock set.

`getlk` builds a temporary `Lock` from `l_start` and `l_len`. If the request can lock, it sets `l_type` to `F_UNLCK`. If not, `canLock` has replaced `l_start`, `l_len`, `l_pid`, `l_whence`, and `l_type` with the conflicting lock's information. `setlk` returns `1` for success and `0` after the bounded retry loop gives up.

## State And Persistence
The implementation is entirely in-memory. `LockTracker` owns two `LockSet` instances, `rlocks` and `wlocks`, plus a mutex. No lock state is persisted to disk or shared hash. `LockSet` stores coalesced `Lock` objects in a vector, so lock identity is normalized by pid and merged ranges rather than preserving individual requests.

## Dependencies And Integration Points
The file depends on `fcntl.h` constants and `struct flock`, `unistd.h`/`pid_t`, C++ threads and chrono for retry sleep, and the EOS MGM namespace macros. It is intended to sit under MGM FUSE lock handling, where owners likely represent FUSE clients or sessions and pid cleanup is needed when clients disconnect.

## Risks
The blocking path is only a polling retry for about 10 ms, not a true condition-variable wait, so it may not match full `F_SETLKW` expectations under contention. `Lock::minus` recreates split locks without preserving `owner`, so partial unlocks can drop owner metadata for surviving ranges; owner-based cleanup/listing can then miss those ranges. `LockSet::add` merges same-pid locks regardless of owner, so different owners using the same pid namespace can be collapsed. There is no validation of negative starts or overflow in `start + len`; `ByteRange` handles `len == -1` as EOF but relies on construction assertions for self-overlap. Return values use `1` and `0` rather than errno-rich errors, so callers must map failures carefully.

## Test Signals
Strong tests should cover overlapping, touching, disjoint, zero-length, and EOF (`l_len == 0` mapped in POSIX input to this code's `len == -1` convention only if callers perform that conversion) ranges. Add tests for read/read compatibility, read/write conflicts, same-pid upgrades and downgrades, unlock splitting into two ranges, pid cleanup, owner cleanup after partial unlocks, `getlk` conflict field mutation, and bounded sleeping behavior. Threaded tests can check that concurrent `setlk` and `removelk` do not corrupt lock vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/fuse-locks/LockTracker.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/fuse-locks/LockTracker.hh -->
# sources/distributed-fs/eos/mgm/fuse-locks/LockTracker.hh

## Purpose
`LockTracker.hh` declares and partly implements a small POSIX byte-range lock model for MGM FUSE locking. It defines the range arithmetic, lock identity, lock-set container, and thread-safe tracker API used by the implementation file.

## Important APIs, Types, And Functions
`Offset` is an alias for `off_t`. The helpers `isPointBetween` and `isPointBetweenOrTouching` implement half-open and inclusive boundary checks.

`ByteRange` stores a start offset and length. Its `end()` returns `start + len` except `len == -1`, which is treated as an infinite range ending at `numeric_limits<Offset>::max()`. `f_lock_len()` converts internal `-1` back to `0` for `struct flock` EOF semantics. `absorb` merges overlapping or touching ranges, `contains` tests full coverage, `minus` subtracts another range and returns zero, one, or two ranges, and `overlap`/`overlapOrTouch` implement conflict and merge checks.

`Lock` combines a `ByteRange`, `pid_t`, and optional owner string. Overlap, containment, absorption, and subtraction only apply to locks with the same pid. `LockSet` declares add, overlap, remove, conflict, count, and owner-list operations over coalesced locks. `LockTracker` exposes `getlk`, `setlk`, `removelk(pid)`, `removelk(owner)`, `inuse`, `getrlks`, and `getwlks`, with private `addLock` and `canLock` helpers plus separate read and write lock sets.

## Control Flow
The header establishes range behavior before tracker behavior. `ByteRange` constructor immediately verifies that a range overlaps itself; invalid ranges print to stderr and terminate the process. `minus` handles six cases: no overlap left, no overlap right, complete removal, removal of start, removal of end, and middle removal with two surviving ranges. `LockSet` is responsible for coalescing and splitting, while `LockTracker` is responsible for read/write compatibility and synchronization.

## State And Persistence
State is in-memory only. `ByteRange` state is two offsets, `Lock` state is a range/pid/owner triple, `LockSet` state is a vector of coalesced locks, and `LockTracker` state is a mutex plus read and write `LockSet`s. The header does not expose persistence hooks, serialization, or distributed coordination.

## Dependencies And Integration Points
The header depends on STL containers, mutex, `fcntl.h` for POSIX lock constants and `struct flock`, `common/Assert.hh`, and MGM namespace macros. It exposes ostream operators for diagnostics. The API is shaped around POSIX locks, but the implementation stores simplified normalized ranges rather than kernel lock objects.

## Risks
Fatal `exit(EXIT_FAILURE)` from `ByteRange` and `updateEnd` makes malformed lock input process-wide fatal instead of returning an error. Internal EOF is represented as `len == -1`, while POSIX uses `l_len == 0`; callers must normalize inputs before construction or EOF locks will be interpreted as zero-length locks. `start + len` can overflow for large positive ranges. Owner metadata is not part of `Lock` equality or same-pid merge decisions, so owner cleanup semantics are approximate. The API does not document whether pid values are globally unique across clients, which matters for FUSE multi-client behavior.

## Test Signals
Unit tests should target `ByteRange::minus`, `absorb`, `overlap`, and EOF conversion first, because tracker correctness depends on those primitives. Additional tests should exercise `Lock::minus` owner preservation expectations, lock coalescing order independence, and public `LockTracker` behavior under conflicting readers and writers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/fuse-locks/LockTracker.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/geobalancer/GeoBalancer.cc -->
# sources/distributed-fs/eos/mgm/geobalancer/GeoBalancer.cc

## Purpose
`GeoBalancer.cc` implements the per-space geotag balancer. It runs as a background MGM thread, periodically computes used-capacity ratios per geotag, identifies geotags above the space average by a configured threshold, chooses files from overfull geotags, and schedules converter jobs so replicas are redistributed across locations. It assumes the converter engine is available and that the default placement policy can create a better scattered placement during conversion.

## Important APIs, Types, And Functions
`GeoBalancer::GeoBalancer` initializes threshold, average fill, last check time, space name, and starts the assisted thread. `Stop` and the destructor join the thread; the destructor also clears cached size objects. `GeotagSize` stores used bytes and capacity with `filled()` behavior declared in the header and asserts positive capacity.

`clearCachedSizes`, `populateGeotagsInfo`, and `fillGeotagsByAvg` manage the cache of `mGeotagFs`, `mFsGeotag`, `mGeotagSizes`, `mAvgUsedSize`, and `mGeotagsOverAvg`. `fileIsInDifferentLocations` checks whether an existing file already spans multiple geotags. `getFileProcTransferNameAndSize` loads file metadata, validates that the file is movable, returns its proc conversion path, and optionally returns file size. `updateTransferList` reconciles scheduled transfer ids with `mFidTracker`. `scheduleTransfer` calls the converter engine and updates cached used bytes optimistically. `chooseFidFromGeotag` picks a random filesystem and random file id. `prepareTransfer`, `prepareTransfers`, `cacheExpired`, and `GeoBalance` drive the scheduling loop.

## Control Flow
The thread waits for the namespace to boot, sleeps ten seconds, then loops until termination. Each pass exits or waits if the MGM is not master, if the converter engine is unavailable or stopped, or if the configured space is missing. Under `FsView::ViewMutex`, it reads the space config keys `geobalancer`, `geobalancer.ntx`, and `geobalancer.threshold`. When enabled, it updates the transfer list, checks whether the configured concurrency is already reached, refreshes geotag-size caches every 300 seconds, and schedules up to the configured number of transfers.

Cache population scans all filesystems in the space view while holding `ViewMutex`, skips missing, offline, non-booted, config-disabled, or geotag-less filesystems, snapshots capacity/free bytes, groups fsids by geotag, and computes the average fill across geotags. Scheduling chooses from geotags whose fill exceeds average by threshold, samples a filesystem with at least one file, samples up to ten random file ids not already scheduled, validates metadata and current locations, and schedules a converter job tagged with `^geobalancer^`.

## State And Persistence
Runtime state is in-memory and per `GeoBalancer` instance: cached geotag-to-fs lists, fs-to-geotag map, allocated `GeotagSize` pointers, over-average geotag list, scheduled transfer map, average fill, threshold, and last cache refresh. Persistent effects happen through `gOFS->mConverterEngine->ScheduleJob`, which creates converter work tracked by `mFidTracker`, and through file movement/conversion performed by downstream components. The balancer optimistically subtracts scheduled file size from the source geotag's cached used bytes so repeated scheduling does not overselect the same location before the next full cache refresh.

## Dependencies And Integration Points
The implementation depends on `FsView` for space membership and filesystem status, namespace prefetch/file metadata services for file validation, `IFsView` random file selection and per-filesystem file counts, `ConverterEngine` for scheduling, `mFidTracker` for active transfer cleanup, `LayoutId` and file id helpers, random utilities, XRootD logging/scheduling headers, and global `gOFS` master/converter/namespace state. It is created by `FsSpace` for non-spare spaces and controlled by space shared-hash config.

## Risks
`populateGeotagsInfo` indexes `mSpaceView[spaceName]` after only assuming the space exists; if called after concurrent removal without the expected lock discipline, null insertion would be dangerous. `mGeotagSizes.erase(geotag)` in `chooseFidFromGeotag` does not delete the `GeotagSize*`, causing a potential leak for emptied geotags until full cache clear cannot see the erased pointer. `fileIsInDifferentLocations` uses `mFsGeotag[*lociter]`, which inserts empty entries for unknown fsids and can make unknown locations look co-located. `chooseFidFromGeotag` returns `-1` in an unsigned file-id type and callers cast to `int`, which is fragile. Scheduling subtracts file size from cached used bytes without guarding underflow. The loop uses `goto wait` and a mix of manual `LockRead`/`UnLockRead`; any new branch must preserve unlock behavior.

## Test Signals
Tests should cover cache population filters, average/threshold selection, transfer-list cleanup from `mFidTracker`, file metadata rejection cases, already-multi-geotag files, proc conversion tag construction, converter failure behavior, and optimistic cache updates. Integration tests should run an enabled geobalancer with mocked filesystems across two or more geotags and verify that only master MGM with running converter schedules jobs and respects `geobalancer.ntx`. Leak checks should cover geotag removal in `chooseFidFromGeotag` and destructor cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/geobalancer/GeoBalancer.cc -->
