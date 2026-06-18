# subset-b-007051 EOS MGM tape GC, replication tracking, filesystem utilities, VID, and WFE research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/SpaceToTapeGcMap.hh -->
# sources/distributed-fs/eos/mgm/tgc/SpaceToTapeGcMap.hh

## Purpose
Declares `SpaceToTapeGcMap`, the MGM-side owner of per-space tape-aware garbage collectors. It is the registry that turns an EOS space name into a `TapeGc` instance and exposes aggregate statistics, space names, JSON dumping, and worker-thread startup.

## Important APIs, types, and functions
The constructor stores an `ITapeGcMgm&` used to construct each `TapeGc`. `createGc()` validates a non-empty space, creates exactly one collector per space, and throws `GcAlreadyExists` on duplicates. `destroyAllGc()` clears all owned collectors. `getGc()` returns a reference or throws `UnknownEOSSpace`. `getStats()`, `getSpaces()`, `toJson()`, and `startGcWorkerThreads()` expose operational state across all collectors.

## Control flow
Callers create collectors as spaces become tape-GC-enabled, then start all workers once configured. Runtime operations lock the map, look up the requested space, and either delegate to the stored `TapeGc` or build aggregate results.

## State and persistence behavior
State is in-memory only: `m_gcs` maps space names to `std::unique_ptr<TapeGc>`, protected by `m_mutex`. There is no direct persistence; the durable behavior is delegated to MGM namespace/config state through each `TapeGc` and its `ITapeGcMgm` interface.

## Dependencies and integration points
Depends on `ITapeGcMgm`, `TapeGc`, and `TapeGcStats`. It is part of the `EOSTGC` namespace and integrates with code that tracks which EOS spaces should run tape-aware disk-replica eviction.

## Risks and test signals
`getGc()` returns a reference after releasing the map lock, so external lifetime must ensure no concurrent `destroyAllGc()` invalidates that reference. `toJson()` manually writes JSON keys without escaping space names. Tests should cover duplicate creation, empty-space errors, unknown lookups, concurrent create/get/destroy behavior, JSON max-length exceptions, and worker startup idempotence through the underlying collectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/SpaceToTapeGcMap.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/TapeGc.cc -->
# sources/distributed-fs/eos/mgm/tgc/TapeGc.cc

## Purpose
Implements the tape-aware garbage collector for one EOS space. It tracks file accesses in an LRU queue and, when space pressure crosses configured thresholds, evicts disk replicas for files that also exist on tape.

## Important APIs, types, and functions
The constructor wires `ITapeGcMgm::getTapeGcSpaceConfig()` into `CachedValue<SpaceConfig>` and initializes `SmartSpaceStats`. `startWorkerThread()` uses an `atomic_flag` to start one worker. `workerThreadEntryPoint()` drains possible evictions then sleeps on `BlockingFlag`. `fileAccessed()` updates the `Lru` queue and logs the first max-queue threshold crossing. `tryToGarbageCollectASingleFile()` is the core policy loop. `getStats()`, `getLruQueueSize()`, `toJson()`, and `diskReplicaQueuedForDeletion()` expose status and update cached free-space accounting.

## Control flow
The worker repeatedly calls `tryToGarbageCollectASingleFile()` until it cannot evict more files, then waits one second or until stopped. A collection attempt loads cached config, queries space stats, returns early if available bytes are high enough or not all expected total bytes are online, pops the least-recently-used fid, reads its size, ignores zero-size or missing metadata as successful queue removal, calls `m_mgm.evictAsRoot(fid)`, and requeues the fid if eviction fails.

## State and persistence behavior
State includes the stop flag, one worker thread, `m_lruQueue` protected by `m_lruQueueMutex`, cached space config and stats, and atomic `m_nbEvicts`. The class itself persists nothing, but `evictAsRoot()` mutates EOS namespace/file replica state asynchronously and `diskReplicaQueuedForDeletion()` updates cached space stats before the next MGM poll.

## Dependencies and integration points
Depends on `ITapeGcMgm` for config, file sizes, and evict command execution; `SmartSpaceStats` for capacity state; `Lru` for access ordering; `SpaceNotFound` for missing spaces; `MaxLenExceeded` for bounded JSON; and EOS logging. `TestingTapeGc.hh` exposes the core collection method for unit tests.

## Risks and test signals
Important edge cases are exception swallowing, lost work if file size lookup fails, indefinite retention if eviction repeatedly fails and requeues the same fid, and thread shutdown joining while an MGM operation is blocked. `toJson()` does not escape string fields. Tests should simulate high/low free-space thresholds, offline total-bytes suppression, missing spaces, zero-size files, missing file size, eviction failure/requeue, successful eviction counter increments, destructor stop behavior, and concurrent `fileAccessed()` with worker eviction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/TapeGc.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/TapeGc.hh -->
# sources/distributed-fs/eos/mgm/tgc/TapeGc.hh

## Purpose
Declares `TapeGc`, the per-space tape-aware disk-replica garbage collector. It combines an access LRU, cached tape-GC configuration, space statistics, worker-thread lifecycle, and eviction counters.

## Important APIs, types, and functions
Public APIs are construction, destruction, `startWorkerThread()`, `fileAccessed(fid)`, `getStats()`, and `toJson()`. Protected internals include `workerThreadEntryPoint()`, `getLruQueueSize()`, `tryToGarbageCollectASingleFile()`, and `diskReplicaQueuedForDeletion()`. Data members include `ITapeGcMgm&`, `m_spaceName`, `BlockingFlag m_stop`, `m_worker`, `Lru m_lruQueue`, `CachedValue<SpaceConfig> m_config`, `SmartSpaceStats m_spaceStats`, and atomic `m_nbEvicts`.

## Control flow
The header establishes the lifecycle: file-access notifications feed the LRU, `startWorkerThread()` runs the worker once, the worker consults config/stats before popping an LRU fid, and successful evictions update counters and cached space accounting.

## State and persistence behavior
All direct state is process-local and protected by mutexes or atomics. Persistent side effects happen through the MGM abstraction: eviction changes replica state and space queries/config come from external MGM views.

## Dependencies and integration points
Includes EOS logging, namespace/file metadata interfaces, console proto headers, TGC helpers (`BlockingFlag`, `CachedValue`, `Lru`, `SmartSpaceStats`, `SpaceConfig`, `TapeGcStats`), and threading primitives. It is owned by `SpaceToTapeGcMap` and tested through `TestingTapeGc`.

## Risks and test signals
Because copy/move/assignment are deleted, ownership is intentionally unique. Tests should assert worker startup is idempotent, stats are sane after exceptions, lock ordering does not deadlock with `ITapeGcMgm`, and the protected eviction method remains deterministic under a fake MGM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/TapeGc.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/TapeGcStats.hh -->
# sources/distributed-fs/eos/mgm/tgc/TapeGcStats.hh

## Purpose
Defines the snapshot structure returned by a tape-aware GC for monitoring and command output.

## Important APIs, types, and functions
`TapeGcStats` has a default constructor that initializes `nbEvicts`, `lruQueueSize`, and `queryTimestamp` to zero. It carries `SpaceStats spaceStats` plus counters for successful evictions and queued LRU entries.

## Control flow
`TapeGc::getStats()` fills this struct from the collector counter, LRU size, `SmartSpaceStats::get()`, and query timestamp. A default-constructed value is used as the fallback on error.

## State and persistence behavior
This is transient reporting state only. It mirrors runtime counters and cached space stats; it does not persist or own resources.

## Dependencies and integration points
Depends on `SpaceStats` and `Lru::FidQueue::size_type` from the TGC subsystem. `SpaceToTapeGcMap::getStats()` aggregates one instance per space.

## Risks and test signals
Zero is both a valid value and the error sentinel for multiple fields, so consumers need context to distinguish "no evictions" from "failed to query." Tests should cover normal population and fallback defaults when `TapeGc::getStats()` catches exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/TapeGcStats.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/TestingTapeGc.hh -->
# sources/distributed-fs/eos/mgm/tgc/TestingTapeGc.hh

## Purpose
Provides a thin test-only subclass of `TapeGc` that exposes the core protected eviction method.

## Important APIs, types, and functions
`TestingTapeGc` forwards constructor arguments to `TapeGc` and uses `using TapeGc::tryToGarbageCollectASingleFile;` to make that method public for unit tests.

## Control flow
Tests can instantiate `TestingTapeGc` with a fake `ITapeGcMgm`, push accesses through `fileAccessed()`, and invoke one eviction attempt without starting a worker thread.

## State and persistence behavior
No new state is added. All state and side effects are inherited from `TapeGc`.

## Dependencies and integration points
Depends directly on `TapeGc.hh`. It is intended for TGC unit tests that need deterministic, single-step garbage collection.

## Risks and test signals
The class intentionally breaks encapsulation for testing, so tests should avoid relying on unrelated protected internals. It is useful for verifying each branch in `tryToGarbageCollectASingleFile()` without sleeps or background-thread timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tgc/TestingTapeGc.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tracker/ReplicationTracker.cc -->
# sources/distributed-fs/eos/mgm/tracker/ReplicationTracker.cc

## Purpose
Implements the MGM replication/creation tracker. It creates tag files for newly created files, removes them once the expected replica count is reached, periodically scans stale tracker entries, cleans abandoned atomic uploads, and optionally triggers layout/space conversion hooks on creation, injection, or access.

## Important APIs, types, and functions
`GetValidLocation()` selects the first non-zero, non-tape filesystem location. The constructor sets root identity and starts an assisted background thread. `Create()` makes a dated tracker directory and tag file. `Access()` checks conversion-on-access policy. `Commit()` removes the tag after replica count reaches layout stripe count and can trigger creation/injection conversion. `ConversionPolicy()` and `ConversionSizePolicy()` read space config. `Prefix()` maps file ctime to `mPath/YYYY/MM/DD/`. `getOptions()` reads default-space tracker config. `backgroundThread()` refreshes enable/conversion state and calls `Scan()`. `Scan()` lists tracker entries, reports status, removes completed/missing tags, cleans old empty directories, and deletes stale atomic target files.

## Control flow
On create, a tag file named by hex fid is stored under the date prefix. On commit, temporary atomic names are ignored; otherwise a file whose disk replica count matches its layout has its tag removed. Conversion hooks build a `/proc/user` file-convert command when configured policy and size filters allow it. The background thread waits for namespace boot, checks default-space `tracker` and `policy.conversion` settings, runs only on the master, and periodically scans the tracker tree.

## State and persistence behavior
Persistent state is represented by namespace tag files under `mPath`, their dated parent containers, and possible deletion of atomic upload files. Conversion jobs are submitted through `ProcCommand`. In-memory state is `mEnabled`, `mConversionEnabled`, root `mVid`, `mPath`, and the assisted thread.

## Dependencies and integration points
Uses global `gOFS`, `eosView`, `eosFileService`, `FsView::gFsView`, namespace locks, `ProcCommand`, `Resolver`, `Prefetcher`, layout helpers, and XRootD error/string types. It integrates with file creation/commit/access paths and default-space configuration.

## Risks and test signals
`Scan()` appends to `out` even when the tracker is disabled without checking `out` for null, which is risky for cleanup callers if disabled. Size-policy parsing uses `std::stol()` without local exception handling. `Access()` has a missing `break` after the `>` policy case, causing the default warning path to run too. Tests should cover disabled cleanup scans, malformed size policies, atomic-file cleanup, missing fids, replica-count thresholds with tape locations, conversion command formation, master-only background behavior, and tag directory cleanup age.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tracker/ReplicationTracker.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tracker/ReplicationTracker.hh -->
# sources/distributed-fs/eos/mgm/tracker/ReplicationTracker.hh

## Purpose
Declares the replication tracker interface and its background-thread state.

## Important APIs, types, and functions
`OperationMode` distinguishes injection, creation, and access conversion policies. `Options` carries enablement, atomic cleanup age, and scan interval. Public methods include `Create()`, `Access()`, `ConversionPolicy()`, `ConversionSizePolicy()`, `Commit()`, `Validate()`, `Scan()`, `Prefix()`, `enabled()/enable()/disable()`, conversion enable/disable helpers, and `getOptions()`.

## Control flow
External MGM operations call `Create`, `Commit`, or `Access`; the tracker thread calls `getOptions()` and `Scan()`. The static `Create()` factory returns a heap-allocated tracker for legacy construction sites.

## State and persistence behavior
The header owns process-local state: an `AssistedThread`, atomic enable flags, an error object, root virtual identity, and the tracker root path. Durable tracker state is implied by namespace files under `mPath`.

## Dependencies and integration points
Depends on `AssistedThread`, `VirtualIdentity`, `IFileMD`, XRootD strings/errors, and MGM namespace macros. It is integrated with global MGM services in the implementation.

## Risks and test signals
`Validate()` is declared but empty in the implementation. Enable flags are atomics, but broader namespace work relies on external locks. Tests should exercise enable/disable idempotence, conversion flag toggling, background thread shutdown, and scan reporting via the optional output string.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/tracker/ReplicationTracker.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/utils/AttrHelper.cc -->
# sources/distributed-fs/eos/mgm/utils/AttrHelper.cc

## Purpose
Implements small attribute-policy helpers used by MGM write paths for owner impersonation, atomic uploads, versioning, and xattr retrieval.

## Important APIs, types, and functions
`checkDirOwner()` evaluates `sys.auth.owner`, including sticky `*` and protocol-qualified identity keys. `checkAtomicUpload()` evaluates `sys.forced.atomic`, `user.forced.atomic`, then CGI fallback. `getVersioning()` evaluates CGI first, then system and user versioning attributes. `getValue()` returns string xattr values by key.

## Control flow
Directory-owner checks build an owner key from `vid.prot` plus either DN for GSI or `uid_string` for other protocols. Comma padding anchors list matching to avoid prefix collisions. On a non-sticky match, the virtual identity is rewritten to the directory uid/gid. Atomic and versioning helpers parse numeric strings with configured precedence.

## State and persistence behavior
No state is persisted. The only mutation is to the caller-provided `VirtualIdentity` and `sticky_owner` output flag.

## Dependencies and integration points
Uses MGM constants such as `SYS_OWNER_AUTH`, `SYS_FORCED_ATOMIC`, `USER_FORCED_ATOMIC`, `SYS_VERSIONING`, and `USER_VERSIONING`; `StringToNumeric`; and EOS logging. It is consumed by request paths evaluating inherited directory xattrs.

## Risks and test signals
`checkAtomicUpload()` treats the mere presence of `atomic_cgi` as true, regardless of its value. Numeric parse failures leave defaults. Sticky owner does not rewrite the VID by design. Tests should cover anchored owner matching, GSI DN versus uid string keys, sticky behavior, parse failures, precedence order, and CGI values like `"0"`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/utils/AttrHelper.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/utils/AttrHelper.hh -->
# sources/distributed-fs/eos/mgm/utils/AttrHelper.hh

## Purpose
Declares attribute helper functions and a templated typed xattr getter for MGM code.

## Important APIs, types, and functions
The namespace `eos::mgm::attr` exposes `checkDirOwner()`, `checkAtomicUpload()`, `getVersioning()`, string `getValue()`, and arithmetic-template `getValue<T>()` enabled only for arithmetic types.

## Control flow
Callers pass an `IContainerMD::XAttrMap`; helpers apply policy-specific precedence. The numeric `getValue()` template finds a key and delegates conversion to `common::StringToNumeric()`.

## State and persistence behavior
Header-only template state is local to callers. No persistence occurs.

## Dependencies and integration points
Depends on namespace container metadata, `VirtualIdentity`, `StringUtils`, and C++ type traits. The functions are part of request attribute handling.

## Risks and test signals
Template conversion behavior depends on `StringToNumeric()` return semantics and target type bounds. Tests should verify signed/unsigned conversions, missing keys, invalid strings, and that non-arithmetic overloads are not selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/utils/AttrHelper.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/utils/FileSystemRegistry.cc -->
# sources/distributed-fs/eos/mgm/utils/FileSystemRegistry.cc

## Purpose
Implements a thread-safe registry that indexes live MGM `FileSystem` objects by fsid, pointer, and queue path.

## Important APIs, types, and functions
`lookupByID()`, `lookupSpaceByID()`, `lookupByQueuePath()`, and `lookupByPtr()` provide read-side lookups. `registerFileSystem()` validates fsid, pointer, queue path, and uniqueness across all indexes. `eraseById()`, `eraseByPtr()`, `exists()`, `size()`, and `clear()` maintain and expose registry contents.

## Control flow
Registration acquires a write lock, rejects collisions and invalid inputs, then inserts all three indexes and asserts equal sizes. Erase operations locate the primary entry, assert corresponding reverse indexes exist, erase all mappings, and reassert invariants. Lookups acquire read locks and return nullable pointers or sentinel values.

## State and persistence behavior
State is process-local: `mById`, `mByFsPtr`, and `mByQueuePath`. It does not own or persist `FileSystem` objects. Durable filesystem configuration is outside this class.

## Dependencies and integration points
Uses `RWMutex`, `FileSystemLocator`, MGM `FileSystem`, `FsView`, EOS logging, and `eos_assert`. It backs `FsView::mIdView`-style lookups used by tracker, WFE, and space utilities.

## Risks and test signals
`lookupSpaceByID()` takes a read lock and then calls `lookupByID()`, which takes another read lock; this depends on read-lock reentrancy/compatibility. Header-provided iterators expose internal maps without locking, so legacy iteration can race if used concurrently. Tests should cover all collision types, fsid zero, null pointer, empty queue path, erase by both keys, queue path uniqueness, and concurrent lookup/register behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/utils/FileSystemRegistry.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/utils/FileSystemRegistry.hh -->
# sources/distributed-fs/eos/mgm/utils/FileSystemRegistry.hh

## Purpose
Declares `FileSystemRegistry`, a compatibility map-like registry for currently registered MGM filesystems with multiple lookup indexes.

## Important APIs, types, and functions
Defines `const_iterator` over the fsid map and exposes `begin()/end()` compatibility methods. Lookup APIs return by id, pointer, queue path, or space. Mutation APIs register, erase, and clear entries. Private `IdAndQueuePath` stores reverse-index metadata.

## Control flow
The public contract requires unique fsid, unique `FileSystem*`, and unique queue path for registration. All indexes are kept in lockstep by the implementation.

## State and persistence behavior
The registry stores raw `mgm::FileSystem*` values but does not own their lifetime. It is in-memory only and protected by `mMutex` for normal methods.

## Dependencies and integration points
Depends on `common/FileSystem.hh`, `mgm/filesystem/FileSystem.hh`, `RWMutex`, and MGM namespace macros. It is a central lookup utility for global filesystem views.

## Risks and test signals
Iterator methods do not acquire locks and should be treated as legacy compatibility hazards. Tests should verify no stale reverse mappings remain after erase and that object lifetime is controlled elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/utils/FileSystemRegistry.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/utils/FileSystemStatusUtils.cc -->
# sources/distributed-fs/eos/mgm/utils/FileSystemStatusUtils.cc

## Purpose
Implements helpers for applying drain-completion/failure status and querying filesystem status by group.

## Important APIs, types, and functions
`ApplyDrainedStatus()` sets drain status to drained, clears drain counters, and when not shutting down marks the durable `configstatus` as `empty`. `ApplyFailedDrainStatus()` marks drain failed and records failed-job count. `FsidsinGroup()` returns fsids in a group matching active/drain status. `GetGroupFsStatus()` returns a map from fsid to active/drain statuses.

## Control flow
Each function locks `FsView::gFsView.ViewMutex`, resolves groups or ids through global views, reads or updates the target `FileSystem`, and logs missing groups or status changes.

## State and persistence behavior
`FileSystemUpdateBatch` applies local status and counter updates. `ApplyDrainedStatus()` also calls `StoreFsConfig(fs)` and sets durable `configstatus=empty` when MGM is not shutting down.

## Dependencies and integration points
Uses `FsView`, global `gOFS`, EOS logging, `FileSystemUpdateBatch`, `ActiveStatus`, and `DrainStatus`. It is used by drain workflows and group-selection logic.

## Risks and test signals
`FsidsinGroup()` accepts status parameters but currently compares against hard-coded `kOnline` and `kNoDrain`, ignoring the arguments. `ApplyDrainedStatus()` calls `StoreFsConfig(fs)` before `fs->applyBatch(batch)`, so tests should confirm durable status ordering is intentional. Tests should cover missing groups, null filesystem targets, shutdown versus non-shutdown drain completion, failed-drain counters, and argument-sensitive filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/utils/FileSystemStatusUtils.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/utils/FileSystemStatusUtils.hh -->
# sources/distributed-fs/eos/mgm/utils/FileSystemStatusUtils.hh

## Purpose
Declares filesystem drain/status utility functions and small status carrier types.

## Important APIs, types, and functions
Functions are `ApplyDrainedStatus()`, `ApplyFailedDrainStatus()`, `FsidsinGroup()`, and `GetGroupFsStatus()`. `FsidStatus` stores active and drain status for one fsid, and `fs_status_map_t` aliases a map of those statuses.

## Control flow
Callers use these helpers after drain jobs finish or fail, and to select/query filesystems in a group by status.

## State and persistence behavior
The header defines no state. Persistence happens in the implementation through filesystem config/status updates.

## Dependencies and integration points
Depends on `common/FileSystem.hh`, STL vectors/maps, and namespace `eos::mgm::fsutils`. It exposes a narrow utility surface to drain and balancing code.

## Risks and test signals
Default filter values imply online/no-drain selection. Tests should ensure the implementation honors the declared parameters and that `FsidStatus` values match target filesystem state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/utils/FileSystemStatusUtils.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/utils/FilesystemUuidMapper.cc -->
# sources/distributed-fs/eos/mgm/utils/FilesystemUuidMapper.cc

## Purpose
Implements a thread-safe bidirectional map between filesystem IDs and UUID strings.

## Important APIs, types, and functions
`injectMapping()` validates positive id/non-empty UUID and rejects conflicting existing mappings. `hasFsid()`, `hasUuid()`, `size()`, and both `lookup()` overloads are read operations. `remove()` by id or UUID deletes both directions. `clear()` drops all mappings. `allocate()` returns an existing id for a known UUID or assigns a free id, preferring max+1 below 64000 and then scanning for holes.

## Control flow
All methods take read or write locks. Mutations maintain `uuid2fs` and `fs2uuid` together. Allocation starts at 1 for an empty map, uses increasing ids when possible, falls back to linear search, and aborts the process if all ids are exhausted.

## State and persistence behavior
State is in-memory only: `fs2uuid` and `uuid2fs`. Persistence of mappings, if any, is external to this class.

## Dependencies and integration points
Uses `RWMutex`, EOS assertions/logging, and `common::FileSystem::fsid_t`. It replaces/encapsulates legacy FsView uuid-fsid mapping behavior.

## Risks and test signals
`allocate()` does not reject an empty UUID, unlike `injectMapping()`. Exhaustion calls `exit(-1)`, which is severe for a library-like utility. The 64000 cap is a legacy limit. Tests should cover id/UUID conflicts, id 0 rejection, empty UUID injection rejection, empty UUID allocation behavior, hole reuse above max threshold, remove consistency, and concurrent allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/utils/FilesystemUuidMapper.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/utils/FilesystemUuidMapper.hh -->
# sources/distributed-fs/eos/mgm/utils/FilesystemUuidMapper.hh

## Purpose
Declares `FilesystemUuidMapper`, a bidirectional uuid-to-fsid utility with allocation support.

## Important APIs, types, and functions
Public methods inject, query, look up, remove, clear, and allocate mappings. The private state is an `RWMutex`, `fs2uuid`, and `uuid2fs`.

## Control flow
The class promises conflict-free injection, sentinel returns (`0` or empty string) for missing lookups, and stable allocation for already-registered UUIDs.

## State and persistence behavior
All state is in-process map state. The class does not store to config or namespace services.

## Dependencies and integration points
Depends on MGM namespace macros, `common/FileSystem.hh`, and `RWMutex`. It is designed for filesystem registration/bootstrap paths that need stable IDs.

## Risks and test signals
The stated 64k capacity affects scalability and failure mode. Tests should verify one-to-one invariants after every public mutation and ensure callers do not treat fsid `0` as allocatable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/utils/FilesystemUuidMapper.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/vid/Vid.cc -->
# sources/distributed-fs/eos/mgm/vid/Vid.cc

## Purpose
Implements the MGM VID administration commands that configure virtual identity mapping, role membership, token sudo policy, public access depth, and geotag mappings.

## Important APIs, types, and functions
`Vid::Set(const char*, bool)` parses `XrdOucEnv` key/value commands and updates `eos::common::Mapping` global tables. Supported commands include `publicaccesslevel`, `tokensudo`, `geotag`, `membership`, and `map`. `Vid::Set(XrdOucEnv&, ...)` wraps parsing with command output. `Vid::Ls()` prints current mapping state. `Vid::Rm()` removes role, geotag, uid/gid map, and tident wildcard entries and optionally deletes config values.

## Control flow
All changes take `Mapping::gMapMutex` write lock. `Set()` validates `mgm.vid.key`, command type, auth mode, pattern quoting, and uid/gid numeric round trips before updating maps. Membership can translate usernames to uids and populate target uid/gid role vectors or sudoer state. Mapping rules build keys like `auth:"pattern":uid/gid`; tident host wildcards also update `gAllowedTidentMatches`. `Rm()` normalizes keys, erases matching in-memory structures, removes tident wildcard allow entries, and deletes persisted config keys when requested.

## State and persistence behavior
Primary state is global in-memory mapping tables: access depth, token sudo mode, geotag map, role vectors, sudoer map, virtual uid/gid maps, and allowed tident matches. With `storeConfig=true`, changes are persisted through `gOFS->mConfigEngine` under the `vid` namespace.

## Dependencies and integration points
Depends on `common::Mapping`, `VirtualIdentity`, config engine, global `gOFS`, XRootD env/string types, and EOS logging. It is the backing implementation for administrative VID commands.

## Risks and test signals
`Rm()`'s `map` branch assigns to `gVirtualUidMap`/`gVirtualGidMap` before deleting config, which looks like an unintended mutation during removal. `Set()` accepts auth `ztn`, while `Rm()`'s auth validation omits `ztn`, creating asymmetry. Numeric parsing uses `atoi` plus string round-trip and may reject formatting variants. Tests should cover every command, username translation failures, tident wildcard insertion/removal, sudo grant/removal persistence, auth-mode symmetry, malformed patterns, missing uid/gid, and `storeConfig=false` replay behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/vid/Vid.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/vid/Vid.hh -->
# sources/distributed-fs/eos/mgm/vid/Vid.hh

## Purpose
Declares the static VID administration interface for setting, listing, and removing MGM virtual identity mappings.

## Important APIs, types, and functions
`Vid` has trivial construction/destruction and static methods `Set(const char*, bool)`, `Set(XrdOucEnv&, int&, XrdOucString&, XrdOucString&, bool)`, `Ls()`, and `Rm()`.

## Control flow
Command handlers parse an XRootD environment, call the static methods, and receive return codes plus stdout/stderr strings. `storeConfig` controls whether operations update only memory or also the config engine.

## State and persistence behavior
The header owns no state. Implementation mutates `common::Mapping` globals and optionally config-engine entries.

## Dependencies and integration points
Depends on MGM namespace macros and XRootD `XrdOucString`/`XrdOucEnv`. It is consumed by admin proc command handling.

## Risks and test signals
Because this is a global static API, tests must isolate and reset `Mapping` globals. Verify wrapper methods set `retc`, `errno`, and stdout/stderr consistently on success/failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/vid/Vid.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/wfe.proto -->
# sources/distributed-fs/eos/mgm/wfe.proto

## Purpose
Defines the legacy protobuf schema for EOS workflow notifications, including workflow metadata, client identity, file/directory metadata, and transport URL.

## Important APIs, types, and functions
Messages are `id`, `checksum`, `clock`, `md`, `security`, `client`, `service`, `workflow`, and `notification`. `md` captures ids, timestamps, ownership, size, checksum, mode, logical path, and xattrs. `workflow` captures event, queue, workflow name, virtual path, service instance, and timestamp.

## Control flow
The schema is a data contract rather than executable code. Producers populate `notification` messages with workflow, client, file, and directory context; consumers read the same fields to act on workflow events.

## State and persistence behavior
Serialized protobuf messages are transient workflow payloads. No storage is defined here, but field numbers are part of the compatibility contract.

## Dependencies and integration points
Uses proto3 and package `eos.wfe`. It relates to WFE notification/proto flows, although `WFE.cc` also uses CTA and RPC protobuf types from other generated schemas.

## Risks and test signals
Message and field names are lowercase, which can be awkward for generated APIs but is wire-compatible. Tests should cover JSON/binary serialization compatibility, xattr map preservation, timestamp precision, and old/new consumer tolerance when fields are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/wfe.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/wfe/WFE.cc -->
# sources/distributed-fs/eos/mgm/wfe/WFE.cc

## Purpose
Implements the MGM workflow engine. It scans persistent workflow queues under the proc workflow path, schedules asynchronous jobs, executes mail/bash/web-notify/protobuf actions, integrates with CTA tape workflows, updates workflow result queues, and publishes active-job statistics.

## Important APIs, types, and functions
`WFE` starts/stops an assisted scanner thread and owns a shared `XrdScheduler`. `WFEr()` is the scan loop. `Job::Save()`, `Load()`, `Move()`, `Results()`, and `Delete()` implement durable queue entries. `Job::DoIt()` dispatches `mail`, `bash`, `notify`, and tape `proto` methods. `HandleNotifyEvents()` sends JSON web notifications. `HandleProtoMethodEvents()` dispatches tape events including prepare, abort_prepare, evict_prepare, create, delete, close, archived, retrieve_failed, archive_failed, offline, and update_fid. `IdempotentPrepare()`, `SendProtoWFRequest()`, `MoveToRetry()`, `MoveWithResults()`, `CollectAttributes()`, and `MoveFromRBackToQ()` are central helpers.

## Control flow
`WFEr()` waits for namespace boot, reads default-space `wfe`, `wfe.interval`, `wfe.ntx`, and `wfe.keepTIME`, and on the master scans today's and yesterday's `q` and `e` queue directories. Ready async jobs are moved to `r`, scheduled, and counted; sync jobs are skipped by the scanner. Old workflow day directories are cleaned periodically. A job file name encodes time, fid, and event; xattrs store action, VID, error message, and retry count.

## State and persistence behavior
Durable workflow state lives in namespace files under `MgmProcWorkflowPath/<day>/<queue>/<workflow>/`. Queue names include queued, running, error/retry, done, failed, and gone/unknown paths (`q`, `r`, `e`, `d`, `f`, `g`). Result xattrs include `sys.wfe.retc`, `sys.wfe.log`, `sys.wfe.errmsg`, `sys.wfe.retry`, `sys.action`, and `sys.vid`. Proto handlers mutate file xattrs such as retrieve request IDs/times/errors, archive errors, CTA objectstore request IDs, archive metadata, and tape locations. Delete removes tape namespace locations before notifying CTA.

## Dependencies and integration points
WFE is deeply integrated with global `gOFS`, `FsView`, namespace prefetching and locks, `ProcCommand`, `ShellCmd`, `WebNotify`, `WFEClient`, CTA protobuf APIs, EOS/CTA reporting helpers, file metadata services, xattr helpers, quota/stat timing, and `EvictCmd`. Bash workflows execute scripts from `/var/eos/wfe/bash/` only when the configured executable has no slash.

## Risks and test signals
The code is concurrency- and side-effect-heavy. Risks include scheduler lifetime leaks, queue moves that save then fail to delete old entries, shell argument injection through substituted metadata, long bash timeouts, many manual placeholder replacement loops, async active-job accounting on early returns, retry attr parse failures, stale jobs in `r` after crashes, and complex tape state races around prepare IDs, archive IDs, and tape location removal. Tests should cover queue persistence and recovery, `MoveFromRBackToQ()`, sync versus async behavior, throttle limits, malformed job filenames/xattrs, bash placeholder substitution and xattr result tags, notify JSON formation, proto endpoint missing, CTA response-code mapping, idempotent prepare with duplicate request IDs, abort with remaining request IDs, archive ID mismatch, delete without archive file id, file-archived GC drop-stripes policy, and retry exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/wfe/WFE.cc -->
