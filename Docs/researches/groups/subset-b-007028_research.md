# subset-b-007028 Research

Grouped source research for EOS MGM egroup membership caching, advertised feature flags, filesystem state/listener integration, fsck collection/repair orchestration, fsck repair entry handling, and the interactive fsck repair helper. Each source file has a marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/egroup/Egroup.cc -->
# sources/distributed-fs/eos/mgm/egroup/Egroup.cc

## Purpose

`Egroup.cc` implements the MGM e-group membership checker declared in `Egroup.hh`. It provides cached LDAP membership lookups for CERN e-groups and a background refresh thread so MGM authorization paths can keep serving from cache instead of blocking under namespace read locks.

## Important APIs, Types, and Functions

The central APIs are `query()`, `Member()`, `refresh()`, `fetchCached()`, `scheduleRefresh()`, `DumpMember()`, `DumpMembers()`, `Reset()`, and test hook `inject()`. `isMemberUncached()` is the real LDAP path. It returns `Status::kMember`, `kNotMember`, or `kError`; `CachedEntry` stores the boolean result plus a steady-clock timestamp.

## Control Flow

Construction enables blocking mode on `mPendingQueue` and starts `Refresh`. `query()` first checks `cache` under `mMutex`; fresh hits return immediately, stale hits return the old value and enqueue a refresh, and misses call `isMemberUncached()` synchronously before storing the result. The refresh thread consumes queued `(username, egroup)` pairs, calls `refresh()`, removes the deduplication key from `mPendingSet`, and pops the queue. `isMemberUncached()` either serves injected test data or initializes an LDAP connection to `ldap://xldap`, sets protocol and network timeout options, searches the CERN user DN with a recursive `memberOf` filter, and checks returned `cn` values for the username.

## State and Persistence Behavior

State is in-memory only: `cache` maps egroup to user to cached entry, `mPendingQueue` and `mPendingSet` hold refresh work, and `injections` simulates LDAP for tests. Cache lifetime is fixed at 1800 seconds. There is no disk persistence; state is reset on process restart or `Reset()`.

## Dependencies and Integration Points

The file depends on OpenLDAP C APIs, EOS logging/string helpers, `common::SteadyClock`, `common::RWMutex`, `AssistedThread`, and `qclient::WaitableQueue`. It integrates with MGM authorization code through `Egroup::Member()` and with admin/debug output through the dump methods.

## Risks and Edge Cases

LDAP base/filter strings are hard-coded for CERN and are not escaped, so unexpected usernames or egroup names are risky. `query()` caches `kError` as non-member on synchronous misses, while `refresh()` refuses to replace cache on `kError`; this can turn transient LDAP failures into temporary denials. `injections` is not protected by `mMutex`, so test or runtime concurrent use would race. The queue has a fixed capacity of 500, and `scheduleRefresh()` does not report enqueue failure. Dump lifetimes can become negative for stale entries.

## Test Signals

Useful tests include injected membership/non-membership/error cases, stale-cache refresh scheduling and deduplication, cache miss behavior on LDAP errors, destructor shutdown of a blocked refresh thread, `Reset()` cache clearing, and dump formatting with controlled `SteadyClock` time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/egroup/Egroup.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/egroup/Egroup.hh -->
# sources/distributed-fs/eos/mgm/egroup/Egroup.hh

## Purpose

`Egroup.hh` declares the MGM e-group support class. It exposes a cache-backed API for checking whether an EOS username belongs to a CERN e-group, while hiding LDAP calls and asynchronous refresh machinery behind one object.

## Important APIs, Types, and Functions

`Egroup::Status` models uncached lookup results: member, not member, or error. `CachedEntry` carries `isMember` and a `std::chrono::steady_clock::time_point`. Public APIs include constructor/destructor, `Reset()`, `query()`, convenience `Member()`, `DumpMember()`, `DumpMembers()`, `scheduleRefresh()`, `fetchCached()`, `inject()`, `getPendingQueueSize()`, and synchronous `refresh()`. Private helpers include `storeIntoCache()`, `isStale()`, background `Refresh()`, and `isMemberUncached()`.

## Control Flow

The header describes a cache-read-first model: callers use `Member()` or `query()`, stale cached values are refreshed asynchronously, and synchronous LDAP is reserved for cache misses or explicit `refresh()`. The object owns its refresh thread and joins it on destruction.

## State and Persistence Behavior

The class owns only process-local state. `kCacheDuration` is a fixed 30-minute TTL. `cache` stores membership entries by egroup and username under `mMutex`. `mPendingQueue` carries background work, while `mPendingSet` plus `mMutexPending` deduplicates queued refreshes. `injections` is a fake LDAP response map for testing. No state is persisted outside memory.

## Dependencies and Integration Points

The declaration depends on MGM namespace macros, EOS `AssistedThread`, `SteadyClock`, `RWMutex`, qclient `WaitableQueue`, XRootD pthread support, STL maps/sets, and chrono. It is intended for MGM permission paths that may already hold read locks, so asynchronous refresh avoids long lock contention.

## Risks and Edge Cases

The API returns only a boolean for `Member()`, so callers cannot distinguish not-member from lookup failure. `CachedEntry()` defaults the timestamp, so consumers must not infer freshness from a default object unless `fetchCached()` succeeded. The pending set key concatenates username and egroup with `:`, which can theoretically collide if either component contains that separator. The class is copyable by default unless prevented elsewhere, but copying thread, mutex, and queue state would be unsafe; callers should treat it as non-copyable.

## Test Signals

Compile tests should include this header independently. Unit tests should exercise `query()`/`Member()` with injected data, TTL staleness using a fake `SteadyClock`, queue size/deduplication from `scheduleRefresh()`, and safe object destruction with outstanding queued work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/egroup/Egroup.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/eos-repair-tool -->
# sources/distributed-fs/eos/mgm/eos-repair-tool

## Purpose

`eos-repair-tool` is an interactive Perl terminal helper for operators repairing EOS fsck findings. It fetches or reads fsck reports, groups logical filenames by fsck tag, displays file diagnostics, and issues EOS CLI repair commands such as verify, adjustreplica, drop, and bulk set operations.

## Important APIs, Types, and Functions

The script uses `Term::ReadKey` in cbreak mode and drives the external `eos -b` CLI. Top-level actions are `r` to write `/tmp/eos.fsck.report`, `f` to load `/tmp/eos.fsck.report` and `/tmp/eos.external.lfn`, `p` to process already loaded sets, `u` to disable/enable fsck collection, and `s` to show fsck status. Inner actions include next/previous navigation, `a`/`A` adjust replica, `v`/`V` verify checksum, `c`, `C`, `X` verify plus checksum/size commit variants, `d` drop a selected replica, `D` try automatic bad-size replica drops, `E` rescan and retain only still-bad files, `e` export the current set, and `y` show checksum-attribute checks.

## Control Flow

The script loops forever clearing the screen, reading one command key, and branching with independent `if` statements. Report loading parses whitespace-separated `key=value` tokens and splits `lfn=` lists by comma into `$lfnhash->{tag}->{lfn}`. Processing presents available tag sets, lets the user select one by numeric key, then loops over LFNs, running `eos file info` and `eos file check` before accepting repair commands.

## State and Persistence Behavior

Runtime state is held in Perl hashes and arrays. Persistent side effects are all external: `/tmp/eos.fsck.report`, optional `/tmp/eos.external.lfn`, `/tmp/eos.set.lfn`, and repair mutations made through the EOS MGM CLI. Terminal mode is restored to normal at script exit.

## Dependencies and Integration Points

The tool depends on Perl, `Term::ReadKey`, a working `eos` client, shell utilities such as `clear`, `grep`, and `unlink`, and an operator with authority to run file repair commands. It complements the C++ fsck engine by providing a human-guided workflow over `eos fsck report` and `eos file check`.

## Risks and Edge Cases

The parser is fragile for quoted values containing spaces. Many shell commands interpolate LFNs directly, so special characters in paths can break commands or create injection risk. The `D` branch contains apparent Perl bugs where `hash->` is used without `$`, and `%$hash` data is not reset per file. Numeric set selection is not validated. Bulk actions can drop or rewrite replicas across an entire set with minimal confirmation.

## Test Signals

Smoke tests can run against mocked `eos` commands and sample fsck report lines. Operator tests should verify parsing of multi-LFN reports, set selection, export output, rescan filtering, terminal mode restoration after quit, and dry-run review of every bulk command path before production use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/eos-repair-tool -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/features/Features.cc -->
# sources/distributed-fs/eos/mgm/features/Features.cc

## Purpose

`Features.cc` defines the static MGM feature advertisement map declared in `Features.hh`. These values describe client-visible EOS behavior such as path encoding, lazy open support, and the inode encoding scheme.

## Important APIs, Types, and Functions

The only function is file-local `checkInodeScheme()`, which reads `EOS_USE_NEW_INODES` and returns `"1"` only when the first environment character is `1`; otherwise it returns `"0"`. `Features::sMap` contains `eos.encodepath=curl`, `eos.lazyopen=true`, and `eos.inodeencodingscheme=<env-derived value>`.

## Control Flow

Control flow runs during static initialization. `checkInodeScheme()` is evaluated while initializing `Features::sMap`, so later environment changes do not alter this process's advertised inode scheme.

## State and Persistence Behavior

The state is a process-global `const std::map`. It persists for the MGM process lifetime and is not written to disk. Its only dynamic input is the environment at static initialization time.

## Dependencies and Integration Points

The implementation depends on `mgm/features/Features.hh` and `getenv()` from the C runtime. Consumers of `Features::sMap` can expose or negotiate feature values with clients or management interfaces.

## Risks and Edge Cases

Static initialization order matters if other globals read `Features::sMap` very early. The environment is sampled once and without validation beyond the first byte. The source banner says `File: ZMQ.hh` in the paired header, which is misleading but not behavioral.

## Test Signals

Tests should start a process with `EOS_USE_NEW_INODES=1`, unset, and other values, then check `eos.inodeencodingscheme`. Compile/link coverage should ensure there is exactly one definition of `Features::sMap`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/features/Features.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/features/Features.hh -->
# sources/distributed-fs/eos/mgm/features/Features.hh

## Purpose

`Features.hh` declares the minimal MGM `Features` class, which acts as a namespace for a static map of feature-name to feature-value strings.

## Important APIs, Types, and Functions

The only public member is `static const std::map<const std::string, const std::string> sMap`. The keys and values are defined in `Features.cc`.

## Control Flow

There is no executable control flow in the header. Consumers include the header and read `Features::sMap`; initialization happens in the `.cc`.

## State and Persistence Behavior

The header declares process-global immutable state owned by the implementation. There is no persistence, mutation API, or synchronization requirement because the map is const after initialization.

## Dependencies and Integration Points

It depends on MGM namespace macros plus `<string>` and `<map>`. It integrates with MGM components that advertise capabilities to clients or administrative commands.

## Risks and Edge Cases

Because the map is a static object, ABI and initialization behavior depend on exactly one linked definition. The type uses `const std::string` as the key type; this works for a read-only map but is unusual and could complicate generic code expecting `std::map<std::string, std::string>`.

## Test Signals

Header self-containment compile tests and feature-advertisement integration tests are enough. Tests should verify known keys are present and values match the implementation under controlled environment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/features/Features.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/filesystem/FileSystem.cc -->
# sources/distributed-fs/eos/mgm/filesystem/FileSystem.cc

## Purpose

`FileSystem.cc` implements the MGM-side `FileSystem` wrapper around `eos::common::FileSystem`. It adds filesystem-change listener registration, shared-hash update notification, drain-transition handling, and local accounting for active balancer transfers.

## Important APIs, Types, and Functions

Key methods are the constructor/destructor, `RegisterWithExistingListeners()`, `UnregisterFromListeners()`, `AttachFsListener()`, `DetachFsListener()`, `NotifyFsListener()`, `ProcessUpdateCb()`, `SetConfigStatus()`, overridden `SetString()`, `IsDrainTransition()`, `ShouldBroadCast()`, `IncrementBalanceTx()`, and `DecrementBalanceTx()`. Static tags include `local.balancer.running`, `stat.geotag`, and `stat.errc`.

## Control Flow

Construction logs the queue path, registers with already interested listeners from the messaging realm, subscribes to the backing shared hash, and attaches `ProcessUpdateCb()`. Shared-hash updates are filtered by key against `mMapListeners` and delivered as `FsChangeListener::Event`. `SetString("configstatus", ...)` redirects to `SetConfigStatus()`. On a broadcast-capable master realm, config-status changes are classified by `IsDrainTransition()`, start or stop `gOFS->mDrainEngine`, repair finished drain state when stopping, and then write the new config status through the base class.

## State and Persistence Behavior

The base `common::FileSystem` owns persistent shared-hash fields. This wrapper owns runtime listener maps, a subscription handle, and atomic `mNumBalanceTx`. `IncrementBalanceTx()`/`DecrementBalanceTx()` write the local running-transfer counter with `SetLongLongLocal()`, so the value is visible in local filesystem state but is not a durable cross-process counter.

## Dependencies and Integration Points

The file depends on `MessagingRealm`, `FsChangeListener`, `FsView`, global `gOFS`, drain engine APIs, and `qclient::SharedHashSubscription`. It is part of the MGM filesystem view and receives storage-node shared-hash updates.

## Risks and Edge Cases

`SetConfigStatus()` assumes callers hold `FsView::ViewMutex`, as documented in the header; missing that lock can race global view state. `DecrementBalanceTx()` can underflow the unsigned atomic if called too often. Listener notification holds `mRWMutex` while invoking listener callbacks, so slow or reentrant listeners could create latency or lock-order issues. A non-broadcasting realm returns true from `SetConfigStatus()` without writing local state.

## Test Signals

Tests should cover drain transition classification, config-status set paths with mocked drain start/stop success and failure, listener attach/detach/update delivery, subscription callback detachment on destruction, and balance counter increment/decrement writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/filesystem/FileSystem.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/filesystem/FileSystem.hh -->
# sources/distributed-fs/eos/mgm/filesystem/FileSystem.hh

## Purpose

`FileSystem.hh` declares the MGM filesystem class. It extends the common filesystem model with MGM-specific listener notification, drain-control entry points, and local balancer transfer accounting.

## Important APIs, Types, and Functions

The class inherits from `eos::common::FileSystem` and `eos::common::LogId`. Public APIs include static `sNumBalanceTxTag`, static `IsDrainTransition()`, constructor/destructor, `AttachFsListener()`, `DetachFsListener()`, `ShouldBroadCast()`, `SetConfigStatus()`, `SetString()`, `IncrementBalanceTx()`, and `DecrementBalanceTx()`. Private members include shared-hash subscription `mSubscription`, listener map `mMapListeners`, listener mutex `mRWMutex`, `mNumBalanceTx`, and helper callbacks.

## Control Flow

The declaration shows that status writes funnel through `SetString()` and `SetConfigStatus()`, while shared-hash updates flow into `ProcessUpdateCb()` and then `NotifyFsListener()`. Listener registration is updated both for new listener attachment and existing listeners when a filesystem object is created.

## State and Persistence Behavior

State spans base filesystem shared-hash state, local listener registrations, local subscription lifecycle, and atomic balancer counter. Listener state is runtime only; base class key/value updates may broadcast or persist according to the common filesystem and messaging realm implementation.

## Dependencies and Integration Points

The header depends on common filesystem/logging, MGM namespace macros, `mq/FsChangeListener.hh`, qclient shared-hash types, and `mq::MessagingRealm`. It integrates with `FsView` locking rules and the drain engine through implementation.

## Risks and Edge Cases

The API documents that `SetConfigStatus()` and `SetString()` must be called with `FsView::ViewMutex`; this is a contract rather than enforced by the type. Listener maps store shared pointers and can prolong listener lifetime. The class relies on callback detachment before destruction to avoid use-after-free.

## Test Signals

Header/API tests should verify construction with a mock realm, attach/detach behavior, listener interest filtering, drain transition return values, and that overriding `SetString()` preserves non-`configstatus` base behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/filesystem/FileSystem.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/fsck/Fsck.cc -->
# sources/distributed-fs/eos/mgm/fsck/Fsck.cc

## Purpose

`Fsck.cc` implements the MGM fsck engine. It collects error sets from QuarkDB, enriches them with namespace-derived offline/no-replica/dark-file accounting, reports them in monitor or JSON form, and optionally submits repair jobs through `FsckEntry`.

## Important APIs, Types, and Functions

Configuration and lifecycle are handled by `Fsck()`, `Stop()`, `ApplyConfig()`, `StoreConfig()`, and `Config()`. Worker loops are `CollectErrs()` and `RepairErrs()`. Reporting uses `PrintOut()`, `Report()`, `ReportJsonFormat()`, `ReportMonitorFormat()`, and `GetFidFormat()`. Error accounting includes `QueryQdb()`, `ResetErrorMaps()`, `AccountOfflineReplicas()`, `AccountNoReplicaFiles()`, `AccountOfflineFiles()`, `AccountDarkFiles()`, `PrintOfflineReplicas()`, and `PrintErrorsSummary()`. Repair backend cleanup uses `RepairEntry()`, `NotifyFixedErr()`, and `ForceCleanQdbOrphans()`.

## Control Flow

`ApplyConfig()` parses stored `fsck` config, supports old and new key names, and calls `Config()`. Enabling collection starts `CollectErrs`; enabling repair requires collection and starts `RepairErrs`. Collector waits for namespace boot and MGM master role, reads all `fsck:<error>` QDB sets into a temporary map, swaps it into `eFsMap`, optionally performs heavy namespace accounting, logs a summary, publishes logs, signals repair, and sleeps for the configured interval. Repair waits for master and `mStartProcessing`, copies `eFsMap`, submits prioritized repair jobs to `mThreadPool`, rate-limits by queue size, cleans orphan entries for missing filesystems, flushes fixed-error notifications, and clears the processing flag.

## State and Persistence Behavior

Configuration is persisted in `FsView::gFsView` global config under `fsck`. Error state is in-memory maps guarded by `mErrMutex`, refreshed from QuarkDB `fsck:*` sets. Successful repair notifications are batched in static local maps inside `NotifyFixedErr()` and removed from QuarkDB by `QSet::srem()` on count, timeout, or forced flush. Logs are in-memory strings guarded by `mLogMutex`.

## Dependencies and Integration Points

The engine depends on global `gOFS`, `FsView`, namespace prefetchers and views, QuarkDB qclient/QSet, JSONCPP, EOS thread pool/assisted thread/logging helpers, `IdTrackerWithValidity`, and `FsckEntry`. It integrates with CLI/admin commands for config, stats, reports, and repair.

## Risks and Edge Cases

The collector and repair loops run only on master, but master transitions during queued work require careful draining. `Log()`/`LogMonitor()` use fixed buffers and `vsprintf`, which is unsafe for long formatted strings. Heavy accounting paths can scan large namespace structures and are explicitly noted as expensive. `RepairErrs()` copies potentially large error maps and submits many jobs. `ForceCleanQdbOrphans()` appears to miss a semicolon after an `eos_static_info` call. `RepairEntry()` assumes `mQcl` is initialized.

## Test Signals

Test signals include config parsing for old/new keys, collect/repair enable transitions, collection interval conversion, QDB parse errors, report formatting in JSON and monitor modes, offline/no-replica/dark-file accounting on synthetic views, repair prioritization/category filtering, fixed-error flush behavior, and master-role stop behavior with queued jobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/fsck/Fsck.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/fsck/Fsck.hh -->
# sources/distributed-fs/eos/mgm/fsck/Fsck.hh

## Purpose

`Fsck.hh` declares the MGM filesystem-check engine. It defines the public control, reporting, collection, and repair API used by admin commands and by `FsckEntry` repair outcomes.

## Important APIs, Types, and Functions

Public APIs include constructor/destructor, `Stop()`, `PrintOut()`, `Config()`, `Report()`, `PublishLogs()`, `Log()`, `LogMonitor()`, `ApplyConfig()`, `StoreConfig()`, `CollectErrs()`, `RepairErrs()`, `RepairEntry()`, `NotifyFixedErr()`, `SetMaxThreadPoolSize()`, `GetThreadPoolInfo()`, and `ForceCleanQdbOrphans()`. The private `ErrMapT` maps error-name to file-id to filesystem-id set. Configuration keys and flags track collection, repair, best-effort mode, repair category, and interval.

## Control Flow

The declaration separates collector, repair submitter, and individual repair entry logic. The collector populates `eFsMap`; the repair thread processes entries and delegates file-specific decisions to `FsckEntry`; fixed notifications flow back through `NotifyFixedErr()` to update QuarkDB.

## State and Persistence Behavior

State includes atomics for display and thread flags, repair category, in-memory logs, collection interval, guarded error maps, unavailable/dark filesystem counters, timestamp, queue/thread-pool limits, assisted threads, thread pool, and QuarkDB client. Persistent effects are stored through config engine and QuarkDB, not directly by the header.

## Dependencies and Integration Points

The header depends on `FsckEntry`, common filesystem/file-id/thread-pool helpers, MGM id tracker, namespace file metadata interfaces, and QuarkDB qclient. It is integrated with `FsView`, global MGM services, and EOS admin/reporting commands.

## Risks and Edge Cases

Several public methods are thread entry points and must tolerate asynchronous shutdown. Many members are atomic, but map/log access still requires the declared mutexes. The public `Log()` APIs are `printf`-style and can be misused by callers. `RepairEntry()` accepts arbitrary error strings and filesystem sets, so validation must be strong in implementation.

## Test Signals

Tests should verify object lifecycle start/stop, thread-pool sizing, config persistence, report API combinations, `NotifyFixedErr()` batching, and category-specific repair dispatch using fake `FsckEntry` or mocked backends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/fsck/Fsck.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/fsck/FsckEntry.cc -->
# sources/distributed-fs/eos/mgm/fsck/FsckEntry.cc

## Purpose

`FsckEntry.cc` implements repair logic for one fsck finding on one file id. It gathers MGM metadata and FST-local metadata, classifies good and bad replicas or stripes, updates namespace metadata when safe, runs drain-transfer-style repair jobs, drops bad replicas, resyncs FST metadata, and reports success or failure to the fsck engine.

## Important APIs, Types, and Functions

The constructor maps `FsckErr` values to repair functions and creates a `DrainTransferJob` factory. Metadata collection is handled by `CollectMgmInfo()`, `CollectAllFstInfo()`, `CollectFstInfo()`, and `GetFstFmd()`. Repair paths are `Repair()`, `RepairMgmXsSzDiff()`, `RepairFstXsSzDiff()`, `RepairInconsistencies()`, `RepairReplicaInconsistencies()`, `RepairRainInconsistencies()`, and `RepairBestEffort()`. Post-actions are `ResyncFstMd()` and `NotifyOutcome()`.

## Control Flow

`Repair()` records MGM stats, fetches MGM metadata from QuarkDB, treats missing MGM metadata as an orphan/ghost cleanup, removes detached files, gathers FST info for all known locations plus the reported fsid, rejects tape-replica files, and dispatches either the reported repair operation or a priority sequence of MGM checksum/size, FST checksum/size, and consistency repairs. Replica checksum/size repairs compare MGM checksum/size, FST stored metadata, and disk stat size to select good and bad fsids. Consistency repairs diverge for replica layouts and RAIN layouts. RAIN logic handles unregistered, missing, differential, and stripe errors with registration, drop, or reconstruction jobs. Best-effort repair selects a reference replica, commits its checksum/size through verifystripe or test-mode mutation, then rebuilds enough replicas.

## State and Persistence Behavior

Each instance owns `mMgmFmd`, a map of FST file info, reported error, best-effort flag, repair dispatch map, repair factory, and QDB client. Persistent effects include namespace file metadata updates, replica location add/remove, dropped replicas, verifystripe checksum/size commits, drain-transfer repair copies, FST resync queries, MGM stat counters, and QuarkDB fsck-set removals through `NotifyOutcome()`.

## Dependencies and Integration Points

The implementation depends on global `gOFS`, `FsView`, namespace services and prefetchers, `MetadataFetcher`, XRootD client filesystem/stat/query APIs, drain transfer jobs, layout helpers, FST FMD parsing, MGM stats, and `proc_fs_dropghosts`.

## Risks and Edge Cases

Repair is destructive in several paths: `DropReplica()`, namespace location removal, detached file removal, and best-effort metadata commits. Best-effort can choose the largest available replica when no MGM match exists, which is operationally useful but risky. Many paths assume `mFsidErr` is non-empty. Network timeouts and missing FST metadata influence whether replicas are considered bad or unrepaired. RAIN over-replication and too many corrupt stripes require manual handling. Destructor removes the file id from the global tracker, so lifecycle ownership matters.

## Test Signals

Tests should cover missing MGM metadata orphan cleanup, detached file removal, tape-replica refusal, checksum/size match and mismatch matrices, unscanned replicas, zero-size no-disk case, replica under/over-replication, RAIN missing/unregistered/stripe errors, best-effort enabled/disabled paths, FST query timeout/error parsing, and `NotifyOutcome()` updates for stripe and diff-replica errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/fsck/FsckEntry.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/fsck/FsckEntry.hh -->
# sources/distributed-fs/eos/mgm/fsck/FsckEntry.hh

## Purpose

`FsckEntry.hh` declares the per-file fsck repair object and related FST metadata/error types. It is the boundary between fsck engine scheduling and concrete file repair operations.

## Important APIs, Types, and Functions

`enum class FstErr` represents FST-side metadata states: none, no contact, not on disk, no FMD info, and non-existing filesystem. `FstFileInfoT` stores local path, disk size, FST FMD helper, and FST error. Type aliases define `FsckRepairJob` as `DrainTransferJob`, `RepairFnT`, and `RepairFactoryFnT`. `FsckEntry` exposes constructor, destructor, and `Repair()`, with repair helpers made public only under `IN_TEST_HARNESS`.

## Control Flow

The header shows a repair object lifecycle: construct with file id, error fsids, expected error type, best-effort flag, and QDB client; call `Repair()`; the implementation gathers MGM/FST metadata, runs a matching repair helper, and notifies outcome. Helper names reveal the major branches: MGM checksum/size diff, FST checksum/size diff, replica/RAIN inconsistency repair, best-effort repair, metadata collection, FST FMD query, resync, and stats/backend notification.

## State and Persistence Behavior

Per-entry state includes file id, error filesystem ids, converted reported fsck error, best-effort flag, MGM metadata protobuf, FST info map, repair-operation dispatch map, repair-job factory, and QDB client. The object itself is transient; implementation methods can mutate persistent namespace metadata and FST/backend state.

## Dependencies and Integration Points

The header depends on EOS logging, common filesystem/FMD types, drain transfer jobs, namespace file metadata interfaces, QuarkDB qclient, and XRootD client filesystem APIs. It integrates with `Fsck` via `NotifyOutcome()` and with drain/transfer infrastructure through `FsckRepairJob`.

## Risks and Edge Cases

The repair factory signature is broad and easy to misuse: source/destination fsids, exclusion sets, drop-source, app tag, and repair-excluded flags all affect destructive behavior. Test harness exposure changes method visibility. `FstFileInfoT` does not initialize `mDiskSize` in its constructor, so code must set it before reading for successful stats.

## Test Signals

Header-level tests should compile both normal and `IN_TEST_HARNESS` builds. Unit tests should inject a fake repair factory and QDB client, validate dispatch for every supported `FsckErr`, and verify FST error enum handling in metadata collection and repair decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/fsck/FsckEntry.hh -->
