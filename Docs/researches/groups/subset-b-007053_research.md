# subset-b-007053

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/interface/LockableNSObject.hh -->
# sources/distributed-fs/eos/namespace/interface/LockableNSObject.hh

Purpose: defines the lockable base for namespace metadata objects, providing read/write lock aliases, per-thread lock tracking, and reentrant-safe helper methods used by file and container metadata implementations.

Important APIs/types/functions: `MDWriteLock` and `MDReadLock` alias `std::unique_lock<std::shared_timed_mutex>` and `std::shared_lock<std::shared_timed_mutex>`. `MapLockTracker` plus thread-local `mThreadIdWriteLockMap` and `mThreadIdReadLockMap` track how many times the current thread has registered a lock for a metadata object address. `LockableNSObjMD` exposes protected `runWriteOp`, `runReadOp`, `lock`, `tryLock`, `registerLock`, `unregisterLock`, `isLocked`, and pure virtual `getMutex`.

Control flow: `runWriteOp` and `runReadOp` check the thread-local tracker before taking the object mutex, avoiding self-deadlock when a locked method calls another locked getter or setter. `lock` acquires only when the object is not already tracked for the requested access and then registers the lock. `tryLock` returns false only when the underlying try-lock fails and otherwise registers recursive ownership. A write lock is also registered as a read lock so reads inside write-locked sections do not attempt to reacquire the mutex.

State and persistence: no persistent state. The only state is thread-local recursion counters keyed by `std::uintptr_t(this)`, plus each derived object’s shared timed mutex.

Dependencies and integration: used by `NSObjectLocker.hh` and by metadata classes implementing `IFileMD` or `IContainerMD`, including `QuarkFileMD` and `QuarkContainerMD`. Depends on `Namespace.hh` and `MDException.hh` for EOS namespace/error conventions.

Risks: tracking by raw object address assumes object lifetime outlives registered locks and that all lock wrappers correctly unregister. Counter imbalance can cause later operations in the same thread to skip real locking. Write locks register in both maps, so unregister ordering must remain symmetric. `std::shared_timed_mutex` semantics do not permit upgrades, so calling write paths while only read-locked remains unsafe.

Test signals: exercised indirectly by QuarkDB metadata tests and specifically by locking-focused test fixtures using `MockContainerMD` plus `BulkNsObjectLocker` tests in `sources/distributed-fs/eos/namespace/ns_quarkdb/tests/HierarchicalViewTest.cc` and `OtherTests.cc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/interface/LockableNSObject.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/interface/Misc.hh -->
# sources/distributed-fs/eos/namespace/interface/Misc.hh

Purpose: provides a small shared metadata interface struct for namespace cache statistics.

Important APIs/types/functions: `CacheStatistics` has fields `enabled`, `maxNum`, `occupancy`, `inFlight`, `numRequests`, and `numHits`, all default-initialized.

Control flow: none; this is a data-only header.

State and persistence: no internal state or persistence. Instances represent a snapshot of cache configuration, capacity, occupancy, inflight fetches, and hit/request counters.

Dependencies and integration: included by namespace service interfaces and implementations that report metadata cache status, such as QuarkDB file/container metadata services.

Risks: counters are plain values in the snapshot; producers must collect them under their own synchronization if they need consistency. The struct does not encode units beyond field names.

Test signals: indirectly covered where file/container service cache statistics are asserted or exposed through namespace monitoring paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/interface/Misc.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/locking/BulkNsObjectLocker.hh -->
# sources/distributed-fs/eos/namespace/locking/BulkNsObjectLocker.hh

Purpose: implements bulk RAII locking for multiple namespace metadata objects while imposing deterministic lock ordering to reduce deadlock risk.

Important APIs/types/functions: `BulkNsObjectLocker<TryLockerType>` accepts objects via `add` and acquires them with `lockAll`. Its nested `LocksVector` owns `std::unique_ptr<TryLockerType>` entries and destroys them in reverse insertion order. `BulkMultiNsObjectLocker<ContainerTryLockerType, FileTryLockerType>` locks container and file sets together, returning nested `Locks` that releases files before containers.

Control flow: single-type bulk locking stores objects in a `std::map` keyed by metadata identifier, so `lockAll` tries locks in ascending id order. If any try-lock fails, callers release accumulated locks and retry until all are held. Multi-locking first tries all containers, then all files; on file failure it releases file locks then container locks and retries with exponential backoff from 10 microseconds to 10 milliseconds.

State and persistence: in-memory only. The locker stores object shared pointers until locking; returned `LocksVector`/`Locks` own the active lock wrappers.

Dependencies and integration: depends on `IContainerMD`, `IFileMD`, and `MDLocking.hh` lock typedefs. It composes with `NSObjectMDTryLock` and the thread-local reentrant tracking in `LockableNSObject.hh`. Used by hierarchical namespace operations that need consistent multi-object locking.

Risks: retry loops can spin indefinitely if another thread continuously holds conflicting locks. Identifier ordering prevents many but not all logical deadlocks when callers mix bulk and non-bulk locking. Duplicate ids collapse in the map, so callers should not expect repeated locks. Move assignment for `Locks` lacks an explicit return statement, which is a C++ correctness warning/risk if used.

Test signals: targeted by `BulkNsObjectLocker` and `BulkNsObjectLockerTryLock` tests in `sources/distributed-fs/eos/namespace/ns_quarkdb/tests/HierarchicalViewTest.cc`, with mock metadata types in `MockContainerMD.hh`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/locking/BulkNsObjectLocker.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/locking/NSObjectLocker.hh -->
# sources/distributed-fs/eos/namespace/locking/NSObjectLocker.hh

Purpose: defines the RAII lock wrappers for individual namespace metadata objects, covering blocking and try-lock modes.

Important APIs/types/functions: `NSObjectMDBaseLock<ObjectMDPtr, LockType>` validates the pointer, constructs a deferred lock on `objectMDPtr->getMutex()`, and exposes `operator->` plus `getUnderlyingPtr`. `NSObjectMDLock` calls the object’s `lock` helper in the constructor and unregisters in the destructor. `NSObjectMDTryLock` calls `tryLock`, exposes `locked()`, and unregisters only when acquisition succeeded.

Control flow: construction throws `MDException(ENOENT)` for null metadata pointers. Successful wrappers delegate actual lock acquisition and recursive tracking to `LockableNSObjMD`. Destruction unregisters the lock tracker before the underlying `LockType` releases on its own destruction.

State and persistence: in-memory RAII state only: a metadata shared pointer and a lock object. The member order intentionally destroys the lock before the shared pointer to avoid metadata destruction while locking machinery may still be active.

Dependencies and integration: included by `MDLocking.hh` aliases for container/file read/write locks and try-locks. Integrates tightly with `LockableNSObject.hh`.

Risks: callers must check `locked()` for try locks before dereferencing for protected mutation. The wrappers rely on derived metadata objects implementing `getMutex`, `registerLock`, and `unregisterLock` consistently. Pointer lifetime and lock lifetime ordering is intentionally delicate.

Test signals: indirectly covered by metadata service operations and directly by bulk locking tests that instantiate try-lock wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/locking/NSObjectLocker.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/locking/RawPtr.hh -->
# sources/distributed-fs/eos/namespace/locking/RawPtr.hh

Purpose: supplies lightweight pointer helpers for lock templates or APIs that need pointer-like access without ownership.

Important APIs/types/functions: `no_delete` is a no-op deleter. `raw_ptr<T>` exposes `element_type`, `pointer`, `get`, `operator*`, `operator->`, bool conversion, and inequality comparison.

Control flow: trivial pointer forwarding; no allocation, deletion, or locking.

State and persistence: stores one raw pointer and never owns or persists it.

Dependencies and integration: lives in the EOS namespace and can satisfy template expectations similar to smart pointers, especially where object locks should operate on raw metadata objects without extending lifetime.

Risks: lifetime is entirely external. Dereferencing null or stale pointers is undefined. The inequality operator is non-const, limiting use with const `raw_ptr` values.

Test signals: covered only through consumers that instantiate lock/helper templates with raw metadata pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/locking/RawPtr.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/CMakeLists.txt -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/CMakeLists.txt

Purpose: builds and installs the QuarkDB-backed EOS namespace library and related inspection/conversion tools.

Important APIs/types/functions: declares `EosNsQuarkdb`, adds the `tests` subdirectory, links against namespace/common libraries, qclient, RocksDB, BZip2, and threads, and builds executables `eos-ns-convert-to-locality-hashes`, `eos-ns-inspect`, `eos-fid-to-path`, and `eos-inode-to-fid`.

Control flow: CMake configures include directories, compiles the library sources, links dependencies, installs the shared/static/runtime artifacts, then defines and installs the standalone utilities.

State and persistence: build configuration only. It controls installed binaries and library linkage, not runtime namespace data.

Dependencies and integration: integrates QuarkDB namespace code with `EosNsCommon`, `qclient`, `ROCKSDB::ROCKSDB`, `BZ2::BZ2`, `CLI11::CLI11`, and test targets.

Risks: missing or incompatible qclient/RocksDB/BZip2 dependencies break the namespace backend build. Tools link mostly against `EosNsCommon-Static`, so source list and library boundaries must stay consistent when new implementation files are added.

Test signals: `add_subdirectory(tests)` wires the QuarkDB namespace test suite into the build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/CacheRefreshListener.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/CacheRefreshListener.cc

Purpose: implements QuarkDB pub/sub callbacks that invalidate MGM metadata caches when external tooling modifies file or container metadata.

Important APIs/types/functions: the constructor creates a `qclient::Subscriber`, subscribes to `constants::sCacheInvalidationFidChannel` and `constants::sCacheInvalidationCidChannel`, and attaches callbacks to `processIncomingFidInvalidation` and `processIncomingCidInvalidation`. Each callback parses the payload with `common::ParseUInt64` and calls `MetadataProvider::dropCachedFileID` or `dropCachedContainerID`.

Control flow: subscription setup happens at construction. Incoming messages are logged, parsed as unsigned ids, and ignored if parsing fails. Valid ids are wrapped in `FileIdentifier` or `ContainerIdentifier` before cache-drop dispatch.

State and persistence: holds subscriptions for listener lifetime; does not persist anything. The effect is cache invalidation in the in-process metadata provider.

Dependencies and integration: depends on `QdbContactDetails`, `qclient/pubsub`, `Constants.hh`, `MetadataProvider.hh`, `Identifiers.hh`, and `ParseUtils`. Created by `QuarkNamespaceGroup::startCacheRefreshListener`.

Risks: callback uses a raw `MetadataProvider*`, so provider lifetime must outlive the listener. Invalid messages are silently ignored after logging only the payload. Subscription callback threading depends on qclient and must not race provider destruction.

Test signals: expected to be integration-tested with cache invalidation flows; direct unit tests are not visible in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/CacheRefreshListener.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/CacheRefreshListener.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/CacheRefreshListener.hh

Purpose: declares the cache refresh listener used to subscribe to metadata invalidation messages from QuarkDB.

Important APIs/types/functions: `CacheRefreshListener(const QdbContactDetails&, MetadataProvider*)`, destructor, private `processIncomingFidInvalidation`, `processIncomingCidInvalidation`, and members for contact details, metadata provider, qclient subscriber, and fid/cid subscriptions.

Control flow: construction and destruction own subscriber/subscription lifetime; callbacks are private implementation details.

State and persistence: stores subscriber state and raw provider pointer only; no persistent data.

Dependencies and integration: integrates qclient pub/sub with the namespace `MetadataProvider`. Used by `NamespaceGroup`.

Risks: raw pointer lifetime and asynchronous callback shutdown ordering are the main hazards. Subscription channels must match the constants used by external invalidation tools.

Test signals: cache invalidation behavior should be covered by integration tests or inspector tooling that publishes invalidation events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/CacheRefreshListener.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/ConfigurationParser.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/ConfigurationParser.hh

Purpose: parses a namespace configuration map into `QdbContactDetails`.

Important APIs/types/functions: `ConfigurationParser::parse` requires `qdb_cluster`, optionally reads `qdb_password`, fills `qclient::Members`, and throws `MDException(EINVAL)` on missing or unparsable cluster data.

Control flow: find mandatory cluster key, parse into members, optionally copy password, return contact details.

State and persistence: stateless parser; all output is in the returned value.

Dependencies and integration: uses qclient `Members`, `Options`, `Handshake`, `QdbContactDetails`, and EOS exception helpers. Similar parsing logic is also present in `QuarkNamespaceGroup::initialize`.

Risks: duplicated parsing logic can diverge from namespace group initialization. It does not validate password with the cluster, only stores it.

Test signals: configuration failure and success cases should be covered through namespace group/plugin initialization tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/ConfigurationParser.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/Constants.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/Constants.hh

Purpose: centralizes key names, suffixes, configuration tags, pub/sub channels, quota keys, and filesystem-view prefixes used by the QuarkDB namespace backend.

Important APIs/types/functions: `constants` includes metadata hash keys, child map suffixes, `meta_map` fields, orphan file set, cache limit option names, invalidation channels, and inode refresh key. `quota` defines quota map prefix and metric suffixes. `fsview` defines filesystem set prefix/suffixes and the no-replica set key.

Control flow: none; string constants only.

State and persistence: these strings define persistent QuarkDB key schema. Changing them affects compatibility with existing namespace data.

Dependencies and integration: consumed by metadata services, views, accounting, cache refresh, inspector tools, and migration/conversion utilities.

Risks: spelling and compatibility are critical. Key changes require migration. The no-replica key is a prefix-like constant but is returned as the full key by `FileSystemHandler`.

Test signals: broad QuarkDB namespace tests indirectly validate key conventions by creating, loading, and inspecting persisted metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/Constants.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/ContainerMD.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/ContainerMD.cc

Purpose: implements `QuarkContainerMD`, the protobuf-backed directory/container metadata object for the QuarkDB namespace.

Important APIs/types/functions: constructors initialize ids, default mode, dense hash map sentinels, service pointers, flusher keys, and clocks. Major methods include `setServices`, `clone`, `InheritChildren`, `findItem`, `addContainer`, `removeContainer`, `addFile`, `removeFile`, permission `access`, name/time/tree/xattr mutators, `serialize`, `deserialize`, `loadChildren`, `initialize`, `initializeWithoutChildren`, `getEnv`, `copyContainerMap`, and `copyFileMap`.

Control flow: child lookup checks local child-name maps under read lock, then asynchronously asks file/container services for resolved ids. Add/remove operations validate empty names and name conflicts across file and container maps, mutate in-memory maps, write hash updates through `MetadataFlusher`, and notify file listeners with tree counter deltas. Serialization writes aligned protobuf bytes plus CRC32C and raw object size; deserialization delegates checksum parsing to `Serialization` then reloads child maps from QuarkDB through `MetadataFetcher`.

State and persistence: primary state is `ContainerMdProto mCont`, lazy `FutureWrapper` maps of files and subcontainers, qclient/flusher service pointers, derived QuarkDB child-map keys, and a high-resolution `mClock`. Persistent state lives in protobuf metadata plus per-container hash maps keyed by id suffixes.

Dependencies and integration: depends on file/container metadata services, `MetadataFlusher`, `MetadataFetcher`, `Serialization`, `PermissionHandler`, `DataHelper` CRC helpers, protobuf, qclient, and listener events. It is created by `QuarkContainerMDSvc` and used by hierarchical views/accounting.

Risks: child map and protobuf parent/name state must remain synchronized with services. `getName` returns a const reference into the protobuf protected by a lock only during access, so callers must not assume long-lived thread safety. Add/remove listener events use `location` as a container id hack. Copy constructor copies service pointers and maps keys but not child maps. Time fields are stored as raw `timespec` bytes, tying persisted representation to layout assumptions.

Test signals: `MetadataTests.cc` covers file/container serialization/deserialization; `VariousTests.cc` covers etag/env formatting through `FRIEND_TEST`; hierarchical tests exercise add/remove and tree behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/ContainerMD.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/ContainerMD.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/ContainerMD.hh

Purpose: declares `QuarkContainerMD`, the QuarkDB implementation of `IContainerMD`.

Important APIs/types/functions: exposes container/file child management, async and sync lookup, metadata getters/setters for ids, ownership, modes, flags, clone data, xattrs, tree counters, access checks, serialization/deserialization, initialization, environment formatting, iterators, and map-copy helpers. Private members include `ContainerMdProto`, service/flusher/qclient pointers, child-map keys, `mClock`, and lazy child maps.

Control flow: most inline getters/setters wrap protobuf access with `runReadOp` or `runWriteOp` inherited from `LockableNSObjMD`. Iterator begin/end methods intentionally skip locking because iterator wrappers lock around use. Generation methods derive values from dense hash map bucket state and end iterator address to detect invalidation.

State and persistence: declares all state for container protobuf metadata and child maps. Persistent representation is the protobuf plus QuarkDB hashes for child ids.

Dependencies and integration: implements `IContainerMD`, depends on `IFileMD`, `MetadataFlusher`, protobuf, qclient, and `FutureWrapper`. Services inject dependencies through constructor or `setServices`.

Risks: many inline methods return protobuf-derived values while hiding lock acquisition, but reference-returning APIs need careful caller lifetime handling. The default constructor leaves services null for tests/dumps, so methods that touch flusher/qclient are invalid in standalone mode. Iterator generation relies on implementation details of the underlying map.

Test signals: mock/test constructors are used in QuarkDB namespace tests; `FRIEND_TEST(VariousTests, EtagFormattingContainer)` targets formatting behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/ContainerMD.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/FileMD.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/FileMD.cc

Purpose: implements `QuarkFileMD`, the protobuf-backed file metadata object for the QuarkDB namespace.

Important APIs/types/functions: constructors, copy/assignment, `clone`, `setName`, location lifecycle methods (`addLocation`, `unlinkLocation`, `removeLocation`, bulk variants), `getEnv`, `serialize`, `initialize`, `deserialize`, `getProto`, `setSize`, time getters/setters, xattr map copy, unlinked-location checks, and alternate checksum methods.

Control flow: mutations use `runWriteOp`; reads use `runReadOp`. Location add/unlink/remove update repeated protobuf fields and notify file service listeners with `LocationAdded`, `LocationUnlinked`, or `LocationRemoved`. `setSize` masks size to 48 bits, computes signed delta, and emits `SizeChange`. Serialization mirrors container serialization with aligned protobuf bytes and CRC32C. `setMTimeNow` resets sync time to zero so sync time falls back to mtime.

State and persistence: primary state is `FileMdProto mFile`, service pointer, and `mClock`. Persistent state is serialized protobuf with checksum/size envelope. Locations, unlinked locations, checksums, xattrs, symlink target, layout, flags, ownership, and times are stored in the protobuf.

Dependencies and integration: depends on `QuarkFileMDSvc`, `Serialization`, `DataHelper`, checksum/string conversion helpers, protobuf, and file change listeners. Files are managed by `QuarkFileMDSvc`, referenced by containers, filesystem view, quota/accounting, and inspector tools.

Risks: assignment copies protobuf and clock but resets `pFileMDSvc` to null, so copied objects cannot notify unless service is reset. Location unlink emits an event even if the location was not found. `getProto` returns a reference without locking for the caller lifetime. Time fields are raw byte copies. `setSize` truncates to 48 bits by design but can surprise callers.

Test signals: `MetadataTests.cc` covers serialization/deserialization; `VariousTests.cc` covers etag/env formatting and alternate checksum behavior; filesystem/accounting tests exercise location and size listener paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/FileMD.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/FileMD.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/FileMD.hh

Purpose: declares `QuarkFileMD`, the QuarkDB implementation of `IFileMD`.

Important APIs/types/functions: exposes id, container id, size, clone metadata, checksum, name, locations, unlinked locations, ownership, layout, flags, link, xattrs, serialization/deserialization, protobuf initialization/access, clock, and alternate checksum APIs. It also declares no-lock helper methods for times and location checks.

Control flow: inline methods wrap protobuf fields with `runReadOp`/`runWriteOp`. Non-inline methods handle validation, listener notification, serialization, and repeated-field manipulation.

State and persistence: declares `FileMdProto mFile`, `pFileMDSvc`, and `mClock`; all durable file metadata is in the protobuf.

Dependencies and integration: implements `IFileMD`, depends on `FileMDSvc.hh` for the Quark service type and `FileMd.pb.h` for storage schema. `FileSystemView` is a friend for direct access.

Risks: friend access and public `getProto` can bypass lock discipline. Default constructor leaves service null for tests/dumps. Some APIs return copies while others expose references through later implementation, so caller expectations need care.

Test signals: `FRIEND_TEST(VariousTests, EtagFormatting)` and metadata tests cover important formatting and serialization paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/FileMD.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/LRU.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/LRU.hh

Purpose: implements a bounded LRU cache for namespace metadata objects that avoids evicting entries still referenced outside the cache.

Important APIs/types/functions: `hasGetId<EntryT>` detects required `getId`. `LRU<IdT, EntryT>` exposes `get`, `put`, `remove`, `size`, `GetMaxNum`, `SetMaxNum`, `GetRequests`, and `GetHits`. Private `Purge` evicts unreferenced old entries; `CleanerJob` asynchronously resets evicted shared pointers.

Control flow: `get` increments request count, finds an id, moves the object to the list tail, increments hits, and returns it. `put` refuses caching when max is zero, returns existing cached object for duplicate ids, purges when full, then inserts at the tail. `Purge` walks from least recently used, skips objects with `use_count() > 1`, erases ids for unreferenced objects, queues them for cleaner disposal, and compacts the dense hash map.

State and persistence: in-memory cache state includes dense hash map id-to-list iterator, list of shared objects, mutex, max size, atomic counters, deletion queue, and cleaner thread. No persistent state.

Dependencies and integration: used by QuarkDB file/container metadata services for object caches. Depends on Google dense hash map, Murmur3 hashing, `ConcurrentQueue`, and `AssistedThread`.

Risks: objects with external references can prevent cache size from falling below target. Dense hash sentinel keys reserve `UINT64_MAX-1` and `UINT64_MAX`-like ids, so id domains must avoid those values. Cleaner shutdown uses a null sentinel and relies on assisted thread termination ordering. `mAvgRtt` issue is elsewhere; here counters are straightforward.

Test signals: `sources/distributed-fs/eos/namespace/ns_quarkdb/tests/LruBenchmark.cc` and cache-related service tests exercise performance and behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/LRU.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/NamespaceGroup.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/NamespaceGroup.cc

Purpose: implements `QuarkNamespaceGroup`, the lifecycle and dependency owner for the QuarkDB namespace plugin.

Important APIs/types/functions: constructor creates a 48-thread `folly::IOThreadPoolExecutor`. `initialize` parses config keys, creates performance monitor, validates QuarkDB version, and records flusher options. Getter methods lazily create file/container services, hierarchical view, filesystem view, accounting views, quota stats, flushers, qclient, executor, cache refresh listener, and performance monitor.

Control flow: initialization requires `queue_path`, `qdb_cluster`, `qdb_flusher_md`, and `qdb_flusher_quota`, optionally reads `qdb_password`, `qclient_flusher_type`, and `qclient_rocksdb_options`, then calls `enforceQuarkDBVersion(getQClient())`. Lazy getters lock a recursive mutex and construct dependencies in dependency order. Destructor tears down listener, accounting, views, services, flushers, qclient, executor, and monitor in explicit order.

State and persistence: stores configuration strings, contact details, recursive mutex, executor, flushers, qclient, services, views, accounting listeners, cache listener, and performance monitor. Persistent namespace state is accessed through qclient and flushers, not stored here.

Dependencies and integration: integrates the plugin with `QuarkFileMDSvc`, `QuarkContainerMDSvc`, `QuarkHierarchicalView`, `QuarkFileSystemView`, `QuarkContainerAccounting`, `QuarkSyncTimeAccounting`, `MetadataFlusher`, `CacheRefreshListener`, `QClPerfMonitor`, and version enforcement.

Risks: initialization creates qclient before optional flusher type parsing, so version checks use default contact options. Lazy construction means call ordering matters for listener registration. Executor must outlive qclient, documented by the destructor order. `startCacheRefreshListener` assumes file service and metadata provider are initialized.

Test signals: plugin/namespace integration tests under `ns_quarkdb/tests` exercise service/view creation and end-to-end namespace behavior; configuration errors are visible through `initialize` return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/NamespaceGroup.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/NamespaceGroup.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/NamespaceGroup.hh

Purpose: declares the QuarkDB namespace group implementation of `INamespaceGroup`.

Important APIs/types/functions: public API includes `initialize`, service/view/accounting/quota getters, `isInMemory`, flusher getters, performance monitor getter, qclient getter, executor getter, and `startCacheRefreshListener`. Private members define all owned services and configuration.

Control flow: the header documents that `initialize` must be called before other functions and that the executor must outlive qclient to avoid qclient future continuations referencing a destroyed executor.

State and persistence: owns runtime objects through `std::unique_ptr` and the performance monitor through `std::shared_ptr`; no direct persistence.

Dependencies and integration: implements `INamespaceGroup` contract consumed by the plugin manager and namespace users. Provides central access to QuarkDB backend components.

Risks: many getters return raw pointers into owned members, so consumers must not outlive the group. Recursive mutex allows nested lazy getter calls, but can also hide complex construction cycles.

Test signals: namespace tests instantiate group/services either directly or through plugin-like setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/NamespaceGroup.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/NsQuarkdbPlugin.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/NsQuarkdbPlugin.cc

Purpose: implements the plugin entry points that register and create the QuarkDB namespace group.

Important APIs/types/functions: `ExitFunc`, `PF_initPlugin`, optional `plugin_coverage` for coverage builds, `NsQuarkdbPlugin::CreateGroup`, and `DestroyGroup`.

Control flow: `PF_initPlugin` constructs `PF_RegisterParams` for `"NamespaceGroup"`, registers it with platform services, and returns `ExitFunc` on success or `nullptr` on registration failure. `CreateGroup` returns `new QuarkNamespaceGroup`; `DestroyGroup` deletes the object or returns `-1` for null.

State and persistence: no persistent state; plugin registration only.

Dependencies and integration: depends on EOS plugin manager ABI, `NamespaceGroup.hh`, and standard streams for registration messages. The plugin manager calls these C-linkage entry points.

Risks: object type safety depends on plugin manager pairing create/destroy correctly. Registration prints to stdout/stderr, which may be undesirable in some daemon contexts. `services` is not null-checked.

Test signals: covered by plugin loading tests or runtime namespace backend selection; coverage builds can call `plugin_coverage`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/NsQuarkdbPlugin.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/NsQuarkdbPlugin.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/NsQuarkdbPlugin.hh

Purpose: declares C ABI plugin entry points and the static factory/destroy wrapper for the QuarkDB namespace plugin.

Important APIs/types/functions: `extern "C" int32_t ExitFunc()`, `extern "C" PF_ExitFunc PF_initPlugin(...)`, `NsQuarkdbPlugin::CreateGroup`, and `DestroyGroup`.

Control flow: declarations only.

State and persistence: none.

Dependencies and integration: includes `Plugin.hh` and `Namespace.hh`; consumed by the plugin implementation and plugin manager.

Risks: ABI signatures must remain stable with the plugin framework. Returned `void*` requires correct cast in destroy path.

Test signals: plugin loading/registration tests cover this interface indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/NsQuarkdbPlugin.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/QClPerformance.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/QClPerformance.cc

Purpose: implements qclient performance metric collection for QuarkDB round-trip times.

Important APIs/types/functions: `QClPerfMonitor::SendPerfMarker` handles `"rtt_us"` markers, updating min, max, average, and per-minute peak map. `GetPerfMarkers` returns `rtt_min`, `rtt_max`, `rtt_avg`, `rtt_peak_1m`, `rtt_peak_2m`, and `rtt_peak_5m`.

Control flow: each RTT marker updates atomics and, under mutex, removes entries older than five minutes, updates the current minute peak, or inserts a new minute bucket. Metric collection scans recent buckets from newest to oldest to compute peak windows.

State and persistence: in-memory atomics and a mutex-protected minute-to-peak map. Metrics reset with process/group lifetime.

Dependencies and integration: implements `qclient::QPerfCallback` and is attached to qclient options by `QuarkNamespaceGroup::getQClient`.

Risks: average is an exponential-ish rolling average, not arithmetic mean. Initial `mMinRtt` is max integer until first marker. Atomic compare/update is not CAS-based, so concurrent updates may lose exact min/max races but remain approximate monitoring. `current_ts - 5` can underflow only at epoch-adjacent times.

Test signals: observable through namespace monitoring; no direct test in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/QClPerformance.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/QClPerformance.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/QClPerformance.hh

Purpose: declares `QClPerfMonitor`, a qclient callback implementation for collecting QuarkDB RTT metrics.

Important APIs/types/functions: constructor initializes min/max/avg, `SendPerfMarker` receives performance callbacks, and `GetPerfMarkers` returns a metrics map. State includes atomic min/max/avg, timestamp-to-peak map, and mutex.

Control flow: callback and collection methods are implemented in the `.cc`.

State and persistence: transient process-local metrics only.

Dependencies and integration: derives from `qclient::QPerfCallback`; returned through namespace group performance monitor.

Risks: callback must stay fast because qclient invokes it from its event loop. The internal map is small but still mutex-protected inside callback.

Test signals: integration monitoring can validate marker emission and returned keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/QClPerformance.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/QdbContactDetails.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/QdbContactDetails.hh

Purpose: packages qclient cluster membership and optional password/handshake settings for QuarkDB access.

Important APIs/types/functions: constructors, `empty`, `constructOptions`, and `constructSubscriptionOptions`. Options enable transparent redirects, two-minute retry timeout, optional HMAC handshake, and push subscriptions for pub/sub.

Control flow: option builders allocate an `HmacAuthHandshake` only when password is non-empty and otherwise return unauthenticated options.

State and persistence: stores `qclient::Members members` and `std::string password`; no persistence.

Dependencies and integration: used by namespace group, metadata flushers, qclient creation, and cache refresh listener.

Risks: password is stored as a plain string in memory. `empty` does not treat missing password as invalid. Retry timeout choices affect failure latency for startup and subscriptions.

Test signals: configuration/parser and integration tests validate member parsing and connection behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/QdbContactDetails.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/VersionEnforcement.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/VersionEnforcement.cc

Purpose: checks that the connected QuarkDB cluster meets the minimum namespace backend version requirement.

Important APIs/types/functions: `enforceQuarkDBVersion(qclient::QClient*)` executes `quarkdb-version`, parses the reply into `qclient::QuarkDBVersion`, compares with target `0.4.2`, logs failures, and returns a boolean.

Control flow: synchronous qclient command waits on `.get()`, logs the reply, parses version text, rejects parse failures and versions older than target, otherwise returns true.

State and persistence: stateless; reads server version only.

Dependencies and integration: called during `QuarkNamespaceGroup::initialize` before successful backend startup.

Risks: assumes non-null reply with string fields; malformed or null replies may crash before parse failure handling. Startup blocks on qclient retry behavior. Target version is hard-coded.

Test signals: integration tests with mocked or real qclient version replies should cover accept/reject paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/VersionEnforcement.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/VersionEnforcement.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/VersionEnforcement.hh

Purpose: declares the QuarkDB version enforcement function.

Important APIs/types/functions: `bool enforceQuarkDBVersion(qclient::QClient *qcl)`.

Control flow: declaration only.

State and persistence: none.

Dependencies and integration: includes qclient version type and forward-declares `QClient`; used by namespace group initialization.

Risks: callers need a live, connected qclient and must handle a false result as startup failure.

Test signals: covered through namespace initialization/version-check tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/VersionEnforcement.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/ContainerAccounting.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/ContainerAccounting.cc

Purpose: implements delayed propagation of file/container subtree accounting deltas up the container hierarchy.

Important APIs/types/functions: constructor starts propagation and queueing `AssistedThread`s when update interval is nonzero. Destructor queues id `0` sentinel and joins. `fileMDChanged`, `AddTree`, `RemoveTree`, `QueueForUpdate`, `PropagateUpdates`, `AsyncQueueForUpdate`, and assisted wrappers implement the accounting flow.

Control flow: file size/tree-change events enqueue the affected container id, using event `location` as container id when no file pointer is present. `AsyncQueueForUpdate` consumes queued deltas, walks parents up to root or depth 255 via `IContainerMDSvc::getContainerMD`, accumulates deltas for each ancestor in the active batch, and stops on sentinel id 0. `PropagateUpdates` swaps accumulate/commit batches, locks each target container for writing, updates tree size/file/container counters, and calls `updateStore`, then sleeps for the configured interval.

State and persistence: in-memory double-buffered batches, mutex, two assisted threads, queue of `(container id, TreeInfos)`, update interval, and container service pointer. Persistent effect is updated container metadata written through `IContainerMDSvc::updateStore`.

Dependencies and integration: registered by `QuarkNamespaceGroup` as a file change listener and injected into container service. Depends on `IFileMDChangeListener`, `IContainerMDSvc`, `MDLocking`, `TreeInfos`, and `ConcurrentQueue`.

Risks: id 0 is reserved as shutdown sentinel; accidental id 0 updates are dropped. Parent walk depth cap can miss pathological trees deeper than 255. Exceptions during propagation are swallowed, leaving counters stale until another repair. Asynchronous batching delays visible accounting updates. Destructor queues sentinel before joining but does not explicitly stop the propagation thread through a sentinel.

Test signals: tree accounting is exercised through hierarchical namespace tests and file size/container add/remove paths; direct tests should assert delayed propagation with update interval 0 and async modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/ContainerAccounting.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/ContainerAccounting.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/ContainerAccounting.hh

Purpose: declares `QuarkContainerAccounting`, the file-change listener that maintains container subtree counters.

Important APIs/types/functions: implements `IFileMDChangeListener` methods `fileMDChanged`, `fileMDRead`, and `fileMDCheck`; exposes `AddTree`, `RemoveTree`, `QueueForUpdate`, `PropagateUpdates`, and `AsyncQueueForUpdate`. Private state includes `UpdateT`, two batches, mutex, accumulate/commit indices, assisted threads, update interval, container service pointer, and update queue.

Control flow: the header defines the public/assisted split: one thread queues ancestor updates, another commits accumulated batches.

State and persistence: transient batching state; persistent updates are performed by implementation through the container metadata service.

Dependencies and integration: depends on namespace interfaces, assisted threading, standard threading containers, and concurrent queue.

Risks: copy/move are deleted because thread and service ownership are nontrivial. Thread lifecycle and queue sentinel protocol must match the implementation.

Test signals: hierarchical/accounting behavior should be validated by namespace tests that inspect tree counters after mutations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/ContainerAccounting.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/FileSystemHandler.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/FileSystemHandler.cc

Purpose: implements cached and streaming access to QuarkDB filesystem file-id sets for regular, unlinked, and no-replica lists.

Important APIs/types/functions: constructors set target and dense hash sentinels. `ensureContentsLoaded`, `ensureContentsLoadedAsync`, `getRedisKey`, `triggerCacheLoad`, `insert`, `erase`, `size`, `getFileList`, `getStreamingFileList`, `nuke`, `getApproximatelyRandomFile`, `hasFileId`, and `clearCache` form the API.

Control flow: first load transitions cache from `kNotLoaded` to `kInFlight`, creates a `FutureSplitter` around `folly::via(pExecutor).then(triggerCacheLoad)`, and returns futures to all waiters. `triggerCacheLoad` synchronizes the flusher, streams the QDB set into a temporary dense hash set, then swaps it into `mContents` under lock and applies any concurrent `SetChangeList` operations. `insert`/`erase` update in-memory cache or change list depending on cache state, then enqueue `SADD`/`SREM` through the flusher. `size` uses cached size when loaded or direct `SCARD` otherwise. Cache clearing drops loaded contents after inactivity if it can acquire the mutex quickly.

State and persistence: in-memory cache status, target, location, qclient/flusher/executor pointers, shared timed mutex, dense hash file-id set, change list, future splitter, last-load timestamp, and steady clock. Persistent state is the QuarkDB set selected by `getRedisKey`.

Dependencies and integration: used by `QuarkFileSystemView`. Depends on `RequestBuilder`, `MetadataFlusher`, qclient `QSet`, folly futures/executor, `SetChangeList`, `FileListRandomPicker`, and filesystem-view constants.

Risks: `ensureContentsLoadedAsync` returns `mSplitter.getFuture()` even when status is `kLoaded`; correctness depends on the splitter retaining the completed future. Streaming iterators are weakly consistent and can race flusher state. `nuke` calls flusher while holding the mutex. `clearCache` uses a short timed lock and may skip cleanup under contention.

Test signals: `sources/distributed-fs/eos/namespace/ns_quarkdb/tests/FileSystemViewTest.cc` has direct `FileSystemHandler` and `FileSystemHandlerCache` tests covering loading, mutation, and cache clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/FileSystemHandler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/FileSystemHandler.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/FileSystemHandler.hh

Purpose: declares file-list iterators and the `FileSystemHandler` cache/controller for QuarkDB filesystem views.

Important APIs/types/functions: `FileListIterator` holds a shared lock over an in-memory `IFsView::FileList`. `StreamingFileListIterator` wraps `qclient::QSet::Iterator`. `FileSystemHandler` constructors target regular/unlinked/no-replica sets and expose loading, insert/erase, size, key lookup, iterators, `nuke`, random selection, membership, and cache clearing. Private `CacheStatus` and `Target` model cache state and set type.

Control flow: declarations establish two iterator modes: locked in-memory iteration and weakly consistent streaming iteration. Cache state transitions are implemented in the `.cc`.

State and persistence: declares all cache state, QDB/flusher pointers, change list, future splitter, last cache load timestamp, and test-visible cache status under `IN_TEST_HARNESS`.

Dependencies and integration: integrates `IFsView`, `IFileMD`, `SetChangeList`, qclient `QSet`, folly futures, executor async support, EOS assertions, and `SteadyClock`.

Risks: iterator validity depends on the chosen mode. In-memory iterator holds the shared lock for its lifetime, which can block writers. Streaming iterator converts QDB strings with `std::stoull` and will throw on corrupt set members.

Test signals: direct tests in `FileSystemViewTest.cc` target this class and expose `getCacheStatus` under test harness builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/accounting/FileSystemHandler.hh -->
