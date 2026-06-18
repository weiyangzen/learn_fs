# Research Report: subset-b-008387

This grouped report covers the Java binding JNI bridge, Java workload adapter, Maven/style metadata, integration tests, and tuple/unit tests listed for `subset-b-008387`. Each source file section is delimited for reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/JavaWorkload.cpp -->
# sources/storage-engines/foundationdb/bindings/java/JavaWorkload.cpp

## Purpose
`JavaWorkload.cpp` implements the C++ simulation workload factory used to run Java workloads inside FoundationDB's workload framework. It creates and owns a JVM, injects Java test workload classes into the class path, registers native methods expected by `com.apple.foundationdb.testing.*`, and adapts the C++ `FDBWorkload` lifecycle (`init`, `setup`, `start`, `check`, `getMetrics`) to Java `AbstractWorkload` methods.

## Important APIs, Types, and Functions
- `workloadFactory(FDBLogger*)` exports the FoundationDB workload factory symbol and returns a static `JavaWorkloadFactory`.
- `JavaWorkloadFactory` caches a weak `JVM` instance so workloads in one process share a JVM while allowing cleanup when no workload remains.
- `JVM` wraps `JavaVM*`, `JNIEnv*`, class path tracking, native method registration, class/method/field lookup helpers, and Java object construction.
- Native callbacks registered into Java include `AbstractWorkload.log`, `WorkloadContext` getters/setters/options, and `Promise.send`.
- `JavaPromise` owns a moved `GenericPromise<bool>` and deletes itself after `send`, making the Java promise object a native pointer holder.
- `JavaWorkload` stores the Java workload global reference, the converted class name, the workload context, and a failure flag.

## Control Flow
The factory creates a `JavaWorkload`, replacing dots in the requested workload name with slash-separated JNI class names. `JavaWorkload::init` reads the `classPath` workload option, splits it on `;` and `,`, adds each path through `URLClassLoader.addURL`, initializes native registrations once, creates a Java `WorkloadContext`, and instantiates the requested workload class. Lifecycle calls allocate a Java `FDBDatabase` wrapper around the native `FDBDatabase*`, allocate a Java `Promise`, call `setup`, `start`, or `check`, then let Java asynchronously call back into `Promise.send`. `getMetrics` calls Java `getMetrics`, iterates the returned `List<PerfMetric>`, reads fields, and pushes `FDBPerfMetric` values back to C++.

## State and Persistence Behavior
Persistent state is process-local and native: the JVM, cached class path set, static Java logger pointer, global Java workload reference, and pending `JavaPromise` objects. Database state is not persisted here; database pointers are passed through to Java wrappers. The code mutates the Java system class loader and globally registers native methods, so JVM state is effectively singleton-like for the process. `JavaWorkload` uses `failed` to short-circuit later lifecycle calls after JNI setup or invocation failures.

## Dependencies and Integration Points
This file depends on `foundationdb/CppWorkload.h`, the FDB C API, JNI, generated JNI headers for testing classes, Boost string splitting/replacement, and Java classes under `com.apple.foundationdb.testing` and `com.apple.foundationdb`. It integrates with Java bindings by selecting `FDB_API_VERSION`, disabling the Java shutdown hook, constructing `FDBDatabase`, and using workload-provided executors.

## Risks and Edge Cases
JNI local reference management is partial; many local references from map iteration, class lookup, and metric iteration are not explicitly deleted, so long-running or high-cardinality workloads could stress local reference tables. `createWorkload` calls `NewGlobalRef(res)` but ignores the return value, leaving `workload` as the original local reference; if this runs beyond the local frame lifetime, that is a correctness risk. `JVM::addToClassPath` assumes the system class loader supports `URLClassLoader.addURL`, which is not true for newer Java module-era class loader implementations unless the environment arranges compatibility. `JavaPromise` deletes itself on `send`; double-send from Java would be use-after-free. Errors during `setup/start/check` set `failed` but do not always complete the C++ promise, which can hang callers if an exception occurs after the native promise was handed off.

## Test Signals
The file is exercised indirectly by simulation workloads that load Java workload classes and by Java binding tests that require the JNI library to be functional. Good test signals include workload lifecycle completion, Java-side logging through native logger pointers, option reads from `WorkloadContext`, and metric extraction. There are no direct unit tests in this subset for the global-reference lifetime or class-loader assumptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/JavaWorkload.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/fdb-java-style.xml -->
# sources/storage-engines/foundationdb/bindings/java/fdb-java-style.xml

## Purpose
`fdb-java-style.xml` is the Checkstyle configuration for FoundationDB Java binding source. It defines formatting, naming, import, block, whitespace, and small design constraints intended to keep Java binding code idiomatic while still visually compatible with the wider FoundationDB codebase.

## Important APIs, Types, and Functions
The file configures Checkstyle's `Checker` root with a `SuppressionFilter` sourced from `suppressions.xml` and a `TreeWalker` containing modules such as `AvoidNestedBlocks`, `EmptyBlock`, `LeftCurly`, `HideUtilityClassConstructor`, `CovariantEquals`, `FallThrough`, `CustomImportOrder`, `AvoidStarImport`, `UnusedImports`, `Indentation`, `ModifierOrder`, naming checks, and whitespace checks.

## Control Flow
Checkstyle loads the DTD-backed XML, applies the suppression filter first, then walks Java ASTs under `TreeWalker`. Modules either enforce structural rules, report source formatting violations, or allow exceptions via explicit properties such as catch parameter naming and custom import ordering.

## State and Persistence Behavior
The file has no runtime state. Its persistent effect is build-time policy: any Maven or CI step invoking Checkstyle with this config will accept, reject, or suppress Java binding source style violations.

## Dependencies and Integration Points
It depends on Checkstyle's `configuration_1_3.dtd` schema and module names available in the configured Checkstyle version. It also depends on `suppressions.xml` being present relative to the Checkstyle invocation. It integrates with the Java binding build and review workflow rather than with runtime code.

## Risks and Edge Cases
The configuration references legacy Checkstyle module/property names; upgrades can break builds if modules are renamed or properties change. Some useful checks are commented out, including `DesignForExtension`, `FinalClass`, and `MagicNumber`, so the file is not a complete quality gate. The `CustomImportOrder` only defines three broad groups and may miss project-specific import grouping expectations.

## Test Signals
The primary signal is Checkstyle execution in Maven/CI. Passing tests show source syntax and style compatibility with this configuration, but not runtime correctness.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/fdb-java-style.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/fdbJNI.cpp -->
# sources/storage-engines/foundationdb/bindings/java/fdbJNI.cpp

## Purpose
`fdbJNI.cpp` is the native JNI bridge for the FoundationDB Java bindings. It exposes Java-native methods for FDB futures, database operations, transaction operations, options, network lifecycle, and JNI library load/unload hooks, translating between Java objects and FoundationDB C API handles.

## Important APIs, Types, and Functions
- Global JNI state includes `g_jvm`, thread-local `g_thread_jenv`, thread-local `g_IFutureCallback_call_methodID`, external-thread tracking, and cached global class/method references for range/key/mapped result objects.
- Error helpers include `throwOutOfMem`, `getThrowable`, `throwNamedException`, `throwRuntimeEx`, `throwParamNotNull`, and `safeThrow`.
- Future natives cover callback registration, blocking, error retrieval, readiness, cancellation, disposal, memory release, and typed getters for bool, int64, byte arrays, string arrays, key arrays, key-range arrays, range results, and mapped range results.
- Database natives create/destroy `FDBDatabase`, set database options, fetch main-thread busyness, create transactions, and return client status futures.
- Transaction natives cover read version, get, getKey, range scans, mapped range scans, direct-buffer result marshalling, estimated range size, split points, set, clear, clear range, atomic mutate, commit, options, committed version, approximate size, versionstamp, key locations, onError, dispose/reset/cancel/watch, and conflict ranges.
- Network/API natives cover API version selection, network options, setup, run, stop, and global reference initialization/cleanup in `JNI_OnLoad` and `JNI_OnUnload`.

## Control Flow
Java calls pass native pointer values as `jlong`. Each JNI method validates pointer and array parameters, converts Java strings or byte arrays into native buffers, calls the matching FDB C API, releases Java array elements with `JNI_ABORT` for input-only arrays, and returns either a native future pointer or a marshalled Java result. Future callbacks are registered by converting Java `Runnable` callbacks to global references and setting `fdb_future_set_callback`; callback execution attaches external client threads to the JVM as daemon threads when necessary, calls `Runnable.run`, then deletes the callback global reference.

Range result marshalling has two paths. Object-array paths copy native result bytes into Java `byte[]` and length arrays, then instantiate `RangeResult`, `KeyArrayResult`, `KeyRangeArrayResult`, `MappedRangeResult`, or `MappedKeyValue`. Direct-buffer paths write compact metadata and bytes into caller-provided direct buffers and truncate to the first result that fits while setting `more=true`.

`JNI_OnLoad` caches global references and constructor/static method IDs for frequently used Java result classes. `Network_run` records the network-thread `JNIEnv`, resolves callback method IDs, installs a network-thread completion hook to detach external threads, then calls `fdb_run_network`.

## State and Persistence Behavior
Native state is process-global: the selected API version, FDB network lifecycle, global class references, and thread-local JNI callback state. Database and transaction state lives in FDB C handles whose lifetime is controlled by explicit Java close/dispose calls. Futures hold native resources until destroyed, cancelled, or memory-released by Java wrappers. The bridge itself does not persist data, but transaction mutation methods directly mutate FoundationDB transaction state that is committed later.

## Dependencies and Integration Points
The file depends on generated JNI headers for Java binding classes, `foundationdb/fdb_c.h`, Java classes such as `FDBException`, `RangeResult`, `MappedRangeResult`, `MappedKeyValue`, `Range`, and `Runnable`, plus the FoundationDB C client library. It is the main integration point between Java APIs and the native C client ABI.

## Risks and Edge Cases
JNI error paths must be exact: missed releases can leak pinned arrays, and releasing with the wrong mode could copy unwanted input buffers back. Several methods allocate local references in loops without explicit cleanup, which can matter for very large result arrays. Callback registration deletes the Java global reference after one callback; this matches FDB future callback semantics but depends on callbacks never firing multiple times. External thread attach/detach relies on a network completion hook and thread-local flags; unusual callback threads or lifecycle races could leak attached daemon threads. Direct-buffer marshalling trusts the supplied `bufferCapacity` and writes native-endian `jint` values, so Java readers must match layout and byte order. `JNI_OnLoad` does not check every `FindClass`/`GetMethodID` result before creating global refs, so class signature drift can fail later or crash earlier depending on pending exceptions.

## Test Signals
Integration tests in this subset exercise many JNI paths: range and mapped range scans, futures and cancellation callbacks, watches, client status, transaction commit state, database opens, and external-client tags. Unit tests with disabled native calls check event counting around JNI calls but avoid real native execution. There is no focused stress test here for local reference limits, direct buffer overflow prevention beyond capacity truncation, or JNI class-cache failure handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/fdbJNI.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/pom.xml.in -->
# sources/storage-engines/foundationdb/bindings/java/pom.xml.in

## Purpose
`pom.xml.in` is a Maven POM template for publishing/building the FoundationDB Java binding artifact. Placeholder tokens `NAME` and `VERSION` are intended to be substituted by the build system.

## Important APIs, Types, and Functions
The template declares Maven coordinates `org.foundationdb:NAME:VERSION`, `jar` packaging, project name `foundationdb-java`, project metadata, organization/developer entries, SCM URL, and Apache 2.0 license metadata.

## Control Flow
There is no executable control flow. The build system expands the template into a real `pom.xml`, and Maven consumes the resulting metadata during packaging, installation, or publication.

## State and Persistence Behavior
The file persists artifact identity and publication metadata. It does not declare dependencies, plugins, source/target levels, or test configuration, so those are expected to be supplied elsewhere in the build.

## Dependencies and Integration Points
It integrates with Maven's POM 4.0.0 model and the FoundationDB release/build process. The description explicitly points users to FoundationDB client releases because the Java binding requires the native client library under a different license.

## Risks and Edge Cases
Publishing correctness depends on token substitution. If `NAME` or `VERSION` are not replaced, invalid or misleading artifact coordinates can be published. Because dependency and plugin declarations are absent, consumers cannot infer the native client dependency from Maven metadata alone.

## Test Signals
Signals are build-time: generated POM validation, Maven package/install/deploy success, and artifact metadata inspection after substitution.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/pom.xml.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/BasicMultiClientIntegrationTest.java -->
# sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/BasicMultiClientIntegrationTest.java

## Purpose
This integration test verifies that multiple FoundationDB client instances can write and read data through the Java API when configured by `MultiClientHelper`.

## Important APIs, Types, and Functions
The class uses JUnit 5, `@RegisterExtension MultiClientHelper`, `FDB.selectAPIVersion(630)`, database options, `Database.run`, `Transaction.set`, `Transaction.get`, and `Tuple` packing/unpacking.

## Control Flow
The test selects API version 630, sets a low trace severity knob, opens one `Database` per cluster file from `FDB_CLUSTERS`, then loops 25 times. For each opened database it writes a random tuple key/value pair in one transaction, reads the key in a second transaction, unpacks the value, and asserts equality. A short sleep separates outer iterations.

## State and Persistence Behavior
It persists random keys into every configured cluster and does not clear them afterward, so repeated runs leave test data behind. Database handles are owned by the helper and reused for the test class.

## Dependencies and Integration Points
It depends on a configured multi-client environment, `FDB_CLUSTERS`, the native external client stack, and tuple encoding. The `MultiClient` tag is used to exclude it from ordinary single-client test runs.

## Risks and Edge Cases
The test uses random keys without a test namespace, creating possible collisions with other tests or previous runs, though the wide random space lowers the chance. It does not close databases itself and relies on helper behavior, but `MultiClientHelper` in this subset does not implement an after-all close callback. It selects a fixed API version rather than `ApiVersion.LATEST`.

## Test Signals
Passing indicates basic cross-client open/write/read behavior, tuple round-trip, and transaction retries through `Database.run` are functional in a multi-client setup.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/BasicMultiClientIntegrationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/CycleMultiClientIntegrationTest.java -->
# sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/CycleMultiClientIntegrationTest.java

## Purpose
This standalone multi-client integration workload tests transaction atomicity by maintaining a four-node directed cycle while concurrent writers transform edges and concurrent checkers validate cycle invariants.

## Important APIs, Types, and Functions
The file defines `CycleMultiClientIntegrationTest`, nested `CycleWorkload`, nested `CycleChecker`, and constants controlling transaction counts and thread count. It uses `FDB.selectAPIVersion(ApiVersion.LATEST)`, `MultiClientHelper`, `FDBOptions` for client threading/external client directory/tracing/knobs, `Database.run`, and tuple encoding.

## Control Flow
`main` selects FDB, configures one client thread per cluster file, opens all databases, initializes keys `0..3` as a cycle, starts writer threads for each database, then starts checker threads and waits for checkers to finish. Writers repeatedly pick a cycle node, read four linked values, and rewrite three edges to reverse part of the cycle. Checkers read four linked values from random starts, assert the fourth points back to the key, sort the observed values, and compare them with `[0,1,2,3]`.

## State and Persistence Behavior
The test writes un-namespaced tuple keys `"0"` through `"3"` to every configured database and leaves the final cycle state in place. Shared static state includes `expected` and helper instances. The checker success flag is per checker instance and read after thread join.

## Dependencies and Integration Points
It depends on external-client multi-cluster setup through `/var/dynamic-conf/lib` and `FDB_CLUSTERS`. It is not a JUnit `@Test`; it is a main-driven workload likely intended for specialized multi-client execution.

## Risks and Edge Cases
Un-namespaced keys are invasive. Writer threads are not joined, so they may still be running while checkers validate and when the program exits. Exceptions inside worker threads are not captured as explicit failures unless they affect the success flag. The read of `succeed` is safe after `join`, but the flag is not volatile for any earlier observation.

## Test Signals
Passing checkers indicate observed transaction snapshots preserve cycle invariants under concurrent transactional rewrites across multi-client database handles.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/CycleMultiClientIntegrationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/DirectoryTest.java -->
# sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/DirectoryTest.java

## Purpose
`DirectoryTest` verifies basic Java directory-layer behavior against a running FoundationDB database: creation, subdirectory creation, moving, duplicate creation errors, and removal of missing directories.

## Important APIs, Types, and Functions
It uses `DirectoryLayer`, `DirectorySubspace`, `DirectoryAlreadyExistsException`, `NoSuchDirectoryException`, `Database.run`, and JUnit `@ExtendWith(RequiresDatabase.class)`.

## Control Flow
Each test opens a database with the latest API version and runs directory operations inside transactions. Creation tests create paths, inspect returned path metadata, and call `exists`. Move tests create source/destination paths and move a subdirectory with `moveTo`. Negative tests assert that duplicate creation and removing nonexistent paths produce the expected directory exceptions, allowing for exceptions wrapped in `CompletionException`.

## State and Persistence Behavior
Tests mutate the directory layer metadata in the default directory layer location. Most tests remove created paths in `finally`, but failures before cleanup or cleanup exceptions can leave directory metadata behind. The test does not isolate paths with UUID prefixes, so names like `foo`, `src`, and `dest` can collide with concurrent runs.

## Dependencies and Integration Points
It depends on a live FDB instance, `RequiresDatabase` health checking, Java directory-layer implementation, transaction retry behavior, and CompletableFuture exception wrapping.

## Risks and Edge Cases
The cleanup in `testCanCreateSubDirectory` removes the final path list after appending `"bar"`, so it removes `foo/bar` but may leave parent `foo` depending on directory-layer semantics. Tests sharing plain path names are brittle under parallel integration test execution. Catching both direct directory exceptions and `CompletionException` is useful but somewhat inconsistent across tests.

## Test Signals
Passing tests show the Java directory layer can create/open/move/remove metadata and preserve expected exception behavior against a real cluster.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/DirectoryTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/FutureIntegrationTest.java -->
# sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/FutureIntegrationTest.java

## Purpose
This integration test validates Java binding future cancellation and callback behavior for FDB reads, including callback execution using both the default executor and a direct executor.

## Important APIs, Types, and Functions
The file defines a `DirectExecutor`, four `@Test` methods tagged `SupportsExternalClient`, and a `testTransaction` helper. It uses `CompletableFuture`, `thenAcceptAsync`, `cancel`, `join`, `Database.run`, and `Transaction.get`.

## Control Flow
Each test passes a transaction lambda into `testTransaction`, which runs it ten times using a normal database and ten times using `fdb.open(null, new DirectExecutor())`. The scenarios cancel a future before use, cancel a future after setting a callback, register a callback after `join`, and cancel futures from inside a callback.

## State and Persistence Behavior
The tests read absent keys and do not write database state. State is limited to futures, callback queues, and executor behavior during each transaction.

## Dependencies and Integration Points
This is a direct signal for `NativeFuture` callback registration/cancellation, JNI callback execution, Java executor dispatch, and the transaction lifetime expectations around futures. It depends on `RequiresDatabase` to ensure a live cluster.

## Risks and Edge Cases
Callbacks are asynchronous; some lambdas may not be forced to complete before the transaction lambda returns unless cancellation or join triggers them. The tests assert callback values are null but do not capture failures from callbacks unless those failures propagate through the executor/future path. Direct executor coverage is valuable because it exercises reentrant callback behavior.

## Test Signals
Passing indicates cancellation does not crash, callbacks can be installed before and after readiness, and callback code can perform additional FDB operations or cancel related futures without deadlocking.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/FutureIntegrationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/GetClientStatusIntegrationTest.java -->
# sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/GetClientStatusIntegrationTest.java

## Purpose
This integration test checks that `Database.getClientStatus()` returns a meaningful healthy client status report from the Java binding.

## Important APIs, Types, and Functions
It uses `FDB.selectAPIVersion(ApiVersion.LATEST)`, `fdb.open()`, `Database.run`, `Transaction.getReadVersion`, `Database.getClientStatus`, and JUnit assertions.

## Control Flow
The test opens a database, runs a read-version transaction to force client initialization, then retrieves client status bytes, converts them to a string, and asserts the JSON-like text contains `"Healthy":true`.

## State and Persistence Behavior
It does not modify database key-value state. It depends on and observes client status state maintained by the native FDB client.

## Dependencies and Integration Points
It exercises the JNI `Database_getClientStatus` path, future byte-array result marshalling, and C API client status reporting. Unlike most integration tests here, it is not annotated with `RequiresDatabase`, so it assumes the test environment provides a reachable database.

## Risks and Edge Cases
String containment is a loose JSON validation and could fail on formatting/schema changes even if the client is healthy. Lack of `RequiresDatabase` means a missing cluster fails rather than skipping or producing the standardized health-check failure.

## Test Signals
Passing indicates the client can connect, complete a read-version transaction, and return a status document showing healthy state through the Java API.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/GetClientStatusIntegrationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/MappedRangeQueryIntegrationTest.java -->
# sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/MappedRangeQueryIntegrationTest.java

## Purpose
This integration/performance test compares ordinary index range queries plus per-record range reads with FoundationDB mapped range queries, while validating that mapped results reconstruct the expected record ranges.

## Important APIs, Types, and Functions
The class defines tuple-key helpers for index and record entries, `insertRecordWithIndex`, `insertRecordsWithIndexes`, `RangeQueryWithIndex`, `rangeQueryAndThenRangeQueries`, `mappedRangeQuery`, `validateRangeResult`, and `assertByteArrayEquals`. It uses `Transaction.getRange`, `Transaction.getMappedRange`, `MappedKeyValue`, `AsyncUtil.whenAll`, `Range.startsWith`, and `StreamingMode.WANT_ALL`.

## Control Flow
The test generates a UUID-backed prefix, inserts 1000 indexed records in batches of 100, then runs the ordinary query and mapped query once each over a random contiguous range of 100 logical records. The ordinary path scans index entries, launches record-range reads in parallel, waits for all, and validates each returned split. The mapped path passes a tuple mapper and validates returned index key/value, mapped range begin/end, and embedded range result for each record.

## State and Persistence Behavior
The test writes namespaced but persistent data under a random `mapped-range-query-<uuid>` prefix. It does not clear data afterward. Static `MAPPER` captures the static `PREFIX` and record mapper tuple.

## Dependencies and Integration Points
It heavily exercises mapped-range JNI marshalling, `MappedKeyValue.fromBytes`, range iterator behavior, tuple encoding, and server support for mapped range. The `main` path reads `FDB_CLUSTERS` via `MultiClientHelper`, while the JUnit test uses the default cluster and `RequiresDatabase`.

## Risks and Edge Cases
The performance instrumentation computes `qps` as `numQueries * 1000L / time`; if a query finishes within 0 ms, this can divide by zero. The test leaves data behind and uses only one query by default, so it is more of a smoke/performance comparison than exhaustive validation. `assertByteArrayEquals` compares printable strings rather than byte arrays, which gives readable failures but can obscure array identity concerns.

## Test Signals
Passing validates mapped range result count, index key/value preservation, mapper-derived range boundaries, and embedded range result content across JNI and Java object reconstruction.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/MappedRangeQueryIntegrationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/MultiClientHelper.java -->
# sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/MultiClientHelper.java

## Purpose
`MultiClientHelper` centralizes multi-client integration-test setup by reading cluster file paths from `FDB_CLUSTERS` and opening one `Database` per configured cluster.

## Important APIs, Types, and Functions
It implements JUnit `BeforeAllCallback`, provides static `readClusterFromEnv`, and exposes package-private `openDatabases(FDB)`.

## Control Flow
`beforeAll` reads and caches cluster files before test execution. `openDatabases` lazily reads cluster files if needed, opens each cluster path with `fdb.open(arg)`, caches the resulting collection, and returns the same collection for later calls.

## State and Persistence Behavior
The helper persists `clusterFiles` and `openDatabases` in the helper instance for the class lifetime. It does not close databases and does not implement `AfterAllCallback`, despite comments in users saying the helper will close databases.

## Dependencies and Integration Points
It depends on the `FDB_CLUSTERS` environment variable using semicolon delimiters and on Java binding database open behavior. It is used by multi-client integration classes in this subset.

## Risks and Edge Cases
Missing `FDB_CLUSTERS` throws `IllegalStateException`. Open databases are not closed, so long-running suites can leak native handles. The cached collection can contain partially opened databases if an exception occurs mid-loop. The helper is not thread-safe, but most setup happens before concurrent workload execution.

## Test Signals
Tests using it signal correct multi-client configuration when they can open all configured cluster files and perform transactions through each `Database`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/MultiClientHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/RangeQueryIntegrationTest.java -->
# sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/RangeQueryIntegrationTest.java

## Purpose
This integration test verifies Java range-query behavior against a live FoundationDB cluster, covering key selectors, inclusive/exclusive ranges, empty scans, and multi-row scans.

## Important APIs, Types, and Functions
It uses `RequiresDatabase`, `Database.run`, `Transaction.clear`, `Transaction.set`, `Transaction.get`, `Transaction.getRange`, `KeySelector`, `AsyncIterable`, `AsyncIterator`, `KeyValue`, and `ByteArrayUtil`.

## Control Flow
`clearDatabase` runs before and after each test, retrying a full database clear up to five times. Individual tests load small data sets, then run transactions that read exact keys or iterate range query results and assert keys/values/counts. The key-selector test generates a random key with a fixed first byte and scans the range for that leading byte.

## State and Persistence Behavior
The setup/teardown clears the full keyspace `[empty, 0xff)`, which is safe only for isolated test clusters. Within tests, state is simple test key-value data written and then cleared.

## Dependencies and Integration Points
It exercises JNI `get`, `getRange`, range iterator Java logic, tuple-independent byte-array comparison, and the live database health gate. It also depends on transaction retry behavior for clearing under heavy CI load.

## Risks and Edge Cases
Full database clears are destructive if run against a non-test cluster. The range `"multi"` to `"multj"` assumes ASCII lexicographic ordering around generated keys. Only 100 rows are used, which may or may not force multiple batches depending on client/server behavior.

## Test Signals
Passing indicates basic range scanning and key selector marshalling work end-to-end through the Java binding and native client.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/RangeQueryIntegrationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/RepeatableReadMultiThreadClientTest.java -->
# sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/RepeatableReadMultiThreadClientTest.java

## Purpose
This standalone multi-client workload attempts to verify repeatable-read semantics: long-running transactions should continue seeing the original value while separate transactions commit a new value and then read it.

## Important APIs, Types, and Functions
The file defines `RepeatableReadMultiThreadClientTest`, nested `OldValueReader`, nested `NewValueReader`, static configuration, and `setupThreads`, `setup`, `readOldValue`, and `setNewValueAndRead`. It uses `FDBOptions` for multi-client setup, `Database.run`, tuple encoding, and JUnit assertions from a main-driven workload.

## Control Flow
`main` configures external clients, opens databases from `FDB_CLUSTERS`, writes `foo=bar`, starts old-value reader threads, sleeps one second, starts new-value writer/reader threads, joins new readers, asserts old readers are still alive, then joins old readers. Old readers run one transaction that repeatedly reads the key with sleeps, expecting `bar`. New readers write `cool` in one transaction and read it in another.

## State and Persistence Behavior
The test writes un-namespaced key `foo` to each configured database and leaves it set to `cool`. Static `threadToOldValueReaders` records thread-to-reader state.

## Dependencies and Integration Points
It depends on multi-client external client configuration, tuple encoding, transaction snapshot behavior, and Java thread scheduling.

## Risks and Edge Cases
There is a likely test bug: `readOldValue` creates `oldValueReader`, but starts `new Thread(OldValueReader.create(db))`, then stores the unused `oldValueReader` in the map. The assertions inspect success flags on instances that never ran, so old-reader failures can be missed. Old readers also perform `Thread.sleep` inside a transaction, making the test timing-sensitive and potentially vulnerable to transaction timeout or retry behavior. It is not a JUnit `@Test`, so execution depends on an external runner invoking `main`.

## Test Signals
If corrected, passing would indicate repeatable-read snapshot semantics across concurrent multi-client transactions. As written, liveness checks still signal that old reader threads ran long enough, but success validation is weakened by the instance mismatch.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/RepeatableReadMultiThreadClientTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/RequiresDatabase.java -->
# sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/RequiresDatabase.java

## Purpose
`RequiresDatabase` is a JUnit 5 extension that enables/skips integration tests based on `run.integration.tests` and performs a before-all health check against a running FoundationDB database.

## Important APIs, Types, and Functions
It implements `ExecutionCondition` and `BeforeAllCallback`. Key functions are `canRunIntegrationTest`, `evaluateExecutionCondition`, and `beforeAll`. It uses `FDB.selectAPIVersion`, optional `external_client_library` configuration, database options, transaction timeout, and JUnit `Assertions.fail`.

## Control Flow
`evaluateExecutionCondition` disables tests only when the system property `run.integration.tests` parses false. `beforeAll` selects FDB, sets external-client options once if configured, opens a database, and attempts up to ten small read transactions with a 5-second transaction timeout and 500 ms backoff. If all attempts fail, it fails the test class with a contextual message.

## State and Persistence Behavior
The static `networkOptionsSet` prevents repeated external-client option setup across classes. No database data is modified; the health check reads key `"test"`.

## Dependencies and Integration Points
It integrates with JUnit 5 extension APIs, Maven/JUnit configuration parameters, FoundationDB network option setup, and all annotated integration tests in this subset.

## Risks and Edge Cases
The condition message says "Database is running" whenever tests are enabled, before the health check actually proves it. `networkOptionsSet` is static and unsynchronized; parallel class initialization could race. Once external client options are set, later classes cannot change them. Missing `run.integration.tests` means tests run by default and fail if no cluster is available.

## Test Signals
Annotated tests get a consistent fail-fast connection check and optional external-client-library setup. A successful `beforeAll` means the Java binding can select the API, open a database, set timeout, and complete a read quickly.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/RequiresDatabase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/SidebandMultiThreadClientTest.java -->
# sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/SidebandMultiThreadClientTest.java

## Purpose
This standalone multi-client workload tests causal consistency between a committed database write and a sideband JVM queue message: a consumer should see the key after the producer commits and then enqueues the key name.

## Important APIs, Types, and Functions
It defines static `db2Queues`, nested `Producer`, nested `Consumer`, and setup/process/check helpers. It uses `BlockingQueue`, `LinkedBlockingQueue`, `ThreadLocalRandom`, `Database.run`, tuple encoding, and JUnit assertions.

## Control Flow
`main` configures external client threading, opens all databases, creates one queue per database, starts producer threads for every database, then starts consumer threads and joins consumers. Each producer commits `txnCnt` random keys and offers each key to the queue after commit. Consumers take keys, read them in transactions, and fail if any read returns null.

## State and Persistence Behavior
The test writes many random tuple keys under `Sideband/Multithread/Test/<suffix>` and does not clear them. Queue state is in-memory per database.

## Dependencies and Integration Points
It depends on external-client multi-cluster setup, Java thread scheduling, transaction commit visibility, and tuple packing. Like other multi-client workloads here, it is main-driven rather than a JUnit test method.

## Risks and Edge Cases
Producers are not joined, while each consumer expects exactly `txnCnt` keys. With five producers and five consumers per database, aggregate counts happen to match, but slow producers can make consumers block indefinitely. Random keys are not namespaced by run id and may collide rarely. The consumer decodes the value but does not assert it equals `"bar"`.

## Test Signals
Passing indicates that once a producer's `Database.run` returns, subsequent consumer transactions in the same database handle set can observe the committed key when driven by an out-of-band Java queue.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/SidebandMultiThreadClientTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/TransactionIntegrationTest.java -->
# sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/TransactionIntegrationTest.java

## Purpose
`TransactionIntegrationTest` verifies Java-binding behavior when operations are attempted after a transaction commit has been submitted or completed.

## Important APIs, Types, and Functions
It uses `FDB`, `Database`, `Transaction`, `CompletableFuture<Void>`, `CompletionException`, `FDBException`, and error code `2017` (`used_during_commit`).

## Control Flow
The test opens a database and repeats ten transactions. Each transaction writes `key1`, starts `commit`, attempts a read and a second commit that should fail with `used_during_commit`, waits for the original commit to succeed, then repeats the same invalid operation checks after commit completion.

## State and Persistence Behavior
The test writes `key1=val1` repeatedly and attempts `key2=val2` after commit submission, expecting that write to have no effect. It does not clear written state.

## Dependencies and Integration Points
It exercises Java transaction state guarding, native commit future behavior, error propagation through `CompletableFuture`, and `RequiresDatabase`.

## Risks and Edge Cases
`expectUsedDuringCommitError` assumes the thrown `CompletionException` cause is always `FDBException`; other exception shapes would cause `ClassCastException` rather than a clean assertion. The test does not verify that `key2` was not committed, only that a later commit attempt fails.

## Test Signals
Passing indicates Java transactions prevent additional native operations once commit is in flight or completed and propagate the expected FDB error code.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/TransactionIntegrationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/WatchesIntegrationTest.java -->
# sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/WatchesIntegrationTest.java

## Purpose
This integration test validates watch behavior in the Java binding, including successful watch triggering, watch limit errors, and cleanup after cancellation or closing.

## Important APIs, Types, and Functions
The class uses `DatabaseOptions.setMaxWatches`, `Transaction.watch`, `CompletableFuture.orTimeout`, `CancellationException`, `CompletionException`, `NativeFuture.close`, and helper methods `ensureConnected`, `setTestKeys`, and `createTestWatch`.

## Control Flow
Each test opens a database, sets a watch limit, ensures the client is connected via read version, writes initial key values, creates watch futures either one per transaction or many in a single transaction, changes keys, and waits for expected completion or error. Over-limit tests expect FDB error code `1032`. Cleanup tests create 100 watches, cancel or close most of them, then verify the remaining watches can complete within the limit.

## State and Persistence Behavior
The tests write fixed prefixes such as `aaa`, `bbb`, `ccc`, `ddd`, and `eee` and leave final values in the database. Watch state is native client state controlled by watch futures and database watch limits.

## Dependencies and Integration Points
It strongly exercises JNI `Transaction_watch`, `NativeFuture` cancellation/close, FDB watch accounting, Java futures, external-client support, and `RequiresDatabase`.

## Risks and Edge Cases
Several tests share the `ddd` prefix, which can cause interference under parallel execution or failed cleanup. Timeouts are environment-sensitive; heavily loaded CI can trigger false failures. The over-limit tests accept the first failing future but do not assert every extra watch fails deterministically.

## Test Signals
Passing indicates watch futures trigger on key changes, watch limits are enforced, and cancelled/closed watches release resources so later watches can complete.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/WatchesIntegrationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/EventKeeperTest.java -->
# sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/EventKeeperTest.java

## Purpose
`EventKeeperTest` verifies Java-side event/instrumentation accounting for range queries and contains disabled checks for JNI call counting around native transaction operations.

## Important APIs, Types, and Functions
It uses `EventKeeper`, `MapEventKeeper`, `Events`, `RangeQuery`, `FakeFDBTransaction`, `AsyncIterator`, `KeyValue`, and `ByteArrayUtil`. Disabled tests instantiate `FDBTransaction` directly and expect `UnsatisfiedLinkError`.

## Control Flow
The active test creates a `MapEventKeeper`, a fake transaction backed by one key-value pair, constructs a `RangeQuery`, iterates all results, validates returned key/value content, computes expected byte accounting, and asserts range fetch, record count, and byte count events. Disabled tests would call native methods without a loaded library to count JNI calls.

## State and Persistence Behavior
All state is in-memory. The fake transaction avoids native resources, and the event keeper accumulates counters for the test.

## Dependencies and Integration Points
It integrates with Java range query iteration and event instrumentation. It depends on `FakeFDBTransaction` modeling range results enough for `RangeQuery`.

## Risks and Edge Cases
The disabled tests mention that ctest library loading can make them segfault, so native instrumentation coverage is intentionally absent in normal runs. Active coverage uses only a single key-value row and one range fetch.

## Test Signals
Passing shows that Java range iteration records fetch count, fetched record count, and byte accounting as expected on the fake transaction path.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/EventKeeperTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/FDBLibraryRule.java -->
# sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/FDBLibraryRule.java

## Purpose
`FDBLibraryRule` is a JUnit 5 extension that selects and preloads a FoundationDB API version before tests that need the native library or API singleton.

## Important APIs, Types, and Functions
The class implements `BeforeAllCallback`, stores an `apiVersion`, exposes `current()`, `v63()`, `get()`, and initializes `instance` in `beforeAll` by calling `FDB.selectAPIVersion`.

## Control Flow
Tests register the extension statically. Before all tests in the class, the extension selects the requested API version and stores the returned singleton-like `FDB` instance for later access.

## State and Persistence Behavior
The extension stores the selected `FDB` instance. Because FDB API selection is process-global/singleton-like, this can affect all later tests in the JVM.

## Dependencies and Integration Points
It depends on JUnit 5 extensions, `ApiVersion.LATEST`, and `FDB.selectAPIVersion`. It is used by tuple tests that require the API/library for versionstamp behavior.

## Risks and Edge Cases
Multiple test classes selecting different API versions in one JVM can conflict with the FDB singleton. The comment acknowledges the cache is only mildly useful because of that singleton behavior. There is no cleanup hook.

## Test Signals
Successful setup indicates the native library/API version can be selected before tuple or binding tests run.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/FDBLibraryRule.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/FakeFDBTransaction.java -->
# sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/FakeFDBTransaction.java

## Purpose
`FakeFDBTransaction` is an in-memory subclass of `FDBTransaction` used by unit tests to exercise Java transaction/range-query logic without a running FoundationDB server or native calls.

## Important APIs, Types, and Functions
It stores a `NavigableMap<byte[], byte[]>`, constructors for map/collection/list backing data, overrides `get`, `getRange_internal`, `closeInternal`, `close`, and `finalize`, and exposes `getNumRangeCalls`.

## Control Flow
Constructors copy supplied key-values into a `TreeMap` using `ByteArrayUtil.comparator`. `get` returns a completed future from the backing map. `getRange_internal` increments a call counter, derives a submap from begin/end `KeySelector`s, optionally reverses it, returns a custom `FutureResults` whose `getResults` materializes `KeyValue` objects until row or target-byte limits are reached, then completes the future immediately.

## State and Persistence Behavior
State is in-memory only: backing data and range-call count. Native pointer values are dummy constructor inputs, and close/finalize are no-ops to avoid native destruction.

## Dependencies and Integration Points
It integrates with `RangeQuery`, `FutureResults`, `RangeResult`, and unit tests such as `RangeQueryTest` and `EventKeeperTest`.

## Risks and Edge Cases
The TODO notes that key-selector semantics are incomplete; the implementation uses only key bytes and `orEqual`, ignoring selector offsets. Target-byte accounting increments after adding a row, so exact boundary behavior may not match the C API. Because the fake extends a native-backed class, constructor behavior in `FDBTransaction` must remain compatible with dummy pointers.

## Test Signals
Useful signals include range-call count, row-limit behavior, reverse iteration ordering, and Java range iterator behavior independent of the native client.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/FakeFDBTransaction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/RangeQueryTest.java -->
# sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/RangeQueryTest.java

## Purpose
`RangeQueryTest` unit-tests Java range-query iteration logic using `FakeFDBTransaction` and a fake `Database`, avoiding a live FoundationDB server.

## Important APIs, Types, and Functions
It defines `EXECUTOR`, `makeFakeDatabase`, and parameterized tests over every `StreamingMode`. It uses `Transaction.getRange`, `AsyncIterable.asList`, `ByteArrayUtil`, and `FakeFDBTransaction.getNumRangeCalls`.

## Control Flow
`makeFakeDatabase` returns an anonymous `Database` that creates fake transactions with incrementing dummy native pointers. Tests build deterministic key-value data, open the fake database/transaction, validate an exact `get`, then issue range scans over `"a"` to `"b"` with no row limit, with row limit, reversed with no row limit, and reversed with row limit. Assertions compare returned keys/values and, for limited cases, confirm only one underlying range request.

## State and Persistence Behavior
All data is held in memory in the fake transaction backing map. Database and transaction close/finalize are no-ops. No persistent database state is involved.

## Dependencies and Integration Points
It depends on fake transaction behavior and Java range query iteration logic. It is a fast unit-level complement to live integration range tests.

## Risks and Edge Cases
Because `FakeFDBTransaction` only partially models key selectors and batching, these tests cannot prove native pagination or selector semantics. The fake database leaves many methods unimplemented, so reuse outside these narrow tests would fail.

## Test Signals
Passing indicates the Java-side range iterable returns expected rows for each streaming mode, respects row limits in the fake path, and handles reverse ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/RangeQueryTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/tuple/ArrayUtilSortTest.java -->
# sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/tuple/ArrayUtilSortTest.java

## Purpose
`ArrayUtilSortTest` checks that the unsafe byte-array lexicographical comparator agrees with the pure Java comparator for sorting and equality comparisons.

## Important APIs, Types, and Functions
It uses `FastByteComparisons.lexicographicalComparerUnsafeImpl`, `lexicographicalComparerJavaImpl`, JUnit `@BeforeAll`, random byte-array sample generation, and comparator `compare`/`compareTo` methods.

## Control Flow
`initTestClass` creates two lists sharing the same randomly generated byte arrays. One test sorts each list with a different comparator and asserts element-by-element equality. Other tests verify same-array comparisons and offset comparisons return zero for both comparator implementations.

## State and Persistence Behavior
Static lists `unsafe` and `java` hold 100001 random arrays up to 2047 bytes for the test class lifetime. No persistent state exists.

## Dependencies and Integration Points
It directly tests tuple byte-array comparison utilities that underpin tuple ordering and range map behavior.

## Risks and Edge Cases
The random seed is not fixed, so failures can be hard to reproduce. Because both lists reference the same byte-array objects, mutation after generation would affect both lists, though no mutation occurs. The test compares two implementations against each other rather than against an independent oracle.

## Test Signals
Passing provides confidence that unsafe comparator optimizations preserve ordering semantics of the Java comparator across many random byte arrays.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/tuple/ArrayUtilSortTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/tuple/ArrayUtilTest.java -->
# sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/tuple/ArrayUtilTest.java

## Purpose
`ArrayUtilTest` validates `ByteArrayUtil` helper behavior for joining, region equality, replacement, splitting, and replacement argument validation.

## Important APIs, Types, and Functions
It tests `ByteArrayUtil.join` overloads, `regionEquals`, `replace` overloads, and `split`. Several placeholder tests for bisect, compare, find, copy, strinc, and printable are disabled.

## Control Flow
The join tests build byte-array parts with empty arrays and delimiters and compare exact expected bytes. `regionEquals`, `replace`, and `split` tests exercise positive, negative, boundary, and repeated-delimiter cases. Later validation tests assert null, negative offset, negative length, and out-of-bounds replacement inputs throw. `replaceWorks` iterates a table of source/pattern/replacement/expected arrays and checks both content and that non-null sources produce a distinct result array.

## State and Persistence Behavior
All state is local test data. No persistent state exists.

## Dependencies and Integration Points
The tested utilities are foundational for tuple encoding, range boundaries, printable assertions, and fake transaction map ordering.

## Risks and Edge Cases
Several utility behaviors are not covered because tests are disabled. The large table-driven replacement test is dense and can be hard to diagnose without the printable error messages. Some older tests catch broad `Exception` instead of asserting exact exception types.

## Test Signals
Passing indicates byte-array concatenation, delimiter handling, splitting, replacement, and validation behavior remain stable for tuple and binding utilities.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/tuple/ArrayUtilTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/tuple/ByteArrayUtilTest.java -->
# sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/tuple/ByteArrayUtilTest.java

## Purpose
`ByteArrayUtilTest` focuses on `ByteArrayUtil.printable`, ensuring every byte value can be rendered and printable ASCII is preserved with escaping for backslash.

## Important APIs, Types, and Functions
It uses `ByteArrayUtil.printable`, UTF-8 encoding via `Charset.forName("UTF-8")`, and JUnit assertions.

## Control Flow
One test constructs bytes for all 0x00 through 0xff values and compares the exact printable string, including hex escapes for control and high bytes. The second test builds incremental ASCII substrings and asserts printable output matches the original string with backslashes escaped.

## State and Persistence Behavior
All state is local arrays/strings. No persistence or external dependency exists.

## Dependencies and Integration Points
Printable byte formatting is used in test error messages and byte-array assertions throughout the tuple and range tests.

## Risks and Edge Cases
The exact expected all-byte string is long and brittle if printable policy intentionally changes. The ASCII test includes DEL as a literal char in the source list but expects normal printable conversion through UTF-8 bytes.

## Test Signals
Passing indicates byte diagnostics are stable and no byte value causes unprintable or malformed diagnostic output.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/tuple/ByteArrayUtilTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/tuple/TupleComparisonTest.java -->
# sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/tuple/TupleComparisonTest.java

## Purpose
`TupleComparisonTest` verifies that semantic tuple comparison agrees with packed-byte unsigned comparison across a broad set of tuple element types and edge cases.

## Important APIs, Types, and Functions
It builds a static ordered list of `Tuple` instances containing integers, `BigInteger`s, signed zeros, infinities, NaNs, byte arrays, nested tuples, Unicode strings, UUIDs, booleans, lists, and complete `Versionstamp`s. A cartesian provider feeds every ordered pair into `testCanCompare`.

## Control Flow
For each tuple pair, the test copies tuples from items, computes semantic `compareTo`, compares packed bytes with `ByteArrayUtil.compareUnsigned`, and compares the original tuple's `compareTo`. It asserts the sign of all comparison methods matches.

## State and Persistence Behavior
The comparison corpus is static immutable test data. There is no external state.

## Dependencies and Integration Points
This test is central to tuple encoding compatibility: FoundationDB tuple keys must preserve logical ordering when packed into byte strings used by the database.

## Risks and Edge Cases
The cartesian product is large and can be slow. It verifies sign agreement but not exact comparator magnitude. The expected order is implicit in the corpus and `Tuple.compareTo`, so a shared bug in semantic and implicit tuple comparison would only be caught by byte comparison.

## Test Signals
Passing indicates packed tuple bytes preserve semantic ordering across numeric, string, binary, nested, UUID, boolean, and versionstamp values.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/tuple/TupleComparisonTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/tuple/TuplePackingTest.java -->
# sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/tuple/TuplePackingTest.java

## Purpose
`TuplePackingTest` validates tuple packing behavior, especially packed-size accounting, add/merge APIs, incomplete versionstamp rules, malformed sequence rejection, UTF-8 validation, prefix packing, and versionstamp position adjustment.

## Important APIs, Types, and Functions
It uses `Tuple`, `Versionstamp`, `ByteArrayUtil`, `Subspace`, `FDBLibraryRule`, parameterized method sources `baseAddCartesianProduct`, `twoIncomplete`, `malformedSequences`, and `wellFormedSequences`, plus reflection against `Tuple.memoizedPackedSize` to exercise validation paths.

## Control Flow
Tests combine base tuples with many item types and assert `getPackedSize`, `pack`, `packWithVersionstamp`, `addAll`, `addObject`, `fromStream`, and prefix packing behave consistently. Versionstamp tests assert incomplete versionstamps cannot be packed normally, exactly one incomplete versionstamp can be packed with appended little-endian position metadata, and two incomplete versionstamps are rejected. Malformed sequence tests feed truncated or invalid encoded byte strings into `Tuple.fromBytes`. Malformed string tests ensure invalid UTF-16 surrogate combinations cannot be sized or packed, including after reflective memoized-size manipulation.

## State and Persistence Behavior
State is local to tests except for `FDBLibraryRule.current()`, which selects/preloads the API version for versionstamp-sensitive behavior. No database data is written.

## Dependencies and Integration Points
The test is a compatibility guard for the tuple layer used by subspaces, directory keys, Java binding tests, and cross-language FoundationDB tuple encoding. It also depends on Java reflection and privileged access for one validation path.

## Risks and Edge Cases
The test intentionally creates a large byte array of size `0x0100fe` to check ambiguous versionstamp representation, which is memory-sensitive but bounded. Reflection against a private field is brittle under tuple implementation refactors. Some assumptions skip cases based on version/API state.

## Test Signals
Passing provides strong evidence that tuple packing size, byte representation, versionstamp handling, malformed input rejection, and prefix/subspace interactions remain compatible.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/tuple/TuplePackingTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/tuple/TupleSerializationTest.java -->
# sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/tuple/TupleSerializationTest.java

## Purpose
`TupleSerializationTest` verifies exact tuple serialization bytes, deserialization round trips, offset/length validation for `fromBytes`, and `packInto(ByteBuffer)` behavior.

## Important APIs, Types, and Functions
It defines a `TupleSerialization` holder, a large `serializedForms` corpus, `offsetAndLengthTuples`, and tests for packed size, packing, depacking, invalid offsets/lengths, partial tuple unpacking, combined tuple unpacking, and ByteBuffer packing. It uses `Tuple`, `Versionstamp`, `ByteArrayUtil`, `FDBLibraryRule`, `ByteBuffer`, `ByteOrder`, and `BufferOverflowException`.

## Control Flow
Parameterized tests compare each tuple's `getPackedSize` and `pack` output to exact expected bytes, then unpack and compare tuple equality. Offset/length tests pack a combined tuple and assert invalid slices fail while zero-length at array end is valid. Pairwise slice tests unpack adjacent tuple encodings and compare to expected combined tuples. `testPackIntoBuffer` packs into buffers with exact size, extra capacity, prefilled prefix bytes, too-small capacity, copied tuple state, and incomplete versionstamp input.

## State and Persistence Behavior
All tuple data is in-memory. `FDBLibraryRule.current()` selects/preloads the FDB API for tests that may require current tuple/versionstamp semantics.

## Dependencies and Integration Points
This is a precise compatibility contract for the Java tuple encoding format used for FoundationDB keys and cross-language interoperability.

## Risks and Edge Cases
The serialized corpus is intentionally brittle: any encoding change breaks tests, which is desirable for compatibility but requires careful migration. `packInto` tests ensure buffer byte order is preserved, but only a small tuple is used for buffer cases.

## Test Signals
Passing shows exact byte-level compatibility for many primitive, binary, string, nested tuple, UUID, boolean, and versionstamp encodings, plus robust slice validation and ByteBuffer packing behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/junit/com/apple/foundationdb/tuple/TupleSerializationTest.java -->
