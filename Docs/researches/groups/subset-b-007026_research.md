# subset-b-007026 Research

Work item: `subset-b-007026`

Scope: EOS MGM filesystem balancer, bulk-request domain/persistence/prepare/query code, FSctl command mapping, and abstract MGM config application.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/balancer/FsBalancer.cc -->
## sources/distributed-fs/eos/mgm/balancer/FsBalancer.cc

Purpose: implements the runtime loop for per-space filesystem balancing. `ConfigUpdate()` reads space configuration from `FsView::gFsView.mSpaceView`, enables/disables balancing, and refreshes thresholds, per-node transfer limits, queue size, thread pool size, and stats interval. `Balance()` is the assisted background thread: it waits for namespace boot, only runs on the master MGM, refreshes `FsBalancerStats`, rotates through unbalanced groups from a random start point, chooses source/destination pairs, and dispatches `DrainTransferJob` tasks on `mThreadPool`.

Important flow: `GetFileToBalance()` samples up to ten random files from the source filesystem, claims each file ID in `gOFS->mFidTracker`, prefetches metadata, excludes existing/unlinked locations as destinations, then chooses a destination with an available node slot. `TakeTxSlot()` and `FreeTxSlot()` update node slot counters, destination filesystem balance-transfer counters, running job count, and file-ID tracking.

State and dependencies: global `gOFS`, `FsView`, `IMaster`, namespace services, `Prefetcher`, `DrainTransferJob`, and `BackOffInvoker`. Risks include reliance on global master state during async task execution, destination selection fairness tied to set order and fid parity, and cleanup waiting on both queue size and `mRunningJobs`. Test signals should cover disabled/slave behavior, malformed config values, slot accounting, fid tracker removal on failures, and destination avoidance for existing replicas.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/balancer/FsBalancer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/balancer/FsBalancer.hh -->
## sources/distributed-fs/eos/mgm/balancer/FsBalancer.hh

Purpose: declares `FsBalancer`, the per-space manager that owns a background assisted thread and a transfer thread pool for balancing files between filesystems inside groups. Construction seeds default config (`threshold=10`, two transfers per node, 25 MB/s rate value, 60-second stats interval, 1000 queued jobs, max 100 worker threads) and starts `Balance()`. Destruction calls `Stop()`.

Important APIs: `Stop()`, `SetMaxThreadPoolSize()`, `GetThreadPoolInfo()`, `SignalConfigUpdate()`, `Balance()`, `TakeTxSlot()`, and `FreeTxSlot()`. Private helpers include `ConfigUpdate()`, `GetFileToBalance()`, and templated `GetRandomIter()`, which returns an iterator at a random one-based index.

State behavior: `mDoConfigUpdate` is atomic; `mRunningJobs` is atomic; most other fields are mutated by the balancer thread and task callbacks. `mBalanceStats` owns group and node-transfer caches. Integration is with `FsBalancerStats`, EOS metadata IDs, `common::ThreadPool`, and `AssistedThread`. Risks include thread start in constructor, join in destructor, no explicit restart API, and exposed internals under `IN_TEST_HARNESS`. Tests should validate random iterator bounds, config-update signaling, thread-pool resizing, and that slot accounting stays balanced under asynchronous completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/balancer/FsBalancer.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/balancer/FsBalancerStats.cc -->
## sources/distributed-fs/eos/mgm/balancer/FsBalancerStats.cc

Purpose: implements cached balancer statistics used by `FsBalancer` to decide which groups and filesystems are transfer endpoints. `UpdateInfo()` asks `FsView` for groups whose deviation exceeds the configured threshold, compares them against `mGrpToMaxDev`, refreshes group priority sets when deviation changes enough or ten minutes have elapsed, and removes groups that are no longer unbalanced.

Important APIs: `NeedsUpdate()` rate-limits refreshes by `mLastTs`; `GetTxEndpoints()` extracts source and destination sets, preferring `mPrioHigh` to `mHigh` and `mPrioLow` to `mLow`; `HasTxSlot()`, `TakeTxSlot()`, and `FreeTxSlot()` maintain per-node in-flight transfer counts behind `mMutex`.

State and persistence: there is no persistent storage; all state is in-memory caches derived from `FsView`. Dependency signals are `FsView::GetUnbalancedGroups()` and `FsView::GetFsToBalance()`. Risks include mixing `system_clock` for update intervals with `steady_clock` for group refresh age, stale priority sets until update thresholds trigger, and node slot entries staying present at zero. Test signals should cover group add/update/remove, priority fallback, refresh interval boundaries, mutex-protected slot increments/decrements, and missing node IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/balancer/FsBalancerStats.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/balancer/FsBalancerStats.hh -->
## sources/distributed-fs/eos/mgm/balancer/FsBalancerStats.hh

Purpose: declares the balancer statistics cache. It defines `BalancePair` and `VectBalanceFs`, then exposes `FsBalancerStats` as a `LogId`-derived helper for group deviation caching and node transfer slot accounting.

Important APIs/types: constructor binds a space name and initializes `mLastTs`; `UpdateInfo(FsView*, double)`, `NeedsUpdate(seconds)`, `GetTxEndpoints()`, `TakeTxSlot()`, `FreeTxSlot()`, and `HasTxSlot()`. The class stores `mGrpToMaxDev` as group to `(deviation, steady_clock timestamp)`, `mGrpToPrioritySets` as group to `FsPrioritySets`, and `mNodeNumTx` as node identifier to active transfer count.

Integration: depends on `mgm/fsview/FsView.hh` for `FsBalanceInfo` and priority sets, and is consumed by `FsBalancer`. Constants `sGrpDevUpdThreshold=0.25` and `sGrpUpdTimeThreshold=10` minutes define cache refresh sensitivity. Risks include coarse refresh constants and private state becoming public under `IN_TEST_HARNESS`. Tests should construct synthetic `FsView` results or harness-access maps to verify endpoint ordering, cache invalidation, and slot-limit behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/balancer/FsBalancerStats.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/BulkRequest.cc -->
## sources/distributed-fs/eos/mgm/bulk-request/BulkRequest.cc

Purpose: provides the static `BulkRequest::BULK_REQ_TYPE_TO_STRING_MAP`, mapping `PREPARE_STAGE`, `PREPARE_EVICT`, and `PREPARE_CANCEL` to stable string names. This backs `BulkRequest::bulkRequestTypeToString()` in the header.

Important behavior: there is no runtime control flow beyond static initialization. The map is used in logging, persistence error messages, and business-layer switch diagnostics. State is process-local and immutable after initialization.

Dependencies are limited to `BulkRequest.hh` and `<map>`. Risks are mostly enum drift: adding a new `BulkRequest::Type` without updating this map can make `bulkRequestTypeToString()` throw `std::out_of_range` in logging/error paths. Test signals should cover every enum value, unsupported/default behavior where relevant, and business-layer persistence for each type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/BulkRequest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/BulkRequest.hh -->
## sources/distributed-fs/eos/mgm/bulk-request/BulkRequest.hh

Purpose: declares the abstract bulk-request domain object. `BulkRequest` holds a unique request ID and a `FileCollection` of paths/errors; subclasses implement `getType()`.

Important APIs/types: `enum Type { PREPARE_STAGE, PREPARE_EVICT, PREPARE_CANCEL }`, `getId()`, pure virtual `getType()`, `getFiles()`, `getFilesMap()`, virtual `addFile(unique_ptr<File>&&)`, `bulkRequestTypeToString()`, and `getAllFilesInError()`. It exposes collection snapshots as shared pointers to containers of raw `File*` or the underlying multimap.

State and integration: owns `mId` and `mFileCollection`; used by factories, prepare manager, business layer, and DAO implementations. Risks include shallow-copy behavior inherited from `FileCollection`, raw pointers in returned vectors that depend on collection lifetime, and `bulkRequestTypeToString()` throwing if the enum map is incomplete. Test signals should verify insertion order, duplicate path handling, file-error filtering, subclass type dispatch, and lifetime assumptions around `getFiles()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/BulkRequest.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/BulkRequestFactory.cc -->
## sources/distributed-fs/eos/mgm/bulk-request/BulkRequestFactory.cc

Purpose: implements convenience constructors for supported bulk-request types. Stage creation either generates a time-based UUID via `BulkRequestHelper` or uses a supplied request ID and optional creation time. Cancel creation wraps the supplied ID in `CancellationBulkRequest`.

Important APIs: `createStageBulkRequest(issuerVid)`, `createStageBulkRequest(requestId, issuerVid)`, `createStageBulkRequest(requestId, issuerVid, creationTime)`, and `createCancelBulkRequest(id)`.

State and dependencies: no persistent state; depends on `StageBulkRequest`, `CancellationBulkRequest`, and `BulkRequestHelper`. Integration points include `BulkRequestPrepareManager` for new stage/cancel requests and `ProcDirectoryBulkRequestDAO` for reconstructing persisted stage requests. Risks are no factory path for `EvictBulkRequest` despite the enum/class existing, and generated IDs relying on `StringConversion::timebased_uuidstring()`. Tests should validate ID propagation, creation-time preservation, issuer identity preservation, and cancel ID matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/BulkRequestFactory.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/BulkRequestFactory.hh -->
## sources/distributed-fs/eos/mgm/bulk-request/BulkRequestFactory.hh

Purpose: declares `BulkRequestFactory`, a static factory for domain request objects. It includes stage, evict, and cancellation request headers, but only declares stage and cancellation creation methods.

Important APIs: overloads for creating stage requests with generated or explicit IDs and explicit creation time, plus `createCancelBulkRequest()`.

Integration: used by prepare-manager hooks and proc DAO reconstruction. State is absent; ownership is via `std::unique_ptr`. Risks include the included-but-not-produced `EvictBulkRequest`, which can confuse callers expecting a complete factory for all enum types. Test signals should compile-check all overloads, verify return dynamic types, and confirm ownership transfer semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/BulkRequestFactory.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/BulkRequestHelper.hh -->
## sources/distributed-fs/eos/mgm/bulk-request/BulkRequestHelper.hh

Purpose: declares a small helper for bulk-request IDs. `generateBulkRequestId()` delegates to `common::StringConversion::timebased_uuidstring()`.

Control flow/state: header-only, stateless, and synchronous. It exists to centralize ID generation for `BulkRequestFactory`.

Dependencies: `mgm/Namespace.hh` and `common/StringConversion.hh`. Risks include ID uniqueness and clock/source behavior being entirely delegated, and tests needing deterministic seams if they assert exact IDs. Test signals should assert non-empty unique-looking values and factory propagation, rather than exact string contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/BulkRequestHelper.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/File.hh -->
## sources/distributed-fs/eos/mgm/bulk-request/File.hh

Purpose: declares the per-file domain value stored inside bulk requests. A `File` carries a path and optional error text.

Important APIs: default/path constructors, `setPath()`, `setError(string)`, `setError(optional<string>)`, `setErrorIfNotAlreadySet()`, `getPath()`, `getError()`, equality by path, and strict ordering by path. Empty string errors are ignored by the string overload.

State/integration: used by `FileCollection`, prepare validation, DAO serialization, query response error accumulation, and proc reconstruction. Risks include path-only identity meaning duplicate failed/success records for the same path compare equal in sets, errors not affecting ordering/equality, and getters returning copies. Tests should cover empty-error handling, first-error preservation, path ordering, and behavior when collected into `std::set<File>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/File.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/FileCollection.hh -->
## sources/distributed-fs/eos/mgm/bulk-request/FileCollection.hh

Purpose: stores bulk-request files in a `multimap<path, unique_ptr<File>>` while preserving insertion order in a parallel vector of iterators. This supports duplicate paths and stable client-visible ordering.

Important APIs/types: `Files` (`vector<File*>`), `FilesMap`, `FilesInsertOrder`, `addFile()`, `getAllFiles()`, `getFilesMap()`, and `getAllFilesInError()`.

State behavior: constructor initializes shared containers; assignment copies the shared `mFiles` pointer but does not copy `mFilesInsertOrder`, which is a notable shallow-copy hazard. `getAllFiles()` materializes raw pointers in insertion order; `getFilesMap()` exposes the shared mutable map; `getAllFilesInError()` returns a set ordered by path, losing duplicate path entries. Tests should cover duplicate insertion order, error extraction, assignment behavior, and lifetime of raw `File*` snapshots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/FileCollection.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/business/BulkRequestBusiness.cc -->
## sources/distributed-fs/eos/mgm/bulk-request/business/BulkRequestBusiness.cc

Purpose: implements the business facade over bulk-request persistence. It logs/times operations and delegates to DAO instances produced by an injected `AbstractDAOFactory`.

Important flow: `saveBulkRequest()` switches on `req->getType()`: stage requests are cast to `StageBulkRequest`, cancellation requests to `CancellationBulkRequest`, and other types throw `PersistencyException`. `getBulkRequest()` retrieves by ID/type and logs hit/miss. `getStageBulkRequest()` retrieves `PREPARE_STAGE`, then releases and static-casts the base pointer to `StageBulkRequest`. `exists()` and `deleteBulkRequest()` pass through.

State/dependencies: owns `mDaoFactory`; each method calls `getBulkRequestDAO()`, potentially creating fresh DAO objects. Depends on logging/stat timing and `PersistencyException`. Risks include unchecked `static_cast`, unsupported evict persistence, repeated DAO construction, and exception behavior in logging paths if type strings are incomplete. Tests should mock the factory/DAO to verify dispatch, exception propagation, null retrieval, and stage downcast assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/business/BulkRequestBusiness.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/business/BulkRequestBusiness.hh -->
## sources/distributed-fs/eos/mgm/bulk-request/business/BulkRequestBusiness.hh

Purpose: declares the storage-agnostic business layer for bulk requests. It receives an `AbstractDAOFactory` and exposes save, fetch, exists, and delete operations to callers such as prepare managers or REST business code.

Important APIs: constructor taking `unique_ptr<AbstractDAOFactory>`, `saveBulkRequest(const BulkRequest*)`, `getBulkRequest(id,type)`, `getStageBulkRequest(id)`, `exists(id,type)`, and `deleteBulkRequest(req)`.

State/integration: owns the factory exclusively and returns `unique_ptr` request objects. It is the integration boundary between domain objects and DAO implementations. Risks include limited type support delegated to the `.cc`, no null request guard in the interface, and tight ownership of factory preventing copy/reuse. Tests should use a fake DAO factory to assert calls and errors without touching proc directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/business/BulkRequestBusiness.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/dao/IBulkRequestDAO.hh -->
## sources/distributed-fs/eos/mgm/bulk-request/dao/IBulkRequestDAO.hh

Purpose: defines the persistence contract for bulk requests. Implementations must save stage and cancellation requests, fetch by ID/type, expire inactive requests, check existence, and delete a request.

Important APIs: overloaded `saveBulkRequest()` for `CancellationBulkRequest` and `StageBulkRequest`, `getBulkRequest(id,type)`, `deleteBulkRequestNotQueriedFor(type, seconds)`, `exists(id,type)`, `deleteBulkRequest(req)`, and virtual destructor.

State/integration: no state; consumed by `BulkRequestBusiness`, `BulkRequestProcCleaner`, and DAO factories. The type-specific save overloads encode current persistence support and exclude evict saves. Risks include new request types requiring interface changes, cancellation semantics being implementation-defined, and no explicit transaction/atomicity contract. Tests should validate each implementation against empty requests, missing IDs, expiry age, and deletion idempotency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/dao/IBulkRequestDAO.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/dao/factories/AbstractDAOFactory.hh -->
## sources/distributed-fs/eos/mgm/bulk-request/dao/factories/AbstractDAOFactory.hh

Purpose: declares the abstract factory for persistence-layer DAOs. It currently has a single product: `getBulkRequestDAO()`.

Important API: `virtual std::unique_ptr<IBulkRequestDAO> getBulkRequestDAO() const = 0` plus virtual destructor.

State/integration: allows `BulkRequestBusiness` to remain independent of proc-directory persistence. Risks are minimal, but repeated factory calls may create independent DAO instances with shared external dependencies. Tests should use fake factories to isolate business logic and verify ownership transfer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/dao/factories/AbstractDAOFactory.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/dao/factories/ProcDirectoryDAOFactory.cc -->
## sources/distributed-fs/eos/mgm/bulk-request/dao/factories/ProcDirectoryDAOFactory.cc

Purpose: implements the proc-directory DAO factory. The constructor stores an `XrdMgmOfs*` and a reference to `ProcDirectoryBulkRequestLocations`; `getBulkRequestDAO()` returns a new `ProcDirectoryBulkRequestDAO` using those dependencies.

State/dependencies: factory does not own the filesystem or locations; both must outlive the factory and produced DAO. Integration appears in cleaner setup and business-layer construction.

Risks: lifetime is by raw pointer/reference, no null checks, and every call creates a new DAO. Tests should verify construction with fake/non-null dependencies and that returned DAO paths derive from the provided locations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/dao/factories/ProcDirectoryDAOFactory.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/dao/factories/ProcDirectoryDAOFactory.hh -->
## sources/distributed-fs/eos/mgm/bulk-request/dao/factories/ProcDirectoryDAOFactory.hh

Purpose: declares `ProcDirectoryDAOFactory`, the concrete `AbstractDAOFactory` for storing bulk requests in EOS proc directories.

Important API/state: constructor accepts `XrdMgmOfs* fileSystem` and `const ProcDirectoryBulkRequestLocations&`; `getBulkRequestDAO()` returns `unique_ptr<IBulkRequestDAO>`. Members are `mFileSystem` and `mBulkReqLocations`.

Integration: used wherever proc-directory persistence is selected, notably cleaner and MGM configuration paths. Risks include non-owning dependencies and no factory-level validation. Test signals should focus on dependency propagation and behavior when the proc location schema changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/dao/factories/ProcDirectoryDAOFactory.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/dao/proc/ProcDirBulkRequestFile.cc -->
## sources/distributed-fs/eos/mgm/bulk-request/dao/proc/ProcDirBulkRequestFile.cc

Purpose: implements the proc-persistence representation of a bulk-request file. It stores the persisted xattr suffix/name, optional file ID, and optional error text.

Important APIs: constructor from name, setters/getters for file ID, error, and name, plus comparison/equality by name. `operator<` enables use as a key in maps of metadata futures.

State/integration: used by `ProcDirectoryBulkRequestDAO::fillBulkRequestFromXattrs()` to distinguish numeric file IDs from encoded missing-file paths, carry error text, and resolve metadata asynchronously. Risks include name-only equality ignoring file ID and error, and `setError()` accepting empty strings. Tests should cover numeric and encoded names, map ordering, and error propagation into reconstructed `File` objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/dao/proc/ProcDirBulkRequestFile.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/dao/proc/ProcDirBulkRequestFile.hh -->
## sources/distributed-fs/eos/mgm/bulk-request/dao/proc/ProcDirBulkRequestFile.hh

Purpose: declares a lightweight wrapper for file entries persisted in proc-directory xattrs. It abstracts whether an entry names a real file by file ID or a missing file by encoded path.

Important APIs: `setFileId()`, `getFileId()`, `setError()`, `getError()`, `setName()`, `getName()`, `operator<`, and `operator==`.

Integration: private helper type for `ProcDirectoryBulkRequestDAO`; depends on `common::FileId` and `std::optional`. Risks include optional file ID access requiring callers to check/value only after successful parse, and comparison not including file ID/error. Tests should verify optional state and ordering before using it in async future maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/dao/proc/ProcDirBulkRequestFile.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/dao/proc/ProcDirectoryBulkRequestDAO.cc -->
## sources/distributed-fs/eos/mgm/bulk-request/dao/proc/ProcDirectoryBulkRequestDAO.cc

Purpose: implements bulk-request persistence using EOS proc directories and directory extended attributes. Stage saves create a request directory and write xattrs; cancellation saves update xattrs on an existing stage request directory.

Important flow: `saveBulkRequest(StageBulkRequest*)` rejects empty requests, creates the proc directory, generates xattrs, persists them under a namespace write lock, and deletes the directory on `PersistencyException`. Stage xattrs include `last_accessed_time`, `issuer_uid`, `creation_time`, and one `fid.<id-or-encoded-path>` entry per file with optional error text. Existing files are resolved through EOS metadata; missing files are URL-escaped with dots forced to `%2E`. `getBulkRequest()` checks directory existence, updates last access time, fetches xattrs, reconstructs stage requests, and resolves numeric fids back to paths while preserving encoded missing paths. `deleteBulkRequestNotQueriedFor()` lists request directories and removes those whose `last_accessed_time` is older than the configured threshold.

State/dependencies: uses raw `XrdMgmOfs*`, proc location schema, root `VirtualIdentity`, namespace locks, `_mkdir`, `_exists`, `_attr_ls`, `_attr_set`, `ProcCommand rm -r`, file metadata futures, and `BulkRequestFactory`. Risks include non-atomic directory create plus xattr update, catch/rethrow by value style, path encoding compatibility (`#:#` legacy), missing xattrs causing hard failures, and no explicit existence check before cancellation update. Tests should cover empty request rejection, missing-file encoding/decoding, xattr schema, cleanup after partial save, retrieval of deleted fids, expiry deletion, and permission/error propagation from `_exists`, `_attr_ls`, and `_attr_set`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/dao/proc/ProcDirectoryBulkRequestDAO.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/dao/proc/ProcDirectoryBulkRequestDAO.hh -->
## sources/distributed-fs/eos/mgm/bulk-request/dao/proc/ProcDirectoryBulkRequestDAO.hh

Purpose: declares the proc-directory DAO implementation and documents its storage model: one directory per bulk request under type-specific proc paths, with request/file data stored as directory xattrs.

Important APIs: implements all `IBulkRequestDAO` methods. Private helpers cover cancellation, directory creation/deletion/existence, path generation, save cleanup, xattr generation/persistence/fetching, stage initialization from xattrs, reconstruction of file lists from xattrs, metadata future initiation, and last-access updates.

State/integration: members include non-owning `XrdMgmOfs*`, proc locations reference, root virtual identity, xattr names (`last_accessed_time`, `issuer_uid`, `creation_time`, `fid.` prefix). Integration is deep with MGM namespace and proc command APIs. Risks include broad private surface, raw pointer lifetime, root identity for all proc operations, and storage schema compatibility. Tests should use fake `XrdMgmOfs`/namespace services or integration fixtures to validate xattr-level persistence and retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/dao/proc/ProcDirectoryBulkRequestDAO.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/dao/proc/ProcDirectoryBulkRequestLocations.cc -->
## sources/distributed-fs/eos/mgm/bulk-request/dao/proc/ProcDirectoryBulkRequestLocations.cc

Purpose: builds and serves the proc-directory path schema for bulk-request persistence. Given a base proc path, it derives `<base>/bulkrequests/`, `stage/`, and `evict/` subdirectories; cancel requests map to the stage directory because cancellation mutates stage requests.

Important APIs: constructor, `getAllBulkRequestDirectoriesPath()`, `getBulkRequestDirectory()`, and `getDirectoryPathWhereBulkRequestCouldBeSaved(type)`.

State/dependencies: stores a map from `BulkRequest::Type` to path plus root bulk-request directory. Risks include string concatenation assumptions about base paths, `at(type)` throwing for unsupported enum values, and duplicate stage/cancel paths being collapsed by `set` output. Tests should verify exact path generation, cancel-to-stage mapping, and behavior for all enum types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/dao/proc/ProcDirectoryBulkRequestLocations.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/dao/proc/ProcDirectoryBulkRequestLocations.hh -->
## sources/distributed-fs/eos/mgm/bulk-request/dao/proc/ProcDirectoryBulkRequestLocations.hh

Purpose: declares the path-schema holder used by proc DAO factories and cleaners. It centralizes where request directories live for each bulk-request type.

Important APIs/state: constructor from `procDirectoryPath`, `getAllBulkRequestDirectoriesPath()`, `getBulkRequestDirectory()`, and `getDirectoryPathWhereBulkRequestCouldBeSaved()`. Private state is `mBulkRequestTypeToPath` and `mBulkRequestDirectory`.

Integration: stored on `XrdMgmOfs` and shared with DAOs/cleaners. Risks include non-normalized paths and map lookup exceptions for future types. Test signals should assert schema stability because persisted request locations depend on these strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/dao/proc/ProcDirectoryBulkRequestLocations.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/dao/proc/cleaner/BulkRequestProcCleaner.cc -->
## sources/distributed-fs/eos/mgm/bulk-request/dao/proc/cleaner/BulkRequestProcCleaner.cc

Purpose: implements a background assisted thread that periodically removes stale proc-directory bulk requests.

Important flow: `Start()` resets the assisted thread; `Stop()` joins it. `backgroundThread()` logs startup, waits for namespace boot, waits until this MGM becomes master, then loops until termination. On each interval, if still master, it creates a `ProcDirectoryDAOFactory`, gets an `IBulkRequestDAO`, calls `deleteBulkRequestNotQueriedFor(PREPARE_STAGE, configured age)`, and logs deletion counts. `IntervalStopwatch` and five-second waits make sleep interruptible.

State/dependencies: depends on global `gOFS`, `IMaster`, proc locations, cleaner config, DAO factory, and `PersistencyException`. Risks include global pointer reliance, only cleaning `PREPARE_STAGE`, repeated DAO construction, waiting for master before main loop but not handling long slave periods except by skipping work, and destructor calling `Stop()`. Tests should cover start/stop idempotence, master-only cleanup, exception logging, interval wake behavior, and configured age propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/dao/proc/cleaner/BulkRequestProcCleaner.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/dao/proc/cleaner/BulkRequestProcCleaner.hh -->
## sources/distributed-fs/eos/mgm/bulk-request/dao/proc/cleaner/BulkRequestProcCleaner.hh

Purpose: declares the proc bulk-request cleaner thread wrapper. It owns an `AssistedThread`, references the proc location schema, and owns immutable cleaner configuration.

Important APIs: constructor, `Start()`, `Stop()`, `backgroundThread(ThreadAssistant&)`, and destructor. The documented behavior is deletion of requests not queried for longer than the configured threshold.

Integration: tied to MGM startup/configuration and global `gOFS` in implementation. Risks include non-owning location reference lifetime, `const unique_ptr` config preventing reconfiguration, and join semantics if `Stop()` is called before start depending on `AssistedThread`. Test signals should validate construction lifetime and thread termination behavior with a fake assistant where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/dao/proc/cleaner/BulkRequestProcCleaner.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/dao/proc/cleaner/BulkRequestProcCleanerConfig.cc -->
## sources/distributed-fs/eos/mgm/bulk-request/dao/proc/cleaner/BulkRequestProcCleanerConfig.cc

Purpose: implements cleaner configuration construction and defaults. The constructor stores interval and stale-age durations. `getDefaultConfig()` returns a one-hour run interval and one-week inactivity threshold.

State/dependencies: simple value object using `std::chrono::seconds` and `std::unique_ptr`. Integration is with `BulkRequestProcCleaner` setup.

Risks: defaults are hard-coded and comments are the main policy documentation. Tests should verify the exact default values (`3600`, `604800`) and custom constructor propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/dao/proc/cleaner/BulkRequestProcCleanerConfig.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/dao/proc/cleaner/BulkRequestProcCleanerConfig.hh -->
## sources/distributed-fs/eos/mgm/bulk-request/dao/proc/cleaner/BulkRequestProcCleanerConfig.hh

Purpose: declares the configuration object for proc bulk-request cleanup. It exposes public duration fields for cleanup interval and inactivity age.

Important APIs/state: constructor, `mInterval`, `mBulkReqLastAccessTimeBeforeCleaning`, and `getDefaultConfig()`.

Integration: owned by `BulkRequestProcCleaner`. Risks include mutable public fields and no validation against zero/negative-equivalent durations. Test signals should include default config and edge intervals if caller validation is added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/dao/proc/cleaner/BulkRequestProcCleanerConfig.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/exception/BulkRequestException.hh -->
## sources/distributed-fs/eos/mgm/bulk-request/exception/BulkRequestException.hh

Purpose: declares a simple `std::exception` subclass carrying a bulk-request error message.

Important API/state: constructor from string stores `mErrorMsg`; `what()` returns `mErrorMsg.c_str()`.

Integration: included by `BulkRequestPrepareManager.cc`, though the read code does not actively throw it there. Risks include class being outside the EOS bulk namespace, unlike most bulk-request code, and `what()` lacking `override` in style. Tests are minimal: construct and assert `what()` stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/exception/BulkRequestException.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/exception/PersistencyException.hh -->
## sources/distributed-fs/eos/mgm/bulk-request/exception/PersistencyException.hh

Purpose: declares the exception used for persistence failures in bulk-request business and DAO layers. It derives from `common::Exception`, preserving EOS error-info integration.

Important API: constructor from string forwards to `common::Exception`. This allows callers such as `PrepareManager` to call `fillXrdErrInfo(error, EIO)`.

Integration: thrown by `BulkRequestBusiness` and `ProcDirectoryBulkRequestDAO`, caught by prepare manager and cleaner. Risks include broad use for both user errors and infrastructure errors; tests should assert message propagation and XRootD error conversion through `common::Exception`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/exception/PersistencyException.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/interface/IMgmFileSystemInterface.hh -->
## sources/distributed-fs/eos/mgm/bulk-request/interface/IMgmFileSystemInterface.hh

Purpose: defines a testable adapter interface over the MGM filesystem operations needed by prepare and query-prepare logic. It decouples `PrepareManager` from direct `XrdMgmOfs` access.

Important APIs: stats recording, tape flag and request-ID limit, error formatting, existence checks by client or virtual identity, xattr listing, access checks, `FSctl`, stat/stat-flag helpers, log ID/host access, and EOS report writing.

Integration: implemented by `RealMgmFileSystemInterface`; consumed by `PrepareManager`. Risks include a broad interface that is still tightly coupled to XRootD and EOS types, and default pointer arguments that fakes must mirror. Test signals should use mocks to drive all prepare validation branches: mapping, redirect/stall, xattr lookup, access failure, stat flags, and workflow dispatch return codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/interface/IMgmFileSystemInterface.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/interface/RealMgmFileSystemInterface.cc -->
## sources/distributed-fs/eos/mgm/bulk-request/interface/RealMgmFileSystemInterface.cc

Purpose: implements `IMgmFileSystemInterface` by forwarding calls to a concrete `XrdMgmOfs` instance and related MGM services.

Important behavior: methods delegate to `MgmStats`, `mTapeEnabled`, `mReqIdMax`, `Emsg`, `_exists`, `_attr_ls`, `_access`, `FSctl`, `_stat`, `_stat_set_flags`, `logId`, host/alias fields, and `mIoStats->WriteRecord()` when present.

State/dependencies: stores non-owning `XrdMgmOfs*`. Integration is the production adapter for `PrepareManager`. Risks include no null guard for `mMgmOfs`, fallback host string behavior, and report records being silently dropped if `mIoStats` is absent. Tests should use fake `XrdMgmOfs` only in integration-style builds; most prepare unit tests should mock the interface instead.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/interface/RealMgmFileSystemInterface.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/interface/RealMgmFileSystemInterface.hh -->
## sources/distributed-fs/eos/mgm/bulk-request/interface/RealMgmFileSystemInterface.hh

Purpose: declares the production implementation of `IMgmFileSystemInterface` backed by `XrdMgmOfs`.

Important APIs: implements every interface method and stores `XrdMgmOfs* mMgmOfs`. The destructor is trivial and does not own the MGM object.

Integration: constructed where MGM prepare/query operations need the real filesystem facade. Risks are raw pointer lifetime and tight compile dependency on `mgm/ofs/XrdMgmOfs.hh`. Test signals should validate forwarding only where wrapper behavior is non-trivial, such as host fallback and report-record guard.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/interface/RealMgmFileSystemInterface.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/prepare/CancellationBulkRequest.hh -->
## sources/distributed-fs/eos/mgm/bulk-request/prepare/CancellationBulkRequest.hh

Purpose: declares the cancellation request type used to cancel files in an existing stage bulk request. It derives from `BulkRequest` and returns `PREPARE_CANCEL`.

Important behavior: constructor takes the request ID, normally matching the stage request being canceled. It adds no extra state beyond base files.

Integration: created by `BulkRequestFactory` and `BulkRequestPrepareManager`, saved by business/DAO as mutations to stage proc directories. Risks include no explicit link type beyond reused ID and files, and comments still saying “prepared”. Tests should verify type dispatch and DAO cancellation xattr update behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/prepare/CancellationBulkRequest.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/prepare/EvictBulkRequest.hh -->
## sources/distributed-fs/eos/mgm/bulk-request/prepare/EvictBulkRequest.hh

Purpose: declares an evict bulk-request subtype returning `PREPARE_EVICT`.

Important behavior: only stores the inherited ID/files and exposes the type. There is no factory method or DAO persistence support in the researched files.

Integration: included by `BulkRequestFactory.hh`, and `PrepareManager` can trigger an evict workflow, but business persistence rejects unsupported types. Risks include partial implementation: callers may assume evict requests are first-class because the type exists. Tests should confirm current unsupported persistence behavior and any future implementation should add factory/business/DAO coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/prepare/EvictBulkRequest.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/prepare/PrepareUtils.cc -->
## sources/distributed-fs/eos/mgm/bulk-request/prepare/PrepareUtils.cc

Purpose: converts XRootD prepare option bitmasks into a readable comma-separated string for logging.

Important flow: masks priority with `Prep_PMASK`, maps `Prep_PRTY0..3`, maps send flags via mask `12`, appends flags for `WMODE`, `STAGE`, `COLOC`, `FRESH`, and under supported XRootD versions `CANCEL`, `QUERY`, and `EVICT`.

State/dependencies: stateless; depends on XRootD version/prepare constants. Risks include the hard-coded send mask and version-dependent output differences. Tests should exercise representative bit combinations, unknown priority/send values, and XRootD-version-gated flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/prepare/PrepareUtils.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/prepare/PrepareUtils.hh -->
## sources/distributed-fs/eos/mgm/bulk-request/prepare/PrepareUtils.hh

Purpose: declares `PrepareUtils`, currently a stateless utility class for prepare option formatting.

Important API: `static std::string prepareOptsToString(int opts)`.

Integration: used by `PrepareManager::doPrepare()` logging. Risks are minimal, but because output is diagnostic, tests should focus on stability for common option combinations used in logs and troubleshooting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/prepare/PrepareUtils.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/prepare/StageBulkRequest.hh -->
## sources/distributed-fs/eos/mgm/bulk-request/prepare/StageBulkRequest.hh

Purpose: declares the stage bulk-request subtype for files to retrieve/prepare. It records issuer identity and creation time in addition to base request ID/files.

Important APIs: constructors with current time or explicit creation time, `getType()` returning `PREPARE_STAGE`, `getIssuerVid()`, and `getCreationTime()`.

State/integration: issuer VID and creation time are immutable members persisted by `ProcDirectoryBulkRequestDAO` xattrs and reconstructed through `BulkRequestFactory`. Risks include only UID being persisted in DAO reconstruction in the read code, while the full `VirtualIdentity` is stored at creation time. Tests should verify creation-time persistence and clarify which identity fields are expected after reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/prepare/StageBulkRequest.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/prepare/manager/BulkRequestPrepareManager.cc -->
## sources/distributed-fs/eos/mgm/bulk-request/prepare/manager/BulkRequestPrepareManager.cc

Purpose: implements the bulk-aware subclass of `PrepareManager`. It injects domain request creation and persistence into the base prepare algorithm.

Important flow: stage initialization creates a `StageBulkRequest` with a generated ID and overwrites `reqid`; cancel initialization creates a `CancellationBulkRequest` using the incoming `reqid`; `addFileToBulkRequest()` appends validated/error files when a request exists; `saveBulkRequest()` delegates to `BulkRequestBusiness` and rethrows `PersistencyException`; `ignorePrepareFailures()` returns true so persisted bulk requests can report per-file failures without failing the whole prepare call.

State/dependencies: stores `shared_ptr<BulkRequestBusiness>` and `unique_ptr<BulkRequest>`. Risks include `getBulkRequest()` moving state out, null business silently skipping persistence, and all prepare failures ignored for this subclass. Tests should cover generated ID return, cancel ID preservation, file additions, persistence exception conversion in base class, and behavior with no business configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/prepare/manager/BulkRequestPrepareManager.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/prepare/manager/BulkRequestPrepareManager.hh -->
## sources/distributed-fs/eos/mgm/bulk-request/prepare/manager/BulkRequestPrepareManager.hh

Purpose: declares the template-method subclass that adds bulk-request management to `PrepareManager` without changing the base prepare workflow.

Important APIs: constructor, `setBulkRequestBusiness()`, `getBulkRequest()`, overrides for stage/cancel initialization, file addition, saving, and failure handling. The base hooks are protected except the retrieval/configuration methods.

State/integration: integrates prepare workflow with `BulkRequestBusiness` persistence. Risks include ownership transfer through `getBulkRequest()` and shared ownership of business layer. Tests should derive or instantiate with mock filesystem/business dependencies to assert hook behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/prepare/manager/BulkRequestPrepareManager.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/prepare/manager/PrepareManager.cc -->
## sources/distributed-fs/eos/mgm/bulk-request/prepare/manager/PrepareManager.cc

Purpose: implements XRootD prepare and query-prepare handling for EOS MGM, including authorization, workflow trigger dispatch, per-file validation, bulk-request hooks, and structured query responses.

Important prepare flow: maps identity unless a VID is supplied, handles stall/redirect macros, counts files, derives action from prepare flags after removing QoS bits, and sets events (`sync::prepare`, `sync::abort_prepare`, `sync::evict_prepare`). For each path it namespace-maps, redirects, checks non-empty path, file existence, parent workflow xattrs, prepare permission, and for stage requests existing retrieve request count. It records per-file errors through `addFileToBulkRequest()`, saves the bulk request before workflow dispatch, returns `SFS_DATA` with generated reqid for stage, and triggers workflows through `FSctl(SFS_FSCTL_PLUGIN)` with `mgm.pcmd=event` parameters and security identity.

Query flow: builds a `FileCollection` from paths, maps identity, checks file existence, stat flags for tape/online state, retrieve request/error xattrs, prepare permission, and fills `QueryPrepareResponse` entries before returning `SFS_DATA`.

State/dependencies: owns `IMgmFileSystemInterface`, mutable `mPrepareAction`, logging/stat macros, XRootD structures, `EosCtaReporter`, xattr helpers, and MGM macros. Risks include macro-heavy control flow, `goto` for per-file error continuation, saving bulk requests before workflow execution, mutable action state across calls, and raw pointers into Xrd linked lists stored before workflow trigger. Tests need broad branch coverage with mocked filesystem: invalid flags, empty opts on tape, missing workflow tags, access failures, max request IDs, persistence failure, workflow failure, and query xattr/stat combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/prepare/manager/PrepareManager.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/prepare/manager/PrepareManager.hh -->
## sources/distributed-fs/eos/mgm/bulk-request/prepare/manager/PrepareManager.hh

Purpose: declares the base manager for prepare operations and query-prepare operations. It exposes public entry points and protected template hooks used by `BulkRequestPrepareManager`.

Important APIs/types: `enum PrepareAction { STAGE, EVICT, ABORT }`, overloads of `prepare()` and `queryPrepare()` for client or pre-mapped VID, hooks `initializeStagePrepareRequest()`, `initializeCancelPrepareRequest()`, `ignorePrepareFailures()`, `setErrorToBulkRequest()`, `saveBulkRequest()`, `addFileToBulkRequest()`, helpers `getPrepareActionsFromOpts()`, `isStagePrepare()`, `triggerPrepareWorkflow()`, and implementation methods `doPrepare()`/`doQueryPrepare()`.

State/integration: `mEpname`, `mPrepareAction`, and `unique_ptr<IMgmFileSystemInterface>`. Risks include `mPrepareAction` requiring initialization before `isStagePrepare()`, broad protected surface, and coupling to EOS/XRootD types. Tests should exercise base behavior and subclass hook behavior separately.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/prepare/manager/PrepareManager.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/prepare/query-prepare/QueryPrepareResult.cc -->
## sources/distributed-fs/eos/mgm/bulk-request/prepare/query-prepare/QueryPrepareResult.cc

Purpose: implements the result wrapper returned by `PrepareManager::queryPrepare()`. It owns a `QueryPrepareResponse`, a finished flag, and a return code.

Important behavior: constructor initializes `mHasQueryPrepareFinished=false` and allocates an empty response. Getters expose the flag, shared response, and return code. Private setters are used by friend `PrepareManager`.

State/integration: no persistence; response is shared so callers can serialize it after query execution. Risks include `mReturnCode` not initialized in the constructor until `setReturnCode()` is called; current factory path sets it immediately after `doQueryPrepare()`. Tests should assert initial finished state, response allocation, and return-code setting through query manager.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/prepare/query-prepare/QueryPrepareResult.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/prepare/query-prepare/QueryPrepareResult.hh -->
## sources/distributed-fs/eos/mgm/bulk-request/prepare/query-prepare/QueryPrepareResult.hh

Purpose: declares the query-prepare result object. It packages completion status, response payload, and XRootD return code.

Important APIs: public constructor, `hasQueryPrepareFinished()`, `getResponse()`, and `getReturnCode()`. Private `setQueryPrepareFinished()` and `setReturnCode()` are accessible to `PrepareManager` via friendship.

Integration: returned to `XrdMgmOfs` query handling, then serialized using `QueryPrepareResponseJson`. Risks include friend-only mutation and uninitialized return code if a caller constructs directly. Tests should validate lifecycle through `PrepareManager::queryPrepare()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/prepare/query-prepare/QueryPrepareResult.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/response/QueryPrepareResponse.hh -->
## sources/distributed-fs/eos/mgm/bulk-request/response/QueryPrepareResponse.hh

Purpose: declares the structured response for `xrdfs query prepare`. `QueryPrepareFileResponse` stores per-file status, and `QueryPrepareResponse` stores the request ID and vector of file responses.

Important fields: path, existence, tape state, online state, requested state, request-ID presence, request time, and error text. A legacy `operator<<` emits JSON-like output; the primary JSON path is via `Jsonifiable` and `QueryPrepareResponseJson`.

State/integration: populated by `PrepareManager::doQueryPrepare()` and serialized by MGM query handling. Risks include manual stream serialization without escaping and public mutable fields. Tests should focus on JSON serializer output and query-manager population for error and state combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/response/QueryPrepareResponse.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/utils/PrepareArgumentsWrapper.hh -->
## sources/distributed-fs/eos/mgm/bulk-request/utils/PrepareArgumentsWrapper.hh

Purpose: wraps construction and cleanup of `XrdSfsPrep` arguments through protobuf utilities. It is useful for tests or callers that need to build prepare requests programmatically.

Important APIs: constructors from request ID/options with optional paths/oinfos, destructor deleting generated `XrdSfsPrep`, `addFile()`, `getNbFiles()`, and `getPrepareArguments()`.

State/dependencies: stores `eos::auth::XrdSfsPrepProto` and a raw `XrdSfsPrep*` generated on demand. Risks include repeated `getPrepareArguments()` overwriting `mPargs` without freeing a previous generated object first, and path/oinfo count mismatches if callers use constructors/adders inconsistently. Tests should cover lifetime cleanup, repeated generation behavior, and path/opaque ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/utils/PrepareArgumentsWrapper.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/utils/json/QueryPrepareResponseJson.hh -->
## sources/distributed-fs/eos/mgm/bulk-request/utils/json/QueryPrepareResponseJson.hh

Purpose: implements JSON serialization for `QueryPrepareResponse` using the common JsonCpp jsonifier base.

Important flow: `jsonify(QueryPrepareResponse*, stringstream&)` creates a root object with `request_id`, initializes `responses` as an array, serializes each file response through a private overload, and writes the JsonCpp value to the stream. Per-file JSON keys mirror the response fields: `path`, `path_exists`, `on_tape`, `online`, `requested`, `has_reqid`, `req_time`, and `error_text`.

State/dependencies: header-defined methods depend on `Json::Value` and `common::JsonCppJsonifier`. Risks include implementation in a header without `inline` keywords if included in multiple translation units, depending on how the build treats it. Tests should assert exact JSON keys/types and escaping for paths/errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/bulk-request/utils/json/QueryPrepareResponseJson.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/commandmap/CommandMap.cc -->
## sources/distributed-fs/eos/mgm/commandmap/CommandMap.cc

Purpose: implements string-to-enum lookup for MGM FSctl commands. A file-scope `std::map` is populated by a static initializer object.

Important behavior: `fsctlMapInit` inserts supported command strings such as `access`, `event`, `mkdir`, `stat`, `txstate`, and `version`. `lookupFsctl(cmd)` returns the matching `FsctlCommand` or `INVALID`.

State/dependencies: anonymous-namespace static map initialized before use in the translation unit. Risks include static initialization order only being safe because all access is through this file, omitted enum values (`schedule2balance`, `schedule2delete`) intentionally not mapped, and map mutability despite being effectively constant. Tests should cover known commands, unknown commands, and enum/map drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/commandmap/CommandMap.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/commandmap/CommandMap.hh -->
## sources/distributed-fs/eos/mgm/commandmap/CommandMap.hh

Purpose: declares the `FsctlCommand` enum and lookup function for command dispatch. It is the typed command vocabulary for MGM FSctl string commands.

Important API/types: `enum class FsctlCommand` with `INVALID` plus command values including access, chmod/chown, event, stat/statvfs, symlink, txstate, and version. `lookupFsctl(const std::string&)` maps user/proc strings to enum values.

Integration: used by FSctl/proc command dispatch code. Risks include enum values that are documented “not used anymore” and values that must stay synchronized with `CommandMap.cc`. Tests should enforce string coverage for all active commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/commandmap/CommandMap.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/config/IConfigEngine.cc -->
## sources/distributed-fs/eos/mgm/config/IConfigEngine.cc

Purpose: implements common behavior for MGM configuration engines: applying in-memory key/value definitions to live subsystems, publishing changes, deleting live config, dumping/filtering config, and resetting state.

Important flow: `ApplyEachConfig()` dispatches by key prefix. It applies filesystem/global config through `FsView`, path maps through `gOFS`, route endpoints through `RouteEndpoint`, quotas through namespace container lookup and `Quota`, VID mappings through `Vid`, geoscheduler parameters through `GeoTreeEngine`, namespace cache config through namespace services, and ignores comments/policy. `ApplyConfig()` clears quotas/mappings/access/space attributes, disables FsSpace defaults, applies all definitions under locks, re-enables defaults, enforces access config, and applies fsck, iostat, drain, traffic shaping, monitoring, and converter config. Publish methods write to the global MGM shared hash. `ApplyKeyDeletion()` removes live fs/map/route/quota/vid entries. `ResetConfig()` clears live config and reloads quota nodes. `DumpConfig()`, `Get()`, `DeleteConfigValueByMatch()`, `IsDeprecated()`, and `FilterDeprecated()` provide query/filter utilities.

State/dependencies: uses global `gOFS`, many MGM subsystems, namespace locks, mapping locks, and `sConfigDefinitions` protected by a recursive mutex. Risks include prefix parsing fragility, wide global side effects, lock ordering, partial apply errors accumulating in `err`, deprecated typo strings (`#conveter`), and route parsing failure handling. Tests should isolate prefix parsers, quota key parsing, publish value escaping, delete paths, deprecated filtering, and reset/apply ordering in integration fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/config/IConfigEngine.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/config/IConfigEngine.hh -->
## sources/distributed-fs/eos/mgm/config/IConfigEngine.hh

Purpose: declares the abstract interface and shared state for MGM configuration engines. It supports load/save/list/autosave implementations while centralizing apply, delete, publish, dump, and filter behavior.

Important APIs/types: `ICfgEngineChangelog` with `AddEntry()` and `Tail()` protected by `RWMutex`; `IConfigEngine` with static `ApplyEachConfig()` and `FormFullKey()`, pure virtual `LoadConfig()`, `SaveConfig()`, `ListConfigs()`, `AutoSave()`, `SetConfigValue()`, `DeleteConfigValue()`, `FilterConfig()`, and concrete `Get()`, `ApplyKeyDeletion()`, `DeleteConfigValueByMatch()`, `ApplyConfig()`, `DumpConfig()`, `ResetConfig()`, `SetAutoSave()`, `PublishConfigChange()`, and `PublishConfigDeletion()`.

State/integration: stores optional changelog, recursive mutex, autosave flag, current config name, and `sConfigDefinitions` map. Subclasses such as QuarkDB engines provide storage-specific behavior. Risks include broad access under `IN_TEST_HARNESS`, shared mutable definitions, and `FormFullKey()` treating null prefix differently from empty prefix. Tests should validate subclass contracts plus common apply/dump/get/delete helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/config/IConfigEngine.hh -->
