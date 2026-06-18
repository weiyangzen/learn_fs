# Research: subset-b-007057

This grouped report covers the source files assigned to `subset-b-007057`. Each file section is wrapped with the exact reconciliation markers used to split source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/VariousTests.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/VariousTests.cc

## Purpose
`VariousTests.cc` is a broad GoogleTest regression suite for the QuarkDB-backed EOS namespace implementation and adjacent namespace utilities. It exercises the test fixture-provided `view()`, QuarkDB client, metadata services, filesystem view, metadata flusher, namespace explorer, checksum/etag helpers, permission parsing, quota accounting, and map iterators.

## Important APIs, Types, and Functions
The file defines three fixture aliases: `VariousTests`, `NamespaceExplorerF`, and `FileMDFetching`, all derived from `eos::ns::testing::NsTestsFixture`. `validateReply()` checks a Redis string reply used by the Folly continuation smoke test. Inline helper `ContainerFilter` implements `ExpansionDecider` and prevents `NamespaceExplorer` descent into a named container. The tests directly use `QuarkHierarchicalView`, `MetadataFetcher`, `RequestBuilder`, `FileSystemIterator`, `NamespaceExplorer`, `FutureVectorIterator`, `QuotaNodeCore`, `PermissionHandler`, `Resolver`, checksum helpers, etag helpers, and container/file map iterators.

## Control Flow
The tests create containers and files through the hierarchical view, flush metadata to QuarkDB where needed, then verify both high-level view behavior and low-level persisted QuarkDB structures. Coverage includes asynchronous `folly::Future` continuations, lookup cache invalidation after manual QuarkDB map edits, filesystem-view location membership and iteration, full-path reconstruction, basic create/get/remove behavior, symlink resolution with absolute and relative targets, loop handling, `mkdir -p`-style path normalization, checksum formatting, hex decoding, etag selection, file/container existence checks, future-vector metadata fetches, corruption handling, namespace traversal order, linked attributes, quota core accounting, ID parsing, object locking order, iterator invalidation, concurrent iterator access, and missing file metadata during exploration.

## State and Persistence Behavior
Most fixture tests mutate a temporary QuarkDB namespace through metadata service caches and then call `mdFlusher()->synchronize()` or service `updateStore()` to persist state. Several tests intentionally bypass the services with raw `qcl().exec()` or `RequestBuilder` operations to simulate corruption, stale maps, or missing data. The suite validates that cached metadata can mask backend deletion until caches are dropped, that persisted metadata survives fixture restarts via `shut_down_everything()`, and that filesystem-view and container-map state remain consistent after file location and namespace mutations.

## Dependencies and Integration Points
The suite integrates GTest, Folly futures/executors, QuarkDB `qclient`, protobuf message comparison, EOS metadata services, namespace explorer, filesystem iterator, inspector attribute utilities, layout/checksum helpers, permission resolver code, and the test fixture in `TestUtils.hh`. It is an integration-style signal for the QuarkDB namespace rather than a narrow unit test.

## Risks and Edge Cases
The tests encode several important risk areas: symlink loop limits and relative link base selection; file-versus-directory error mapping; stale cache behavior; direct QuarkDB corruption; checksum length/padding compatibility; old/new inode encoding in etags and resolver parsing; quota node behavior when parents are detached; iterator survival when dense hash maps reallocate; and lock ordering between containers and files. Some assertions are order-sensitive for namespace exploration and filesystem iteration, so changes to iteration ordering can break tests even if semantic contents remain valid.

## Test Signals
This file itself is the test signal. Passing it indicates basic and edge-case behavior for QuarkDB namespace lookup, persistence, metadata fetch, exploration, attribute inheritance, checksum/etag formatting, quota accounting, ID conversion, locking, and iterators. Failures usually point to cross-layer regressions because most tests touch more than one service.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/VariousTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/utils/break-file.py -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/utils/break-file.py

## Purpose
`break-file.py` is a Python 2 test utility for corrupting a target file by overwriting random byte ranges with random bytes. It is intended to generate damaged metadata or data files for corruption-path tests.

## Important APIs, Types, and Functions
The only named function is `printHelp()`, which prints the expected command-line form. The main block reads `filename`, optional `numRegions`, and optional maximum region size values, uses `os.stat()` to determine file size, opens the file in read/write mode, chooses random offsets and sizes, builds an `array.array('c')`, and writes random characters into the file.

## Control Flow
The script validates argument count, parses integer options, stats the requested file, then loops `numRegions` times. Each iteration chooses an offset within the file, chooses a random region size bounded by `maxRegionSize`, clamps the offset so the write stays inside the file, seeks, creates random bytes, and writes them. It exits with distinct nonzero codes for missing arguments, stat failure, and I/O failure.

## State and Persistence Behavior
The script destructively modifies the input file in place. It does not create backups, does not use atomic replacement, and does not seed the PRNG for reproducibility. Because the file is opened as `"r+"`, writes occur directly against the original file descriptor.

## Dependencies and Integration Points
It depends only on Python standard modules `sys`, `os`, `random`, and `array`. It likely feeds namespace or serialization corruption tests by damaging files outside the script.

## Risks and Edge Cases
The code is Python 2-only: print statements, `except OSError, e`, `xrange`, `file()`, and `array('c')` are incompatible with Python 3. There is also an apparent parsing bug: when four arguments are supplied, `numRegions = int(sys.argv[3])` is assigned again instead of assigning `maxRegionSize`, so the documented maximum region size argument is ignored and the region count is overwritten. Empty files can also cause invalid offset behavior because random offset and clamping assume a positive size.

## Test Signals
No direct tests are in this file. Useful signals would verify argument parsing, Python version expectations, non-empty file mutation, and preservation of file length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tests/utils/break-file.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tools/EosConvertToLocalityHashes.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/tools/EosConvertToLocalityHashes.cc

## Purpose
This standalone migration tool converts older QuarkDB namespace metadata stored in hash buckets into the newer locality-hash layout. It is explicitly described as a temporary compatibility tool for EOS instances created before the automatic new layout cutoff.

## Important APIs, Types, and Functions
`processFileBucket(qclient::QClient&, uint64_t)` scans one old file metadata bucket, deserializes each `FileMdProto`, computes a locality hint from the parent container ID and file name, and invokes `CONVERT-HASH-FIELD-TO-LHASH`. `processContainerBucket(qclient::QClient&, uint64_t)` does the same for `ContainerMdProto`, using parent ID and container name. `main()` parses a single comma-separated QuarkDB member list, configures `qclient::QClient` with transparent redirects and timeout retries, then iterates all configured file and container bucket IDs.

## Control Flow
Each bucket processor runs `HLEN` against the old bucket, aborts on unexpected response types, prints progress, then iterates a `qclient::QHash`. On every item it deserializes the protobuf payload via `Serialization::deserialize()`, aborts on parse errors, builds the locality hint with `LocalityHint::build()`, and sends the conversion command. Progress is printed every 1024 entries. `main()` processes `1024 * 1024` file buckets and `128 * 1024` container buckets, calling each bucket processor twice, presumably to tolerate conversion side effects while iterating the bucket.

## State and Persistence Behavior
The tool mutates QuarkDB namespace metadata layout in place. It reads old hash bucket keys such as `<bucket> + sFileKeySuffix` or `<bucket> + sContKeySuffix` and writes locality-hash entries under `constants::sFileKey` or `constants::sContainerKey`. Failures call `std::abort()`, so partial conversion is possible and operational recovery depends on command idempotency.

## Dependencies and Integration Points
It depends on QuarkDB client APIs, `qclient::Members`, `qclient::QHash`, EOS namespace constants, metadata serialization, request/persistency headers, and `LocalityHint`. It integrates at the storage-layout level rather than through the higher-level metadata services.

## Risks and Edge Cases
This is a dangerous live-data migration utility. It lacks dry-run mode, authentication handling, checkpointing, resumable progress state, or detailed error recovery. The double-processing loop makes idempotency of `CONVERT-HASH-FIELD-TO-LHASH` critical. Because it aborts on a single malformed protobuf, one corrupt metadata entry can stop the whole conversion. Performance is dominated by scanning more than one million file buckets even if most are empty.

## Test Signals
There are no tests in this file. Useful validation would run against a controlled QuarkDB dataset with known old buckets, verify locality-hash entries and locality hints, rerun to prove idempotency, and inject malformed bucket values to confirm failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tools/EosConvertToLocalityHashes.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tools/Fid2PathTool.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/tools/Fid2PathTool.cc

## Purpose
`Fid2PathTool.cc` is a small CLI that converts an EOS file ID into its hexadecimal file ID and corresponding FST data path prefix form.

## Important APIs, Types, and Functions
The program uses `CLI::App` to require `--fid`, then calls `eos::common::FileId::Fid2Hex()` and `eos::common::FileId::FidPrefix2FullPath()`. It prints `id`, `fxid`, and `path` fields to standard output. Although it includes `qclient/QClient.hh`, the tool does not use QuarkDB.

## Control Flow
`main()` builds the CLI parser, parses arguments, converts the signed integer `fid` to a hex string, uses hard-coded prefix `/data/`, derives the full path, prints the three lines, and exits zero. CLI parse errors are delegated to `app.exit(e)`.

## State and Persistence Behavior
The tool is read-only and stateless. It does not inspect filesystem state or namespace metadata; the output is purely a deterministic transformation of the supplied ID.

## Dependencies and Integration Points
It integrates with the common EOS file ID encoding helpers used by FST path layout logic. Operators can use it for diagnostics when correlating namespace IDs with on-disk data paths.

## Risks and Edge Cases
The input type is `int64_t`, so negative values may be accepted by the CLI and passed into file-ID conversion unless `FileId` rejects or normalizes them internally. The `/data/` prefix is hard-coded, so deployments using another data root need to reinterpret output. The command description says "translate fids to FST paths", but it does not validate that the path exists.

## Test Signals
Useful tests would compare known fid-to-hex and fid-to-path conversions, parse-error behavior for missing `--fid`, and edge cases for zero, large, and negative IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tools/Fid2PathTool.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tools/InodeToFidTool.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/tools/InodeToFidTool.cc

## Purpose
`InodeToFidTool.cc` is a tiny diagnostic CLI that converts an encoded file inode back into an EOS file ID.

## Important APIs, Types, and Functions
The tool uses `CLI::App` to require `--inode`, then calls `eos::common::FileId::InodeToFid()` and prints the resulting `fid`.

## Control Flow
`main()` constructs the CLI parser, parses `--inode` into an `unsigned long long`, returns parser errors through `app.exit(e)`, converts the inode, prints a single line, and exits zero.

## State and Persistence Behavior
The tool is deterministic and read-only. It does not contact QuarkDB, access files, or persist output.

## Dependencies and Integration Points
It depends on `common/FileId.hh`, sharing the same inode/fid conversion logic used by resolver and etag code paths. It is operationally useful for debugging inode strings or FST metadata.

## Risks and Edge Cases
The command description mistakenly mirrors the fid-to-path tool text. It accepts any unsigned integer the CLI parser allows, including values that may decode to zero or non-file container encodings. Validation is delegated entirely to `FileId::InodeToFid()`.

## Test Signals
Known old-encoding and new-encoding inode samples should be tested, along with zero, container-like inode values, and missing-argument CLI behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tools/InodeToFidTool.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tools/InspectionTool.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/tools/InspectionTool.cc

## Purpose
`InspectionTool.cc` is the main command-line front end for inspecting, scanning, validating, and repairing a QuarkDB-backed EOS namespace. It wires a large CLI surface to the `Inspector` service and its output sinks.

## Important APIs, Types, and Functions
`MemberValidator` validates comma-separated QuarkDB member strings through `qclient::Members::parse()`. `IdValidator` validates uint64 strings but is not actively used in the visible option setup. `addClusterOptions()` attaches common `--members`, retry, password, and password-file options. `addDryRun()` adds the common `--no-dry-run` gate for mutating commands. `main()` defines all subcommands and dispatches to `Inspector` methods.

## Control Flow
The CLI requires a subcommand. Read-only commands include deprecated `dump`, `scan`, `print`, `stripediff`, `one-replica-layout`, `scan-dirs`, `scan-files`, `scan-deathrow`, `check-naming-conflicts`, `check-cursed-names`, `check-orphans`, `check-fsview-missing`, `check-fsview-extra`, `check-shadow-directories`, and `check-simulated-hardlinks`. Dangerous repair commands include `fix-detached-parent`, `fix-shadow-file`, `drop-from-deathrow`, `drop-empty-cid`, `change-fid`, `rename-fid`, `rename-cid`, and `overwrite-container`; these default to dry-run unless `--no-dry-run` is supplied. After parsing, the tool reads an optional password file, parses an optional metadata filter expression, constructs `QdbContactDetails`, builds a `qclient::QClient`, selects a text or JSON output sink, checks connectivity, sets the metadata filter, and dispatches to exactly one `Inspector` method.

## State and Persistence Behavior
Read-only commands stream namespace metadata and consistency findings. Repair commands can mutate FileMD, ContainerMD, deathrow entries, parent/container maps, fsview-related metadata, or raw protobuf fields depending on the selected inspector method. Dry-run is the default for commands marked dangerous, but the tool still connects to and scans live QuarkDB.

## Dependencies and Integration Points
The tool integrates CLI11, QuarkDB `qclient`, EOS password handling, `QdbContactDetails`, metadata filter parsing, inspector operations, and output sink abstractions (`StreamSink`, `JsonStreamSink`, `JsonLinedStreamSink`). It is an operational entry point over the lower-level namespace inspector library.

## Risks and Edge Cases
Because this file is mostly option wiring, risks concentrate in argument ambiguity, dry-run semantics, and dispatch correctness. Shared variables such as `fid`, `cid`, `json`, `fullPaths`, and `newParent` are reused across subcommands; CLI11 subcommand isolation makes that workable but easy to break when adding options. Several commands are explicitly dangerous and rely on operator intent plus `--no-dry-run`. Client-side filtering still streams all metadata, so `--where` can be expensive. Password-file permission checks happen in `PasswordHandler`, and connection retry behavior changes when `--connection-retries` is zero.

## Test Signals
Useful tests should cover command parsing, required option groups, default dry-run behavior, password/password-file exclusivity, JSON/minimal sink selection, filter parse failures, connectivity failure handling, and one dispatch smoke test per subcommand using a fake or controlled `Inspector`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/tools/InspectionTool.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/utils/FutureVectorIterator.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/utils/FutureVectorIterator.hh

## Purpose
`FutureVectorIterator` is a template helper that consumes either a `folly::Future<std::vector<folly::Future<T>>>` or an already available vector of futures and exposes sequential readiness and fetch semantics. It makes batched asynchronous metadata fetches easier to consume without losing ordering.

## Important APIs, Types, and Functions
The class stores `mainFuture`, `futureVectorPopulated`, `futureVector`, and `futureVectorNext`. Public methods are the destructor, constructors, move assignment from the top-level future, `isMainFutureReady()`, `size()`, `isReady()`, and `fetchNext(T&)`. Private helpers `processMainFuture()` and `waitAll()` populate and drain the vector.

## Control Flow
`isReady()` first checks whether the top-level future has produced the vector; if not ready it returns false. Once populated, EOF is considered ready, otherwise readiness is the readiness of the next future in order. `fetchNext()` blocks as needed, returns false at EOF, otherwise gets the current future, moves the result into `out`, and advances the cursor. `size()` blocks until the top-level future resolves. The destructor calls `waitAll()`, which drains unconsumed futures so outstanding asynchronous work completes before destruction.

## State and Persistence Behavior
The class has no persistence. Its state is the ownership of Folly futures and the current sequential index. It consumes futures by move and is therefore single-pass.

## Dependencies and Integration Points
It depends on Folly futures and EOS `MDException`. It is used by namespace metadata fetch flows that fetch child file/container metadata asynchronously but need ordered iteration and readiness polling.

## Risks and Edge Cases
`waitAll()` catches only `eos::MDException`; other exceptions escaping future `.get()` calls can propagate from the destructor, which is risky during stack unwinding. The move-assignment operator drains existing work before replacing it, which can block unexpectedly. Readiness is strictly sequential, so a later ready future is hidden until all earlier futures are ready. `size()` can block even though its name does not advertise blocking outside the comment.

## Test Signals
`VariousTests.cc` covers empty construction, delayed top-level future readiness, sequential readiness, ordered fetches, EOF behavior, and later futures becoming ready before earlier ones.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/utils/FutureVectorIterator.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/utils/QuotaRecomputer.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/utils/QuotaRecomputer.cc

## Purpose
`QuotaRecomputer.cc` implements recalculation of quota accounting for a QuarkDB namespace quota node by traversing namespace contents and rebuilding a `QuotaNodeCore`.

## Important APIs, Types, and Functions
`QuotaRecomputer::QuotaRecomputer(qclient::QClient*, folly::Executor*)` stores the QuarkDB client and executor. Internal `QuotaNodeFilter` implements `ExpansionDecider` and permits traversal through the root quota container and non-quota descendants, but stops descent into nested quota nodes. `QuotaRecomputer::recompute()` resets the output core, validates the root container ID, creates a `NamespaceExplorer`, and accounts every file.

## Control Flow
`recompute()` clears `qnc`, rejects `cont_id == 0`, configures `ExplorationOptions` with depth limit 2048 and the quota filter, starts exploration at `cont_uri`, and loops over `explorer.fetch(item)`. File items contribute logical size from `item.fileMd.size()` and physical size as `size * LayoutId::GetSizeFactor(layout_id)`, keyed by UID and GID. Directory items are used only for traversal. On completion it returns an OK `MDStatus`.

## State and Persistence Behavior
The function does not write QuarkDB. It reconstructs accounting into the caller-supplied `QuotaNodeCore`, replacing any previous contents. The result depends on current namespace metadata, file layout IDs, and the explorer's handling of corrupt or missing metadata.

## Dependencies and Integration Points
It depends on `NamespaceExplorer`, `ExpansionDecider`, `QuotaNodeCore`, QuarkDB client access, Folly executor scheduling, namespace constants, and common layout size-factor logic. It integrates with quota repair or validation flows that need to recalculate quota nodes from source metadata.

## Risks and Edge Cases
Nested quota nodes are deliberately skipped, so recomputation is scoped to one quota subtree and relies on correct `QUOTA_NODE_FLAG` state. The hard-coded depth limit can exclude extremely deep namespace trees. Physical size is estimated from layout factor rather than confirmed replica state. If `NamespaceExplorer` throws on corruption, recomputation can fail mid-run after clearing the output core.

## Test Signals
Direct tests are not present in this file. Indirect signals include namespace explorer traversal tests and `QuotaNodeCore` accounting tests in `VariousTests.cc`. Dedicated tests should build nested quota-node trees and verify skipped subtrees and physical-size calculations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/utils/QuotaRecomputer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/utils/QuotaRecomputer.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/utils/QuotaRecomputer.hh

## Purpose
`QuotaRecomputer.hh` declares the public utility class used to recompute quota-node accounting from a QuarkDB namespace subtree.

## Important APIs, Types, and Functions
The header forward-declares `qclient::QClient`, `folly::Executor`, `QuotaNodeCore`, and `IView`, then declares `class QuotaRecomputer`. Its constructor takes a QuarkDB client pointer and executor pointer. `MDStatus recompute(const std::string& cont_uri, IContainerMD::id_t cont_id, QuotaNodeCore& core)` is the only public operation.

## Control Flow
The header does not implement control flow, but it defines a call contract: callers provide both the quota-node URI and container ID plus mutable output accounting core. The implementation resets and fills that core.

## State and Persistence Behavior
The class stores raw, non-owning pointers to `QClient` and `folly::Executor`. It does not own namespace services or quota nodes. Persistence behavior is read-only in the implementation; output state is returned through `QuotaNodeCore&`.

## Dependencies and Integration Points
The API sits between QuarkDB namespace exploration and quota accounting. It includes `IContainerMD.hh`, `Namespace.hh`, and `MDException.hh` for namespace types and status handling. Consumers must ensure the client and executor outlive the recomputer.

## Risks and Edge Cases
Raw pointer lifetime is the main API risk. Passing `nullptr` for either dependency is not guarded in the declaration and would fail later in implementation. Requiring both URI and ID can introduce inconsistency if they do not refer to the same container; the implementation uses both independently.

## Test Signals
Header-level tests are not applicable. Integration tests should instantiate with fixture QuarkDB state, verify nonzero quota-node recomputation, invalid ID behavior, and nested quota-node exclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/utils/QuotaRecomputer.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/views/HierarchicalView.cc -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/views/HierarchicalView.cc

## Purpose
`HierarchicalView.cc` implements `QuarkHierarchicalView`, the QuarkDB-backed hierarchical namespace view for EOS. It maps path-oriented operations onto file/container metadata services, handles symlink traversal, creates and removes namespace entries, reconstructs paths from IDs, and integrates quota node management.

## Important APIs, Types, and Functions
The implementation defines constructor/destructor, `configure()`, three-phase `initialize()`, `finalize()`, `getItem()`, `getFileFut()`, `getFile()`, `createFile()`, `createLink()`, `unlinkFile()`, `removeFile()`, `getContainerFut()`, `getContainer()`, `createContainer()`, `removeContainer()`, URI reconstruction methods, `getRealPath()`, quota-node methods, rename methods, and `getParentContainer()`. Private helpers include `getPathInternal()`, two `getPathDeferred()` overloads, `getPathExpectContainer()`, URI-building futures, `extractFileMD()`, `extractContainerMD()`, and `UpdateStoreGuard`.

## Control Flow
Path lookup starts at `pRoot`, converts URI chunks with `PathProcessor`, and repeatedly consumes chunks in `getPathInternal()`. Container states handle `"."`, `".."`, and child `findItem()` lookups. File states in the middle of a path are either errors or symlinks; symlink targets are inserted into the pending chunk deque, absolute links reset state to root, relative links resolve from the link's parent. Cache-hit futures are consumed immediately, while cache misses return a Folly future that resumes on the executor. Creation functions resolve parent paths, check conflicts, create metadata through services, attach to parent maps, and update stores. URI reconstruction climbs parent container IDs into a deque, again suspending on metadata cache misses. Quota operations search parent chains for `QUOTA_NODE_FLAG`, register/remove quota nodes, and meld child quota data into parents on removal.

## State and Persistence Behavior
The view owns `QuarkQuotaStats` and an IO thread pool executor, stores non-owning pointers to QuarkDB client, metadata flusher, container service, and file service, and caches the root container. Metadata persistence is delegated to `updateFileStore()` and `updateContainerStore()` on the services. Some operations update one side of a relationship before the other, such as `removeContainer()` deleting metadata then removing the parent map entry. `UpdateStoreGuard` batches container store updates during recursive container creation. `finalize()` deletes quota stats and finalizes services.

## Dependencies and Integration Points
The implementation depends on EOS namespace interfaces, QuarkDB metadata services, `QuarkQuotaStats`, `PathProcessor`, Folly futures/executors, metadata exceptions, and common logging/assertion utilities. It is the central integration point for higher-level namespace APIs using QuarkDB persistence.

## Risks and Edge Cases
Important risks include symlink loop limits, relative symlink semantics, stale service caches, partially persisted create/remove/rename operations, lock ordering for `getUri(IFileMD*)`, root special cases, detached parent containers during URI/quota traversal, and exceptions in asynchronous continuations. `createContainer()` notes eventual consistency and carefully avoids creating a directory over a broken symlink. `getRealPath()` returns a path built from the resolved parent and final chunk but treats the single-chunk case differently. Rename operations update parent maps and object names but rely on callers to hold required locks.

## Test Signals
`VariousTests.cc` directly covers basic create/get behavior, symlink traversal and loops, path normalization, persistence across restart, cache invalidation, URI reconstruction, quota-node corruption handling, locking order, iterators, and missing metadata behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/views/HierarchicalView.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/views/HierarchicalView.hh -->
# sources/distributed-fs/eos/namespace/ns_quarkdb/views/HierarchicalView.hh

## Purpose
`HierarchicalView.hh` declares `QuarkHierarchicalView`, the QuarkDB implementation of the EOS `IView` interface. It presents path-based file/container operations, quota-node APIs, rename APIs, and async metadata lookup surfaces.

## Important APIs, Types, and Functions
The public API overrides service setters/getters, `configure()`, `initialize()` phases, `finalize()`, `getFileFut()`, `getFile()`, `getItem()`, `createFile()`, `createLink()`, `updateFileStore()`, `removeLink()`, `unlinkFile()`, `removeFile()`, `getContainerFut()`, `getContainer()`, `createContainer()`, `updateContainerStore()`, `removeContainer()`, `getUri()` overloads, `getUriFut()` overloads, `getRealPath()`, quota node methods, `getQuotaStats()`, `setQuotaStats()`, `renameContainer()`, `renameFile()`, `inMemory()`, and `getParentContainer()`. Private APIs expose the resumable path and URI lookup machinery used by the implementation.

## Control Flow
The declaration makes clear that the view is both synchronous and asynchronous. Synchronous methods typically wrap future-returning methods and call `.get()`. Private helpers accept current lookup state and pending path chunks so asynchronous operations can resume after service futures complete.

## State and Persistence Behavior
The class stores raw pointers to `qclient::QClient`, `MetadataFlusher`, container service, file service, and quota stats, plus a shared root container and a unique executor. It reports `inMemory() == false`, signaling that operations are backed by persistent QuarkDB state. Store updates are delegated to the configured metadata services.

## Dependencies and Integration Points
The header includes the namespace base, metadata service interfaces, `IView`, and QuarkDB quota stats. It is consumed wherever the QuarkDB namespace view is constructed or manipulated through the generic `IView` interface.

## Risks and Edge Cases
Ownership is mixed: `pQuotaStats` is owned and deleted by the view, while most other pointers are non-owning. `setQuotaStats()` deletes the existing stats object but assumes ownership of the supplied pointer. The comments on `getUri(IFileMD*)` document a deadlock risk if callers lock files before calling URI reconstruction because the implementation also locks or fetches parent containers.

## Test Signals
Public behavior is exercised heavily by `VariousTests.cc`. Constructor/configuration and quota-stats ownership would benefit from additional lifecycle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/ns_quarkdb/views/HierarchicalView.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/Attributes.hh -->
# sources/distributed-fs/eos/namespace/utils/Attributes.hh

## Purpose
`Attributes.hh` provides inline helpers for EOS extended attribute lookup with support for linked attributes. A metadata object can carry `sys.attr.link` pointing to a container whose attributes are inherited unless overridden locally.

## Important APIs, Types, and Functions
The file defines attribute key constants `kAttrLinkKey`, `kAttrTmpEtagKey`, and `kAttrObfuscateKey`. `populateLinkedAttributes(const XAttrMap&, XAttrMap&, bool)` merges linked attributes without overriding existing keys and optionally rewrites linked `sys.*` keys to `sys.link.*`. `populateLinkedAttributes(IView*, XAttrMap&, bool)` follows `sys.attr.link` through the view. `listAttributes()` overloads handle `IContainerMD*`, `IFileMD*`, and `FileOrContainerMD`. Template `getAttribute()` retrieves a key locally first, then follows the linked container with prefetching and read locking.

## Control Flow
List operations clear and seed `out` from the target's own attributes, then call linked population. If the link is absent or empty, nothing else happens. If the linked container lookup fails, the link attribute is modified in output to append " - not found" and a debug log is emitted. `getAttribute()` first checks the target directly; if not present and no link exists it returns false. With a link, it prefetches, gets the container, acquires a read lock, checks for the key, and returns the linked value if present.

## State and Persistence Behavior
These helpers do not persist metadata changes. They build returned maps and strings from current metadata state. The only mutation is to the caller-provided output map when a linked container is missing.

## Dependencies and Integration Points
The file integrates `IView`, `Prefetcher`, string utilities, logging, and metadata locking. It is used by namespace exploration and user-facing metadata display paths that need effective attributes rather than only local attributes.

## Risks and Edge Cases
Linked attribute inheritance depends on `sys.attr.link` pointing to a directory; file links or missing paths are treated as not found. Prefixing applies only to inherited `sys.*` attributes, preserving non-system names. `getAttribute()` writes `errno` on link lookup failure, which can leak state into callers. Because this header is inline/template-heavy, changes can have broad rebuild impact.

## Test Signals
`VariousTests.cc` includes linked-attribute tests for containers, not-found links, overriding, and prefixing of inherited system attributes. Additional tests should cover `getAttribute()` on file metadata and prefetch failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/Attributes.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/BalanceCalculator.hh -->
# sources/distributed-fs/eos/namespace/utils/BalanceCalculator.hh

## Purpose
`BalanceCalculator.hh` defines an in-memory statistics accumulator for summarizing file data distribution by filesystem ID, EOS space, scheduling group, and size order.

## Important APIs, Types, and Functions
`BalanceCalculator` initializes several `google::dense_hash_map` members with required empty keys. `account(const std::shared_ptr<IFileMD>&)` adds one file's size to per-filesystem, per-space, per-scheduling-group, and first-location size-distribution counters. `printSummary(S&)` emits human-readable lines for each accumulated dimension.

## Control Flow
For each file location, `account()` reads the location ID and file size. Location zero is logged and skipped. It updates `filesystembalance`, uses the first nonzero location to bin size by `log10(size)`, then acquires a read lock on `FsView::gFsView.ViewMutex`, looks up the filesystem, snapshots it, and adds size to space and scheduling-group maps. `printSummary()` iterates each map and uses `StringConversion::GetReadableSizeString()` to format byte totals and averages.

## State and Persistence Behavior
All state is local to the calculator instance. It reads global filesystem view state under lock but does not modify it. Output is emitted to the caller's stream.

## Dependencies and Integration Points
Although the header does not include all visible dependencies itself, it relies on EOS file metadata, global `FsView`, filesystem snapshots, dense hash maps, XRootD string types, math functions, and common string conversion. It is likely included from contexts that already provide those definitions.

## Risks and Edge Cases
The header is sensitive to include order because dependencies are not explicit in this file. The size-bin lower-limit calculation uses `((bin) - 1) > 0`, which makes low bins display zero lower bounds. Only the first location contributes to size-distribution counts, while all locations contribute to balance volumes. Missing filesystem snapshots simply omit space/group accounting.

## Test Signals
No local tests were read. Tests should account files with multiple locations, zero location, missing filesystem view entries, and known sizes crossing powers of ten, then verify printed summaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/BalanceCalculator.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/Buffer.hh -->
# sources/distributed-fs/eos/namespace/utils/Buffer.hh

## Purpose
`Buffer.hh` implements a small data buffer abstraction on top of `std::vector<char>` with optional read-only external storage mode. It is used by namespace utilities such as checksum formatting.

## Important APIs, Types, and Functions
`Buffer` constructors initialize owned vector storage or copy from another buffer. `operator=` deep-copies from the other buffer. `getDataPtr()` returns either vector data or an external pointer. `setDataPtr()` switches the buffer to external storage with explicit length. `getDataPadded()` returns zero for out-of-range reads. `getSize()`, `setSize()`, `putData()`, `grabData()`, and `getCRC32()` provide size, append, copy-out, and checksum operations.

## Control Flow
In owned mode, `putData()` resizes the vector and appends bytes; `grabData()` copies from the vector after bounds checking. In external mode, `putData()` throws `MDException(EINVAL)` because the structure is read-only, while reads and padded access use `data` and `len`. `getCRC32()` computes zlib CRC32 over `getDataPtr()` and `size()`.

## State and Persistence Behavior
The class owns data only in vector mode. External mode stores a raw pointer without owning lifetime. It has no persistence. Copy assignment resets to owned mode and copies bytes from the source's visible data.

## Dependencies and Integration Points
It depends on zlib and `MDException`. It integrates with checksum and serialization helpers that need byte buffers with padded reads for legacy checksum display.

## Risks and Edge Cases
Calling `getDataPtr()` on an empty owned vector uses `&operator[](0)`, which is undefined for truly empty vectors. `getCRC32()` uses `size()` rather than `getSize()`, so external-buffer mode may compute over the vector's size rather than `len`; this is a likely bug if CRC32 is used after `setDataPtr()`. External pointer lifetime is unmanaged and can dangle.

## Test Signals
Useful tests should cover owned append/copy, external read-only behavior, `grabData()` bounds, padded reads, empty buffers, and CRC32 in both owned and external modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/Buffer.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/Checksum.hh -->
# sources/distributed-fs/eos/namespace/utils/Checksum.hh

## Purpose
`Checksum.hh` provides inline namespace checksum formatting and hex parsing helpers for file metadata and protobuf metadata.

## Important APIs, Types, and Functions
`appendChecksumOnStringAsHexNoFmd()` formats a `Buffer` into hexadecimal according to a layout ID's nominal checksum length, optional separator, and optional override length. `appendChecksumOnStringAsHex()` adapts that logic to an `IFileMD`. `appendChecksumOnStringProtobuf()` adapts protobuf checksum bytes into a `Buffer`. `hexArrayToByteArray()` overloads parse hex strings into raw byte strings.

## Control Flow
Formatting determines the layout's checksum length through `LayoutId::GetChecksumLen()`, chooses either the nominal or override target length, then appends two lowercase hex characters per byte. If target length exceeds the nominal checksum length, zeros are emitted. Separators are inserted between bytes when requested. The function returns false only when the nominal checksum length is zero. Hex parsing requires even length, converts two characters at a time with `strtol(..., 16)`, and clears output on parse failure.

## State and Persistence Behavior
All helpers are stateless and operate on caller-provided output strings. They do not modify metadata.

## Dependencies and Integration Points
The helpers depend on layout encoding, protobuf `FileMdProto`, `Buffer`, and `IFileMD`. They are used by etag generation, printing, and tests that need stable checksum text.

## Risks and Edge Cases
Formatting pads missing checksum bytes with zeros to preserve compatibility, which can hide truncated checksum storage in display paths. `appendChecksumOnStringProtobuf()` copies protobuf bytes into a mutable buffer before formatting. Hex parsing pushes a byte before checking whether `strtol` consumed both characters, then clears on failure; this is safe for output but noteworthy. `strtol` accepts signs and whitespace if present in the two-character slice in standard C semantics, though full two-character consumption limits most invalid forms.

## Test Signals
`VariousTests.cc` covers MD5 and CRC32 formatting, separators, override length padding, null `IFileMD`, and hex parsing for invalid and mixed-case input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/Checksum.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/DataHelper.cc -->
# sources/distributed-fs/eos/namespace/utils/DataHelper.cc

## Purpose
`DataHelper.cc` implements checksum and ownership-copy utility functions declared in `DataHelper.hh`.

## Important APIs, Types, and Functions
`computeCRC32()` and `updateCRC32()` wrap zlib CRC32. `computeCRC32C()`, `updateCRC32C()`, and `finalizeCRC32C()` wrap EOS's CRC32C implementation. `copyOwnership()` copies UID/GID from a source path to a target path, optionally ignoring non-root callers.

## Control Flow
CRC helpers call the underlying checksum functions with appropriate initialization or existing CRC state. `copyOwnership()` checks `getuid()`: non-root callers return silently when `ignoreNoPerm` is true, otherwise throw `MDException(EFAULT)`. Root callers `stat()` the source path, then `chown()` the target to the source UID/GID, throwing `MDException(errno)` on either failure.

## State and Persistence Behavior
Checksum helpers are pure. `copyOwnership()` mutates filesystem metadata on the target path when run as root. It does not change file contents and does not roll back partial failures.

## Dependencies and Integration Points
The implementation depends on zlib, EOS CRC32C code, POSIX `getuid`, `stat`, and `chown`, and `MDException`. It is a low-level namespace/common utility for data conversion and ownership preservation workflows.

## Risks and Edge Cases
`void*` buffer parameters allow mutable-looking access even though checksum functions only read. `copyOwnership()` silently no-ops for non-root by default, which is convenient but can mask ownership preservation failures. It uses `stat()` rather than `lstat()`, so source symlinks are followed. Permission and filesystem errors are surfaced as metadata exceptions.

## Test Signals
Tests should compare CRC32/CRC32C against known vectors, incremental update equivalence, finalize behavior, root/non-root `copyOwnership()` behavior, missing source errors, and target `chown()` failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/DataHelper.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/DataHelper.hh -->
# sources/distributed-fs/eos/namespace/utils/DataHelper.hh

## Purpose
`DataHelper.hh` declares static utility methods for CRC calculation and copying POSIX file ownership metadata.

## Important APIs, Types, and Functions
`DataHelper` exposes `computeCRC32()`, `updateCRC32()`, `computeCRC32C()`, `updateCRC32C()`, `finalizeCRC32C()`, and `copyOwnership(const std::string& target, const std::string& source, bool ignoreNoPerm = true)`.

## Control Flow
The header contains declarations only. The intended call flow is direct static invocation without object construction.

## State and Persistence Behavior
CRC functions are stateless by contract. `copyOwnership()` is the only API with persistent side effects, changing target file ownership in the implementation when permissions allow.

## Dependencies and Integration Points
The header includes only integer and string types, keeping the interface light. It is suitable for inclusion by namespace code that needs checksums or ownership preservation without pulling in POSIX and zlib implementation details.

## Risks and Edge Cases
Raw `void*` buffers provide no length safety beyond the explicit `len` argument. The `ignoreNoPerm` default means callers must opt in to strict permission failure when ownership copying is required for correctness.

## Test Signals
Header-level tests are not applicable. Implementation tests should verify known checksums and ownership-copy permission behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/DataHelper.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/Descriptor.cc -->
# sources/distributed-fs/eos/namespace/utils/Descriptor.cc

## Purpose
`Descriptor.cc` implements low-level file descriptor and IPv4 socket helpers declared in `Descriptor.hh`. It provides blocking/full-length read and write loops, offset reads, socket setup, DNS resolution, and socket option wrappers.

## Important APIs, Types, and Functions
Static `resolve()` resolves a hostname into `sockaddr_in`, using `gethostbyname()` on Apple and `gethostbyname_r()` with a dynamically resized buffer elsewhere. Implemented methods include `Socket::init()`, `connect()`, `bind()`, `listen()`, `accept()`, `Descriptor::close()`, `readBlocking()`, `readNonBlocking()`, `offsetReadNonBlocking()`, `tryRead()`, `write()`, `Socket::setsockopt()`, and `Socket::getsockopt()`.

## Control Flow
Socket methods lazily initialize TCP sockets when needed, resolve addresses, configure IPv4 `sockaddr_in`, and throw `DescriptorException` on syscall failures. Descriptor read/write methods loop until the requested byte count is satisfied. Blocking reads treat EOF as an error. Non-blocking file-style reads optionally sleep and retry on EOF when a nonzero poll interval is supplied. `tryRead()` returns the number of bytes available before EOF. `accept()` wraps the accepted descriptor in a heap-allocated `Socket`.

## State and Persistence Behavior
The classes wrap integer file descriptors and mutate `pFD` on initialization and close. They do not own descriptors through RAII destructors in this implementation; callers must call `close()` or manage wrapper lifetime carefully. Socket operations affect OS network state.

## Dependencies and Integration Points
The implementation uses POSIX sockets, `read`, `write`, `pread`, `lseek`, DNS APIs, and errno strings. It is a legacy utility layer for code needing simple descriptor/socket abstractions.

## Risks and Edge Cases
`Socket::listen(unsigned queue)` ignores its `queue` argument and always passes 20. On `connect()` and `bind()` failures, descriptors are closed but `pFD` is not reset to -1. `readBlocking()` reports `strerror(errno)` on EOF even though errno may be stale. The helper supports IPv4 only and uses obsolete hostname APIs. `DescriptorException` does not derive from `std::exception`, so normal catch patterns may miss it. `Socket::accept()` transfers ownership through a raw pointer.

## Test Signals
Tests should cover full and partial reads/writes, EOF handling with and without polling, offset reads, try-read byte counts, socket connect/bind/listen failures, queue argument behavior, and descriptor state after errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/Descriptor.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/Descriptor.hh -->
# sources/distributed-fs/eos/namespace/utils/Descriptor.hh

## Purpose
`Descriptor.hh` declares simple wrappers around file descriptors and sockets plus a stream-building exception type.

## Important APIs, Types, and Functions
`DescriptorException` stores an `std::ostringstream` and exposes `getMessage()`. `Descriptor` stores `int pFD` and declares descriptor assignment, lookup, `seek()`, `close()`, blocking/non-blocking reads, offset reads, `tryRead()`, and `write()`. `Socket` derives from `Descriptor`, defines `Protocol { TCP, UDP }`, and declares initialization, connect, bind, listen, accept, close, and socket option wrappers.

## Control Flow
The header itself has minimal inline behavior: constructors initialize or wrap file descriptors, `seek()` delegates to `lseek()`, and socket constructors delegate to `Descriptor`. The implementation supplies syscall loops and error handling.

## State and Persistence Behavior
`Descriptor` stores a raw descriptor value and does not declare a destructor that closes it. Ownership semantics are therefore manual. `Socket::accept()` returns an owning raw pointer by contract in comments.

## Dependencies and Integration Points
It depends on POSIX descriptor/socket headers and is used by legacy namespace code requiring direct system I/O wrappers. It intentionally avoids higher-level networking abstractions.

## Risks and Edge Cases
`DescriptorException` is not derived from `std::exception` despite including `<exception>`, which can surprise callers. No copy/move controls are declared for `Descriptor` or `Socket`, so accidental copying can duplicate wrapper objects around the same FD. Manual close requirements invite leaks.

## Test Signals
Header behavior should be validated through implementation tests for descriptor lifecycle, copy hazards, exception catching style, and accepted socket ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/Descriptor.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/Etag.cc -->
# sources/distributed-fs/eos/namespace/utils/Etag.cc

## Purpose
`Etag.cc` implements EOS namespace etag generation for FST metadata, namespace file metadata, protobuf file metadata, and container metadata. It preserves compatibility with S3 expectations and historical inode encodings.

## Important APIs, Types, and Functions
Internal `findInode(uint64_t fid)` chooses legacy or new fid-to-inode conversion at a 34 billion fid threshold. Public overloads include `calculateEtag(bool useChecksum, const fst::FmdBase&, std::string&)`, `calculateEtagInodeAndChecksum(const fst::FmdBase&, std::string&)`, `calculateEtagInodeAndMtime(uint64_t, uint64_t, std::string&)`, `calculateEtag(const ns::FileMdProto&, std::string&)`, `calculateEtag(const IFileMD*, std::string&)`, and `calculateEtag(IContainerMD*, std::string&)`.

## Control Flow
FST metadata etags either use checksum or inode+mtime depending on the supplied flag. Checksum-based etags omit inode when checksum type is MD5 so S3 receives a pure MD5 etag; non-MD5 checksums include `inode:checksum`. Namespace file/protobuf overloads first honor forced temporary etag attribute `sys.tmp.etag`. If the layout has a checksum length, they format checksum bytes similarly with MD5 special-casing. Without checksum, they extract modification/change time and fall back to `inode:mtime`. Container etags honor `sys.tmp.etag`, otherwise use hex container ID plus tree mtime seconds and milliseconds.

## State and Persistence Behavior
The functions are pure formatting helpers. They read metadata attributes, IDs, layout IDs, checksums, and timestamps, then overwrite the caller-provided output string. No metadata is modified.

## Dependencies and Integration Points
The file depends on `Etag.hh`, `IFileMD`, `FileId`, FST metadata, checksum helpers, layout IDs, and container/file metadata interfaces. It integrates with HTTP/S3-facing metadata and printing paths that require stable etag strings.

## Risks and Edge Cases
The 34B fid threshold is a compatibility hack that must remain aligned with file ID encoding. File protobuf mtime is recovered by `memcpy` from raw string bytes into a `timespec`-like struct, so malformed or short serialized timestamps could be dangerous if upstream validation is absent. MD5 special handling changes etag shape compared with other checksum types. `calculateEtag(const IFileMD*)` does not null-check the pointer.

## Test Signals
`VariousTests.cc` covers forced temporary etags, inode+mtime fallback, Adler-style inode+checksum etags, pure MD5 etags, and container etag formatting. Additional tests should cover the fid threshold boundary and malformed protobuf timestamp data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/utils/Etag.cc -->
