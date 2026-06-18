# subset-b-007054 Research

Grouped research for EOS QuarkDB namespace accounting, explorer, flusher, and inspector files.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/FileSystemView.cc -->
## sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/FileSystemView.cc

Purpose: Implements `QuarkFileSystemView`, the QuarkDB-backed `IFsView` that tracks which file IDs live on each filesystem, which files have no replicas, and which files are unlinked on a filesystem. It is the update/listing layer behind filesystem-view accounting and delegates concrete set persistence/cache behavior to `FileSystemHandler`.

Important APIs and control flow: the constructor stores `QClient`/`MetadataFlusher` and creates an 8-thread folly IO executor. `configure()` scans backend keys through `loadFromBackend()`, initializes the no-replica handler, and starts `CleanCacheJob()`. `fileMDChanged()` reacts to file lifecycle events: creation inserts non-link files into no-replica; deletion removes from no-replica; `LocationAdded` initializes the regular filesystem handler, inserts the file, then removes no-replica; `LocationRemoved` may reinsert no-replica and removes stale unlinked membership; `LocationUnlinked` inserts into unlinked and removes from regular. `fileMDCheck()` is the repair path: it async-schedules `SADD`/`SREM` operations against no-replica, regular, and unlinked sets and waits on `AsyncHandler`.

State and persistence: in-memory maps `mFiles` and `mUnlinkedFiles` map filesystem IDs to `FileSystemHandler`s, protected only for map access by `mMutex`; handler internals own their content/cache synchronization. QuarkDB keys use `RequestBuilder`/`fsview` constants. Destructive operations are intentionally ordered after additive ones where crash consistency matters, so crashes should leave over-accounting rather than missing file references. `CleanCacheJob()` periodically clears handler caches after 45 minutes of inactivity pressure.

Dependencies and integration: integrates `IFileMDChangeListener`, `IFsView`, `QuarkFileMD`, `FileSystemHandler`, `MetadataFlusher`, `QScanner`, `QSet`, `RequestBuilder`, and EOS logging. `parseFsId()` and `getQdbFileSystemIterator()` support backend discovery.

Risks and test signals: test event ordering for all location transitions, especially no-replica transitions with active and unlinked locations. `getFileSystemIterator()` returns only regular `mFiles`, so repair loops may not scan unlinked-only filesystem IDs. `clearUnlinkedFileList()` nukes the backend handler and returns false if no handler is cached. Parse failures from malformed keys are logged and skipped. Stress tests should cover concurrent `fileMDChanged()`, cache cleaner activity, backend scans, and crash/replay repair via `fileMDCheck()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/FileSystemView.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/FileSystemView.hh -->
## sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/FileSystemView.hh

Purpose: Declares the filesystem-view API and helper iterators for QuarkDB-backed namespace accounting. The header documents the Redis/QuarkDB set layout: `fsview:<fsid>:files`, `fsview:<fsid>:unlinked`, and the no-replica set.

Important APIs and types: `QdbFileSystemIterator` wraps a moved `std::set` of filesystem IDs discovered from backend scans. `ListFileSystemIterator` snapshots filesystem IDs from the in-memory handler map. `QuarkFileSystemView` implements `IFsView` with methods for file change notifications, consistency repair, regular/unlinked/no-replica file iterators, streaming variants, count queries, random file selection, unlinked-list cleanup, filesystem iteration, and membership checks.

State and persistence: the class owns one no-replica `FileSystemHandler`, two maps of regular and unlinked handlers keyed by filesystem ID, a folly executor shared by handlers, and an assisted cache-cleaner thread. It stores non-owning pointers to `qclient::QClient` and `MetadataFlusher`; callers must ensure their lifetime exceeds the view. Map mutex protection is explicitly scoped to map membership, not handler contents.

Dependencies and integration: depends on EOS namespace interfaces, `FileSystemHandler`, QuarkDB constants, `QClient`, `AssistedThread`, and `MetadataFlusher`. The exposed `parseFsId()` helper is part of backend-key discovery and repair tooling.

Risks and test signals: the header includes itself, which is harmless due to guards but unusual and worth watching during include cleanup. API consumers must handle `nullptr` iterators for unknown filesystems. Tests should validate iterator validity, snapshot behavior, initialization/fetch semantics, streaming list behavior, and that `finalize()`, `shrink()`, `AddTree()`, and `RemoveTree()` are intentionally no-ops for this view.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/FileSystemView.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/QuotaNodeCore.cc -->
## sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/QuotaNodeCore.cc

Purpose: Implements the in-memory quota accumulator for one quota node. It tracks logical bytes, physical bytes, and file counts per UID and GID, independent of QuarkDB persistence.

Important APIs and control flow: getter methods acquire shared locks and return zero for missing IDs. `addFile()` and `removeFile()` update both user and group counters under an exclusive lock. `meld()` adds every counter from another core. Assignment replaces both maps; `operator<<` partially replaces entries present in the update core; equality compares both maps. `setByUid()`, `setByGid()`, `filterByUid()`, and `filterByGid()` support targeted repair/update workflows.

State behavior: `mUserInfo` and `mGroupInfo` are `std::map`s guarded by a `std::shared_timed_mutex`. Missing entries are created on add/remove/set. Filtering builds a copy of keys before erasing, avoiding iterator invalidation.

Dependencies and integration: used by `IQuotaNode`/`QuarkQuotaNode` as the cached in-memory copy of persisted quota hash data. It has no direct backend dependency, so it is suitable for isolated unit tests.

Risks and test signals: `removeFile()` subtracts from unsigned counters without bounds checks, so duplicate removes or inconsistent repair input can underflow to huge values. `meld()`, assignment, and equality call `std::lock(mtx, other.mtx)` and then manually unlock both mutexes instead of using RAII lock guards; exceptions during map copy/add would leave locks held. Self-assignment/self-meld may also be risky with `std::lock` on the same mutex. Tests should cover missing-ID getters, add/remove balance, underflow behavior, partial update semantics, filtering, equality, and concurrent reader/writer access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/QuotaNodeCore.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/QuotaNodeCore.hh -->
## sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/QuotaNodeCore.hh

Purpose: Declares `QuotaNodeCore`, the synchronized data model for per-quota-node user/group usage accounting. It is the common state object that QuarkDB quota nodes cache and expose through the quota interfaces.

Important APIs and types: `UsageInfo` contains `space`, `physicalSpace`, and `files`, with additive and equality operators. Public methods expose per-user/per-group logical space, physical space, and file count; mutators add/remove files; bulk operations meld, assign, partially update, set selected IDs, and filter to selected IDs. `getUids()` and `getGids()` expose keys present in the maps.

State and access: the header defines `mUserInfo` and `mGroupInfo` as private maps protected by mutable `std::shared_timed_mutex`. It grants friendship to quota abstractions and `QuarkQuotaNode`, allowing persistence code to read/write maps directly.

Dependencies and integration: depends on EOS namespace types and POSIX UID/GID identifiers. Its role is intentionally backend-agnostic; `QuotaStats.cc` translates this state to QuarkDB hash fields.

Risks and test signals: the friend access bypasses the public locking API in callers such as backend import/replacement, so tests should include thread-safety assumptions around `QuarkQuotaNode`. The default `UsageInfo` zero initialization is a useful invariant. Validate that `operator<<` means "replace only entries present in update", not a full merge or clear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/QuotaNodeCore.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/QuotaStats.cc -->
## sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/QuotaStats.cc

Purpose: Implements QuarkDB-backed quota nodes and the quota-node manager. It persists quota counters into two hashes per container/quota node: UID counters and GID counters.

Important APIs and control flow: `QuarkQuotaNode::addFile()` and `removeFile()` compute physical size through `IQuotaStats::getPhysicalSize()`, stage a single `HINCRBYMULTI` through `MetadataFlusher`, then update the local `QuotaNodeCore`. `meld()` scans another node's UID/GID hashes and increments this node's hashes before melding the cache. `updateFromBackend()` scans both hashes, parses `<id>:logical_size|physical_size|files` fields, populates core maps, and deletes zeroed fields. `replaceCore()` deletes both backend hashes and writes all counters from a replacement core. `updateCore()` partially overwrites backend fields from an update core. `QuarkQuotaStats` lazily loads nodes, registers new nodes, removes nodes, scans all quota IDs, and parses key names.

State and persistence: backend mutations are staged through `MetadataFlusher`, so immediate reads through `QClient` may lag unless synchronized elsewhere. `pNodeMap` caches loaded quota nodes. `updateFromBackend()` mutates `pCore` maps directly via friendship and cleans zero entries from QuarkDB.

Dependencies and integration: depends on quota interfaces, `QuotaNodeCore`, QuarkDB constants, `QHash`, `QScanner`, `MetadataFlusher`, and string tokenization. It is tied to `IContainerMD::id_t` as the quota-node ID.

Risks and test signals: there is no mutex around `pNodeMap`, so manager calls appear single-thread-assumed. `replaceCore()` stages `DEL` followed by many `HSET`s; a crash mid-flush can temporarily erase or partially rewrite quota state unless the background flusher replay guarantees cover it. `updateFromBackend()` does not clear existing core maps before scanning, so missing backend fields may leave stale in-memory fields unless entries become explicit zeroes. Tests should exercise key parsing, lazy load vs register collision, add/remove/meld persistence requests, zero cleanup, partial update semantics, and flusher synchronization expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/QuotaStats.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/QuotaStats.hh -->
## sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/QuotaStats.hh

Purpose: Declares the QuarkDB quota accounting implementation. It documents the per-container hash layout for user and group quota counters and exposes the quota-node and manager classes.

Important APIs and types: `QuarkQuotaNode` extends `IQuotaNode` and provides file add/remove, node meld, backend refresh, full core replacement, and partial core update. It stores UID/GID hash keys plus non-owning backend/flusher pointers inherited from `QuarkQuotaStats`. `QuarkQuotaStats` extends `IQuotaStats`, creates and caches `IQuotaNode`s, removes quota nodes, returns all quota IDs, and contains static helpers for key construction and parsing.

State and persistence: the interface maps one quota node to one container ID. Backend state is split into `quota:<id>:uid` and `quota:<id>:gid` style hashes using suffix constants. In-memory cache ownership is in `pNodeMap`; backend write durability is delegated to `MetadataFlusher`.

Dependencies and integration: integrates with EOS quota interfaces, container IDs, QuarkDB `QClient`, and `MetadataFlusher`. `QuarkQuotaStats` is a friend of `QuarkQuotaNode` for dependency access, while `QuarkQuotaNode` relies on inherited `IQuotaNode::pCore`.

Risks and test signals: since methods return raw `IQuotaNode*` owned by `pNodeMap`, consumers must not retain pointers past `removeNode()` or destruction. Tests should lock down documented key names, duplicate-node errors, null return for missing nodes, and that `configure()` intentionally has no runtime configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/QuotaStats.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/SetChangeList.hh -->
## sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/SetChangeList.hh

Purpose: Provides a small template change list for applying ordered insert/delete operations onto STL-like set containers. It is a utility for staging changes before applying them to an in-memory set.

Important APIs and control flow: `push_back()` records an insertion; `erase()` records a deletion tombstone; `size()` and `clear()` manage the pending list. `apply(Container&)` replays operations in insertion order, calling `container.insert(item)` or `container.erase(item)`.

State and dependencies: stores a `std::list<Item>`, where each item contains an operation enum and a copy of `T`. It depends only on EOS namespace macros and standard containers, with no persistence or threading behavior.

Integration points: suitable for code that needs deterministic set mutation replay after accumulating changes, especially when event order matters. The target container only needs compatible `insert()` and `erase()` methods.

Risks and test signals: repeated insert/delete operations are preserved and replayed, so the final state depends on order. There is no deduplication, conflict compaction, locking, or exception isolation. Tests should verify replay order, duplicate operations, deletion of absent entries, custom comparable element types, and clear/reuse behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/SetChangeList.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/SyncTimeAccounting.cc -->
## sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/SyncTimeAccounting.cc

Purpose: Implements asynchronous synchronous-time/mtime propagation for container metadata. On `MTimeChange`, it queues the changed container and later propagates terminal mtime up ancestors that opt in with `sys.mtime.propagation`.

Important APIs and control flow: the constructor initializes two update batches and starts an assisted propagation thread when the interval is nonzero. `containerMDChanged()` queues only `MTimeChange` events. `QueueForUpdate()` deduplicates within the accumulating batch and moves repeated IDs to the end as most recent. `PropagateUpdates()` swaps accumulate/commit batches, walks the commit list in reverse, fetches containers, write-locks them, checks propagation attributes, removes `sys.tmp.etag`, copies the leaf mtime to `TMTime`, updates storage, and stops at root, depth 255, missing attribute, unchanged propagated time, already-updated node, or metadata exception.

State and persistence: all pending updates live in two `UpdateT` batches protected by `mMutexBatch`; storage updates go through `IContainerMDSvc::updateStore()`. `INamespaceStats` receives batch size and execution-time metrics when configured. Shutdown sets `mShutdown` and joins the thread.

Dependencies and integration: integrates `IContainerMDChangeListener`, `IContainerMDSvc`, container write locking, EOS logging, `AssistedThread`, and namespace stats.

Risks and test signals: with update interval zero, callers can invoke `PropagateUpdates(nullptr)` for a one-shot drain; otherwise it loops and sleeps. The reverse-order traversal and `upd_nodes` set are important for avoiding redundant ancestor writes. The code catches `MDException` and silently stops that chain. Tests should cover dedup ordering, opt-in attribute behavior, tmp-etag removal, unchanged-time early exit, depth limit, shutdown behavior, stats emission, and service exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/SyncTimeAccounting.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/SyncTimeAccounting.hh -->
## sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/SyncTimeAccounting.hh

Purpose: Declares `QuarkSyncTimeAccounting`, a listener that batches container mtime propagation and commits it asynchronously or manually.

Important APIs and types: public methods include the constructor with container service, update interval, and optional namespace stats; deleted copy/move operations; `containerMDChanged()`; `PropagateUpdates()`; `QueueForUpdate()`; and `setNamespaceStats()`. `UpdateT` combines an ordered list of container IDs with a map from ID to list iterator so repeated updates can be deduplicated and moved.

State behavior: two `UpdateT` slots represent the accumulating and committing batches. `mAccumulateIndx`/`mCommitIndx` are swapped under `mMutexBatch`. `mShutdown`, `mUpdateIntervalSec`, `mThread`, and the service pointer control worker lifecycle. The service and stats pointers are non-owning.

Dependencies and integration: depends on namespace metadata interfaces, assisted threading, logging, locking utilities, and stats. It is intended to be registered as an `IContainerMDChangeListener`.

Risks and test signals: users must ensure the container metadata service outlives the accounting object and that stats pointer updates are externally safe. Tests should inspect the two-batch queue model, no-thread mode, destructor join behavior, and the listener action filter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/SyncTimeAccounting.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/explorer/NamespaceExplorer.cc -->
## sources/distributed-fs/eos/namespace/ns_quarkdb/explorer/NamespaceExplorer.cc

Purpose: Implements recursive namespace exploration over QuarkDB metadata, primarily for find-like commands. It walks from a requested path, yields containers and files, optionally counts children, filters expansion, and resolves linked attributes.

Important APIs and control flow: `SearchNode` starts async fetches for container metadata and child container maps. `handleAsync()` stages child containers when ready and either starts a file listing or a file-count query depending on `ignoreFiles`/filtering. `expand()` validates parent expectations, stages sorted children, and returns the next child node by ownership transfer. `fetchChild()` drains `FutureVectorIterator<FileMdProto>`, swallowing `MDException`s in a retry loop. `NamespaceExplorer` constructor resolves the static path synchronously; if the last path component is not a container, it may resolve it as a single file. `fetch()` emits a single file search result, or performs DFS: visit container, run expansion decider/depth limit, yield file children, expand subcontainers, then pop exhausted nodes.

State and persistence behavior: the explorer is read-only and has no consistency guarantees against pending flusher writes. It stores a static path, a DFS stack, cached linked attributes keyed by link target, and per-node futures for metadata, maps, file lists, and counts.

Dependencies and integration: uses `MetadataFetcher`, `PathProcessor`/`SplitPath`, `Attributes::populateLinkedAttributes`, `IView::getItem()` for linked attrs, folly futures/executors, and EOS path utilities.

Risks and test signals: `depthLimit` defaults to zero and is compared with `>=`, so callers must understand whether zero means no recursion or root-only behavior. `fetchChild()` catches `MDException` and loops, which could spin if the iterator repeatedly throws. Full path generation is rebuilt on every fetch. Tests should cover file-vs-container path resolution, sorted child order, parent mismatch warning, expansion filtering, linked-attribute cache behavior, ignore-files counts, and depth-limit semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/explorer/NamespaceExplorer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/explorer/NamespaceExplorer.hh -->
## sources/distributed-fs/eos/namespace/ns_quarkdb/explorer/NamespaceExplorer.hh

Purpose: Declares the QuarkDB namespace exploration API and traversal node type. It provides a higher-level read path for recursively listing namespace items without going through normal mutable services.

Important APIs and types: `ExpansionDecider` is the caller-supplied policy hook for pruning container expansion. `ExplorationOptions` controls depth, expansion filtering, linked-attribute population, link prefixing, optional `IView`, and file suppression. `NamespaceItem` is the returned item union with full path, attrs, file/container flag, metadata proto, expansion-filter state, and direct child counts. `SearchNode` encapsulates async metadata/listing state for one container. `NamespaceExplorer::fetch()` is the public iterator-like API.

State and integration: `NamespaceExplorer` keeps non-owning references to `QClient` and a folly executor, plus DFS state and linked-attribute cache. `SearchNode` owns futures and child nodes, and is a friend-managed implementation detail.

Dependencies: protobuf metadata types, namespace identifiers, `IContainerMD`, `IView`, `FutureVectorIterator`, folly futures, and `QClient`.

Risks and test signals: callers requesting linked attributes must provide `options.view`, or the constructor throws an EOS metadata exception. Returned `NamespaceItem` contains both file and container proto fields but only one is meaningful. Tests should verify option validation, ownership transfer from `SearchNode::expand()`, `canVisit()` behavior when futures fail, and correct child count fields for filtered vs unfiltered containers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/explorer/NamespaceExplorer.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/flusher/MetadataFlusher.cc -->
## sources/distributed-fs/eos/namespace/ns_quarkdb/flusher/MetadataFlusher.cc

Purpose: Implements the asynchronous metadata write queue toward QuarkDB. It wraps `qclient::BackgroundFlusher` with RocksDB-backed persistency, convenience Redis command helpers, synchronization, queue metrics, and notifier logging.

Important APIs and control flow: constructors build a background flusher from contact details and either default `RocksDBPersistency` or a builder-selected flusher type/options, then call `synchronize()` to wait for initial state. The destructor joins the monitoring thread and synchronizes all queued writes. Command helpers stage `HSET`, `HINCRBY`, `DEL`, `HDEL`, `SADD`, and `SREM`; `exec()`/`execute()` support arbitrary requests. `synchronize()` waits until a target queue index, defaulting to the latest currently enqueued item, is acknowledged, logging warnings every second while pending. `queueSizeMonitoring()` logs pending/enqueued/acknowledged/index stats every 10 seconds when there is queued work.

State and persistence: `BackgroundFlusher` owns the durable local queue and remote delivery. `persistencyConfig` caches the persistency type returned by the flusher. `id` is derived from the RocksDB path basename and used in logs.

Dependencies and integration: central dependency for quota and filesystem accounting writes. It uses `QdbContactDetails`, qclient builders, RocksDB persistency/config, assisted threads, and EOS logging.

Risks and test signals: command helpers are fire-and-forget until explicit synchronization or destruction. Crash recovery depends on the qclient persistent flusher implementation. `synchronize()` can wait indefinitely on a permanently unacknowledged index. Tests should use fake/background flusher hooks to verify command vector formation, target-index behavior, notifier logging, persistency type caching, and destructor flushing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/flusher/MetadataFlusher.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/flusher/MetadataFlusher.hh -->
## sources/distributed-fs/eos/namespace/ns_quarkdb/flusher/MetadataFlusher.hh

Purpose: Declares the metadata flusher facade used by QuarkDB namespace components to enqueue Redis-style mutations without blocking hot paths on network round trips.

Important APIs and types: `ItemIndex` identifies background queue entries. `MetadataFlusher` constructors configure queue path, QuarkDB contact details, and optional flusher type/RocksDB options. `exec()` is a variadic request builder; explicit helpers cover common commands; `synchronize()` blocks until an acknowledged queue index; `getPersistencyType()` reports the selected persistent queue. `FlusherNotifier` implements qclient notification callbacks for network and unexpected-response events.

State and integration: the class owns the notifier, background flusher, queue-size monitoring thread, ID string, and cached persistency config. It is injected into accounting services and other metadata writers as a non-owning dependency from their perspective.

Dependencies: namespace metadata interfaces for context, QuarkDB constants, qclient background flusher/persistency abstractions, and standard containers.

Risks and test signals: `exec(const Args... args)` requires arguments convertible to `std::string` and copies them into a vector. Consumers should not assume immediate visibility after helper calls. Tests should validate notifier dispatch, request construction, lifecycle synchronization, and behavior when a custom flusher type is configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/flusher/MetadataFlusher.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/AttributeExtraction.cc -->
## sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/AttributeExtraction.cc

Purpose: Implements string extraction of selected `FileMdProto` fields for inspector filtering and output logic.

Important APIs and control flow: `AttributeExtraction::asString()` clears output, then handles `xattr.<name>` specially by looking up the protobuf xattr map and returning true even if the attribute is absent. It supports built-in fields `fid`, `pid`, `uid`, `gid`, `size`, `layout_id`, octal `flags`, `name`, `link_name`, formatted `ctime`, `mtime`, checksum string `xs`, comma-separated `locations`, comma-separated `unlink_locations`, and formatted `stime`. Unknown attribute names return false.

State and dependencies: stateless helper functions convert flags to octal and serialize repeated location vectors. Time formatting delegates to `Printing::parseTimespec()` and `timespecToTimestamp()`. Checksum extraction delegates to `appendChecksumOnStringProtobuf()`. It uses `common::startsWith()`.

Integration points: `StringEvaluator` in `FileMetadataFilter.cc` calls this when evaluating non-literal variables in filter expressions.

Risks and test signals: absent xattrs produce an empty string but are still considered valid, enabling comparisons against empty values. `serializeLocations()` uses `int` against `vec.size()`, which is acceptable for normal protobuf repeated fields but not ideal for very large vectors. Tests should cover every supported attribute, unknown variables, missing xattrs, time byte parsing, checksum formatting, and list serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/AttributeExtraction.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/AttributeExtraction.hh -->
## sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/AttributeExtraction.hh

Purpose: Declares the inspector helper for extracting file metadata attributes into strings.

Important API: `AttributeExtraction::asString(const FileMdProto&, const std::string& attr, std::string& out)` returns whether the attribute name is supported and writes the string representation to `out`. The class is purely static and has no owned state.

Dependencies and integration: depends on EOS namespace macros and the `FileMdProto` protobuf. It is consumed by file metadata filters and any inspector code that needs uniform string representations for metadata fields.

Risks and test signals: the API distinguishes unsupported attribute names from supported-but-empty values, so callers should inspect the boolean rather than just `out`. Tests should verify this contract for missing xattrs and unknown field names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/AttributeExtraction.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/ContainerScanner.cc -->
## sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/ContainerScanner.cc

Purpose: Implements full-namespace scanning for container metadata, with optional asynchronous full-path resolution and direct child counts.

Important APIs and control flow: `ContainerScannerPrimitive` iterates the `eos-container-md` locality hash, deserializes each value into `ContainerMdProto`, tracks scanned count, and records deserialization errors. `ContainerScanner` wraps the primitive. When neither full paths nor counts are requested, it delegates directly. When active, `ensureItemDequeFull()` fills a deque up to 500 items, starting `MetadataFetcher::resolveFullPath()` and/or `countContents()` futures for each proto. `getItem()` returns the front proto and optionally moves the buffered `Item` with pending futures to the caller.

State and persistence: scanning is read-only over QuarkDB locality hashes. Buffered mode separates backend scan progress from caller consumption and tracks its own `mScanned` count.

Dependencies and integration: depends on `QLocalityHash`, namespace serialization, `MetadataFetcher`, folly futures, and container protobufs. Inspector commands can combine this scanner with output sinks and consistency checks.

Risks and test signals: `hasError()` in active mode returns `!mItemDeque.empty() && mScanner.hasError(err)`, which can hide scanner errors after the buffer drains. Futures may resolve after item retrieval and can carry metadata lookup errors. Tests should cover deserialization failures, direct vs buffered modes, count futures, path futures, scan-count semantics, and error reporting at end of scan.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/ContainerScanner.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/ContainerScanner.hh -->
## sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/ContainerScanner.hh

Purpose: Declares primitive and enhanced scanners for iterating all container metadata stored in QuarkDB.

Important APIs and types: `ContainerScannerPrimitive` exposes iterator-style `valid()`, `next()`, `hasError()`, `getItem()`, and `getScannedSoFar()`. `ContainerScanner::Item` bundles a `ContainerMdProto`, future full path, future file count, and future container count. `ContainerScanner` exposes the same iterator-style API with optional full-path and count enrichment.

State and integration: the enhanced scanner owns a primitive scanner, a `QClient` reference, option flags, an active-mode item deque, and scan count. It is intended for inspector tooling that may need richer but more expensive metadata per container.

Dependencies: `QClient`, `QLocalityHash`, protobuf metadata, and folly futures.

Risks and test signals: callers must call `next()` after `getItem()` to consume entries. In enriched mode, futures are returned to the caller and must be awaited/handled there. Tests should validate item move behavior, default future values when enrichment is disabled, and buffer refill around the 500-item threshold.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/ContainerScanner.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/FileMetadataFilter.cc -->
## sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/FileMetadataFilter.cc

Purpose: Implements a small expression language for filtering file metadata by string equality/inequality and logical conjunction.

Important APIs and control flow: `StringEvaluator` either returns a literal or delegates a variable to `AttributeExtraction::asString()`. `EqualityFileMetadataFilter` evaluates both sides and compares them, optionally reversed for `!=`. `LogicalMetadataFilter` short-circuits `||` and `&&`, though the parser currently only constructs `&&`. `FilterExpressionLexer::lex()` tokenizes parentheses, single-quoted literals, `==`, `!=`, `&&`, `||`, and alphabetic variable sequences. `FilterExpressionParser` lexes input, then recursively consumes blocks and equality expressions into filter objects.

State behavior: filters are heap-composed through `std::unique_ptr`. Parser state tracks token vector, current index, status, debug flag, and final filter. `getFilter()` transfers ownership and is intended for one call.

Dependencies and integration: consumed by inspector commands to decide whether a `FileMdProto` should be shown. Depends on `AttributeExtraction`, EOS `common::Status`, and assertion/status helpers.

Risks and test signals: lexer recognizes `||`, but `consumeBlock()` only accepts `&&`, leaving OR effectively unsupported unless parenthesized parsing is extended. Variable lexing stops only on whitespace or end, so punctuation like `)` following a variable can be swallowed into the variable token in expressions without spaces. The `|` error message says "single stray '||'". Constructor does not check for trailing tokens after `consumeBlock()`. `isValid()` evaluates variables on an empty proto, which validates attribute names but may perform formatting defaults. Tests should cover lexer errors, missing spaces around parentheses/operators, unsupported OR, trailing garbage, invalid variables, short-circuit behavior, and literal/attribute comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/FileMetadataFilter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/FileMetadataFilter.hh -->
## sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/FileMetadataFilter.hh

Purpose: Declares file metadata filter abstractions and the expression lexer/parser used by QuarkDB inspector tools.

Important APIs and types: `FileMetadataFilter` is the abstract interface with `isValid()`, `check()`, and `describe()`. `StringEvaluator` represents either a literal string or metadata variable. `EqualityFileMetadataFilter` compares two evaluators. `LogicalMetadataFilter` composes two filters with AND/OR semantics. `TokenType` and `ExpressionLexicalToken` model the expression language. `FilterExpressionLexer::lex()` tokenizes strings; `FilterExpressionParser` parses input and returns a filter plus status.

State and integration: parser/filter objects own their composed subfilters via `unique_ptr`. The interface is designed for inspectors scanning many `FileMdProto` records and applying the same parsed predicate repeatedly.

Dependencies: `FileMdProto`, EOS namespace macros, and `common::Status`.

Risks and test signals: the grammar supported by implementation is narrower than the enum suggests. Callers must check `getStatus()` before using `getFilter()`, and must call `getFilter()` only once. Tests should verify `describe()` stability, validity reporting, parser ownership transfer, and expected grammar documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/FileMetadataFilter.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/FileScanner.cc -->
## sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/FileScanner.cc

Purpose: Implements full-namespace scanning for file metadata, with optional asynchronous parent-path resolution.

Important APIs and control flow: `FileScannerPrimitive` iterates `eos-file-md` through `QLocalityHash`, deserializes each value into `FileMdProto`, tracks scanned count, and stores deserialization error text. `FileScanner` wraps it. In direct mode it delegates calls to the primitive. In full-path mode, `ensureItemDequeFull()` prefetches up to 500 file protos and starts a `MetadataFetcher::resolveFullPath()` future for each file's container ID. `getItem()` returns the proto and optionally moves the buffered `Item` containing the future path.

State and persistence: read-only scan over QuarkDB metadata. Buffered mode has separate primitive progress and public `mScanned` consumption count.

Dependencies and integration: used by inspector commands and consistency checks that need to scan every file. Depends on `Serialization`, `MetadataFetcher`, `QLocalityHash`, `FileMdProto`, and folly futures.

Risks and test signals: active-mode `hasError()` has the same buffer-dependent behavior as `ContainerScanner`, potentially hiding errors after the deque is empty. Full path future resolves only the parent container path; consumers need to append or format the file name as appropriate. Tests should cover invalid serialized records, direct/buffered count differences, full-path future errors, item move semantics, and buffer refill.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/FileScanner.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/FileScanner.hh -->
## sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/FileScanner.hh

Purpose: Declares primitive and enhanced scanners for iterating all file metadata stored in QuarkDB.

Important APIs and types: `FileScannerPrimitive` offers iterator-style validity, advance, error, item, and scan-count methods. `FileScanner::Item` contains a file proto and future full path. `FileScanner` exposes the same iterator interface, adding optional path prefetching.

State and integration: the enhanced scanner keeps the primitive scanner, backend client reference, full-path flag, active flag, deque of prefetched items, and consumption count. It is a reusable utility under inspector code.

Dependencies: `QClient`, `QLocalityHash`, file metadata protobufs, and folly futures.

Risks and test signals: in non-active mode, the optional `Item*` argument to `getItem()` is ignored because the primitive only returns the proto. Callers requiring full path must instantiate with `fullPaths=true`. Tests should verify direct-mode behavior, active-mode default item futures, and that `valid()` reflects the deque rather than primitive validity when buffering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/FileScanner.hh -->
