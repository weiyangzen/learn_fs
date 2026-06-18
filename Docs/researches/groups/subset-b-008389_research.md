# Research Group subset-b-008389

This grouped report covers FoundationDB Java binding package docs, directory layer APIs, subspace/tuple utilities, Java binding workload hooks, and selected async directory test harness files. Each section is delimited for reconciliation into a source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/package-info.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/package-info.java

## Purpose
This package descriptor documents `com.apple.foundationdb.async` as support code for asynchronous programming around Java `CompletableFuture`s in the FoundationDB binding.

## Important APIs, Types, And Functions
The file exports no runtime API; its only declaration is the package-level Javadoc and `package com.apple.foundationdb.async`. The referenced surface is `java.util.concurrent.CompletableFuture`, and the actual package contains helpers such as `AsyncUtil`, `AsyncIterable`, and `AsyncIterator` consumed by directory and test code in this group.

## Control Flow, State, And Persistence
There is no executable control flow or persistence. Its effect is documentation generation and package organization for asynchronous FoundationDB helper types.

## Dependencies And Integration Points
The directory layer relies heavily on `AsyncUtil.whileTrue`, `getAll`, `collect`, and ready futures. This descriptor gives those helpers a documented namespace in generated Java API docs.

## Risks And Test Signals
Risk is documentation drift: if async helpers change semantics, this descriptor is too generic to warn users. Test signals are indirect through compilation and generated Javadoc; no unit behavior is exercised by this file.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/Directory.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/Directory.java

## Purpose
`Directory` is the public interface for objects managed by the FoundationDB directory layer. It models a hierarchical directory path, its layer byte string, and operations on itself or subdirectories.

## Important APIs, Types, And Functions
The interface exposes `getPath`, `getLayer`, and `getDirectoryLayer`, then asynchronous methods for `createOrOpen`, `open`, `create`, `moveTo`, `move`, `remove`, `removeIfExists`, `list`, and `exists`. Convenience default overloads use `DirectoryLayer.EMPTY_PATH` and `EMPTY_BYTES` for root-relative or no-layer cases. Methods return `CompletableFuture` and accept `TransactionContext` for writes or `ReadTransactionContext` for reads.

## Control Flow
Control flow is mostly declarative: defaults delegate to fuller overloads. Implementations are expected to resolve relative subpaths against the directory, open or create nodes, validate layers, and return `DirectorySubspace` handles.

## State And Persistence Behavior
This file defines the persistence contract rather than storing state itself. Creates record directory metadata and optional layer/prefix. Moves rewrite directory metadata without changing the physical content prefix. Removes clear directory metadata and contents, with warnings that previously opened clients can still write under an old prefix.

## Dependencies And Integration Points
`DirectoryLayer` implements the root behavior; `DirectorySubspace` implements directory-scoped behavior; `DirectoryPartition` specializes partition roots. Exception classes in this package are named in the API contract.

## Risks And Test Signals
Risks include misuse of root-relative versus absolute paths, layer mismatch handling, stale open handles after remove/move, and manual prefix collisions. Test signals should cover every overload family, error future propagation, read-only versus write transaction usage, partition delegation, and idempotent `removeIfExists`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/Directory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryAlreadyExistsException.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryAlreadyExistsException.java

## Purpose
This exception identifies attempts to create or move a directory to a path where a directory already exists.

## Important APIs, Types, And Functions
`DirectoryAlreadyExistsException` extends `DirectoryException` and has a package-private constructor taking a `List<String>` path. It fixes the base message to `Directory already exists`.

## Control Flow, State, And Persistence
The class is thrown by directory create/open logic when `allowOpen` is false and an existing node is found, and by move when the destination node already exists. It stores the offending path through the superclass.

## Dependencies And Integration Points
It depends on `DirectoryException` for path formatting and on `DirectoryUtil.pathStr` through the superclass. It is part of the public exception hierarchy named by `Directory.create` and `Directory.move` docs.

## Risks And Test Signals
The constructor is package-private, so tests generally observe it through `DirectoryLayer` operations. Test signals include duplicate create, move onto existing directory, and async exceptional completion preserving the path.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryAlreadyExistsException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryException.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryException.java

## Purpose
`DirectoryException` is the base runtime exception for directory-layer failures that correspond to a specific path.

## Important APIs, Types, And Functions
It extends `RuntimeException`, exposes a public final `List<String> path`, and has a package-private constructor combining a base message with `DirectoryUtil.pathStr(path)`.

## Control Flow, State, And Persistence
There is no persistence. State is the path reference and formatted message. The class deliberately does not defensively copy the list, so callers should avoid mutating paths after exception construction.

## Dependencies And Integration Points
Subclasses include `DirectoryAlreadyExistsException`, `NoSuchDirectoryException`, and `MismatchedLayerException`. `DirectoryLayer` throws this base class directly for invalid root removal.

## Risks And Test Signals
Risk centers on mutable `path` aliasing and package-private construction limiting external specialization. Tests should check exception class, message path formatting, and path field contents from failing directory operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryLayer.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryLayer.java

## Purpose
`DirectoryLayer` is the main Java implementation of FoundationDB directories. It maps human-readable hierarchical paths to compact binary content prefixes and stores directory metadata in a node subspace.

## Important APIs, Types, And Functions
Constructors accept node/content `Subspace`s and an `allowManualPrefixes` flag. Static helpers create layers with custom node or content subspaces, and `getDefault` returns the singleton default layer using node prefix `0xFE` and empty content prefix. Public operations implement `Directory`: `createOrOpen`, `open`, `create`, `move`, `remove`, `removeIfExists`, `list`, and `exists`. Key internals include `createOrOpenInternal`, `createInternal`, `openInternal`, `removeInternal`, `removeRecursive`, `isPrefixFree`, `checkVersion`, `checkOrWriteVersion`, `NodeFinder`, `Node`, `PrefixFinder`, and `HighContentionAllocator`.

## Control Flow
Read paths first validate directory-layer version and walk subdirectory links with `NodeFinder`. Create/open either opens an existing node, delegates into a partition, or allocates/validates a prefix and writes parent-child and layer metadata. Move checks version, rejects moving root or a directory into its own subtree, resolves old and new nodes, delegates partition-internal moves, writes a destination parent link, and removes the old parent link. Remove validates non-root paths, delegates into partitions when needed, clears content and metadata ranges, then recursively clears descendant nodes.

## State And Persistence Behavior
Persistent metadata lives under `nodeSubspace`: root version, high-contention allocation counters/recent markers, layer entries, and subdirectory pointers keyed by `SUB_DIR_KEY` plus child name. Content lives under allocated prefixes in `contentSubspace`. `checkOrWriteVersion` initializes `{1,0,0}` in little-endian ints; `VersionCheck` blocks future major versions and `WritableVersionCheck` makes future minor versions read-only. Automatic prefixes are allocated with transaction conflict management and then checked against existing key ranges and directory metadata. Manual prefixes are rejected unless enabled and also must be prefix-free.

## Dependencies And Integration Points
The implementation depends on FoundationDB `Transaction`, `ReadTransaction`, `Range`, `MutationType.ADD`, `AsyncUtil`, `AsyncIterator`, `Subspace`, `Tuple`, and `ByteArrayUtil`. `DirectorySubspace` and `DirectoryPartition` are returned handles. The high-contention allocator is integrated with FDB conflict ranges and snapshot reads.

## Risks And Edge Cases
Prefix allocation is correctness-critical: collisions with manually allocated prefixes or existing data become `IllegalStateException`/`IllegalArgumentException`. `NodeFinder` must stop at partitions and load metadata before partition tests. Recursive removal clears opened directories while stale clients may still write under old prefixes. The allocator synchronizes on a class object to avoid transaction-local races, with comments noting this is not ideal. Path lists and layer arrays are not always defensively copied internally. Root open/remove/move behavior is intentionally special.

## Test Signals
Strong tests include duplicate create, open missing, layer mismatch, version compatibility, manual prefix allow/deny, automatic prefix collision detection, remove recursion, list ordering/content, exists across normal and partition directories, move into self, move to missing parent, move across partitions, and high-concurrency creation under contention.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryLayer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryMoveException.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryMoveException.java

## Purpose
`DirectoryMoveException` represents invalid directory move requests, such as moving root, moving into a descendant, or crossing partition boundaries.

## Important APIs, Types, And Functions
It extends `RuntimeException`, exposes `sourcePath` and `destPath`, and formats both paths with `DirectoryUtil.pathStr`.

## Control Flow, State, And Persistence
It is constructed synchronously or during async composition before any valid move mutation is completed. The object records source and destination path references.

## Dependencies And Integration Points
`DirectoryLayer.moveTo`, `DirectoryLayer.move`, and `DirectorySubspace.moveTo` use this class to report invalid move shapes. It is documented on the `Directory` interface.

## Risks And Test Signals
The source/destination lists are not defensively copied. Tests should trigger root move, self-subtree move, and cross-partition move, then assert class, message, and path fields.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryMoveException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryPartition.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryPartition.java

## Purpose
`DirectoryPartition` represents a directory-layer partition root. It is a directory handle but intentionally not a usable content subspace; clients must create children under it.

## Important APIs, Types, And Functions
The constructor creates a nested `DirectoryLayer` with node subspace `prefix + DEFAULT_NODE_SUBSPACE_PREFIX` and content subspace `prefix`, sets that nested layer path, and records the parent layer. It overrides all subspace operations (`get`, `getKey`, `pack`, `unpack`, `range`, `contains`, `subspace`) to throw `UnsupportedOperationException`. `getLayerForPath` routes empty-path operations to the parent layer and child operations to the partition layer.

## Control Flow
The class delegates directory operations through inherited `DirectorySubspace` behavior, except empty-path remove/exists/move context is resolved back to the parent layer. Direct content key operations fail immediately.

## State And Persistence Behavior
Persistent partition metadata is created by `DirectoryLayer` using the special `PARTITION_LAYER` byte string. This wrapper changes namespace layout so descendant directories allocate inside the partition prefix.

## Dependencies And Integration Points
It extends `DirectorySubspace`, depends on `DirectoryLayer`, `Subspace`, `Tuple`, `Range`, and `ByteArrayUtil.join`, and is constructed by `DirectoryLayer.contentsOfNode` when node layer equals `partition`.

## Risks And Test Signals
Risks include accidentally treating partition roots as content subspaces, incorrect empty-subpath routing, and equality/hash behavior needing to account for parent layer. Tests should assert every forbidden subspace method throws, child directory operations succeed, and cross-partition moves are rejected.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryPartition.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectorySubspace.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectorySubspace.java

## Purpose
`DirectorySubspace` combines a normal tuple `Subspace` for directory contents with a `Directory` handle for operations relative to the path used to open it.

## Important APIs, Types, And Functions
It stores `path`, `layer`, and `directoryLayer`; extends `Subspace`; implements all `Directory` operations by delegating to the backing layer after computing a partition-relative subpath. It overrides `toString`, `equals`, `hashCode`, `getPath`, `getLayer`, and `getDirectoryLayer`.

## Control Flow
Create/open/list/move delegate through `directoryLayer` using `getPartitionSubpath`. `moveTo`, `remove`, `removeIfExists`, and `exists` call `getLayerForPath` first so subclasses such as `DirectoryPartition` can redirect empty-path operations.

## State And Persistence Behavior
The object is a client-side handle. It holds an immutable-by-convention path and layer byte string, and its inherited `Subspace` prefix determines where content keys are packed. `getLayer` returns a copy, but the constructor stores the path list reference.

## Dependencies And Integration Points
It is returned by `DirectoryLayer` for ordinary directories and inherited by `DirectoryPartition`. It integrates with `PathUtil`, `ByteArrayUtil.printable`, `TransactionContext`, `ReadTransactionContext`, and `Subspace`.

## Risks And Test Signals
Risks include mutable path aliasing, partition path slicing errors, and equality depending on both layer identity and prefix. Tests should cover relative create/list/remove, `moveTo` absolute path validation, `getLayer` defensive copy, subspace packing inherited from `Subspace`, and partition subclass overrides.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectorySubspace.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryUtil.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryUtil.java

## Purpose
`DirectoryUtil` is a package-private formatting helper for directory paths.

## Important APIs, Types, And Functions
The only method, `pathStr(List<String>)`, renders null as `null` and non-null paths as comma-separated elements inside parentheses.

## Control Flow, State, And Persistence
There is no mutable state or persistence. The method iterates over path components and appends them without escaping or quoting.

## Dependencies And Integration Points
All directory exceptions use this helper to produce path strings; `DirectorySubspace.toString` also uses it.

## Risks And Test Signals
Because components are not escaped, commas or parentheses in path elements can make messages ambiguous. Tests should verify null, empty, single-element, and multi-element formatting because exception messages depend on it.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryVersionException.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryVersionException.java

## Purpose
This runtime exception reports incompatible on-database directory-layer metadata versions.

## Important APIs, Types, And Functions
`DirectoryVersionException` extends `RuntimeException` with a package-private message constructor.

## Control Flow, State, And Persistence
`DirectoryLayer.VersionCheck` throws it when the stored major version is newer than the binding supports. `WritableVersionCheck` also throws when the stored minor version is newer for write operations, making the layer read-only.

## Dependencies And Integration Points
It is tied to `DirectoryLayer.VERSION` and the `rootNode/version` metadata key. It protects Java clients interacting with directories created by newer bindings.

## Risks And Test Signals
Tests should seed version metadata for equal, newer patch, newer minor, and newer major versions to verify read/write compatibility behavior and error messages.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/DirectoryVersionException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/MismatchedLayerException.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/MismatchedLayerException.java

## Purpose
This exception reports opening an existing directory with a non-empty expected layer byte string that differs from the stored layer.

## Important APIs, Types, And Functions
It extends `DirectoryException` and exposes `stored` and `opened` byte arrays. The message uses `ByteArrayUtil.printable` for binary-safe layer rendering.

## Control Flow, State, And Persistence
`DirectoryLayer.openInternal` throws it when `layer.length > 0` and arrays differ. Empty expected layer acts as no layer check.

## Dependencies And Integration Points
It is part of the `Directory.open` and `createOrOpen` contract and depends on `ByteArrayUtil` for diagnostics.

## Risks And Test Signals
The byte arrays are stored by reference, so caller mutation can affect fields. Tests should cover matching layers, empty expected layer, mismatched binary layer bytes, and async exceptional completion.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/MismatchedLayerException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/NoSuchDirectoryException.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/NoSuchDirectoryException.java

## Purpose
`NoSuchDirectoryException` reports operations against a directory path that does not exist.

## Important APIs, Types, And Functions
It extends `DirectoryException` with a package-private constructor and fixed base message `No such directory`.

## Control Flow, State, And Persistence
`DirectoryLayer` throws it from open, create-with-open-disallowed, move source lookup, move parent lookup, remove with `mustExist`, and list when a node is absent. No persistence occurs in the exception itself.

## Dependencies And Integration Points
It relies on `DirectoryException` for path storage and formatting and is documented by `Directory` methods.

## Risks And Test Signals
Tests should cover missing open/list/remove/move-source/move-parent and verify the path reported is absolute relative to the active layer or partition.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/NoSuchDirectoryException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/PathUtil.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/PathUtil.java

## Purpose
`PathUtil` provides public static helpers for creating and manipulating directory path lists.

## Important APIs, Types, And Functions
Methods are `join(List<String>, List<String>)`, `extend(List<String>, String...)`, `from(String...)`, `popFront`, and `popBack`. Outputs are `LinkedList` copies.

## Control Flow, State, And Persistence
All methods are pure in-memory list operations. `popFront` and `popBack` reject empty paths with `IllegalStateException`.

## Dependencies And Integration Points
`DirectoryLayer` uses `popBack` and `join` for parent resolution and absolute path formatting. `DirectorySubspace` uses `join` for partition-relative delegation. Tests and users can build paths with `from` and `extend`.

## Risks And Test Signals
No validation is performed on path component contents or null elements. Tests should cover copy semantics, empty-pop errors, and list order preservation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/PathUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/package-info.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/package-info.java

## Purpose
This package descriptor documents the directory layer as tools for managing hierarchical key subspaces.

## Important APIs, Types, And Functions
The file exports package Javadoc only. It describes paths as tuples/lists of strings, directory-associated subspaces, short prefixes, and links to general directory documentation.

## Control Flow, State, And Persistence
No runtime code executes here. The documented state model is path-to-prefix metadata plus content subspaces managed by `DirectoryLayer`.

## Dependencies And Integration Points
The descriptor frames `Directory`, `DirectoryLayer`, `DirectorySubspace`, and `DirectoryPartition` for generated API docs.

## Risks And Test Signals
Risk is documentation drift around path representation and partition behavior. Javadoc generation and link validation are the main direct signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/directory/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/package-info.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/package-info.java

## Purpose
This package descriptor documents the core Java FoundationDB API and encourages transaction retry-loop helpers.

## Important APIs, Types, And Functions
It references `Database`, `TransactionContext.run`, `TransactionContext.runAsync`, `Transaction.commit`, and transaction developer documentation. There is no executable API in this file.

## Control Flow, State, And Persistence
The documented control flow is that clients should run work inside binding-managed retry loops so database commits complete successfully before the outer call returns.

## Dependencies And Integration Points
The file is integrated with Javadoc for the root `com.apple.foundationdb` package and contextualizes directory, tuple, and subspace layers.

## Risks And Test Signals
Documentation can drift as API-version or retry-loop guidance changes. Direct test signals are compilation and generated docs; behavior is tested through the referenced classes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/subspace/Subspace.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/subspace/Subspace.java

## Purpose
`Subspace` is the Java binding helper for namespacing FoundationDB keys with a raw byte prefix plus an optional tuple prefix.

## Important APIs, Types, And Functions
Constructors accept no prefix, a `Tuple`, raw bytes, or both. Core methods are `get`, `subspace`, `getKey`, `pack`, `packWithVersionstamp`, `unpack`, `range`, `contains`, `equals`, `hashCode`, and `toString`.

## Control Flow
Construction joins raw bytes with `prefix.pack()`, rejecting incomplete versionstamps through tuple packing. Packing delegates to `Tuple.pack(rawPrefix)`. Unpack first checks `contains` and decodes after `rawPrefix.length`. Range delegates to tuple range with the raw prefix.

## State And Persistence Behavior
The only state is `rawPrefix`, held as a final byte array. Returned `pack()` values are copies, but the raw-byte constructor and join behavior should be considered carefully for caller mutation of input arrays before construction completes. No database writes occur; the class defines key layout for callers.

## Dependencies And Integration Points
It depends on `Range`, `Tuple`, `Versionstamp`, and `ByteArrayUtil`. `DirectorySubspace` extends it, tuple tests exercise it, and directory code uses subspaces for metadata and content.

## Risks And Test Signals
Risks include prefix containment mistakes, unpacking keys outside the subspace, incomplete versionstamp use in constructor prefixes, and raw byte aliasing assumptions. Tests should cover pack/unpack round trips, range bounds, nested subspaces, `packWithVersionstamp` prefix offset adjustment, and equality/hash consistency.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/subspace/Subspace.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/subspace/package-info.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/subspace/package-info.java

## Purpose
This package descriptor documents subspaces as tuple-prefixed namespaces for application data.

## Important APIs, Types, And Functions
It exports package Javadoc only and points users toward `Subspace` and developer-guide sub-keyspace documentation.

## Control Flow, State, And Persistence
No code executes here. The documented persistence model is that packed tuple keys share a prefix and unpacking removes that prefix.

## Dependencies And Integration Points
The descriptor supports generated documentation for `com.apple.foundationdb.subspace`, which is used by directory and tuple APIs.

## Risks And Test Signals
Documentation drift is the primary risk. Direct validation is limited to Javadoc generation; behavioral tests belong to `Subspace` and directory integration tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/subspace/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/testing/AbstractWorkload.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/testing/AbstractWorkload.java

## Purpose
`AbstractWorkload` is a base class for Java workloads driven by FoundationDB's native simulation/testing infrastructure.

## Important APIs, Types, And Functions
It stores a `WorkloadContext`, creates a small `ThreadPoolExecutor`, exposes `getExecutor`, declares abstract `setup`, `start`, and `check` methods taking `Database` and `Promise`, and provides overridable `getMetrics` and `getCheckTimeout`. Static `log` delegates to a native logger.

## Control Flow
The constructor captures the current process ID and creates an executor whose `beforeExecute` restores that process ID in the context before running work. Subclasses implement lifecycle phases and can use the executor for async tasks.

## State And Persistence Behavior
State is the workload context and executor. Persistence is external through database operations performed by subclasses and native logging. `shutdown` exists but is private, implying lifecycle may be managed reflectively or by native code.

## Dependencies And Integration Points
It depends on `Database`, `Promise`, `PerfMetric`, `WorkloadContext`, Java concurrency types, and native JNI functions. The testing harness likely instantiates subclasses from the simulation workload engine.

## Risks And Test Signals
Risks include executor leaks if `shutdown` is not invoked, native logger initialization, process ID propagation across threads, and no bounded queue due to `SynchronousQueue`. Tests should verify lifecycle callbacks, promise completion, metrics collection, and native integration behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/testing/AbstractWorkload.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/testing/PerfMetric.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/testing/PerfMetric.java

## Purpose
`PerfMetric` is a mutable Java bean for reporting named workload performance metrics.

## Important APIs, Types, And Functions
It stores `name`, `value`, `averaged`, and `formatCode`. Constructors default `averaged` to true and format to `"%.3g"`, with getters and setters for every field.

## Control Flow, State, And Persistence
There is no control flow beyond construction and property access. Persistence/reporting happens in the external workload harness that consumes instances from `AbstractWorkload.getMetrics`.

## Dependencies And Integration Points
It is used by Java workload implementations and native test infrastructure to collect metrics.

## Risks And Test Signals
Risks include invalid format strings, mutable metrics being changed after collection, and lack of units. Tests should check default constructor behavior, custom averaged/format settings, and harness formatting.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/testing/PerfMetric.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/testing/Promise.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/testing/Promise.java

## Purpose
`Promise` is a JNI-backed one-shot boolean completion object used by Java workloads to signal native test harness phases.

## Important APIs, Types, And Functions
It stores a native pointer `nativePromise`, a `wasSet` flag, private constructor, `canBeSet`, and `send(boolean)`, which calls a native static `send(long, boolean)`.

## Control Flow, State, And Persistence
`send` rejects second completion with `IllegalStateException`, sets `wasSet`, and forwards the value to native code. State is local plus the native promise handle.

## Dependencies And Integration Points
It integrates with `AbstractWorkload.setup/start/check` and native simulation code that can construct instances despite the private constructor.

## Risks And Test Signals
`wasSet` is not synchronized, so concurrent send attempts can race. Native pointer lifetime is external. Tests should cover one-shot behavior, double-send failure, and JNI completion observed by the harness.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/testing/Promise.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/testing/WorkloadContext.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/testing/WorkloadContext.java

## Purpose
`WorkloadContext` is a JNI wrapper exposing simulation/workload context values to Java workload code.

## Important APIs, Types, And Functions
It stores a native `impl` pointer and exposes `getProcessID`, `setProcessID`, `getClientID`, `getClientCount`, `getSharedRandomNumber`, and overloaded `getOption` for string, long, boolean, and double defaults. All operations delegate to native methods.

## Control Flow, State, And Persistence
The Java object has minimal local state. Calls cross into native code to read or mutate workload context; `setProcessID` affects context used by executor threads in `AbstractWorkload`.

## Dependencies And Integration Points
It is consumed by `AbstractWorkload` and native simulation bindings. Private construction implies native or reflective instantiation.

## Risks And Test Signals
Risks include invalid native pointer lifetime, option type mismatch, and thread context propagation. Tests should verify option defaults, client identity values, process ID set/get, and behavior under executor callbacks.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/testing/WorkloadContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/ByteArrayUtil.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/ByteArrayUtil.java

## Purpose
`ByteArrayUtil` provides tuple-layer and general byte-array helpers for concatenation, replacement, splitting, unsigned comparison, prefix ranges, integer encoding, and printable diagnostics.

## Important APIs, Types, And Functions
Important methods include `join`, `interludeJoin`, `regionEquals`, `replace`, `split`, `compareUnsigned`, `comparator`, `startsWith`, `strinc`, `keyAfter`, `encodeInt`, `decodeInt`, `printable`, and package-private `nullCount`. It extends `FastByteComparisons`.

## Control Flow
Join computes total length then copies parts and optional interludes. Replace can do a sizing pass when replacement length differs, then a writing pass into a `ByteBuffer`. Split scans for delimiters and returns copied segments. `strinc` strips trailing `0xff` then increments the last remaining byte.

## State And Persistence Behavior
All methods are stateless and allocate new arrays except methods writing into a caller-supplied `ByteBuffer`. `encodeInt`/`decodeInt` use little-endian order for FoundationDB atomic mutation operands.

## Dependencies And Integration Points
The tuple encoder uses null replacement/count helpers. Directory code uses `startsWith`, `strinc`, `join`, and `printable`. Core `KeyValue` diagnostics use printable formatting.

## Risks And Test Signals
Risks include null argument behavior, offset/length validation, delimiter edge cases, `strinc` on all-`0xff` input, `replacement == null` deletion semantics, and unsigned compare portability through `FastByteComparisons`. Tests should cover embedded zero bytes, leading/trailing delimiters, mutation operand round trips, and prefix range boundaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/ByteArrayUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/FastByteComparisons.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/FastByteComparisons.java

## Purpose
`FastByteComparisons` supplies unsigned lexicographic byte-array comparison with a pure Java implementation and an optional `sun.misc.Unsafe` fast path.

## Important APIs, Types, And Functions
Public/package APIs are `compareTo`, `comparator`, `lexicographicalComparerJavaImpl`, and `lexicographicalComparerUnsafeImpl`. Internal `LexicographicalComparerHolder` picks `UnsafeComparer` for unaligned x86/x86_64 architectures when reflection succeeds, otherwise `PureJavaComparer`.

## Control Flow
The pure comparer scans byte by byte and compares unsigned values. The unsafe comparer reads eight bytes at a time, handles native endianness, locates the first differing byte on little-endian systems, then falls back to byte scanning for the tail.

## State And Persistence Behavior
Static initialization caches the best comparer and unsafe byte-array base offset. There is no persistence.

## Dependencies And Integration Points
`ByteArrayUtil`, `Tuple`, `TupleUtil`, and `Versionstamp` depend on this comparison order to match FoundationDB key ordering. It uses `AccessController`, reflection, `ByteOrder`, and `sun.misc.Unsafe`.

## Risks And Test Signals
Portability is the main risk: `sun.misc.Unsafe`, module access restrictions, architecture detection, and endian logic can differ by JVM. Tests should compare pure and unsafe results across offsets, lengths, equal arrays, prefix arrays, signed-byte values, and random data.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/FastByteComparisons.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/IterableComparator.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/IterableComparator.java

## Purpose
`IterableComparator` compares iterable tuple items in the same order as FoundationDB tuple byte encodings.

## Important APIs, Types, And Functions
The class implements `Comparator<Iterable<?>>`; its only behavior is `compare`, which iterates both sides and delegates item ordering to `TupleUtil.compareItems`.

## Control Flow, State, And Persistence
Comparison proceeds element-wise until a non-zero item comparison or one iterable ends. A longer iterable sorts after its prefix. The comparator has no mutable state or persistence.

## Dependencies And Integration Points
`Tuple.compareTo` uses this comparator when packed bytes are unavailable or incomplete versionstamps make byte order unsafe. `TupleUtil` uses another instance for nested collection comparison.

## Risks And Test Signals
Risks include unsupported element types surfacing as `IllegalArgumentException`, iterator side effects, and consistency with packed tuple bytes. Tests should compare tuples, raw lists, nested lists, prefix cases, floats/NaN, UUIDs, strings with surrogate pairs, and byte arrays.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/IterableComparator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/StringUtil.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/StringUtil.java

## Purpose
`StringUtil` validates UTF-16 strings and computes tuple-compatible UTF-8 ordering and packed sizes.

## Important APIs, Types, And Functions
Package-private methods are `validate`, `compareUtf8`, `packedSize`, and `adjustForSurrogates`. It defines fixed error messages for high/low surrogate malformations.

## Control Flow
Validation scans for well-formed surrogate pairs. `compareUtf8` skips a common prefix, then adjusts surrogate-range code units so Java UTF-16 comparison aligns with Unicode code point/UTF-8 byte ordering. `packedSize` counts encoded UTF-8 bytes and extra null escaping.

## State And Persistence Behavior
The class is stateless and non-instantiable. No database persistence occurs, but its output determines tuple key byte layout.

## Dependencies And Integration Points
`TupleUtil` calls `validate` before string encoding, `packedSize` for buffer sizing, and `compareUtf8` for semantic tuple comparison without packing.

## Risks And Test Signals
Risks include incorrect surrogate ordering, malformed UTF-16 acceptance/rejection, and packed-size mismatch causing buffer overflow. Tests should cover ASCII, null characters, BMP non-ASCII, supplementary code points, isolated high/low surrogates, and compare consistency with packed byte order.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/StringUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/Tuple.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/Tuple.java

## Purpose
`Tuple` is the public sortable typed key container for the Java binding. It serializes Java values into FoundationDB's cross-language tuple encoding and compares in key order.

## Important APIs, Types, And Functions
It supports `String`, `byte[]`, numeric types, `BigInteger`, `Float`, `Double`, `UUID`, `Boolean`, `Versionstamp`, nested `List`/`Tuple`, and `null`. APIs include typed `add` methods, `addObject`, `addAll`, `pack`, `packInto`, `packWithVersionstamp`, `fromBytes`, `fromItems`, `fromList`, `fromStream`, typed getters, `range`, `compareTo`, `equals`, `hashCode`, `toString`, `getPackedSize`, and `hasIncompleteVersionstamp`.

## Control Flow
Public add methods create new `Tuple` instances with appended or merged element lists. Packing validates incomplete versionstamp rules, memoizes packed bytes, and delegates encoding to `TupleUtil`. Versionstamp packing appends an offset suffix and adjusts it when a prefix is added. Deserialization slices/copies bytes, unpacks through `TupleUtil`, and memoizes the original packed representation.

## State And Persistence Behavior
The object is effectively immutable through public APIs but stores mutable internal memoization: packed bytes, hash, and packed size. `getItems` copies the element list, while `getRawItems` is package-private. Packed keys are the persistence format used by FoundationDB clients; incomplete versionstamps are only valid for versionstamped mutations.

## Dependencies And Integration Points
It depends on `TupleUtil`, `ByteArrayUtil`, `IterableComparator`, `Range`, `Versionstamp`, and `Subspace`. Directory metadata, examples, tests, and application key modeling all use this class.

## Risks And Test Signals
Risks include non-thread-safe memoization, mutable nested lists or byte arrays altering semantics after tuple creation, numeric conversion surprises for generic `Number`, incomplete versionstamp misuse, packed-size bugs, and equality based on tuple byte order. Tests should cover cross-language encoding vectors, all supported types, null handling, nested values, versionstamp suffix offsets for old/new API versions, range bounds, hash/equality memoization, and malformed byte input.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/Tuple.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/TupleUtil.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/TupleUtil.java

## Purpose
`TupleUtil` is the package-private encoder/decoder and comparator implementation behind `Tuple`.

## Important APIs, Types, And Functions
It defines tuple type codes, `DecodeState`, `EncodeState`, floating-point bit transforms, integer byte sizing, versionstamp offset adjustment, `getCodeFor`, overloaded `encode`, `decode`, `compareItems`, `unpack`, `pack`, `packWithVersionstamp`, `getPackedSize`, and `hasIncompleteVersionstamp`.

## Control Flow
Encoding dispatches by Java type, writes type codes, escapes embedded null bytes in strings/byte arrays, transforms floats/doubles for sortable byte order, encodes integers with variable-length positive/negative forms, and records exactly one incomplete versionstamp position. Decoding reads type codes, validates truncation, reverses escaping and numeric transforms, validates UTF-8, and recursively decodes nested tuples. Comparison mirrors encoded order without necessarily packing.

## State And Persistence Behavior
The utility is stateless except for local encode/decode state. Its byte output is the persistent key format used in FoundationDB. Versionstamp suffix size depends on `FDB.instance().getAPIVersion()`: older APIs use a 2-byte offset and newer APIs use a 4-byte offset.

## Dependencies And Integration Points
It depends on `FDB` for API version, `ByteArrayUtil` for null escaping and unsigned comparison, `StringUtil`, `Versionstamp`, `IterableComparator`, `UUID`, `BigInteger`, and `ByteBuffer`. `Tuple`, `Subspace`, directory code, and tests rely on exact compatibility.

## Risks And Test Signals
This is compatibility-critical. Risks include type-code drift, buffer size mismatch, malformed UTF-8 handling, nested null escaping, BigInteger range/order edge cases, float NaN ordering, old versus new versionstamp offset formats, and unsupported type errors. Tests should include official tuple conformance vectors, fuzz round trips, compare-versus-packed-order checks, API-version-specific versionstamp tests, and malformed/truncated input cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/TupleUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/Versionstamp.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/Versionstamp.java

## Purpose
`Versionstamp` represents the 12-byte FoundationDB versionstamp tuple value: 10 transaction-version bytes plus a 2-byte user version.

## Important APIs, Types, And Functions
Static APIs are `fromBytes`, `incomplete`, `incomplete(int)`, `complete(byte[])`, `complete(byte[], int)`, and `unpackUserVersion`. Instance APIs include `isComplete`, `getBytes`, `getTransactionVersion`, `getUserVersion`, `compareTo`, `equals`, `hashCode`, and `toString`.

## Control Flow
Factories validate lengths and unsigned-short user version bounds, then create big-endian 12-byte arrays. `fromBytes` marks a stamp complete if any transaction-version byte differs from the all-`0xff` incomplete sentinel. Comparison sorts complete stamps before incomplete stamps; complete stamps compare unsigned by all bytes, incomplete stamps compare by user version.

## State And Persistence Behavior
State is `complete` plus `versionBytes`. `getBytes` deliberately returns the internal array for performance, so callers can mutate the object if careless. Incomplete stamps are used with `SET_VERSIONSTAMPED_KEY` and completed by the database at commit time.

## Dependencies And Integration Points
`TupleUtil` encodes/decodes versionstamps and enforces incomplete versionstamp count. `Tuple` and `Subspace` expose versionstamp packing. `VersionstampSmokeTest` and tuple tests exercise database round trips.

## Risks And Test Signals
Risks include internal byte-array mutation, sentinel completeness detection, unsigned user-version bounds, compare order for complete versus incomplete stamps, and interaction with tuple versionstamp offsets. Tests should cover factory validation, equality/hash after mutation risks, user-version unpacking, tuple pack/unpack, and actual database versionstamped mutations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/Versionstamp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/package-info.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/package-info.java

## Purpose
This package descriptor documents tuple serialization utilities for typed data in FoundationDB keys and values.

## Important APIs, Types, And Functions
It exports package-level Javadoc referencing `Tuple` and FoundationDB data modeling documentation. It describes packed tuples as suitable for indexes and organizational keyspace structures.

## Control Flow, State, And Persistence
No runtime code executes. The documented persistence behavior is tuple byte encoding with predictable sort order.

## Dependencies And Integration Points
It frames the tuple layer used by `Subspace`, `DirectoryLayer`, tests, examples, and application code.

## Risks And Test Signals
Documentation drift is the main risk, especially supported types and sort-order guarantees. Direct test signal is Javadoc generation; behavioral tests live in tuple conformance and performance tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/overview.html.in -->
# sources/storage-engines/foundationdb/bindings/java/src/main/overview.html.in

## Purpose
This Javadoc overview introduces the Java binding, installation, basic usage, and the included Tuple and Directory APIs.

## Important APIs, Types, And Functions
The HTML references client binaries, Maven Central artifact `org.foundationdb:fdb-java`, `FDB.selectAPIVersion(ApiVersion.LATEST)`, `Database`, `Transaction`, `Tuple`, and directory/subspace APIs. It includes a runnable-style example that opens the default database and writes/reads a tuple key.

## Control Flow, State, And Persistence
The example selects an API version, opens a database, runs a transaction that sets key `Tuple.from("hello").pack()` to value `Tuple.from("world").pack()`, then runs a second transaction to read and unpack it.

## Dependencies And Integration Points
This file feeds generated Java documentation and links to FoundationDB docs for client installation, cluster files, tuple data modeling, and directory usage.

## Risks And Test Signals
Risks include stale supported API version range, outdated Maven URL/artifact, example imports drifting, and links moving. Direct tests are documentation build checks and example compilation/smoke tests against a running cluster.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/overview.html.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/AbstractTester.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/AbstractTester.java

## Purpose
`AbstractTester` is the base class for Java binding performance/correctness test programs.

## Important APIs, Types, And Functions
It defines `NUM_RUNS`, ASCII charset, fields for `TesterArgs`, `Random`, `TestResult`, and `FDB`, abstract `testPerformance(Database)`, `runTest`, `run`, `multiVersionDescription`, and `wrapAndPrintError`.

## Control Flow
`run` parses CLI arguments, selects the current test API version, configures multi-version/external-client options, runs the test, catches errors into `TestResult`, and saves results. `runTest` opens the database in a try-with-resources block and calls subclass performance logic.

## State And Persistence Behavior
State includes parsed options, selected FDB API object, random test result collector, and output directory persistence through `result.save`. Database persistence is controlled by subclasses.

## Dependencies And Integration Points
It depends on `FDB`, `Database`, `TesterArgs`, `TestApiVersion`, and `TestResult`. Other test classes extend it for benchmarks and binding validation.

## Risks And Test Signals
Risks include invalid option combinations, external-client configuration order, swallowed parse failures, and result reporting after exceptions. Tests should cover CLI modes, failed `fdb.open`, subclass exception capture, and output serialization.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/AbstractTester.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/AsyncDirectoryExtension.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/AsyncDirectoryExtension.java

## Purpose
`AsyncDirectoryExtension` implements asynchronous stack-machine instructions for testing the Java directory and subspace APIs against binding conformance scenarios.

## Important APIs, Types, And Functions
It stores a list of directory/subspace handles, active `dirIndex`, and `errorIndex`. `processInstruction` wraps `executeInstruction` and reports failures through test `DirectoryUtil.pushError`. `executeInstruction` handles `DirectoryOperation` values for creating subspaces/layers, changing current directory, create/open/create, move, remove, list, exists, pack/unpack/range/contains, open subspace, log subspace/directory, and strip prefix.

## Control Flow
Each instruction pops typed values from `Instruction`, calls the selected async directory/subspace method, and pushes outputs back to the stack. Errors are converted to stack-test errors instead of escaping. `DIRECTORY_EXISTS` forces a read version first because Java's root `DirectoryLayer.exists` can otherwise return true without reading, while other bindings perform a read.

## State And Persistence Behavior
`dirList` persists handles across instructions. Some instructions write to the database, especially directory mutations and log operations that store path/layer/exists/children under tuple-packed log keys. Directory state itself is persisted by `DirectoryLayer`.

## Dependencies And Integration Points
It depends on `Instruction`, `DirectoryOperation`, test `DirectoryUtil`, `StackUtils`, `AsyncUtil`, `Directory`, `DirectoryLayer`, `DirectorySubspace`, `Subspace`, `Tuple`, and `Range`. It complements synchronous `DirectoryExtension` and cross-binding stack tests.

## Risks And Test Signals
Risks include type casts from stack parameters, null handle handling through `errorIndex`, async exception wrapping hiding exact failure points, path count conventions for remove/list/exists, and compatibility quirks such as forced read versions. Tests should execute every directory opcode, compare async and sync extension behavior, cover null/error index paths, and validate logged directory metadata.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/AsyncDirectoryExtension.java -->
