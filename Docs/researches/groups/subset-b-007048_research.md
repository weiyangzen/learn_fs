# Research: subset-b-007048

Work item covering EOS MGM QDB master election, quota accounting/enforcement, and recycle-bin cleanup/restore policy files. Each file section is bounded by the reconciliation markers required for splitting into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/qdbmaster/QdbMaster.cc -->
# sources/distributed-fs/eos/mgm/qdbmaster/QdbMaster.cc

## Purpose
`QdbMaster.cc` implements the `QdbMaster` concrete `IMaster` backend for QuarkDB-backed EOS MGM deployments. It boots the namespace plugin, supervises QuarkDB lease ownership, transitions an MGM between slave and master behavior, applies master configuration, toggles namespace cache settings, and starts/stops master-only services.

## Important APIs and functions
- `QdbMaster::QdbMaster` stores the local `host:port` identity and creates a `qclient::QClient` from `QdbContactDetails`.
- `Init()` marks namespace state as booting and starts the `Supervisor` assisted thread.
- `BootNamespace()` loads the `NamespaceGroup` plugin, builds QuarkDB namespace configuration, initializes container/file/filesystem/accounting views, registers `Quota::MapSizeCB`, runs namespace `initialize1/initialize2`, starts cache refresh listening, and sets `gOFS->mNamespaceState`.
- `Supervisor()` is the main election loop. It waits for namespace boot, calls `AcquireLeaseWithDelay()`, refreshes `mMasterIdentity` from `GetLeaseHolder()`, and dispatches `SlaveToMaster()` or `MasterToSlave()` on role changes.
- `ConfigureTimeouts()` reads `EOS_QDB_MASTER_INIT_LEASE_MS` and `EOS_QDB_MASTER_LEASE_MS`, caps regular lease validity at five minutes, and ensures transition leases are at least as long as steady-state leases.
- `AcquireLease()`, `ReleaseLease()`, and `GetLeaseHolder()` use QuarkDB commands `lease-acquire`, `lease-release`, and `lease-get` against static key `master_lease`.
- `SlaveToMaster()` drains in-flight requests, refreshes inode providers, enables config broadcasts, applies config, loads quota nodes, enables namespace caching, starts WFE recovery, broadcasts master id, and starts LRU, recycler, device tracker, geotree refresh, and tape GC if enabled.
- `MasterToSlave()` clears master status, stops master-only engines, stalls/drains requests, disables config broadcast and namespace caching, applies config once during initial slave boot, and stops tape GC if configured.
- `PostSlaveToMaster()` runs an optional `mgmofs.postslavetomaster` shell hook with old/new master ids and a 60 second timeout.
- `ApplyMasterConfig()` serializes config application with a static mutex, restarts drain handling, disables direct FsView config engine interaction through `ConfigResetMonitor`, and autoloads `gOFS->MgmConfigAutoLoad`.
- `SetMasterId()` currently only arranges an acquire delay when called on the current master for a different target; it does not write a new lease holder directly.
- `IsRemoteMasterOk()` builds a root URL from the current master id and checks reachability via `XrdCl::FileSystem::Ping`.

## Control flow
Startup flows through `Init()` and `BootNamespace()` in parallel with the supervisor: `BootNamespace()` completes namespace initialization and then waits until `mOneOff` is cleared by the supervisor. The supervisor installs a boot stall rule, waits for namespace state `kBooted`, attempts to acquire or observe the QDB lease, and performs a one-off master or slave transition. Later loop iterations renew/observe the lease at half the lease interval when a master exists, react to lease loss by moving master to slave, and react to lease acquisition by moving slave to master and invoking the optional post-transition hook.

The transition paths deliberately gate client traffic. `SlaveToMaster()` sets a short stall rule, disables request acceptance, waits for in-flight requests to drain, refreshes metadata providers, applies config, starts master-only services, removes the stall, writes the master lockfile, and then delays accepting requests for `sMasterDelaySec` in the supervisor loop. `MasterToSlave()` removes the lockfile, stops master-only services, stalls/drains, disables broadcasts and namespace caching, and leaves the process as a listener.

## State and persistence
- Persistent election state lives in QuarkDB under `QdbMaster::sLeaseKey` (`master_lease`) with values managed by QuarkDB lease commands.
- Local role state is held in atomics `mIsMaster`, `mOneOff`, `mConfigLoaded`, `mAcquireDelay`, and `mDoMasterDelay`; master identity string access is protected by `mMutexId`.
- Namespace boot state and all services are global through `gOFS`; this file mutates `mNamespaceState`, namespace service pointers, request tracker state, messaging broadcast mode, config engine state, cache settings, and status lockfiles.
- Config persistence is delegated to the MGM config engine. This file loads config but does not itself persist master election decisions.
- The optional post-transition hook is external process state and is only logged on failure; the transition is already complete when it runs.

## Dependencies and integration points
`QdbMaster` is tightly coupled to MGM globals and services: `XrdMgmOfs`, `Access`, `Quota`, `WFE`, `Fsck`, `LRU`, `Recycle`, `Devices`, `GeoTreeEngine`, `ConverterEngine`, `IConfigEngine`, `MessagingRealm`, tape GC, namespace plugin interfaces, QuarkDB namespace constants, `qclient`, XRootD client ping, and shell command execution. `BootNamespace()` is the bridge between the plugin manager and the global namespace service pointers consumed by most MGM subsystems. `SlaveToMaster()` integrates quota loading and recycler startup, making these research files part of the master failover path.

## Risks and edge cases
- `GetLeaseHolder()` parses a textual `lease-get` reply and includes `pos_end - pos + 1`, which can retain a newline in `mMasterIdentity`; downstream URL construction and string comparison must tolerate or normalize this.
- `SetMasterId()` constructs `hostname + std::to_string(port)` without a colon, unlike the constructor identity documentation. If this is user reachable, comparisons to `mIdentity` can be misleading.
- Master transitions call `std::abort()` on config or tape-GC start failures. That is defensible for consistency but high impact during failover.
- The supervisor depends on `mConfigLoaded`; if autoload is empty, `ApplyMasterConfig()` returns false and transition paths can abort. This may be intentional for QDB deployments but is a deployment-sensitive behavior.
- Many operations use global mutable state with lock ordering spread across subsystems. Deadlock risk is mitigated in `ApplyMasterConfig()` by `ConfigResetMonitor`, but transitions still touch request tracker, namespace services, messaging, access rules, and engines in sequence.
- `PostSlaveToMaster()` builds a shell command by concatenating quoted master ids. Values are expected MGM identities, but any future untrusted source would need stronger argument passing.

## Test signals
No direct unit tests for `QdbMaster` were found in the scanned tree. Useful validation signals are integration/failover tests with QuarkDB lease acquisition/loss, namespace boot failure injection, config autoload failure behavior, master-to-slave service shutdown, post-transition hook timeout/failure, and XRootD remote master ping handling. Because `SlaveToMaster()` starts `Recycle` and calls `Quota::LoadNodes()`, recycle/quota integration tests also indirectly exercise successful master transition prerequisites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/qdbmaster/QdbMaster.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/qdbmaster/QdbMaster.hh -->
# sources/distributed-fs/eos/mgm/qdbmaster/QdbMaster.hh

## Purpose
`QdbMaster.hh` declares the QuarkDB implementation of the MGM master interface. It exposes the `IMaster` operations needed by the rest of MGM while hiding lease acquisition, role transition, namespace cache management, and supervisor-thread details.

## Important APIs and types
- `class QdbMaster : public IMaster` is non-copyable and owns a `qclient::QClient` plus an `AssistedThread`.
- Public interface overrides include `Init`, `BootNamespace`, `ApplyMasterConfig`, `IsMaster`, `IsRemoteMasterOk`, `GetMasterId`, `SetMasterId`, `GetServiceDelay`, `GetLog`, and `PrintOut`.
- `sLeaseKey` is the static QuarkDB lease key shared by all MGM nodes in the election group.
- `POST_SLAVE_TO_MASTER_TIMEOUT` defines a 60 second cap for the optional post-transition script.
- Private transition helpers are `Supervisor`, `AcquireLease`, `AcquireLeaseWithDelay`, `ReleaseLease`, `GetLeaseHolder`, `SlaveToMaster`, `PostSlaveToMaster`, and `MasterToSlave`.
- Namespace caching helpers `DisableNsCaching`, `EnableNsCaching`, and timeout helper `ConfigureTimeouts` are private implementation details.

## Control flow and state model
The header shows an object with two identities: immutable local `mIdentity` and mutex-protected `mMasterIdentity`. `mIsMaster`, `mOneOff`, and `mConfigLoaded` control role and boot progress. `mAcquireDelay` deliberately pauses reacquisition after a manual master change request. `mLeaseValidity`, `mDoMasterDelay`, `mMasterDelayDeadline`, and static `sMasterDelaySec` shape lease renewal and post-promotion request admission.

`GetMasterId()` takes `mMutexId` and returns a copy, while `UpdateMasterId()` is private and uses the same mutex. `IsMaster()` is a simple atomic read. The class owns its supervisor thread and joins it in the destructor.

## Persistence behavior
The header itself does not define persistence, but its fields identify the persisted/remote source of truth as the QuarkDB lease key. Local role fields are process-local and rebuilt on restart by `Init()` and the supervisor. The config-loaded flag tracks whether MGM config was loaded during transitions, not whether it is durably stored.

## Dependencies and integration points
The declaration depends on `IMaster`, `AssistedThread`, and `QdbContactDetails`, with a forward declaration of `qclient::QClient`. Because public methods match `IMaster`, other MGM code can interact through the abstract master interface; the implementation still requires QDB contact details and a local host-port identity.

## Risks and test signals
The interface exposes very little direct configurability, so most testing must instantiate with a fake or test QuarkDB client only if the implementation is made injectable. Current ownership of `std::unique_ptr<qclient::QClient>` and private lease methods make isolated unit tests difficult. Race-focused tests should cover concurrent `GetMasterId()`, destructor thread join behavior, `IsMaster()` visibility, and acquire-delay semantics after `SetMasterId()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/qdbmaster/QdbMaster.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/quota/Quota.cc -->
# sources/distributed-fs/eos/mgm/quota/Quota.cc

## Purpose
`Quota.cc` implements EOS MGM quota state, namespace quota-node binding, quota printing, admin set/remove operations, quota checks for writes and placement, statfs-style quota reporting, and quota accounting repair hooks. It bridges namespace quota statistics (`IQuotaNode`) with MGM global configuration and scheduler placement.

## Important APIs and functions
- Static state: `Quota::pMapQuota` maps normalized quota paths to `SpaceQuota*`, `pMapInodeQuota` maps quota container ids to `SpaceQuota*`, `pMapMutex` protects both, and `gProjectId` defaults to gid `99`.
- `SpaceQuota::SpaceQuota(path, cont_id)` binds to an existing container id, obtains or registers an `IQuotaNode`, and computes a layout size factor. It intentionally does not create a namespace container.
- `SpaceQuota::GetQuota`, `SetQuota`, `RmQuota`, `ResetQuota`, and `AddQuota` manipulate `mMapIdQuota`, using a packed `tag:id` index.
- `UpdateLogicalSizeFactor()` reads path attributes and policy layout to translate raw/logical bytes through `LayoutId::GetSizeFactor`.
- `UpdateFromQuotaNode()`, `AccountNsToSpace()`, `UpdateIsSums()`, and `UpdateTargetSums()` import live namespace accounting into the in-memory map and maintain aggregate "all user/group" values.
- `CheckWriteQuota()` enforces user, group, and project volume/inode limits for a requested write.
- `PrintOut()` emits table or monitoring output for user/group/summary quota views.
- `Quota::CreateQuotaDir()` is the only namespace-container creation path and refuses to create on non-`ENOENT` errors to avoid shadow quota directories.
- `Quota::CreateQuotaObj()` creates the in-memory `SpaceQuota` for an existing quota node and indexes it by path and quota-node id.
- `LoadNodes()` discovers quota-node ids from namespace quota stats, resolves URIs, creates missing in-memory objects by container id, and refreshes them.
- `SetQuotaTypeForId()` creates/binds the quota node if needed, sets logical and raw volume quota values, and persists config engine entries.
- `RmQuotaTypeForId()`, `RmQuotaForId()`, `RmQuotaForTag()`, and `RmSpaceQuota()` remove quota values or nodes from memory, config, and namespace quota registration.
- `GetResponsibleSpaceQuota()` finds the longest quota path prefix for a data path; `Exists`, `ExistsResponsible`, `GetResponsibleSpaceQuotaPath`, `QuotaByPath`, and `QuotaBySpace` wrap lookup variants.
- `FilePlacement()` checks physical space membership, space quota enablement, `CheckWriteQuota`, nominal physical quota, and then delegates placement to `Scheduler::FilePlacement`.
- `MapSizeCB()` computes physical usage as file size times layout size factor and is registered during QDB namespace boot.
- `RemoveFile()` and `AddFile()` update namespace quota accounting by file id, used by conversion and repair flows.
- `RefreshFromNsQuota()` drops cached "is" values for an exact quota path and refreshes from namespace accounting.

## Control flow
Quota setup flows from admin commands or master promotion. Admin `quota set` calls `SetQuotaTypeForId()`, which normalizes the path, ensures the backing container exists via `CreateQuotaDir()`, ensures a `SpaceQuota` object exists via `CreateQuotaObj()`, computes the relevant user/group and volume/inode tag, updates in-memory quota values, and writes corresponding config entries. Master promotion calls `Quota::LoadNodes()`, which discovers existing namespace quota nodes and creates in-memory objects without creating containers.

Write-time enforcement enters through `Quota::Check()` or `Quota::FilePlacement()`. Both locate the longest matching quota node and call `SpaceQuota::CheckWriteQuota()`. That method refreshes current namespace usage for the uid/gid and optional project quota, detects which targets are configured, and requires all configured user+group constraints to pass. If neither user nor group quotas are configured, project quota can authorize the write. Root uid bypasses quota checks.

Reporting flows through `Quota::PrintOut()`: it first reloads nodes, locks FsView and quota maps, then either prints all quota nodes or the responsible node for a supplied path. `SpaceQuota::PrintOut()` collects unique ids under its own mutex, optionally resolves uid/gid names outside the lock, and formats user, group, and aggregate tables.

## State and persistence
In-memory quota state lives in `SpaceQuota::mMapIdQuota`, keyed by packed quota tag and uid/gid/project id. `mDirtyTarget` tracks whether aggregate target sums need recomputation. `mQuotaNode` points at namespace-owned quota accounting, and `mLayoutSizeFactor` caches layout-dependent raw/logical translation.

Persistent namespace state includes quota-node registration on containers and live quota accounting in the namespace services. Persistent config state is stored through `gOFS->mConfigEngine` under the `"quota"` section. `CreateQuotaDir()` synchronizes the QuarkDB metadata flusher after creating a new quota directory so the directory is durable before quota registration/config persistence proceeds.

## Dependencies and integration points
This file depends on MGM globals (`gOFS`), namespace services (`IView`, `IContainerMD`, `IFileMD`, `IQuotaNode`, QuarkDB namespace group/flusher), `FsView`, `Scheduler`, `Policy`, `LayoutId`, mapping utilities, table formatting, and XRootD strings/mutexes. It is called by admin/user quota commands, WebDAV quota reporting, MGM open/file placement paths, recycle policy statistics, LRU logic, namespace repair commands, and conversion/tape-related flows that adjust quota accounting.

## Risks and edge cases
- Locking is complex: namespace locks, quota map locks, `SpaceQuota::mMutex`, and FsView locks appear in multiple combinations. Changes need strict lock-order review.
- `GetResponsibleSpaceQuota()` scans all quota paths linearly and uses prefix matching; path normalization and trailing slash behavior are critical to avoid accidental broader matches.
- `LoadNodes()` contains a suspicious `first` flag path where `first` is initialized true and only set false inside `if (!first)`, so intended re-grabbing behavior may not execute as written. The loop still releases locks inside the first iteration, making this worth closer review.
- `RmSpaceQuota()` wraps a raw pointer from `pMapQuota` in `std::unique_ptr` while also erasing from maps. That transfers deletion responsibility locally; callers must not retain stale `SpaceQuota*` after map removal.
- `SetQuotaTypeForId()` stores both logical and raw volume values. The `EOS_MGM_QUOTA_SET_BY_LOGICAL` environment variable changes interpretation of the input value, so admin tooling and tests must fix expected semantics.
- Several methods assume a fully initialized global `gOFS` and namespace services, making isolated unit tests difficult and failure modes process-global.
- Project quota behavior uses a magic gid (`99`) and overloads group quota tags. Incorrect configuration can cause double counting or unexpected project-only authorization.

## Test signals
No focused `Quota` unit test was found in the scanned output. Useful test coverage would include quota directory creation refusing non-`ENOENT`, logical/raw quota conversion with and without `EOS_MGM_QUOTA_SET_BY_LOGICAL`, longest-prefix responsible quota selection, project quota aggregation, root bypass, user+group both-required behavior, `QuotaByPath`/`QuotaBySpace` free-space semantics when no quota is set, and `RefreshFromNsQuota()` clearing only "is" tags. Integration signals already exist through admin quota commands, file placement in `XrdMgmOfsFile.cc` and `proc/user/File.cc`, recycle quota statistics, and conversion accounting calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/quota/Quota.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/quota/Quota.hh -->
# sources/distributed-fs/eos/mgm/quota/Quota.hh

## Purpose
`Quota.hh` declares the MGM quota model. `SpaceQuota` represents one quota node and its in-memory counters/targets, while `Quota` provides static process-wide lookup, mutation, enforcement, reporting, placement, and accounting APIs.

## Important APIs and types
- `SpaceQuota` owns a display path, an `IQuotaNode*`, an `XrdSysMutex`, refresh timestamps, a layout size factor, dirty-target flag, and `mMapIdQuota`.
- `SpaceQuota::eQuotaTag` enumerates current, logical current, target, and aggregate quota counters for users and groups.
- `SpaceQuota::CheckWriteQuota()` is the key enforcement primitive for uid/gid plus requested bytes/inodes.
- `SpaceQuota::PrintOut()` formats a quota node for CLI/monitoring output.
- Private `SpaceQuota` helpers cover packed map indexing, quota get/set/reset/add/remove, namespace refresh, target/current sum recomputation, tag conversion, percentage/status rendering, enable checks, and quota-node pointer refresh.
- `Quota::IdT` distinguishes uid and gid quota operations; `Quota::Type` distinguishes volume, inode, and all operations.
- Public `Quota` APIs cover creating quota objects/directories, existence and responsible-node lookup, individual quota reporting, set/remove operations by id or tag, node removal, group statistics, namespace refresh, write checks, physical-size mapping, node loading/cleanup, printing, file placement, aggregate quota retrieval, quota lookup by path/inode, statfs data, add/remove file accounting, and forced namespace refresh.
- Static `Quota::pMapMutex` is public for cross-component locking, while maps are private.

## Control flow and state model
The header documents a deliberate split between container creation and quota-object creation. `CreateQuotaDir()` is the only API that may create a namespace directory and is reserved for explicit admin quota set operations. `CreateQuotaObj()` binds a `SpaceQuota` to an already existing namespace container id. This distinction prevents load/refresh paths from fabricating shadow quota directories after transient backend failures.

Most static APIs expect callers or implementations to normalize paths to trailing slash form. Responsible-node lookup is longest-prefix based, so quota enforcement can apply to subtrees without exact path matches. `FilePlacement()` is declared as scheduler-facing and requires the FsView lock. Several comments declare required lock ownership for refresh and quota-node address update paths.

## Persistence behavior
The header identifies two persistence layers: namespace quota nodes/containers and the config engine quota entries. `SpaceQuota` itself is an in-memory projection of namespace stats and configured targets. `pMapQuota` and `pMapInodeQuota` are rebuilt by `LoadNodes()` and destroyed by `CleanUp()`.

## Dependencies and integration points
The quota interface depends on scheduler placement types, common logging/layout/mapping/RWMutex utilities, namespace `IQuota`, XRootD strings, and Google dense hash headers. Integration points include MGM command processors for admin/user quota management, file placement/open code, WebDAV quota responses, recycle policy quota statistics, LRU/tape/conversion flows, and QDB namespace boot through `Quota::MapSizeCB` and `Quota::LoadNodes`.

## Risks and test signals
The API surface is mostly static and global, which simplifies call sites but makes dependency injection difficult. Public exposure of `pMapMutex` means external code can participate in locking, increasing lock-order risk. The comments around `CreateQuotaDir()` and constructor behavior are important invariants: tests should ensure non-admin load paths never create containers. Tag conversion helpers are private; behavior is validated indirectly through set/remove by id/tag and config entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/quota/Quota.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/recycle/Recycle.cc -->
# sources/distributed-fs/eos/mgm/recycle/Recycle.cc

## Purpose
`Recycle.cc` implements EOS MGM recycle-bin management: background retention cleanup, listing, restore, purge, configuration commands, recycle-project id setup, path demangling, and utility handling for symlink-like directory listings. It is a master-only subsystem started by `QdbMaster::SlaveToMaster()`.

## Important APIs and functions
- Static configuration/state: `gRecyclingPrefix` (`/recycle/` before MGM proc prefix adjustment), `gRecyclingAttribute` (`sys.recycle`), directory postfix `.d`, version key `sys.recycle.version.key`, project recycle-id key `sys.forced.recycleid`, root identity `mRootVid`, and `mLastRemoveTs`.
- Local helper `AllHierarchyHasXattr()` verifies every directory in a subtree has a given xattr/value, excluding version directories via `_find` options.
- `CollectEntries()` periodically scans the recycle prefix, selects old date shards and empty upper directories based on `GetCutOffDate()`, and populates `mPendingDeletions` by container id/path.
- `RemoveEntries()` spreads deletion across remove intervals using `cid % total_slots`, honors dry-run, and stops early if quota watermarks are back within limits.
- `RemoveSubtree()` recursively finds and permanently deletes files and directories under a recycle subtree, deepest first, with guards against deleting `/` or paths outside the recycle prefix.
- `GetCutOffDate()` computes a date string from the current clock minus keep time minus one extra day.
- `Recycler()` is the assisted background thread: waits for namespace boot, applies recycle config, sleeps on config update or timeout, checks master/enabled state, refreshes ratio watermarks, and runs collection/removal when keep-time is configured and watermarks require cleanup.
- `Print()` lists recycle contents or summary quota data. It supports all/admin listing, per-user listing, recycle-id listing, project-path filtering, date filtering, monitoring output, optional details, max entries, id translation, and dtrace display.
- `IsAllowedToRestore()` allows user recycle restores only for the owning uid and otherwise checks parent directory ACL read permission.
- `GetPathFromRestoreKey()` resolves `fxid:<hex>` or `pxid:<hex>` keys to file/container paths and verifies the object is under the recycle prefix.
- `DemanglePath()` converts flattened `#:#` names plus `.hexid`/`.d` suffix back to original paths.
- `Restore()` resolves a recycle key, checks permissions, reconstructs original path, optionally creates missing parents, handles conflicts by renaming existing targets when forced, renames the recycled object back, and optionally restores versions through the stored version key.
- `Purge()` permanently deletes one recycle key or a dated subtree, restricted to root/sudo/admin roles.
- `Config()` handles root-only recycle commands for adding/removing recycle xattrs, lifetime, ratio, collect/remove intervals, dry-run, enforce, and enable flags. It delegates policy storage to `RecyclePolicy::Config()` and wakes the recycler.
- `RecycleIdSetup()` creates a project recycle directory, applies optional ACLs, and propagates `sys.forced.recycleid` recursively across a project subtree with verification retries.
- `HandlePotentialSymlink()` strips `" -> target"` suffixes only when the full displayed name does not stat, allowing recycle operations to target symlink entries.

## Control flow
The background recycler starts via `Start()` in the header and enters `Recycler()`. After namespace boot and initial config application, it sleeps until a config update or calculated timeout. Only the master runs cleanup. When enabled, ratio configuration first refreshes watermarks from quota statistics. If keep time is nonzero and current usage is not within ratio limits, the thread collects candidates and removes a bounded slot of them.

Interactive flows use static methods. Listing builds a `printmap` of `uid:<id>` or `rid:<id>` top-level directories based on caller privileges and arguments, then either walks detailed entries to reconstruct restore metadata or prints recycle quota summary from `Quota::GetGroupStatistics()`. Restore and purge both first resolve safe recycle paths, reject paths outside the recycle prefix, and then delegate to MGM filesystem operations using `mRootVid`.

Project setup starts from a real namespace container, rejects proc hierarchy paths, chooses an existing or container-id-based recycle id, creates `/recycle/rid:<id>`, applies ACLs through `AclCmd`, recursively sets the xattr, and verifies propagation with repeated `_find` scans.

## State and persistence
Recycle entries are persisted as renamed namespace objects under the recycle prefix with path layout `<prefix>/<uid:...|rid:...>/<year>/<month>/<day>/<shard>/<mangled-original>.<16hex>[.d]`. Directory entries use `.d`. The recycle path itself is returned through `XrdOucErrInfo` by `RecycleEntry::ToGarbage`.

Policy state is persisted through `RecyclePolicy::StoreConfig()` in FsView global config. Recycle configuration by subtree uses recursive xattrs with key `sys.recycle`; recycle projects use `sys.forced.recycleid`. Version restoration links use `sys.recycle.version.key`. Cleanup candidate state `mPendingDeletions` is in-memory only and recomputed by collection.

## Dependencies and integration points
The file depends on `XrdMgmOfs` filesystem operations, `FsView`, ACL parsing/commands, quota statistics, QDB master role checks, MGM proc commands, namespace prefetchers, container iterators, common path/string utilities, and `BackOffInvoker`. Callers include `proc/user/RecycleCmd.cc` and gRPC namespace recycle methods. `proc/user/Rm.cc` and `RmCmd.cc` use `RecycleEntry::ToGarbage()` for moving deleted objects into the structure this file manages.

## Risks and edge cases
- Destructive cleanup uses root identity and recursive deletion. The prefix guard in `RemoveSubtree()` is critical; any change to prefix normalization must preserve it.
- `Print()` summary divides by quota maximums without local zero guards in the formatting branch; empty or zero quota maps need careful handling.
- `GetPathFromRestoreKey()` declares an outer `fmd` but shadows it with `auto fmd` inside the file lookup block, so the later `if (!force_file && !fmd)` tests the still-null outer pointer. That means container lookup is attempted even after file lookup succeeded unless `force_file` is true; normally the already-filled `recycle_path` still saves behavior, but this is a concrete code smell.
- Date filters only validate digits and `/`, not semantic date shape. This avoids injection but may still produce broad or empty scans.
- Cleanup scheduling by `cid % total_slots` spreads load but can leave items pending if collection/removal intervals are misconfigured or ids cluster.
- `RecycleIdSetup()` retries xattr propagation but concurrent namespace mutations can still race with verification.
- Restore conflict handling renames existing targets with their inode suffix; failure leaves the recycled object untouched but may already have created parent paths.

## Test signals
`sources/distributed-fs/eos/unit_tests/mgm/RecycleTests.cc` covers `GetCutOffDate()` with a fake clock and `DemanglePath()` for invalid paths and encoded file names. More coverage is warranted for restore-key resolution, forced restore conflict behavior, purge permission checks, project recycle-id propagation, symlink display handling, and recycler cleanup slot/watermark behavior. Integration signals include user recycle commands, gRPC recycle methods, and rm command paths that send objects to garbage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/recycle/Recycle.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/recycle/Recycle.hh -->
# sources/distributed-fs/eos/mgm/recycle/Recycle.hh

## Purpose
`Recycle.hh` declares the recycle-bin subsystem interface and its background cleanup object. It exposes static command-style operations for configuration, listing, restoring, purging, project setup, restore-key lookup, and path demangling, plus instance methods for running the recycler thread and reading policy state.

## Important APIs and types
- `Recycle::RecycleListing` is a vector of string maps used by listing callers needing structured results.
- Static strings define recycle namespace layout and xattr keys: prefix, recycle attribute, directory postfix, version key, recycle-id xattr key.
- `Config()`, `RecycleIdSetup()`, `Print()`, `Restore()`, `GetPathFromRestoreKey()`, `DemanglePath()`, and `Purge()` are the command-facing static API.
- `InRecycleBin()` and `IsTopRecycleBin()` are lightweight path predicates.
- Constructor accepts `fake_clock` for testable time behavior; destructor calls `Stop()`.
- `Start()` and `Stop()` manage an `AssistedThread` running `Recycler()`.
- `NotifyConfigUpdate()`, `GetCollectInterval()`, `Dump()`, `IsEnforced()`, and `IsEnabled()` expose policy/runtime state.
- Private helpers include restore authorization, subtree removal, symlink handling, candidate collection/removal, and cutoff-date calculation.

## Control flow and state model
The header shows a hybrid design: most user operations are static and operate through MGM globals, while one `Recycle` instance owns the background thread, `RecyclePolicy`, pending deletion map, fakeable clock, and config-update condition variable. `Stop()` notifies the condition variable before joining, which prevents shutdown from waiting for a long remove interval.

`mPendingDeletions` maps container ids to full paths, allowing removal to be distributed by id. `mPolicy` stores atomics for enable/enforce/keep/ratio/dry-run/interval/watermark settings. Test harness builds can access internals through the `IN_TEST_HARNESS` public section.

## Persistence behavior
The header identifies persistence via namespace xattrs and recycle directory paths rather than an external database. The instance state is transient; on restart, pending deletions are discovered again by scanning the recycle tree. Policy persistence is delegated to `RecyclePolicy`.

## Dependencies and integration points
The declaration depends on `Namespace.hh`, `RecyclePolicy`, `AssistedThread`, `SystemClock`, generated `Recycle.pb.h`, XRootD strings, and virtual identity types. It is integrated with MGM master lifecycle, user/gRPC recycle commands, rm command recycling, quota policy, ACLs, and namespace filesystem operations.

## Risks and test signals
The static API makes permission and prefix validation central: callers can invoke powerful restore/purge/config operations without constructing a `Recycle` object. Unit tests already use `fake_clock` and `IN_TEST_HARNESS` for cutoff-date and demangle behavior. Further tests should target `Stop()` wakeup, `IsTopRecycleBin()` trailing slash normalization, `InRecycleBin()` prefix pitfalls, and config update notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/recycle/Recycle.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/recycle/RecycleEntry.cc -->
# sources/distributed-fs/eos/mgm/recycle/RecycleEntry.cc

## Purpose
`RecycleEntry.cc` implements the object-level move-to-recycle operation used when a file or directory tree is deleted but should be recoverable. It computes the dated recycle-bin shard, creates it if necessary, fixes ownership, mangles the original path into a flat name, and renames the namespace object into the recycle area.

## Important APIs and functions
- Static `sMaxEntriesPerDir` limits one shard directory to 100000 entries before advancing the shard index.
- Static `mRootVid` is used for unrestricted MGM filesystem operations.
- The constructor stores original path, top recycle directory, owner ids, object id, and builds `mRecycleId` as `uid:<owner>` for user recycling or `rid:<rid>` for project recycling. It strips a trailing slash from `mRecycleDir`.
- `GetRecyclePrefix()` builds `<recycle-dir>/<uid|rid>/<YYYY>/<MM>/<DD>/<index>`, reuses an existing shard if not over the entry limit, otherwise creates it with root privileges and changes ownership to the original owner.
- `ToGarbage()` detects directory-tree recycling by a trailing slash, replaces every `/` in the original path with `#:#`, appends the 16-hex namespace id and `.d` for directories, then calls `_rename()` into the computed recycle prefix.

## Control flow
Deletion code constructs `RecycleEntry` with the path, recycle directory, optional project id, virtual identity pointer, owner uid/gid, and file/container id. `ToGarbage()` normalizes directory paths, computes a reusable or new dated shard via `GetRecyclePrefix()`, constructs the final recycle path, and performs one namespace rename. On success, it stores the recycle path in the error object as informational output.

## State and persistence
This file persists recycle state by moving the object in the namespace. No separate metadata record is written here; the encoded file name contains the original path and object id, and the directory layout contains owner/project and deletion date. Ownership of shard directories is updated to the deleted object's original owner/group.

## Dependencies and integration points
It depends on `Recycle.hh` for postfix constants, `XrdMgmOfs` for `_stat`, `_mkdir`, `_chown`, and `_rename`, `VirtualIdentity::Root()`, and XRootD error handling. Callers found in `proc/user/Rm.cc` and `proc/user/RmCmd.cc` invoke `ToGarbage()` for recursive removals.

## Risks and edge cases
- `GetRecyclePrefix()` checks `buf.st_blksize > sMaxEntriesPerDir` to decide shard fullness. `st_blksize` is normally filesystem block size, not entry count; if EOS overloads this value in `_stat`, that should be documented, otherwise sharding may not work as intended.
- Path mangling is reversible only because restore strips the final `.16hex` and optional `.d`; original names containing `#:#` sequences can be ambiguous after demangling.
- The constructor accepts but does not use the `VirtualIdentity* vid` parameter.
- All work uses root identity; safety relies on caller authorization and destination prefix correctness.
- A rename failure leaves the original object in place and returns an MGM error; a prefix creation/chown failure may leave empty directories behind.

## Test signals
No direct `RecycleEntry` tests were found. Existing recycle demangle tests cover the reverse name format partially. Valuable tests would include file versus directory postfix construction, project versus user recycle id construction, shard rollover behavior, ownership update failure, and rename error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/recycle/RecycleEntry.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/recycle/RecycleEntry.hh -->
# sources/distributed-fs/eos/mgm/recycle/RecycleEntry.hh

## Purpose
`RecycleEntry.hh` declares a small value/operation class that models a single file or directory-tree entry being moved into the recycle bin.

## Important APIs and types
- `RecycleEntry(path, recycle_dir, rid, vid, owner_uid, owner_gid, id)` captures all data needed to recycle one namespace object. Empty `rid` means user-based recycling; non-empty `rid` means project recycling.
- `ToGarbage(epname, error)` is the public operation that moves the object into the recycle bin and reports MGM-style status.
- Private static `sMaxEntriesPerDir` controls recycle shard sizing.
- Private fields store source path, top recycle directory, recycle id string, original owner uid/gid, namespace object id, and static root identity.
- Private `GetRecyclePrefix()` computes or creates the dated shard directory.

## Control flow and state model
The class is designed for short-lived use: construct from deletion context, call `ToGarbage()`, then discard. It does not own namespace metadata directly; it delegates all side effects to the implementation through `gOFS` operations. The source path may be modified during directory recycling to remove the trailing slash.

## Persistence behavior
Persistent effects are the namespace rename into the recycle tree and creation/ownership update of recycle shard directories. The object id and original path are encoded into the destination name, while owner/project/date are encoded into directories.

## Dependencies and integration points
The declaration depends on MGM namespace definitions, `XrdOucErrInfo`, string/string_view, uid/gid types, and `VirtualIdentity`. It is consumed by user rm command implementations and pairs with `Recycle::DemanglePath()`/`Restore()` for recovery.

## Risks and test signals
The API exposes only one operation but takes several loosely typed strings and numeric ids, so caller correctness is important. The unused `vid` constructor parameter in the implementation suggests either an incomplete feature or stale signature. Tests should validate path encoding contracts against `Recycle::DemanglePath()` and ensure project recycle id behavior matches `RecycleIdSetup()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/recycle/RecycleEntry.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/recycle/RecyclePolicy.cc -->
# sources/distributed-fs/eos/mgm/recycle/RecyclePolicy.cc

## Purpose
`RecyclePolicy.cc` implements the persistent runtime policy for recycle-bin cleanup. It parses/stores recycle config, exposes formatted dumps, obtains recycle quota statistics, computes low watermarks, and decides whether cleanup can stop because usage has dropped below configured limits.

## Important APIs and functions
- `ApplyConfig(FsView*)` reads the `"recycle"` global config string, tokenizes space-separated `key=value` pairs, tolerates missing values as empty strings, and applies each with `Config()`.
- `StoreConfig()` serializes enable/enforce/keep-time/ratio/collect/remove/dry-run fields back to `FsView::gFsView.SetGlobalConfig("recycle", ...)`.
- `Config(key, value, msg)` parses and applies one key. Supported keys are `recycle-keep-time`, `recycle-ratio`, `recycle-collect-time`, `recycle-remove-time`, `recycle-dry-run`, `recycle-enforce`, and `recycle-enable`; unknown keys are ignored.
- `Dump(delim)` reports current atomic state and watermarks.
- `GetQuotaStats()` returns group/project quota values for `Recycle::gRecyclingPrefix` and `Quota::gProjectId`.
- `RefreshWatermarks()` reads used/max logical bytes and files, skips updates while below the configured ratio, otherwise sets low watermarks to `(ratio - 0.1) * max`.
- `IsWithinLimits()` checks current recycle quota stats against low watermarks and returns true once either inode or space usage is below its low watermark; with no ratio or no stats, it returns false so time-based cleanup may continue.

## Control flow
On recycler startup, `Recycle::Recycler()` calls `ApplyConfig()` to populate atomics from stored FsView config. User config commands call `RecyclePolicy::Config()` through `Recycle::Config()`, which updates a value, logs a dump, and immediately stores the full config string. During cleanup, `RefreshWatermarks()` is called before collection/removal when a ratio is configured; `RemoveEntries()` periodically calls `IsWithinLimits()` and stops deleting when usage is low enough.

## State and persistence
Runtime state is stored in atomics: enabled, enforced, keep time, space keep ratio, dry-run, collect interval, remove interval, low-space watermark, and low-inode watermark. Persistent state is the serialized global `"recycle"` config in FsView. Quota usage is external state read from the quota subsystem.

## Dependencies and integration points
The policy depends on `Recycle` constants, `Quota::GetGroupStatistics`, `SpaceQuota` tag values, `XrdMgmOfs`, `FsView`, and common tokenization/logging. It is owned by the `Recycle` instance and is tested with a mock subclass overriding `GetQuotaStats()` and `StoreConfig()`.

## Risks and edge cases
- `Config()` returns true on empty values before key validation. This is useful for tolerant parsing but can hide malformed config entries.
- Numeric parsing catches all exceptions and returns clear messages, but range checks are mostly performed by `Recycle::Config()`, not here. Direct callers of `RecyclePolicy::Config()` can set unusual intervals or ratios.
- `RefreshWatermarks()` uses `999999999` as a denominator fallback for zero max values; this avoids division by zero but can produce surprising ratio behavior for zero-quota configurations.
- `IsWithinLimits()` returns true if either inode or space watermark is under-run, not necessarily both. This matches the implementation but should be intentional for cleanup stop policy.
- Unknown keys are silently ignored, which helps compatibility but can hide operator typos in raw config.

## Test signals
`sources/distributed-fs/eos/unit_tests/mgm/RecyclePolicyTests.cc` covers no-limit behavior, above/below watermark transitions, valid config parsing, invalid numeric parsing, dry-run toggles, and explicit enforce disable. Additional tests should cover enable key validation, unknown key behavior, empty-value behavior, zero max quota stats, and direct ratio range assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/recycle/RecyclePolicy.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/recycle/RecyclePolicy.hh -->
# sources/distributed-fs/eos/mgm/recycle/RecyclePolicy.hh

## Purpose
`RecyclePolicy.hh` declares the cleanup policy object used by `Recycle`. It defines supported config keys, runtime atomic settings, quota-stat hooks, and policy methods for applying, storing, dumping, and evaluating cleanup thresholds.

## Important APIs and types
- `RecyclePolicy` derives from `eos::common::LogId` and declares `Recycle` as a friend so the recycler can access policy internals.
- Public methods are `ApplyConfig(FsView*)`, virtual `StoreConfig()`, `Config(key, value, msg)`, `RefreshWatermarks()`, `IsWithinLimits()`, virtual `GetQuotaStats()`, and `Dump(delim)`.
- Static key constants define the serialized config contract: keep time, ratio, collect time, remove time, dry-run, enforce, and enable.
- Runtime atomics include `mEnabled`, `mEnforced`, `mKeepTimeSec`, `mSpaceKeepRatio`, `mDryRun`, `mCollectInterval`, `mRemoveInterval`, `mLowSpaceWatermark`, and `mLowInodeWatermark`.
- `IN_TEST_HARNESS` can expose internals publicly for unit tests.

## Control flow and state model
The class is intentionally small and mostly atomic so the recycler thread and config commands can share policy state with minimal locking. `StoreConfig()` and `GetQuotaStats()` are virtual, which enables the existing tests to mock persistence and quota input while exercising parsing and watermark logic.

## Persistence behavior
Persistence is abstracted behind `StoreConfig()` but implemented in the `.cc` file as FsView global config. The header makes the serialized keys stable public constants, so command handlers and tests can refer to the same strings.

## Dependencies and integration points
The declaration depends on MGM namespace definitions, common logging/mapping, namespace `IView`, and atomics. It forward declares `FsView`. It is owned by `Recycle`, called by recycle command handling, and uses quota statistics keyed by `SpaceQuota` tags in the implementation.

## Risks and test signals
Using `std::atomic<double>` for ratio state is straightforward but still requires platform support assumptions. Interval atomics use `std::chrono::seconds`, so any code compiling this header depends on atomic support for that trivially copyable representation. The public key constants and virtual hooks are good test seams; existing `RecyclePolicyTests` already mock the two virtual methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/recycle/RecyclePolicy.hh -->
