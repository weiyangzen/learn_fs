# subset-b-007056 research

Grouped research for EOS QuarkDB namespace persistency and tests. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/MetadataProviderShard.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/MetadataProviderShard.hh

Purpose: Declares `MetadataProviderShard`, the asynchronous QDB metadata fetch/cache shard used by QuarkDB-backed file and container services.
Important APIs/types/functions: constructor wires non-owning `qclient::QClient`, `IContainerMDSvc`, `IFileMDSvc`, and `folly::Executor`; public fetch APIs are `retrieveContainerMD`, `retrieveFileMD`, and `hasFileMD`; cache controls include drop/insert/set-size/stats methods; private `processIncomingFileMdProto` and `processIncomingContainerMD` convert protobuf/backend tuples into service-owned metadata objects.
Control flow: callers request metadata by ID, in-flight maps deduplicate concurrent fetches through `folly::FutureSplitter`, and completion handlers materialize objects before caching.
State/persistence: persistent state lives in QDB and protobufs; this class owns only in-memory LRU caches and in-flight futures guarded by `mMutex`.
Dependencies/integration: depends on `LRU`, QuarkDB metadata classes, service interfaces, qclient, and Folly futures; it is a backend boundary for `FileMDSvc`/`ContainerMDSvc`.
Risks: stale cache entries require invalidation via explicit drop/insert paths; non-owning pointers require services/client/executor lifetime discipline; FutureSplitter maps must be erased reliably on failures.
Test signals: `FileMDSvcTest.LoadTest` checks repeated futures for the same fid coalesce to one in-memory object; locking tests assert metadata retrieval should not lock the returned object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/MetadataProviderShard.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/NextInodeProvider.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/NextInodeProvider.cc

Purpose: Implements monotonic inode allocation backed by a QDB hash field, with local block reservation to reduce backend round trips.
Important APIs/types/functions: `InodeBlock::{reserve,getFirstFreeID,empty,blacklistBelow}`; `NextInodeProvider::{configure,getFirstFreeId,reserve,blacklistBelow}`; private `getDBValue`, `allocateInodeBlock`, and `blacklistDBThreshold`.
Control flow: `reserve()` first consumes the current `InodeBlock`; when empty, `allocateInodeBlock()` atomically advances `pHash[pField]` with `hincrby`, creates a local range, then returns the first value. `getFirstFreeId()` peeks local state or returns `getDBValue()+1`.
State/persistence: local state is `mInodeBlock` and growing `mStepIncrease`; durable high-water mark is the QDB hash value. Block size grows by one until just over 5000, trading restart waste for fewer QDB writes.
Dependencies/integration: uses `qclient::QHash`, EOS assertions/logging, and service constants through callers such as `UnifiedInodeProvider`.
Risks: `configure()` must precede use; `std::stoull` over signed storage and unchecked buffer format can throw; blacklisting only updates QDB when the local block is exhausted, so high-water mark can lag until needed.
Test signals: `NextInodeProviderTest` covers sequential allocation, restart continuation with tolerated gaps, blacklisting, off-by-one around `2^32`, negative thresholds, and multiple resets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/NextInodeProvider.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/NextInodeProvider.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/NextInodeProvider.hh

Purpose: Declares the block allocator and QDB-backed provider used to issue unique file/container inode IDs.
Important APIs/types/functions: `InodeBlock` models a contiguous `[start,start+len)` allocation with peek, reserve, empty, and blacklist operations. `NextInodeProvider` exposes `configure(qclient::QHash&, field)`, `getFirstFreeId()`, `reserve()`, and `blacklistBelow()`.
Control flow: users configure a hash field, call `reserve()` for the next ID, and optionally blacklist imported/restored IDs so future allocations skip them.
State/persistence: `InodeBlock` is in-memory only; `NextInodeProvider` persists only the largest reserved ID in QDB through a non-owning `QHash*` and field string. `mMtx` serializes provider operations.
Dependencies/integration: forward-declares `qclient::QHash`, relies on EOS namespace macros, and is composed by `UnifiedInodeProvider`.
Risks: header does not express configured/unconfigured state, so misuse is a runtime/null-pointer concern; comments contain minor spelling errors but not behavioral ambiguity; integer boundary handling is critical because EOS identifiers can exceed 32-bit ranges.
Test signals: standalone `InodeBlock` tests validate empty and negative-length blocks, reserve order, and blacklisting; provider tests validate QDB persistence semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/NextInodeProvider.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/RequestBuilder.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/RequestBuilder.cc

Purpose: Implements stateless factories for Redis/QuarkDB requests used by metadata services and filesystem accounting.
Important APIs/types/functions: `writeContainerProto` and `writeFileProto` serialize metadata objects into `eos::Buffer` and emit `LHSET`; low-level overloads accept ID, locality hint, and serialized blob; read/delete/count APIs emit `LHGET`, `LHDEL`, and `LHLEN`; invalidation APIs emit `PUBLISH`; filesystem-key helpers build `fsview:<location>:files` and `fsview:<location>:unlinked`.
Control flow: object overloads serialize through interface virtuals, convert identifiers with `stringify`/`SSTR`, and return vector<string> command payloads for qclient execution.
State/persistence: no state is stored here; commands target persistent keys from `namespace/ns_quarkdb/Constants.hh`.
Dependencies/integration: integrates `IFileMD`, `IContainerMD`, `Buffer`, EOS string conversion, and constants used by `FileSystemView`, services, and tests.
Risks: read APIs currently omit locality hints; command construction depends on exact key/channel constants; serialized blobs are opaque and must match `Serialization`/metadata object formats.
Test signals: `FileSystemView.FileSetKey` asserts filesystem key formats; service integration tests indirectly exercise read/write/delete/count command paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/RequestBuilder.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/RequestBuilder.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/RequestBuilder.hh

Purpose: Declares `RequestBuilder`, the central stateless command-construction API for QuarkDB namespace metadata.
Important APIs/types/functions: `RedisRequest` is `std::vector<std::string>`; static methods cover container/file protobuf writes, reads, deletes, metadata counts, cache invalidation publish messages, and filesystem accounting set keys.
Control flow: callers assemble a request locally and pass it to qclient/backends; this header intentionally exposes no execution or retry behavior.
State/persistence: no mutable state; persistence is represented by the target QDB command/key layout.
Dependencies/integration: includes namespace interface types and identifier wrappers; source implementation binds it to constants such as `sContainerKey`, `sFileKey`, and cache invalidation channels.
Risks: because commands are plain string vectors, there is no type-level distinction between command name, key, field, hint, and blob; adding new command formats requires test coverage for exact argument ordering.
Test signals: direct coverage exists for filesystem key helpers; broader service tests and metadata flush paths depend on stable command construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/RequestBuilder.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/Serialization.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/Serialization.cc

Purpose: Implements deserialization helpers for EOS metadata protobuf buffers and integer values with checksum/status handling.
Important APIs/types/functions: overloaded `deserializeNoThrow` for `FileMdProto`, `ContainerMdProto`, and `int64_t`; throwing wrappers `deserializeFile` and `deserializeContainer`.
Control flow: protobuf buffer decoding reads a CRC32C and object-size prefix, computes CRC32C over the remaining aligned payload, compares checksums, then parses protobuf through `google::protobuf::io::ArrayInputStream`. Integer decoding copies bytes into a null-terminated string and validates `strtoll` consumed the full input.
State/persistence: no retained state; it interprets the persisted binary layout produced by metadata serialization.
Dependencies/integration: depends on `Buffer`, `DataHelper` CRC32C, generated protobuf classes, `MDStatus`, and `MDException`.
Risks: the implementation assumes buffers contain at least two 32-bit fields; malformed/truncated buffers may read before returning `MDStatus`; `align_size` includes any padding while parser uses `obj_size`, so serialization format compatibility is strict.
Test signals: currently active tests do not directly cover this file; disabled `MetadataTests.cc` code shows intended checksum-corruption checks for file/container metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/Serialization.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/Serialization.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/Serialization.hh

Purpose: Declares the metadata deserialization facade used by QuarkDB services and metadata objects.
Important APIs/types/functions: `Serialization::deserializeFile`, `deserializeContainer`, non-throwing overloads for file/container protobufs and `int64_t`, plus templated `deserialize(const char*, size_t, T&)`.
Control flow: callers can choose exception-based wrappers or `MDStatus` returns. The template wraps raw memory in an `eos::Buffer` and dispatches to the matching overload.
State/persistence: stateless; its contract is the persisted buffer format and type-specific decoding.
Dependencies/integration: forward-declares protobuf types, includes `MDException` and `Buffer`, and depends on implementation checksumming/parsing.
Risks: the template uses `setDataPtr((char*)str, len)`, so callers must ensure the pointed memory outlives deserialization and is compatible with `Buffer` ownership semantics; only explicitly overloaded types are supported.
Test signals: disabled metadata serialization tests document intended coverage; active tests indirectly exercise deserialization when services reload metadata after `shut_down_everything()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/Serialization.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/UnifiedInodeProvider.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/UnifiedInodeProvider.cc

Purpose: Implements a facade that allocates file and container IDs either from separate counters or from one shared inode stream.
Important APIs/types/functions: `configure`, `reserveFileId`, `reserveContainerId`, blacklist methods, and first-free peeks for both ID classes.
Control flow: `configure()` reads `constants::sUseSharedInodes` from the metadata map. If `"yes"`, only the file provider is configured and both file/container operations route through it; otherwise, file and container providers use `sLastUsedFid` and `sLastUsedCid`.
State/persistence: holds a non-owning `QHash*`, `mSharedInodes`, and unique pointers to `NextInodeProvider`s. Persistent high-water marks remain in the QDB hash fields managed by those providers.
Dependencies/integration: wraps `NextInodeProvider`, `qclient::QHash`, and namespace constants; used by metadata services that create new files/containers.
Risks: no synchronization around `configure()` or shared flag; callers must configure before reservation; shared-inode mode changes the semantic coupling of file and container IDs and must match cluster metadata.
Test signals: `HierarchicalViewTest.CustomContainerId` and `CustomFileId` indirectly validate counter advancement after explicit IDs; `NextInodeProviderTest` covers the underlying allocator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/UnifiedInodeProvider.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/UnifiedInodeProvider.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/UnifiedInodeProvider.hh

Purpose: Declares the combined inode provider interface for file and container metadata services.
Important APIs/types/functions: public methods reserve, blacklist, and peek first-free IDs for file and container namespaces; private fields track shared-inode mode, metadata hash, and per-kind `NextInodeProvider` instances.
Control flow: services use one facade regardless of whether deployment metadata says file/container IDs are shared or separate.
State/persistence: state is minimal in-memory routing plus provider objects; durable state is delegated to QDB hash fields.
Dependencies/integration: includes `NextInodeProvider.hh` and qclient `QHash`; constants are used in the implementation.
Risks: the header exposes no explicit initialized check, so dereferencing null providers is possible if used before `configure()`; behavior after reconfigure is not documented.
Test signals: covered through service creation and custom-ID integration tests rather than direct unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/UnifiedInodeProvider.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/CMakeLists.txt -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/CMakeLists.txt

Purpose: Builds QuarkDB namespace tests and benchmark executables.
Important APIs/types/functions: `eos-ns-quarkdb-tests` includes service/view/filtering/inode/other test units and links GTest/gmock plus `EosNsCommon-Static` and Folly; `eosnsbench` builds from `EosNamespaceBenchmark.cc`; `eos-lru-benchmark` builds from `LruBenchmark.cc` and links `EosCommon` and CLI11.
Control flow: CMake adds the repository root to includes, declares executables, applies `_FILE_OFFSET_BITS=64` to namespace benchmark, links libraries, and installs test/benchmark binaries.
State/persistence: no runtime state, but comments state the unit tests require a running QuarkDB instance.
Dependencies/integration: integrates the test suite with the broader EOS build and install layout.
Risks: `VariousTests.cc` is referenced here but outside this research item; test success depends on external QDB environment and build-time package availability.
Test signals: this is the build entry point for all active test files in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/ContainerMDSvcTest.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/ContainerMDSvcTest.cc

Purpose: Integration tests for QuarkDB-backed container metadata service behavior.
Important APIs/types/functions: `ContainerMDSvcF` derives from `NsTestsFixture`; tests use `containerSvc()`, `mdFlusher()`, and `view()`.
Control flow: `BasicSanity` creates root/child containers, manipulates access mode, hierarchy links, attributes, updates stores, synchronizes flushers, removes a subtree member, restarts services with `shut_down_everything()`, verifies persisted state, then cleans up. `getContainerMDWhenContIsLockedShouldNotLock` locks a container and ensures ID retrieval in another thread does not block on that metadata lock.
State/persistence: validates QDB persistence of container count, names, hierarchy, access metadata, and extended attributes across service restart.
Dependencies/integration: depends on container/file services, metadata flusher, hierarchical view, and the shared QDB fixture.
Risks: fixed ID assumptions during cleanup can couple tests to allocator state; concurrency test only checks join completion, not timing.
Test signals: strong coverage for container CRUD, attribute replacement, permission checks, flush/reload, and non-locking retrieval semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/ContainerMDSvcTest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/EosNamespaceBenchmark.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/EosNamespaceBenchmark.cc

Purpose: Nominal namespace performance benchmark source, but the real benchmark implementation is disabled with `#if 0`.
Important APIs/types/functions: disabled code defines `bootNamespace`, `closeNamespace`, `PrintStatus`, `RThread`, `RunReader`, and a CLI-style main that creates directory/file trees and measures parallel reads with/without a global `RWMutex`; active code is only `int main(){ return 0; }`.
Control flow: active executable exits immediately. Disabled flow would create namespace services manually, populate `/eos/nsbench/...`, collect Linux stat/memory metrics, and spawn XRootD threads for read benchmarks.
State/persistence: active path has none; disabled path would persist large metadata sets in QDB.
Dependencies/integration: includes EOS namespace services, timing/memory helpers, XRootD thread/string types, and POSIX headers.
Risks: benchmark binary currently gives a false sense of coverage/performance measurement because all work is compiled out; disabled code may be stale relative to `QuarkNamespaceGroup` fixture patterns.
Test signals: no active behavioral signal beyond successful compilation/linking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/EosNamespaceBenchmark.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/FileMDSvcTest.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/FileMDSvcTest.cc

Purpose: Integration tests for QuarkDB-backed file metadata service and tree accounting helper arithmetic.
Important APIs/types/functions: `FileMDSvcF`, `fileSvc()->createFile/updateStore/removeFile/getFileMD/getFileMDFut`, `mdFlusher()->synchronize`, and `TreeInfos` operators.
Control flow: `LoadTest` creates five files, persists them, removes two, finalizes/reinitializes, restarts services, verifies surviving and deleted IDs, checks multiple futures for one fid point to the same in-memory object, then removes remaining files. `TreeInfos` checks zero/negation/addition behavior.
State/persistence: validates QDB file count, object names, deletion persistence, and cache/future state after reload.
Dependencies/integration: uses constants, file/container services, hierarchical view, test fixture, and private access to `FileSystemView` for testing.
Risks: relies on allocator starting from known IDs through fixture flush; future coalescing assertion is pointer-identity based and could be invalidated by intentional cache design changes.
Test signals: strong for file CRUD, persistence across restart, missing-ID exceptions, future deduplication, and basic accounting arithmetic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/FileMDSvcTest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/FileSystemViewTest.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/FileSystemViewTest.cc

Purpose: Integration and unit tests for filesystem accounting views, QDB set handlers, iterators, random file selection, and change-list behavior.
Important APIs/types/functions: helpers `getRandomLocation`, `countReplicas`, `countUnlinked`; tests cover `RequestBuilder` fs keys, `parseFsId`, `FileSystemView`, `StreamingFileListIterator`, `FileSystemHandler`, cache clearing, and `SetChangeList`.
Control flow: `BasicSanity` creates thousands of files under a hierarchy, assigns/removes/unlinks locations, flushes, restarts, validates replica/unlinked/no-replica counts, URI lookup, and cleanup. Other tests populate QDB sets, verify list/streaming iterators, mutate handlers, clear caches after clock advances, and apply pending set changes.
State/persistence: heavily exercises QDB sets under `fsview:*`, flusher durability, and in-memory cache status.
Dependencies/integration: depends on qclient `QSet`, Folly executor, filesystem accounting classes, hierarchical view, and test utilities.
Risks: random data and large counts can be slow/flaky with an underprovisioned QDB; cache tests use a test harness private-clock hook.
Test signals: broad coverage of filesystem view persistence, iterator completeness, handler backend consistency, cache eviction timing, and set delta semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/FileSystemViewTest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/HierarchicalViewTest.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/HierarchicalViewTest.cc

Purpose: Large integration/regression suite for hierarchical namespace behavior, quota accounting, locking, path resolution, symlinks, and concurrent metadata access.
Important APIs/types/functions: uses `IView` create/get/rename/unlink/remove APIs, `IContainerMD`/`IFileMD` locking wrappers, `BulkNsObjectLocker`, `QuotaRecomputer`, `Resolver`, `RmrfHelper`, and helper `mapSize/createFiles`.
Control flow: tests create nested trees, assert path/name validation and conflicts, rename files/containers, reverse-resolve URIs, prevent deletion with replicas, restart and verify persistence, compute quotas, recompute nested quotas, check custom IDs, verify bulk lock ordering/waiting, mutate file size/location state concurrently, propagate mtime, follow symlinks, and stress cache clearing plus ID/path lookups across threads.
State/persistence: validates QDB hierarchy, quota nodes, tree size/file/container counters, location/unlinked-location sets, symlink targets, and metadata after service restart.
Dependencies/integration: integrates nearly all namespace layers: services, accounting views, lock helpers, resolver, quota recomputer, flusher, and qclient-backed fixture.
Risks: timing assertions with sleeps can be slow/flaky; several tests depend on deterministic IDs; one cleanup TODO documents a known problematic lost-container cleanup path.
Test signals: the strongest behavioral suite in this subset, especially for concurrency, locking semantics, quota isolation, rename safety, and cache reload correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/HierarchicalViewTest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/LruBenchmark.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/LruBenchmark.cc

Purpose: Command-line benchmark for concurrent `eos::LRU` cache reads.
Important APIs/types/functions: global mutex/condition variable and `gDoneWork`; dummy `Entry`; `Populate`; worker function `WokerThread` (typo in name); CLI11 `main` options `--size`, `--num_threads`, and `--num_requests`.
Control flow: populate an LRU, create worker threads, sleep briefly to let them block on a condition variable, notify all, each worker performs sequential `get()` calls starting at a random key, then main measures elapsed microseconds and prints a kHz rate.
State/persistence: all state is in-process memory; no QDB persistence.
Dependencies/integration: uses `namespace/ns_quarkdb/LRU.hh`, CLI11, C++ threading, atomics, and EOS random helper.
Risks: condition-variable wait has no predicate in workers, so missed/spurious wakeups are possible; `gDoneWork` is global and not reset for repeated in-process runs; throughput is read-only and does not measure eviction behavior.
Test signals: benchmark-only, not part of GTest assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/LruBenchmark.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/Main.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/Main.cc

Purpose: GTest entry point for `eos-ns-quarkdb-tests`.
Important APIs/types/functions: `main(int argc,char** argv)` initializes a fixed scratch path, calls `testing::InitGoogleTest`, then `RUN_ALL_TESTS()`.
Control flow: removes `/tmp/eos-ns-tests/`, recreates it with mode `0755`, initializes GoogleTest, and runs the full test binary.
State/persistence: clears local queue/scratch state before tests; QDB state is flushed by `NsTests` fixture construction, not here.
Dependencies/integration: includes GTest and `MetadataFlusher.hh`; uses POSIX `mkdir` and `system("rm -rf ...")`.
Risks: hard-coded `/tmp/eos-ns-tests/` and shell `rm -rf` are destructive within that path; no error checks for removal or directory creation; parallel test binaries would share the same scratch directory.
Test signals: provides deterministic local filesystem setup for the active test suite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/Main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/MetadataFiltering.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/MetadataFiltering.cc

Purpose: Unit tests for metadata attribute extraction and filter expression evaluation/parsing on `FileMdProto`.
Important APIs/types/functions: `StringEvaluator`, `AttributeExtraction::asString`, `EqualityFileMetadataFilter`, `LogicalMetadataFilter`, `FilterExpressionLexer`, and `FilterExpressionParser`.
Control flow: tests literal/variable evaluation, invalid variables, extraction of IDs, uid/gid, size, layout, flags, names, timestamps, checksum, locations, and unlinked locations; then checks equality, inequality, logical AND/OR, lexical tokenization, mismatched quotes, parentheses, and parser output descriptions.
State/persistence: no backend state; all data is in a local protobuf.
Dependencies/integration: uses generated file metadata protobuf, layout ID helper, inspector filter/extraction classes, and GTest.
Risks: tests compare exact human-readable `describe()` strings, so harmless formatting changes break them; checksum extraction expects a shortened hex representation; parser coverage here is positive/basic and not exhaustive for invalid grammar.
Test signals: good unit-level coverage of inspector filtering behavior used to scan/select metadata by attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/MetadataFiltering.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/MetadataTests.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/MetadataTests.cc

Purpose: Intended unit tests for file/container metadata serialization, deserialization, and checksum validation, but the actual tests are compiled out with `#if 0`.
Important APIs/types/functions: disabled tests use `MockFileMDSvc`, `MockContainerMDSvc`, `QuarkFileMD`, `QuarkContainerMD`, metadata setters/getters, `serialize`, `deserialize`, and checksum corruption.
Control flow: disabled `FileMd` test populates a file object with name, parent, times, size, uid/gid, layout, checksum, locations/unlinked locations, serializes/deserializes, compares environment output, then corrupts checksum and expects an exception. Disabled `ContainerMd` mirrors this for container fields and xattrs.
State/persistence: only in-memory `Buffer` serialization; no QDB backend.
Dependencies/integration: would depend on mocks, metadata concrete classes, and GMock expectations for listeners.
Risks: because tests are inactive, serialization regressions rely on integration reload tests rather than direct unit coverage; mock headers are also disabled.
Test signals: currently no active GTest cases in this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/MetadataTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/MockContainerMD.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/MockContainerMD.hh

Purpose: Test subclass of `QuarkContainerMD` that records lock registration/unregistration order for locking tests.
Important APIs/types/functions: `MockContainerMD` inherits `QuarkContainerMD` and `enable_shared_from_this`; static vectors track write/read lock and unlock sequences; overrides `getIdentifier`, `registerLock`/`unregisterLock` for `MDWriteLock` and `MDReadLock`; accessor and `clearVectors` helpers expose/reset traces.
Control flow: construction sets a fixed `ContainerIdentifier`; when EOS lock wrappers register/unregister, overrides call base behavior then append `shared_from_this()` to the appropriate trace vector.
State/persistence: process-global static vectors only; no backend persistence.
Dependencies/integration: used by `OtherTests.cc` with `BulkNsObjectLocker` and `NSObjectLocker`; depends on `ContainerMD.hh` and lock types.
Risks: static vectors are defined in a header, which can violate ODR if included in multiple translation units; shared_from_this requires instances be managed by `shared_ptr`.
Test signals: active tests validate lock/unlock counts and ordering through this mock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/MockContainerMD.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/MockContainerMDSvc.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/MockContainerMDSvc.hh

Purpose: Disabled GMock service stub for container metadata tests.
Important APIs/types/functions: inside `#if 0`, `MockContainerMDSvc` derives from `QuarkContainerMDSvc` and declares mocks for lifecycle, configuration, CRUD, listener notification, lost+found, parent creation, service wiring, accounting wiring, and first-free ID lookup.
Control flow: no active control flow because the class is compiled out.
State/persistence: none active; if enabled, it would mock service interactions in memory.
Dependencies/integration: includes GMock, test namespace macros, and `ContainerMDSvc.hh`; referenced by disabled `MetadataTests.cc`.
Risks: inactive mock may drift from the real service interface; header filename comment says `.cc`; enabling it may require updating method signatures to current interfaces.
Test signals: no active tests depend on it today.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/MockContainerMDSvc.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/MockFileMDSvc.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/MockFileMDSvc.hh

Purpose: Disabled GMock file metadata service stub intended for metadata object unit tests.
Important APIs/types/functions: inside `#if 0`, `MockFileMDSvc` derives from `IFileMDSvc` and mocks lifecycle/configuration, future and synchronous lookup, existence checks, create/update/remove, counts, listener notification, quota/container service wiring, visitor traversal, first-free ID, and cache statistics.
Control flow: none active because the mock class is compiled out.
State/persistence: none active; if enabled, behavior would be controlled by GMock expectations.
Dependencies/integration: includes GMock, test namespace macros, and file service interface; referenced by disabled serialization tests.
Risks: likely stale relative to current `IFileMDSvc`; inactive code provides no compile-time signal for interface changes.
Test signals: no active test coverage uses this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/MockFileMDSvc.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/Namespace.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/Namespace.hh

Purpose: Small namespace macro helper for QuarkDB namespace tests.
Important APIs/types/functions: `USE_EOSNSTESTING`, `EOSNSTESTING_BEGIN`, and `EOSNSTESTING_END` macros wrap or import `eos::ns::testing`.
Control flow: no runtime behavior; this is preprocessor structure only.
State/persistence: none.
Dependencies/integration: included by fixtures, mocks, and tests to place utilities under the test namespace consistently.
Risks: macro-based namespace management can obscure braces and is sensitive to include order, but the file is simple and conventional for this test area.
Test signals: indirectly required for all fixture and mock compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/Namespace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/NextInodeProviderTest.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/NextInodeProviderTest.cc

Purpose: Unit/integration tests for `InodeBlock` and QDB-backed `NextInodeProvider`.
Important APIs/types/functions: `NextInodeProviderTest` fixture, `qclient::QHash`, `NextInodeProvider`, and `InodeBlock`.
Control flow: provider tests create a QDB hash counter, clear it, reserve sequences, destroy/recreate providers, blacklist thresholds, and assert reserved values/high-water marks. Block tests construct ranges, reserve and peek IDs, and blacklist within/across the range.
State/persistence: validates QDB hash field `counter` as persistent largest-reserved value; also validates local block state and restart gaps caused by pre-reserved blocks.
Dependencies/integration: depends on live QuarkDB through `NsTestsFixture::createQClient`, qclient `QHash`, and the allocator implementation.
Risks: `firstRunLimit`/`secondRunLimit` loops are large and can be slow; assertions intentionally allow wasted IDs after restart, so gaps are accepted behavior.
Test signals: excellent coverage of monotonicity, blacklisting semantics, 64-bit boundary behavior, off-by-one correctness, and reset persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/NextInodeProviderTest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/NsTests.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/NsTests.cc

Purpose: Implements shared fixture infrastructure for QuarkDB namespace tests.
Important APIs/types/functions: `FlushAllOnConstruction`, `NsTests` constructor/destructor, `getContactDetails`, `getMembers`, `initServices`, service/view/qclient/flusher accessors, `shut_down_everything`, `createQClient`, `populateDummyData1`, and `cleanNSCache`.
Control flow: fixture reads QDB host/password env vars or `/etc/eos.keytab`, builds test config, flushes QDB with `FLUSHALL`, lazily initializes `QuarkNamespaceGroup`, configures services/views/flushers, initializes the hierarchical view, and tears services down on destruction.
State/persistence: owns test config, namespace mutex, optional size mapper, a QDB-flush guard, and the namespace group. QDB is reset per fixture construction.
Dependencies/integration: central integration point for qclient, namespace group, services, flusher, accounting views, and environment configuration.
Risks: `FLUSHALL` is destructive on the configured QDB; defaults target `localhost:9999`; reading `/etc/eos.keytab` can unexpectedly set a password; lazy initialization hides setup failures until first accessor.
Test signals: enables almost every integration test in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/NsTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/NsTests.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/NsTests.hh

Purpose: Declares the shared QuarkDB namespace test fixture and QDB reset guard.
Important APIs/types/functions: `FlushAllOnConstruction`, `SizeMapper`, `NsTests`, lazy service/view accessors, flusher/qclient helpers, `setSizeMapper`, `populateDummyData1`, `cleanNSCache`, and protected `initServices`.
Control flow: tests derive from `NsTestsFixture` in `TestUtils.hh`, then call fixture accessors; initialization is deferred until first use.
State/persistence: holds `RWMutex`, config map, flush guard, `unique_ptr<QuarkNamespaceGroup>`, and optional quota size mapper.
Dependencies/integration: forward-declares service/view/flusher types, includes `NamespaceGroup.hh`, `Members.hh`, and namespace test macros.
Risks: shared fixture API can encourage tests to depend on deterministic allocator state after `FLUSHALL`; no copying controls are explicit, though ownership fields make copying unavailable.
Test signals: this header is the public contract for all integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/NsTests.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/OtherTests.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/OtherTests.cc

Purpose: Miscellaneous unit tests for path processing, LRU cache behavior, QDB configuration parsing, and namespace lock helper behavior.
Important APIs/types/functions: `checkPath`, `SplitPath`, `PathProcessor::insertChunksIntoDeque/absPath`, `LRU`, `ConfigurationParser::parse`, `QdbContactDetails`, `BulkContainerReadLock`, and `ContainerRead/WriteLock`.
Control flow: tests normalize/split paths across absolute/relative/trailing slash cases, prepend chunks into non-empty deques, populate/purge LRU while holding a reference to prevent eviction, normalize dot/dot-dot paths, parse QDB cluster/password config, and use `MockContainerMD` to assert bulk/read/write lock registration counts/order.
State/persistence: no external persistence except parsing configuration values; LRU and mock lock traces are in memory.
Dependencies/integration: uses common path helpers, namespace `LRU`, config parser, lock classes, and mock container metadata.
Risks: LRU test encodes eviction purge size behavior; lock-order assertions contain a likely copy/paste loop over `lockedContainers` instead of unlock vector.
Test signals: covers low-level utility invariants that larger namespace tests rely on.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/OtherTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/TestUtils.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/TestUtils.hh

Purpose: Shared small test utilities and the concrete GTest fixture type.
Important APIs/types/functions: debug macro `DBG`; overloaded template `verifyContents` for EOS-style iterators and STL iterator ranges; `NsTestsFixture` deriving from `NsTests` and `::testing::Test`.
Control flow: `verifyContents` walks an iterator/range, checks each element exists in an expected set, erases matched elements, and fails if unexpected items or missing expected items remain.
State/persistence: no persistent state; functions consume a copy of the expected set.
Dependencies/integration: includes GTest, namespace macros, and `NsTests.hh`; used by filesystem iterator and set tests.
Risks: diagnostics are minimal and do not print offending values; iterator overload assumes pointer-like `it->valid()/next()/getElement()` API.
Test signals: central assertion helper for unordered contents in QDB set/list iterator tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/TestUtils.hh -->
