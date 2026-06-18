# Research Group subset-b-008388

This grouped report covers the core FoundationDB Java binding package under `sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb` plus the small `async` support interfaces/utilities in this subset. Each section is delimited for reconciliation into a source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/ApiVersion.java.cmake -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/ApiVersion.java.cmake

## Purpose
This CMake-templated Java source defines the generated `ApiVersion` holder used by the Java bindings to advertise the maximum API version supported by the compiled FoundationDB client package.

## Important APIs, Types, And Functions
`ApiVersion` is a public class with a single public constant, `LATEST`, substituted from `@FDB_AV_LATEST_BINDINGS_VERSION@` during the build. `FDB.selectAPIVersion(int)` uses this value to reject application requests for newer binding behavior than this jar/native library combination supports.

## Control Flow
There is no runtime control flow beyond class loading. Build flow replaces the CMake token before Java compilation; runtime API selection reads the constant when validating the requested API version.

## State And Persistence Behavior
The only state is an immutable class constant baked into the compiled class. It is not persisted separately and does not change for the lifetime of a loaded jar.

## Dependencies And Integration Points
It depends on the FoundationDB build system for substitution and integrates directly with `FDB.selectAPIVersion`. It is part of the Java public API surface, so downstream applications may also compare their compatibility gates against it.

## Risks And Edge Cases
Incorrect substitution can make the Java binding accept or reject the wrong API version. Because the constant is compiled into client code, mixing jars and native libraries from different builds can produce confusing compatibility failures.

## Test Signals
Build tests should assert the generated source contains a numeric `LATEST` value. Runtime tests should cover selecting the latest version, rejecting values above latest, and rejecting versions below the binding minimum.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/ApiVersion.java.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/Cluster.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/Cluster.java

## Purpose
`Cluster` preserves the deprecated cluster-oriented API while delegating actual database opening to `FDB.open`. It gives old callers a `Cluster` object that records a cluster file path and executor without owning native cluster resources.

## Important APIs, Types, And Functions
`Cluster` extends `NativeObjectWrapper`, but its constructor passes `0`, making it immediately closed from the native-wrapper perspective. `options()` returns a no-op `ClusterOptions`. `openDatabase()` and `openDatabase(Executor)` call `FDB.instance().open(clusterFile, executor)`.

## Control Flow
Deprecated `FDB.createCluster` constructors instantiate `Cluster`; callers then call `openDatabase`, which re-enters the singleton `FDB` open path, starting the network if needed and creating an `FDBDatabase`.

## State And Persistence Behavior
State is limited to the Java-side `clusterFile`, `executor`, and no-op options object. `closeInternal` is empty because no native pointer is owned.

## Dependencies And Integration Points
It depends on `FDB`, `Database`, `ClusterOptions`, `Executor`, and `NativeObjectWrapper`. It exists for source/binary compatibility with applications written before direct database open was preferred.

## Risks And Edge Cases
Because the wrapper is constructed with pointer `0`, inherited closed-state behavior can surprise code that treats it like other native wrappers. Cluster options are silently no-op. Any failure in API initialization or network startup appears when `openDatabase` delegates to `FDB`.

## Test Signals
Tests should verify deprecated creation delegates to `FDB.open`, preserves custom executors and cluster file paths, and that closing a `Cluster` is harmless.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/Cluster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/ClusterOptions.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/ClusterOptions.java

## Purpose
`ClusterOptions` is a deprecated options holder retained for the deprecated `Cluster` API. Current FoundationDB Java bindings expose no settable cluster-level options.

## Important APIs, Types, And Functions
The class extends `OptionsSet` and only exposes a constructor accepting an `OptionConsumer`. It adds no option setter methods of its own.

## Control Flow
Construction simply passes the consumer to `OptionsSet`. In `Cluster`, that consumer is a lambda that ignores all option codes and parameters.

## State And Persistence Behavior
It stores only the inherited option consumer reference. No native state is updated unless a future subclass method uses `OptionsSet.setOption`.

## Dependencies And Integration Points
It depends on `OptionsSet` and `OptionConsumer` and is reachable from `Cluster.options()`.

## Risks And Edge Cases
The class may mislead users into assuming cluster options still exist. Its behavior is intentionally inert in the current cluster wrapper.

## Test Signals
Compatibility tests should ensure `Cluster.options()` still returns a non-null `ClusterOptions` and that constructing it does not touch native state.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/ClusterOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/Database.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/Database.java

## Purpose
`Database` is the public interface for a FoundationDB database connection. It creates transactions, exposes database options/status, provides retry-loop transaction helpers, and defines the resource-close contract.

## Important APIs, Types, And Functions
The interface extends `AutoCloseable` and `TransactionContext`. Key methods are `createTransaction`, `options`, `getMainThreadBusyness`, synchronous/asynchronous `read` and `run` overloads, `close`, and `getClientStatus`. Default methods route no-executor overloads through `getExecutor`.

## Control Flow
Client code normally obtains a `Database` from `FDB.open`, then executes work through `run` or `runAsync`. Implementations create a transaction, call user logic, commit for mutating paths, and retry through `Transaction.onError` for retryable `FDBException`s.

## State And Persistence Behavior
The interface describes a native database resource that must be closed. No state is stored by the interface itself; `FDBDatabase` owns the native pointer, executor, options, and optional instrumentation.

## Dependencies And Integration Points
It integrates with `Transaction`, `ReadTransaction`, `TransactionContext`, `DatabaseOptions`, `EventKeeper`, Java `CompletableFuture`, `Executor`, and user-supplied `Function`s. `LocalityUtil` and retry helpers consume this interface.

## Risks And Edge Cases
Retryable blocks can execute multiple times after unknown commit results, so user code must be idempotent or otherwise safe. Failure to close databases leaks native resources. Custom executors can affect callback ordering and liveness.

## Test Signals
Tests should cover transaction creation, sync and async retry loops, read-only aliases, custom executor propagation, close idempotence through implementation, status retrieval, and exception propagation from user functions and commits.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/Database.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/DirectBufferIterator.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/DirectBufferIterator.java

## Purpose
`DirectBufferIterator` is the shared base for iterating JNI-filled direct `ByteBuffer` range-query result chunks without first marshaling the entire payload through regular Java arrays.

## Important APIs, Types, And Functions
It stores `byteBuffer`, `current`, `keyCount`, and `more`. `readResultsSummary()` rewinds the buffer and reads native-endian `keyCount` and `more`; `hasNext`, `count`, `hasMore`, and `currentIndex` expose parsed state. `close()` returns the buffer to `DirectBufferPool`.

## Control Flow
`FutureResults.getResults()` or `FutureMappedResults.getResults()` borrows a buffer, calls a native direct-fill function, then creates a concrete direct-buffer iterator. The subclass reads items after `readResultsSummary`.

## State And Persistence Behavior
The iterator owns one borrowed direct buffer until `close`. Parsed cursor state is mutable and in-memory. Closing returns reusable buffers to the singleton pool and nulls the local reference.

## Dependencies And Integration Points
It depends on `ByteBuffer`, `ByteOrder.nativeOrder`, `DirectBufferPool`, and concrete `RangeResultDirectBufferIterator` / `MappedRangeResultDirectBufferIterator`.

## Risks And Edge Cases
Callers must call `readResultsSummary` before `hasNext`, `count`, or `hasMore`. Buffer format must match JNI exactly. Returning a buffer while still reading would corrupt results, so the try-with-resources conversion must finish before close.

## Test Signals
Tests should feed native-order buffers with empty and multi-row chunks, verify `more` parsing, assert close returns buffers to the pool, and exercise misuse before summary parsing under assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/DirectBufferIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/DirectBufferPool.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/DirectBufferPool.java

## Purpose
`DirectBufferPool` is a singleton pool of direct byte buffers used to reduce JNI range-query copy overhead when direct-buffer range queries are enabled on `FDB`.

## Important APIs, Types, And Functions
`getInstance()` returns the static singleton. `resize(int, int)` allocates a new `ArrayBlockingQueue` of direct buffers and enforces `MIN_BUFFER_SIZE`. `poll()` borrows a buffer or returns null when empty. `add(ByteBuffer)` returns a buffer only if its capacity matches the current pool generation.

## Control Flow
`FDB.resizeDirectBufferPool` calls `resize`. Range future wrappers call `poll`; on hit, JNI fills the direct buffer and a direct iterator returns it through `close`; on miss, the wrapper falls back to array-based native marshaling.

## State And Persistence Behavior
The pool keeps an in-memory queue and current buffer capacity. Resizing discards the old queue reference; outstanding old buffers are ignored when returned if their capacity no longer matches.

## Dependencies And Integration Points
It depends on Java NIO direct buffers and is used by `FutureResults`, `FutureMappedResults`, and `DirectBufferIterator`.

## Risks And Edge Cases
Large pool sizes allocate off-heap memory eagerly and can throw `OutOfMemoryError`. An empty pool is not fatal but reduces performance. Resizing during active queries intentionally drops old buffers and can temporarily reduce hit rates.

## Test Signals
Tests should cover minimum-size rejection, successful resize, pool exhaustion returning null, buffer return after resize, and range futures correctly falling back when `poll` misses.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/DirectBufferPool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/EventKeeper.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/EventKeeper.java

## Purpose
`EventKeeper` is the instrumentation contract for counting Java binding events such as JNI calls, fetched bytes, range-query fetches, direct-buffer hits/misses, and range-fetch latency.

## Important APIs, Types, And Functions
The interface defines `count`, `increment`, `timeNanos`, `time`, `getCount`, `getTimeNanos`, and `getTime`. Nested `Event` names events and marks time events. `Events` enumerates built-in driver metrics including `JNI_CALL`, `BYTES_FETCHED`, and `RANGE_QUERY_FETCH_TIME_NANOS`.

## Control Flow
Instrumentation-aware classes check for a non-null `EventKeeper`, increment counters before JNI calls, count bytes after marshaling, and record range fetch timing through `timeNanos`.

## State And Persistence Behavior
The interface requires implementations to be thread-safe but stores no state itself. Implementations decide whether metrics remain in memory, are exported, or are aggregated elsewhere.

## Dependencies And Integration Points
It integrates with `FDB.open(..., EventKeeper)`, `FDBDatabase`, `FDBTransaction`, typed future wrappers, range iterators, and `MapEventKeeper`.

## Risks And Edge Cases
Implementations run on application and callback threads, so slow or unsafe implementations can affect query latency. The interface documents time events but does not enforce that only time events are timed.

## Test Signals
Tests should verify expected counters for gets, range fetches, direct-buffer hits/misses, byte accounting, and time conversion through several `TimeUnit`s.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/EventKeeper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FDB.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FDB.java

## Purpose
`FDB` is the Java binding entry point and singleton owner for API-version selection, native library loading, network lifecycle, database opening, global network options, direct-buffer configuration, and error predicate access.

## Important APIs, Types, And Functions
Important public APIs include `selectAPIVersion`, `instance`, `options`, `open` overloads, deprecated `createCluster` overloads, `startNetwork`, `stopNetwork`, `disableShutdownHook`, `setUnclosedWarning`, `enableDirectBufferQuery`, and `resizeDirectBufferPool`. Native methods bridge API selection, network setup/run/stop, option setting, error predicates, and database creation.

## Control Flow
Static initialization tries to load `fdb_c`, then loads `fdb_java`, and creates a daemon callback executor. `selectAPIVersion` validates the requested version, calls native `Select_API_version`, and installs the singleton. `open` synchronizes network startup, creates a native database pointer, and wraps it in `FDBDatabase`. `startNetwork` configures native networking, installs an optional shutdown hook, and runs `Network_run` on a supplied executor. `stopNetwork` calls `Network_stop` and waits on a semaphore until the network thread exits.

## State And Persistence Behavior
The singleton and selected API version are JVM-global and immutable after selection. Network lifecycle flags prevent restart after stop. Direct-buffer query preference and warning preference are mutable instance settings. No persistent files are written by `FDB` itself.

## Dependencies And Integration Points
It depends on `JNIUtil`, generated `ApiVersion`, `NetworkOptions`, `Database`, `FDBDatabase`, `Cluster`, `DirectBufferPool`, and the native FoundationDB JNI library. Most other binding classes reach `FDB.instance()` for defaults, warnings, or direct-buffer flags.

## Risks And Edge Cases
API version can be selected only once. `stopNetwork` is terminal. Shutdown hook ordering can race application hooks unless disabled. Native library load failures surface during class initialization. `startNetwork` swallows network-thread errors after printing to stderr.

## Test Signals
Tests should cover API-version bounds, singleton repeat selection, network start idempotence, stop terminal behavior, database open with default/custom executor and event keeper, shutdown-hook disable, direct-buffer toggles, and native-load failure paths in integration packaging tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FDB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FDBDatabase.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FDBDatabase.java

## Purpose
`FDBDatabase` is the concrete native-backed implementation of `Database`. It owns the database pointer, creates native transactions, applies database options, and implements synchronous/asynchronous retry loops.

## Important APIs, Types, And Functions
It extends `NativeObjectWrapper` and implements `Database` plus `OptionConsumer`. Key methods are `run`, `runAsync`, `read`, `readAsync`, `createTransaction`, `setOption`, `getMainThreadBusyness`, `getClientStatus`, and `closeInternal`. Native methods create/dispose transactions, set database options, query busyness, and fetch client status.

## Control Flow
`run` creates a transaction, repeatedly invokes user logic, commits, and calls `onError` on runtime failures until success or non-retryable failure. `runAsync` performs the same loop with `AsyncUtil.whileTrue`, storing the final return value and closing the latest transaction in `whenComplete`. `createTransaction` locks the database pointer, wraps the native transaction, and sets used-during-commit protection compatibility options.

## State And Persistence Behavior
State includes the native database pointer, `DatabaseOptions`, executor, and optional `EventKeeper`. Closing disposes the native database once. Finalization warns and closes if the object is collected while still open.

## Dependencies And Integration Points
It depends on `FDBTransaction`, `NativeObjectWrapper`, `AsyncUtil`, `FutureKey`, `DatabaseOptions`, and native JNI database calls. `FDB.open` constructs it.

## Risks And Edge Cases
Retry loops may re-execute user code, so side effects outside FDB must be controlled. `runAsync` only routes `RuntimeException` through `onError`; other throwables become `CompletionException`. Finalizers are a last-resort leak detector and should not be relied on for cleanup.

## Test Signals
Tests should cover successful sync/async runs, retry after retryable commit/user errors, transaction closure after all paths, option forwarding under lock, client status future creation, and unclosed-resource warning behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FDBDatabase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FDBTransaction.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FDBTransaction.java

## Purpose
`FDBTransaction` is the concrete native-backed implementation of `Transaction`. It exposes reads, writes, conflict ranges, range queries, mapped range queries, commit, retry/reset semantics, watches, locality address lookup, and snapshot reads.

## Important APIs, Types, And Functions
The class extends `NativeObjectWrapper` and implements `Transaction` and `OptionConsumer`. It owns `database`, `executor`, `TransactionOptions`, optional `EventKeeper`, a `transactionOwner` flag, and a `ReadSnapshot` view. Public methods wrap native transaction calls for read versions, `get`, `getKey`, range reads, mapped range reads, conflict ranges, mutations, commit, committed version, versionstamp, approximate size, watch, `onError`, cancel, and key locations.

## Control Flow
Most methods increment instrumentation, acquire `pointerReadLock`, call JNI using `getPtr`, wrap native futures in typed `NativeFuture` subclasses, and release the lock. Snapshot methods route reads through the same transaction with the snapshot flag and suppress read conflict additions. Range methods construct lazy `RangeQuery` or `MappedRangeQuery` objects. `onError` unwraps completion exceptions, rejects non-`FDBException`s, calls native `Transaction_onError`, transfers pointer ownership to a new transaction wrapper, invalidates the old wrapper, and closes the replacement on retry failure.

## State And Persistence Behavior
The native pointer is single-owner except during `onError` transfer. After transfer, the old transaction throws on further pointer access. Write mutations and conflict ranges are stored by the native transaction until commit/reset/dispose. No Java-side persistence occurs; close disposes the native transaction if still owner.

## Dependencies And Integration Points
It integrates with `Database`, `ReadTransaction`, `Transaction`, `RangeQuery`, `MappedRangeQuery`, all typed future classes, `ByteArrayUtil`, `StreamingMode`, `MutationType`, `ConflictRangeType`, `TransactionOptions`, and native JNI transaction functions.

## Risks And Edge Cases
Using a transaction after `onError` invalidates it. Null validation exists for `set` and `clear`, but not every native call validates all byte arrays before JNI. Snapshot mapped ranges are unsupported. Range iterators must not outlive the transaction for long. The unused native `Transaction_reset` declaration suggests historical API drift.

## Test Signals
Tests should cover point reads, snapshot reads, key selectors, range and mapped range iteration, conflict range behavior, mutation null checks, commit and committed version, `onError` pointer invalidation, cancel/watch, close idempotence, instrumentation counts, and transaction-use-after-reset errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FDBTransaction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureBool.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureBool.java

## Purpose
`FutureBool` adapts a native FoundationDB future returning a boolean into a Java `CompletableFuture<Boolean>`.

## Important APIs, Types, And Functions
The constructor passes the pointer to `NativeFuture` and registers the marshal callback on the supplied executor. `getIfDone_internal` calls native `FutureBool_get`.

## Control Flow
When the native future becomes ready, `NativeFuture.marshalWhenDone` invokes `FutureBool_get`, completes the Java future, and disposes the native future through the base `postMarshal`.

## State And Persistence Behavior
State is the inherited native future pointer until callback completion, cancellation, or close. No persistent state exists.

## Dependencies And Integration Points
It depends on `NativeFuture`, `Executor`, `FDBException`, and JNI support for boolean future extraction.

## Risks And Edge Cases
Callback registration must occur after subclass initialization. Closing before completion completes the future exceptionally. Native errors propagate as exceptional completion.

## Test Signals
Tests should cover successful true/false completion, native error propagation, cancellation forwarding, close-before-ready behavior, and executor callback execution.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureBool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureInt64.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureInt64.java

## Purpose
`FutureInt64` adapts native 64-bit integer futures, such as read versions, estimated sizes, and approximate transaction sizes, into Java `CompletableFuture<Long>`.

## Important APIs, Types, And Functions
It extends `NativeFuture<Long>`, registers a marshal callback in the constructor, and implements `getIfDone_internal` through native `FutureInt64_get`.

## Control Flow
Native readiness triggers callback execution on the provided executor; the base class reads the long, completes the Java future, and disposes the native handle.

## State And Persistence Behavior
Only the inherited native pointer is mutable. Completion value is stored by `CompletableFuture` after marshaling.

## Dependencies And Integration Points
It is used by `FDBTransaction.getReadVersion`, `getEstimatedRangeSizeBytes`, and `getApproximateSize`.

## Risks And Edge Cases
Native integer width and Java `long` mapping must match. Exceptional native futures must become `FDBException` completions.

## Test Signals
Tests should cover successful value completion, large positive values, native errors, cancellation, and explicit close.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureInt64.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureKey.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureKey.java

## Purpose
`FutureKey` adapts native futures that return a single key-like byte array and records fetched-byte instrumentation.

## Important APIs, Types, And Functions
It extends `NativeFuture<byte[]>`, stores an optional `EventKeeper`, calls native `FutureKey_get`, and overrides `postMarshal` to count `BYTES_FETCHED` when the result is non-null.

## Control Flow
Native readiness triggers byte-array extraction, Java future completion, byte counting, and native future disposal.

## State And Persistence Behavior
State consists of the inherited native pointer and an event keeper reference. The returned byte array is a Java copy from native memory.

## Dependencies And Integration Points
It is used for `getKey`, `getVersionstamp`, and database client status paths that return key/byte payloads. It depends on `EventKeeper.Events`.

## Risks And Edge Cases
Null values are not counted, which is correct for absent values but means diagnostics differ by result presence. Large keys/status payloads are fully copied into heap memory.

## Test Signals
Tests should verify value completion, byte-count increment, null result behavior, native errors, and close/cancel behavior inherited from `NativeFuture`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureKey.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureKeyArray.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureKeyArray.java

## Purpose
`FutureKeyArray` adapts native futures returning an array of keys, currently used for range split points.

## Important APIs, Types, And Functions
It extends `NativeFuture<KeyArrayResult>`, registers a callback, and calls native `FutureKeyArray_get` from `getIfDone_internal`.

## Control Flow
After native readiness, the JNI layer returns a `KeyArrayResult`; the base future completes and disposes the native future.

## State And Persistence Behavior
Only the inherited pointer is mutable. Result data is copied into `KeyArrayResult`.

## Dependencies And Integration Points
It is created by `FDBTransaction.getRangeSplitPoints` and depends on `KeyArrayResult`.

## Risks And Edge Cases
Large split-point arrays can allocate many byte arrays. JNI length metadata must match concatenated key bytes.

## Test Signals
Tests should cover empty and multi-key results, native error propagation, and malformed JNI result handling through `KeyArrayResult` constructor tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureKeyArray.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureKeyRangeArray.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureKeyRangeArray.java

## Purpose
`FutureKeyRangeArray` adapts native futures returning arrays of `Range` values into Java `CompletableFuture<KeyRangeArrayResult>`.

## Important APIs, Types, And Functions
It extends `NativeFuture<KeyRangeArrayResult>` and calls native `FutureKeyRangeArray_get`.

## Control Flow
The base callback machinery waits for native readiness, invokes the typed getter, completes the Java future, and disposes the native handle.

## State And Persistence Behavior
State is the native pointer before completion and the `KeyRangeArrayResult` after completion.

## Dependencies And Integration Points
It depends on `KeyRangeArrayResult`; it is part of the binding's typed native-future family even if this subset does not show a direct creator.

## Risks And Edge Cases
Range array ownership and copying are JNI-sensitive. Because the class is package-private, accidental external misuse is limited.

## Test Signals
Tests should cover empty/ranged results, native error completion, cancellation, and `KeyRangeArrayResult` list behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureKeyRangeArray.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureMappedResults.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureMappedResults.java

## Purpose
`FutureMappedResults` represents a ready native mapped-range query chunk. Unlike scalar futures, it completes to a lightweight `MappedRangeResultInfo` and defers actual result marshaling until the iterator requests the chunk.

## Important APIs, Types, And Functions
It extends `NativeFuture<MappedRangeResultInfo>`, stores direct-buffer enablement and optional instrumentation, overrides `postMarshal` to avoid automatic close, checks native error through `Future_getError`, and exposes `getResults()` for array or direct-buffer marshaling.

## Control Flow
Native readiness completes the Java future with `MappedRangeResultInfo(this)` but leaves the native future open. `MappedRangeQuery.FetchComplete` calls `data.get()`, which calls `getResults`; that borrows a direct buffer when enabled, fills it through JNI, builds a `MappedRangeResult`, and later closes the native future in the fetch completion finally block.

## State And Persistence Behavior
The native future pointer remains live after readiness until the owning range iterator closes it. Direct buffers are borrowed transiently and returned by the direct iterator.

## Dependencies And Integration Points
It integrates with `MappedRangeQuery`, `MappedRangeResultInfo`, `MappedRangeResult`, `MappedRangeResultDirectBufferIterator`, `DirectBufferPool`, and `EventKeeper`.

## Risks And Edge Cases
Forgetting to close the future after consuming results leaks native memory. Direct-buffer format must match `MappedRangeResultDirectBufferIterator`. Instrumentation counts hit/miss and JNI calls before marshaling.

## Test Signals
Tests should cover direct-buffer hit and miss paths, native error before marshaling, deferred close semantics, empty/multi-row mapped chunks, and cancellation from iterator cancel.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureMappedResults.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureResult.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureResult.java

## Purpose
`FutureResult` adapts native futures returning a value byte array from point reads and records fetched-byte metrics.

## Important APIs, Types, And Functions
It extends `NativeFuture<byte[]>`, stores an optional `EventKeeper`, calls native `FutureResult_get`, and counts result bytes in `postMarshal`.

## Control Flow
`FDBTransaction.get` creates it. On native readiness, `NativeFuture` marshals the value, completes the Java future, calls `postMarshal`, and closes the native future.

## State And Persistence Behavior
The native pointer is held until completion/cancel/close. The marshaled value is a heap byte array or null for absent keys.

## Dependencies And Integration Points
It depends on `EventKeeper` and is the point-read counterpart of `FutureKey`.

## Risks And Edge Cases
Absent values produce null and no byte count. Large values allocate heap memory, while range queries may use direct buffers if enabled.

## Test Signals
Tests should cover present and absent values, byte accounting, native errors, cancellation, and explicit close.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureResults.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureResults.java

## Purpose
`FutureResults` represents a native range-query result chunk and defers expensive result marshaling until `RangeQuery` consumes the ready chunk.

## Important APIs, Types, And Functions
It extends `NativeFuture<RangeResultInfo>`, stores direct-buffer enablement and optional instrumentation, returns `RangeResultInfo(this)` after checking `Future_getError`, overrides `postMarshal` to avoid automatic close, and exposes `getResults()` for either `FutureResults_get` or `FutureResults_getDirect`.

## Control Flow
`FDBTransaction.getRange_internal` creates it. Readiness completes the Java future without disposing native memory. `RangeQuery.FetchComplete` calls `RangeResultInfo.get`, which marshals the current chunk, updates iterator state, then closes the future in a finally block.

## State And Persistence Behavior
Native memory stays live between readiness and chunk consumption. Direct buffers are borrowed per marshaling attempt and returned after constructing `RangeResult`.

## Dependencies And Integration Points
It connects `FDBTransaction`, `RangeQuery`, `RangeResultInfo`, `RangeResult`, `RangeResultDirectBufferIterator`, `DirectBufferPool`, and `EventKeeper`.

## Risks And Edge Cases
If iterator code fails to close a `FutureResults`, native memory can leak. Direct-buffer capacity must handle at least one maximum-size key/value pair. Errors are checked before result extraction, not by automatic base close.

## Test Signals
Tests should cover array and direct-buffer marshaling, empty chunks, `more` flag propagation, future close after consumption, hit/miss metrics, and native error propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureResults.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureStrings.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureStrings.java

## Purpose
`FutureStrings` adapts native futures returning string arrays, used for storage server address locality information.

## Important APIs, Types, And Functions
The class extends `NativeFuture<String[]>`, registers the marshal callback, and calls native `FutureStrings_get`.

## Control Flow
`FDBTransaction.getAddressesForKey` creates it. Native readiness triggers string array extraction and Java future completion through the base class.

## State And Persistence Behavior
Only the inherited pointer is mutable before completion; completed string arrays live on the Java heap.

## Dependencies And Integration Points
It integrates with `LocalityUtil.getAddressesForKey` through `FDBTransaction`.

## Risks And Edge Cases
Locality information can be unavailable and complete exceptionally. Address format depends on transaction options such as include-port.

## Test Signals
Tests should cover successful address arrays, unavailable-locality errors, cancellation, and executor callback behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureStrings.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureVoid.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureVoid.java

## Purpose
`FutureVoid` adapts native futures whose meaningful result is success or error, such as commit, watch, and transaction `onError`.

## Important APIs, Types, And Functions
It extends `NativeFuture<Void>` and implements `getIfDone_internal` by calling inherited native `Future_getError`; non-success errors are thrown, otherwise null is returned.

## Control Flow
Native readiness invokes error inspection, completes the Java future with null on success, and closes the native future through the base class.

## State And Persistence Behavior
The native pointer is held until completion, cancellation, or close. Completed value is always null.

## Dependencies And Integration Points
It is used by `FDBTransaction.commit`, `watch`, and `onError`.

## Risks And Edge Cases
Correctness depends on `Future_getError` distinguishing success from failure. Unknown-result commit errors propagate as exceptional completion and must be handled by retry loops.

## Test Signals
Tests should cover success, retryable and non-retryable errors, cancellation, close-before-ready, and use in `Transaction.onError`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FutureVoid.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/JNIUtil.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/JNIUtil.java

## Purpose
`JNIUtil` loads FoundationDB native libraries either from explicit system properties, embedded classpath resources, or platform library search paths. It also exports embedded libraries to temporary files.

## Important APIs, Types, And Functions
`loadLibrary(String)` is the package-level loader used by `FDB` static initialization. `exportLibrary(String)` exposes resource extraction. Private helpers detect OS/arch, map library names, build resource paths, copy streams, and save resources as temp files.

## Control Flow
`loadLibrary` first checks `FDB_LIBRARY_PATH_<LIBNAME>` system property and calls `System.load` if present. Otherwise it detects the OS, maps the library name, verifies extension sanity, exports `/lib/<os>/<arch>/<mapped-name>` to a temp file, loads it, and eagerly deletes on Linux/macOS when possible. Missing embedded resources become `UnsatisfiedLinkError`.

## State And Persistence Behavior
The utility writes temporary files for embedded native libraries and marks them `deleteOnExit`. No long-lived Java state is stored.

## Dependencies And Integration Points
It depends on `System` properties, classpath resources, Java IO, and is called by `FDB` to load `fdb_c` and `fdb_java`.

## Risks And Edge Cases
Unsupported architectures or OS names throw immediately. Security managers can block property reads. Embedded resource absence, temp-file IO failures, or extension mismatches break native loading. Eager deletion is disabled on Windows.

## Test Signals
Packaging tests should cover resource paths for supported OS/arch pairs, property override loading, export failure when resource missing, macOS `.dylib` to `.jnilib` mapping, and temp-file cleanup flags.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/JNIUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/KeyArrayResult.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/KeyArrayResult.java

## Purpose
`KeyArrayResult` is a Java value container for native results encoded as concatenated key bytes plus per-key lengths.

## Important APIs, Types, And Functions
The constructor splits `keyBytes` according to `keyLengths` and populates `keys`. `getKeys()` returns the internal list.

## Control Flow
JNI constructs or passes data to this constructor for APIs such as range split points. The constructor walks length metadata, copies each segment, and appends it to the result list.

## State And Persistence Behavior
The object stores copied byte arrays in an in-memory `ArrayList`. The returned list is mutable and not defensively copied.

## Dependencies And Integration Points
It is returned by `FutureKeyArray` and `ReadTransaction.getRangeSplitPoints`.

## Risks And Edge Cases
Malformed lengths can overrun `keyBytes` and throw array-copy exceptions. Exposing the mutable list allows callers to mutate the result container.

## Test Signals
Tests should cover empty arrays, multiple keys, zero-length keys, malformed length totals, and list mutability expectations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/KeyArrayResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/KeyRangeArrayResult.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/KeyRangeArrayResult.java

## Purpose
`KeyRangeArrayResult` wraps an array of `Range` objects returned by native calls into a list-oriented Java result object.

## Important APIs, Types, And Functions
The constructor stores `Arrays.asList(keyRangeArr)` in `keyRanges`. `getKeyRanges()` exposes that list.

## Control Flow
Native JNI code supplies a `Range[]`; Java code wraps it without copying individual ranges.

## State And Persistence Behavior
The list is fixed-size but backed by the original array. `Range` objects contain byte-array references and are not deeply copied here.

## Dependencies And Integration Points
It is returned by `FutureKeyRangeArray` and depends on `Range`.

## Risks And Edge Cases
Because the list is array-backed, changes to the original array would be visible if retained elsewhere. Range byte arrays are mutable by reference.

## Test Signals
Tests should cover empty and multi-range arrays, fixed-size list behavior, and equality of wrapped ranges.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/KeyRangeArrayResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/KeySelector.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/KeySelector.java

## Purpose
`KeySelector` models FoundationDB order-based key selection: a base key, an `orEqual` flag, and an offset used by `getKey` and range boundaries.

## Important APIs, Types, And Functions
Factory methods create common selectors: `lastLessThan`, `lastLessOrEqual`, `firstGreaterThan`, and `firstGreaterOrEqual`. `add(int)` returns an offset-adjusted selector. `getKey()` returns a defensive copy; `orEqual`, `getOffset`, and `toString` expose selector fields.

## Control Flow
Transactions pass selectors to JNI by copying the key and reading flag/offset. Range iterators update selectors after each chunk using `firstGreaterThan(lastKey)` or `firstGreaterOrEqual(lastKey)` depending on direction.

## State And Persistence Behavior
The selector is intended immutable; the stored constructor key is not defensively copied, but `getKey` returns a copy. No persistence occurs.

## Dependencies And Integration Points
It is used by `ReadTransaction.getKey`, all range overloads, `RangeQuery`, `MappedRangeQuery`, and debug formatting through `ByteArrayUtil`.

## Risks And Edge Cases
Constructor callers can mutate the passed key array after construction. Large offsets are documented as inefficient. Misunderstanding selector semantics can create off-by-one range boundaries.

## Test Signals
Tests should cover all factory encodings, `add`, key defensive copy on getter, constructor-array mutation behavior, string formatting, and range continuation selectors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/KeySelector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/KeyValue.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/KeyValue.java

## Purpose
`KeyValue` is the public value type representing one key/value pair returned from range reads and nested mapped-range results.

## Important APIs, Types, And Functions
The constructor stores `key` and `value`; `getKey` and `getValue` return those arrays. `equals`, `hashCode`, and `toString` use array-content comparison and printable byte formatting.

## Control Flow
Range result constructors and direct-buffer iterators instantiate `KeyValue` for each row; clients consume instances through `AsyncIterator` or `asList`.

## State And Persistence Behavior
The object stores references to byte arrays and does not defensively copy them. It is otherwise immutable by field assignment, but array contents remain mutable.

## Dependencies And Integration Points
It is central to `RangeResult`, `RangeQuery`, `MappedKeyValue`, `LocalityUtil`, and `ReadTransaction` range APIs.

## Risks And Edge Cases
Callers can mutate arrays returned by getters, changing equality/hash behavior after insertion into hash collections. Large values in `toString` may be expensive or verbose.

## Test Signals
Tests should cover content equality, hash consistency, string formatting for binary keys, and mutation implications if arrays are changed after construction.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/KeyValue.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/LocalityUtil.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/LocalityUtil.java

## Purpose
`LocalityUtil` exposes advanced locality helpers for discovering key-server boundary keys and storage server addresses for a key.

## Important APIs, Types, And Functions
`getBoundaryKeys(Database, byte[], byte[])` and `getBoundaryKeys(Transaction, byte[], byte[])` return `CloseableAsyncIterator<byte[]>`. `getAddressesForKey(Transaction, byte[])` delegates to `FDBTransaction`. `BoundaryIterator` implements retrying iteration over system keyspace. `keyServersForKey` prefixes keys with `\xff/keyServers/`.

## Control Flow
Boundary iteration creates or derives a transaction, enables system-key and lock-aware options, scans `/keyServers/` system keys, strips the prefix from each returned key, advances `begin`, and composes `onHasNext` with retry handling. On transaction-too-old after progress, it creates a fresh transaction and restarts from the current boundary; other runtime errors flow through `onError`.

## State And Persistence Behavior
`BoundaryIterator` owns a transaction, current begin key, last begin, end key, current block iterator, next future, and closed flag. It must be closed to release the transaction; finalization warns and closes as a fallback.

## Dependencies And Integration Points
It depends on `Transaction`, `Database`, `AsyncIterator`, `CloseableAsyncIterator`, `AsyncUtil`, `ByteArrayUtil`, and transaction system-key options.

## Risks And Edge Cases
Boundary results are approximate and non-transactional. `next` requires a completed positive `onHasNext`; otherwise it throws. Only real `FDBTransaction` supports address lookup; wrappers get locality-unavailable errors.

## Test Signals
Tests should cover prefix construction, boundary iteration over multiple blocks, retry after transaction-too-old, close/finalizer behavior, unsupported transaction address lookup, and options set on locality transactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/LocalityUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/MapEventKeeper.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/MapEventKeeper.java

## Purpose
`MapEventKeeper` is a simple thread-safe in-memory `EventKeeper` implementation useful for tests, diagnostics, and lightweight metric collection.

## Important APIs, Types, And Functions
It stores a `ConcurrentMap<Event, Count>`. `count` increments a counter. `timeNanos` increments both count and duration. `getCount` and `getTimeNanos` read current atomic values. `Count` contains two `AtomicLong`s.

## Control Flow
Each recording call uses `computeIfAbsent` to create a counter and then updates atomic fields. Reads return zero for missing events.

## State And Persistence Behavior
All metric state is in memory for the life of the keeper. No reset or export API is provided beyond getters.

## Dependencies And Integration Points
It implements `EventKeeper` and can be passed to `FDB.open` to instrument `FDBDatabase`, transactions, futures, and range iterators.

## Risks And Edge Cases
The map grows for every distinct event key, so custom high-cardinality events can leak memory. Time events are not validated; `timeNanos` works for any event.

## Test Signals
Tests should cover concurrent increments, missing events returning zero, timing count plus duration behavior, and use with built-in range metrics.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/MapEventKeeper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/MappedKeyValue.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/MappedKeyValue.java

## Purpose
`MappedKeyValue` extends `KeyValue` with mapper range metadata and nested range results returned by FoundationDB mapped range queries.

## Important APIs, Types, And Functions
It stores `rangeBegin`, `rangeEnd`, and `rangeResult`. Getters expose each. `fromBytes(byte[], int[])` decodes concatenated native bytes and lengths into key, value, mapped range bounds, and nested `KeyValue`s. `takeBytes` advances a small `Offset` cursor. Equality, hash, and string formatting include all fields.

## Control Flow
JNI array-based mapped range results call `fromBytes`; direct-buffer results construct `MappedKeyValue` directly. Consumers iterate through `MappedRangeQuery` or call `asList`.

## State And Persistence Behavior
The object stores byte-array and list references. It is field-immutable but not deeply immutable because arrays and the list can be mutated externally.

## Dependencies And Integration Points
It depends on `KeyValue`, `ByteArrayUtil`, and is used by `MappedRangeResult`, `MappedRangeQuery`, and `ReadTransaction.getMappedRange`.

## Risks And Edge Cases
The serialization format is coupled to native `FDBMappedKeyValue`. Malformed lengths throw exceptions or copy out of bounds. The raw `rangeResult` list can be null or mutable.

## Test Signals
Tests should cover decoding valid mapped rows with zero and multiple nested results, malformed length counts, equality/hash including nested results, and direct constructor behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/MappedKeyValue.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/MappedRangeQuery.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/MappedRangeQuery.java

## Purpose
`MappedRangeQuery` is the lazy asynchronous iterable for mapped range reads, mirroring `RangeQuery` but yielding `MappedKeyValue` rows produced by a server-side mapper.

## Important APIs, Types, And Functions
It implements `AsyncIterable<MappedKeyValue>`. `asList` optimizes exact streaming into one chunk when possible. `iterator()` returns `AsyncRangeIterator`, which tracks current and next chunks, outstanding fetches, row limit, continuation selectors, cancellation, and fetch futures. `FetchComplete` updates chunk state after native completion.

## Control Flow
Construction is passive, but the iterator starts the first fetch. Each chunk request calls `FDBTransaction.getMappedRange_internal`. When a chunk completes, the iterator consumes `MappedRangeResultInfo`, updates remaining row count and begin/end continuation, and prefetches the next chunk on the first `next` call for each current chunk.

## State And Persistence Behavior
Iterator state is mutable and synchronized. Native chunk futures remain open until `FetchComplete` consumes and closes them. `remove` clears the last returned key from the originating transaction.

## Dependencies And Integration Points
It depends on `FDBTransaction`, `KeySelector`, `StreamingMode`, `MappedRangeResult`, `FutureMappedResults`, `AsyncUtil`, and `EventKeeper`.

## Risks And Edge Cases
The TODO notes duplicated logic with `RangeQuery`. Snapshot mapped ranges are blocked by `FDBTransaction.ReadSnapshot`. Cancellation assumes `nextFuture` and `fetchingChunk` are initialized. Byte accounting counts only top-level key/value lengths, not nested range result bytes.

## Test Signals
Tests should cover exact `asList`, iterative chunk prefetch, row limits, reverse iteration, empty results, cancellation, remove semantics, fetch failures, and instrumentation counters.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/MappedRangeQuery.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/MappedRangeResult.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/MappedRangeResult.java

## Purpose
`MappedRangeResult` is the package-private container for one mapped-range result chunk and its continuation flag.

## Important APIs, Types, And Functions
Constructors accept either a `MappedKeyValue[]` or a `MappedRangeResultDirectBufferIterator`. `getSummary()` returns last key, row count, and `more`. `toString` prints values and continuation state.

## Control Flow
Native array marshaling constructs it directly. Direct-buffer marshaling calls `readResultsSummary`, iterates mapped rows, and stores them in a list. Range iterators use the summary to decide continuation selectors and termination.

## State And Persistence Behavior
The result stores a list of mapped values and immutable `more` flag. The list from `Arrays.asList` is fixed-size; the direct-buffer path uses a mutable `ArrayList`.

## Dependencies And Integration Points
It depends on `MappedKeyValue`, `MappedRangeResultDirectBufferIterator`, and `RangeResultSummary`.

## Risks And Edge Cases
`getSummary` uses the last returned key as continuation; wrong native ordering breaks iteration. Result list mutability differs between constructors.

## Test Signals
Tests should cover empty/non-empty summaries, `more` propagation, direct-buffer decoding, and constructor list behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/MappedRangeResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/MappedRangeResultDirectBufferIterator.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/MappedRangeResultDirectBufferIterator.java

## Purpose
`MappedRangeResultDirectBufferIterator` decodes mapped-range rows from a JNI-filled direct buffer.

## Important APIs, Types, And Functions
It extends `DirectBufferIterator` and implements `Iterator<KeyValue>` while returning `MappedKeyValue` from `next`. It reads length-prefixed key, value, range begin, range end, nested result count, and nested length-prefixed key/value pairs.

## Control Flow
After `readResultsSummary`, `MappedRangeResult` loops over this iterator. Each `next` consumes bytes from the buffer in native serialization order and increments `current`.

## State And Persistence Behavior
The cursor is the inherited buffer position plus `current` count. Close returns the direct buffer to the pool.

## Dependencies And Integration Points
It depends on `DirectBufferIterator`, `MappedKeyValue`, and `KeyValue`, and is used by `FutureMappedResults.getResults`.

## Risks And Edge Cases
The iterator declares `Iterator<KeyValue>` but returns `MappedKeyValue`, relying on covariance. It uses a raw `ArrayList` without generic parameter. Malformed buffer lengths can underflow or throw.

## Test Signals
Tests should decode rows with zero and multiple nested results, verify `NoSuchElementException`, malformed buffer handling, and buffer return through close.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/MappedRangeResultDirectBufferIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/MappedRangeResultInfo.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/MappedRangeResultInfo.java

## Purpose
`MappedRangeResultInfo` is a lightweight readiness token that defers mapped range result marshaling to its owning `FutureMappedResults`.

## Important APIs, Types, And Functions
The constructor stores a `FutureMappedResults`; `get()` calls `f.getResults()`.

## Control Flow
`FutureMappedResults.getIfDone_internal` creates this object after native error checking. `MappedRangeQuery.FetchComplete` calls `get` when it is ready to consume the chunk.

## State And Persistence Behavior
It stores only a reference to the native future wrapper. It does not own resources directly, but its reference keeps the future reachable until consumed.

## Dependencies And Integration Points
It integrates `FutureMappedResults` and `MappedRangeQuery`.

## Risks And Edge Cases
Calling `get` after the underlying future is closed will fail. Repeated `get` calls may attempt repeated native marshaling from the same native future and should not be assumed safe.

## Test Signals
Tests should verify deferred `get` calls, close-after-consumption behavior, and failure after underlying future closure.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/MappedRangeResultInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/NativeFuture.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/NativeFuture.java

## Purpose
`NativeFuture` is the common bridge from FoundationDB native futures to Java `CompletableFuture`s, handling callback registration, result marshaling, cancellation, close, and native pointer synchronization.

## Important APIs, Types, And Functions
Subclasses implement `getIfDone_internal`. `registerMarshalCallback` installs a JNI callback that schedules `marshalWhenDone` on an executor. `close` disposes the native future and fails incomplete Java futures. `cancel` cancels both Java and native futures. `getPtr` asserts read-lock ownership and rejects closed futures.

## Control Flow
Subclasses construct with a native pointer, initialize their fields, then call `registerMarshalCallback`. Native readiness invokes the Java callback at most once; `marshalWhenDone` locks, extracts the typed value, completes or completes exceptionally, and calls `postMarshal`. Most subclasses inherit `postMarshal` close behavior; range chunk subclasses override it.

## State And Persistence Behavior
The class stores a mutable native pointer protected by a read/write lock. Closing atomically zeros the pointer and disposes native resources. Completion state is inherited from `CompletableFuture`.

## Dependencies And Integration Points
All typed future classes extend it. It depends on JNI functions for callback registration, disposal, cancellation, error retrieval, and readiness.

## Risks And Edge Cases
Registering callbacks in the base constructor would race subclass initialization, hence the explicit pattern. Range future subclasses that override `postMarshal` must be closed manually after result extraction. Closing an incomplete future changes Java completion to `IllegalStateException`.

## Test Signals
Tests should cover callback completion, subclass initialization order, native exception propagation, close/cancel races, range-future manual close behavior, and `getPtr` after close.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/NativeFuture.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/NativeObjectWrapper.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/NativeObjectWrapper.java

## Purpose
`NativeObjectWrapper` is the base class for closeable Java objects that own a native FoundationDB pointer, such as databases and transactions.

## Important APIs, Types, And Functions
It stores `cPtr`, `closed`, and a read/write lock. `close` atomically marks the wrapper closed and invokes subclass `closeInternal(ptr)`. `getPtr` asserts read-lock ownership and rejects closed access. `checkUnclosed` prints leak warnings based on `FDB.instance().warnOnUnclosed`.

## Control Flow
Subclasses lock `pointerReadLock`, call `getPtr`, and invoke JNI. When closed, the write lock prevents new pointer readers, zeros the pointer, and delegates native disposal outside the lock.

## State And Persistence Behavior
Pointer state is in-memory and terminal after close. No persistent state exists. Finalizers in subclasses call `checkUnclosed` and `close`.

## Dependencies And Integration Points
`FDBDatabase`, `FDBTransaction`, and deprecated `Cluster` extend it.

## Risks And Edge Cases
The read-lock assertion is not enforcement when assertions are disabled, so callers must follow the locking convention. Finalizer-based cleanup is nondeterministic. `Cluster` passes pointer `0`, making it immediately closed.

## Test Signals
Tests should cover close idempotence, pointer rejection after close, concurrent close versus JNI access, leak warning toggles, and subclass disposal invocation exactly once.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/NativeObjectWrapper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/OptionConsumer.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/OptionConsumer.java

## Purpose
`OptionConsumer` is the internal target interface for encoded FoundationDB option setters.

## Important APIs, Types, And Functions
It defines `setOption(int code, byte[] parameter)`. Generated option wrapper classes call this through `OptionsSet`.

## Control Flow
An `OptionsSet` method encodes a typed parameter, then calls the consumer. Concrete consumers such as `FDBDatabase` and `FDBTransaction` forward codes and bytes to native JNI option setters under pointer locks.

## State And Persistence Behavior
The interface stores no state. Implementations may mutate native network, database, or transaction option state.

## Dependencies And Integration Points
It is used by `OptionsSet`, `ClusterOptions`, generated `NetworkOptions`, `DatabaseOptions`, and `TransactionOptions`.

## Risks And Edge Cases
The option code and byte parameter are untyped at this layer, so correctness depends on generated wrapper methods. Null parameters are valid for option codes with no argument.

## Test Signals
Tests should verify typed option wrappers encode into expected code/byte pairs and concrete consumers forward them to the correct native layer.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/OptionConsumer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/OptionsSet.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/OptionsSet.java

## Purpose
`OptionsSet` is the abstract base for generated FoundationDB option classes, providing common encoding helpers for no-argument, byte-array, string, and long-valued options.

## Important APIs, Types, And Functions
`getOptionConsumer` returns the underlying target. Protected `setOption` overloads encode null, raw bytes, UTF-8 strings, and little-endian 64-bit integers before calling the `OptionConsumer`.

## Control Flow
Generated option methods in subclasses call one of the protected helpers with a native option code. The helper serializes the parameter and delegates to the consumer, which forwards it to JNI.

## State And Persistence Behavior
The class stores only the consumer reference. Option state lives in the native object receiving the code.

## Dependencies And Integration Points
It depends on `ByteBuffer`, `ByteOrder.LITTLE_ENDIAN`, UTF-8 `Charset`, and `OptionConsumer`. Generated `NetworkOptions`, `DatabaseOptions`, and `TransactionOptions` rely on it.

## Risks And Edge Cases
Long encoding must remain little-endian to match the C API. String encoding is always UTF-8. Raw byte arrays are passed by reference to the consumer, so consumer implementations should not retain mutable arrays unexpectedly.

## Test Signals
Tests should cover encoding of null, string, long endianness, byte pass-through, and consumer invocation counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/OptionsSet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/Range.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/Range.java

## Purpose
`Range` is the public value type for an inclusive begin key and exclusive end key in FoundationDB keyspace.

## Important APIs, Types, And Functions
The constructor stores `begin` and `end` as public final byte arrays. `startsWith(byte[])` builds a prefix range using `ByteArrayUtil.strinc`. `equals`, `hashCode`, and `toString` provide content-based behavior and printable formatting.

## Control Flow
Read and clear overloads accept `Range` and unpack begin/end. Prefix range construction validates non-null prefix and calculates the first key after the prefix.

## State And Persistence Behavior
`Range` stores byte-array references without copying; fields are final but array contents are mutable.

## Dependencies And Integration Points
It is used by `ReadTransaction`, `Transaction`, `KeyRangeArrayResult`, and range/clear helper overloads. It depends on `ByteArrayUtil`.

## Risks And Edge Cases
Mutating `begin` or `end` after construction changes equality/hash and API behavior. `startsWith` relies on `strinc` behavior for all-0xff prefixes, which may throw depending on utility semantics.

## Test Signals
Tests should cover equality/hash, null prefix rejection, prefix range boundaries, binary string formatting, and mutation implications.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/Range.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/RangeQuery.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/RangeQuery.java

## Purpose
`RangeQuery` is the lazy asynchronous iterable for normal range reads, yielding `KeyValue` rows with chunked fetching, prefetch, limits, reverse support, and streaming-mode hints.

## Important APIs, Types, And Functions
It implements `AsyncIterable<KeyValue>`. `asList` optimizes exact mode into one native chunk or collects via iteration. `AsyncRangeIterator` tracks current chunk, next prefetched chunk, outstanding fetch, previous key for remove, row limit, iteration number, begin/end selectors, fetch future, and cancellation. `FetchComplete` processes each native result chunk.

## Control Flow
The iterator starts a first fetch immediately. `onHasNext` observes current chunk state or waits for `nextFuture`. `next` returns buffered rows, starts the next fetch on the first row of a chunk, swaps in prefetched chunks, records metrics, or waits recursively when no row is ready. Fetch completion updates continuation selectors from the last key and closes the `FutureResults`.

## State And Persistence Behavior
Iterator state is synchronized and mutable. Native range futures remain live only until chunk consumption. `remove` clears the last returned key in the underlying transaction; durability depends on later commit.

## Dependencies And Integration Points
It depends on `FDBTransaction.getRange_internal`, `FutureResults`, `RangeResult`, `RangeResultSummary`, `StreamingMode`, `AsyncUtil`, `EventKeeper`, and `KeySelector`.

## Risks And Edge Cases
The query should not span more than a few seconds because it uses the originating transaction. Cancellation assumes active futures exist. Blocking `hasNext` and recursive `next` use `join`, which wraps exceptions. Prefetch state must avoid reentrant fetches.

## Test Signals
Tests should cover exact `asList`, iterator mode, limits, reverse continuation, empty ranges, multi-chunk prefetch, remove, cancellation, fetch failures, and metrics for bytes/fetch counts/timing.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/RangeQuery.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/RangeResult.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/RangeResult.java

## Purpose
`RangeResult` is the package-private container for one normal range-query chunk and its `more` continuation flag.

## Important APIs, Types, And Functions
Constructors accept a test list, native concatenated key/value bytes with lengths, or a `RangeResultDirectBufferIterator`. `getSummary()` returns last key, key count, and `more`.

## Control Flow
Array-based native marshaling splits alternating key/value lengths into `KeyValue`s. Direct-buffer marshaling reads the summary and iterates rows. `RangeQuery` uses the summary to decide next fetch boundaries.

## State And Persistence Behavior
The result stores an in-memory list of copied `KeyValue`s and immutable `more`. The list can be mutated within the package.

## Dependencies And Integration Points
It depends on `KeyValue`, `RangeResultDirectBufferIterator`, and `RangeResultSummary`.

## Risks And Edge Cases
Odd length arrays throw `IllegalArgumentException`. Incorrect native length metadata can copy from wrong offsets. Continuation correctness depends on last-key ordering.

## Test Signals
Tests should cover empty chunks, odd length rejection, multi-row byte splitting, direct-buffer construction, and summary generation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/RangeResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/RangeResultDirectBufferIterator.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/RangeResultDirectBufferIterator.java

## Purpose
`RangeResultDirectBufferIterator` decodes standard range-query key/value rows from a direct buffer filled by JNI.

## Important APIs, Types, And Functions
It extends `DirectBufferIterator` and implements `Iterator<KeyValue>`. `next` reads key length, value length, key bytes, and value bytes from the current buffer position, increments `current`, and returns a `KeyValue`.

## Control Flow
`RangeResult` calls `readResultsSummary`, then repeatedly calls `next` for the parsed count.

## State And Persistence Behavior
State is inherited buffer cursor and row index. Closing returns the direct buffer to `DirectBufferPool`.

## Dependencies And Integration Points
It is used by `FutureResults.getResults` and depends on `KeyValue`.

## Risks And Edge Cases
Malformed or undersized buffers throw `BufferUnderflowException` or allocate bad sizes. `next` requires summary parsing first.

## Test Signals
Tests should cover single and multi-row decoding, empty result behavior, `NoSuchElementException`, and buffer return on close.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/RangeResultDirectBufferIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/RangeResultInfo.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/RangeResultInfo.java

## Purpose
`RangeResultInfo` is a lightweight readiness token for deferred normal range result marshaling.

## Important APIs, Types, And Functions
It stores a `FutureResults` reference and exposes `get()` to call `f.getResults()`.

## Control Flow
`FutureResults.getIfDone_internal` returns this after native error checking. `RangeQuery.FetchComplete` calls `get` when ready to consume the chunk.

## State And Persistence Behavior
It stores only the future reference. Resource ownership remains with `FutureResults`.

## Dependencies And Integration Points
It connects `FutureResults` to `RangeQuery`.

## Risks And Edge Cases
Repeated `get` calls or calls after future close are not safe API contracts. The object is package-private to keep use constrained.

## Test Signals
Tests should cover deferred marshaling, close-after-use, and failure after underlying future closure.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/RangeResultInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/RangeResultSummary.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/RangeResultSummary.java

## Purpose
`RangeResultSummary` packages the continuation-relevant metadata for a range chunk: last key, row count, and whether more data exists.

## Important APIs, Types, And Functions
Fields are `lastKey`, `keyCount`, and `more`. `toString` formats the last key with `ByteArrayUtil.printable`.

## Control Flow
`RangeResult` and `MappedRangeResult` produce summaries; range iterators consume them to decrement remaining row counts and update begin/end selectors.

## State And Persistence Behavior
The object is immutable by fields but stores a byte-array reference for `lastKey`.

## Dependencies And Integration Points
It is shared by normal and mapped range query implementations.

## Risks And Edge Cases
Null `lastKey` signals empty chunks and causes iterators to complete false. Mutating the last-key array after summary creation could alter debug output and continuation if reused.

## Test Signals
Tests should verify empty and non-empty summaries, `more` propagation, and printable formatting.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/RangeResultSummary.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/ReadTransaction.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/ReadTransaction.java

## Purpose
`ReadTransaction` is the public read-only transaction interface. It defines snapshot semantics, read version control, point reads, key selector resolution, range read overloads, mapped range reads, estimated range sizes, split points, and read conflict helpers.

## Important APIs, Types, And Functions
Key APIs include `isSnapshot`, `snapshot`, `getReadVersion`, `setReadVersion`, `get`, `getKey`, many `getRange` overloads over `KeySelector`, `byte[]`, and `Range`, `getMappedRange`, `getEstimatedRangeSizeBytes`, `getRangeSplitPoints`, `addReadConflictRangeIfNotSnapshot`, and `addReadConflictKeyIfNotSnapshot`. `ROW_LIMIT_UNLIMITED` is `0`.

## Control Flow
Implementations normalize overloads to selector-based forms and return lazy `AsyncIterable`s. Snapshot views route reads with relaxed conflict behavior and suppress conflict range additions.

## State And Persistence Behavior
The interface stores no state. Implementations read from the associated transaction and may add native read conflict ranges unless using snapshot mode.

## Dependencies And Integration Points
It depends on `AsyncIterable`, `AsyncIterator`, `KeySelector`, `Range`, `KeyValue`, `MappedKeyValue`, `StreamingMode`, and `ReadTransactionContext`.

## Risks And Edge Cases
Read-only transactions still need commit for full conflict checking in normal use. Snapshot reads relax isolation. Range iterables depend on transaction lifetime and should be consumed promptly.

## Test Signals
Tests should cover overload normalization, snapshot conflict behavior, range streaming modes, estimated size/split points, mapped range availability, and read retry helpers through contexts.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/ReadTransaction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/ReadTransactionContext.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/ReadTransactionContext.java

## Purpose
`ReadTransactionContext` abstracts objects that can execute read-only transactional functions, including `Database`, `Transaction`, and snapshot/read transaction views.

## Important APIs, Types, And Functions
It defines synchronous `read(Function<? super ReadTransaction,T>)`, asynchronous `readAsync(Function<? super ReadTransaction, ? extends CompletableFuture<T>>)` and `getExecutor()`.

## Control Flow
Concrete database contexts create retrying transactions; transaction contexts execute the function directly on the existing transaction; async variants return or compose `CompletableFuture`s.

## State And Persistence Behavior
The interface stores no state. Implementations decide whether a new transaction is created and retried or existing transaction state is used.

## Dependencies And Integration Points
It is extended by `ReadTransaction`, `TransactionContext`, and `Database`, and it uses Java `Function`, `CompletableFuture`, and `Executor`.

## Risks And Edge Cases
Code written against this abstraction may not know whether it is inside a retry loop or a single transaction. User functions must be safe under the concrete context's retry behavior.

## Test Signals
Tests should verify database retrying versus transaction direct execution, async exception wrapping, and executor propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/ReadTransactionContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/Transaction.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/Transaction.java

## Purpose
`Transaction` is the public read/write transaction interface combining read operations, write mutations, conflict-range control, commit/retry lifecycle, watches, and transaction-specific options.

## Important APIs, Types, And Functions
It extends `AutoCloseable`, `ReadTransaction`, and `TransactionContext`. Important methods include `getDatabase`, write and clear operations, conflict range/key methods, `mutate`, `options`, `commit`, committed version helpers, `getVersionstamp`, `getApproximateSize`, `watch`, `onError`, `cancel`, `close`, and direct `run`/`read` context methods.

## Control Flow
Client code builds operations on a transaction, calls `commit`, and on retryable failures calls `onError` to get a reset transaction. Database retry loops automate this sequence.

## State And Persistence Behavior
Implementations hold native transaction state: read version, read/write conflict ranges, mutations, options, watches, and commit status. Close disposes uncommitted native state.

## Dependencies And Integration Points
It integrates with `MutationType`, `TransactionOptions`, `Database`, tuple utilities, `Range`, `KeySelector`, and async contexts.

## Risks And Edge Cases
Transactions are invalid after `onError` in this binding. Unknown commit results can cause user code to be re-run. Watches and range iterators must be managed with transaction lifetime.

## Test Signals
Tests should cover writes, clears, atomic mutations, conflict range APIs, commit success/failure, retry with `onError`, versionstamp and committed version, watch cancellation, and close idempotence.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/Transaction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/TransactionContext.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/TransactionContext.java

## Purpose
`TransactionContext` abstracts objects capable of running read/write transactional functions, either by creating retrying database transactions or by executing inside an existing transaction.

## Important APIs, Types, And Functions
It extends `ReadTransactionContext` and defines `run(Function<? super Transaction,T>)` plus `runAsync(Function<? super Transaction, ? extends CompletableFuture<T>>)`.

## Control Flow
Database implementations wrap functions in retry/commit loops. Transaction implementations call the supplied function directly without automatic commit.

## State And Persistence Behavior
The interface stores no state. Concrete behavior depends on whether the context owns a transaction or is a transaction.

## Dependencies And Integration Points
It is implemented by `Database` and `Transaction`, allowing higher-level code to accept either a database or transaction context.

## Risks And Edge Cases
Ambiguity between retrying database context and direct transaction context can matter for side effects and commit timing. Async functions must return futures whose failures propagate correctly.

## Test Signals
Tests should cover generic helpers working against both database and transaction contexts, sync/async exception propagation, and executor use inherited from read context.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/TransactionContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/AsyncIterable.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/AsyncIterable.java

## Purpose
`AsyncIterable` is the FoundationDB binding abstraction for asynchronously iterable result sets such as range queries.

## Important APIs, Types, And Functions
It extends `Iterable<T>` but narrows `iterator()` to return `AsyncIterator<T>`. `asList()` asynchronously materializes all results into a list.

## Control Flow
Implementations return iterators that expose asynchronous readiness through `onHasNext`. `asList` may either optimize the provider-specific operation or delegate to `AsyncUtil.collect`.

## State And Persistence Behavior
The interface stores no state. Implementations may own transactions, native futures, or buffered chunks.

## Dependencies And Integration Points
It is implemented by `RangeQuery`, `MappedRangeQuery`, and wrappers returned by `AsyncUtil.mapIterable`.

## Risks And Edge Cases
Materializing large ranges with `asList` can consume substantial memory. Iterators may need cancellation/close depending on implementation.

## Test Signals
Tests should verify iterator covariance, `asList` behavior for empty/large sequences, and integration with `AsyncUtil.collect`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/AsyncIterable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/AsyncIterator.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/AsyncIterator.java

## Purpose
`AsyncIterator` extends Java `Iterator` with non-blocking readiness and cancellation for FoundationDB asynchronous result streams.

## Important APIs, Types, And Functions
`onHasNext()` returns a `CompletableFuture<Boolean>` indicating whether `next` can produce another element. `hasNext` remains the blocking form. `next` returns the next element and may block if readiness was not awaited. `cancel` stops outstanding asynchronous work.

## Control Flow
Range iterators implement `onHasNext` around chunk fetch futures. Utility wrappers in `AsyncUtil` delegate readiness, next, remove, and cancel to underlying iterators.

## State And Persistence Behavior
The interface stores no state. Implementations usually keep cursor state and outstanding futures.

## Dependencies And Integration Points
It is central to `RangeQuery`, `MappedRangeQuery`, `LocalityUtil.BoundaryIterator`, `AsyncUtil`, and `CloseableAsyncIterator`.

## Risks And Edge Cases
Calling `next` without awaiting readiness can block. Cancellation semantics depend on implementation and may affect all consumers of shared work.

## Test Signals
Tests should cover readiness futures, blocking `hasNext`, `next` after exhaustion, cancellation, remove delegation, and exception propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/AsyncIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/AsyncUtil.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/AsyncUtil.java

## Purpose
`AsyncUtil` provides utility functions for composing `CompletableFuture`s and consuming/mapping `AsyncIterable`/`AsyncIterator` streams without blocking.

## Important APIs, Types, And Functions
Constants `DONE`, `READY_TRUE`, and `READY_FALSE` avoid repeated completed-future allocation. Utilities include `applySafely`, `forEach`, `forEachRemaining`, `collect`, `collectRemaining`, `mapIterable`, two `mapIterator` overloads, `whileTrue`, `success`, `whenReady`, `composeExceptionally`, `composeHandle`, `composeHandleAsync`, `getAll`, `tag`, `whenAny`, and `whenAll`. `LoopPartial` implements stack-safe asynchronous looping.

## Control Flow
Iteration helpers call `onHasNext`, process an item, and loop via `whileTrue`. Mapping wrappers delegate iterator state to underlying iterators while applying a synchronous function in `next`. Composition helpers adapt Java `CompletableFuture.handle` forms that return nested futures. `whileTrue` runs synchronously through already-completed futures and schedules continuations only when needed.

## State And Persistence Behavior
The class is stateless aside from static completed futures. Per-call accumulator lists and loop objects are local.

## Dependencies And Integration Points
It depends on `FDB.DEFAULT_EXECUTOR`, Java futures, executors, and functional interfaces. `FDBDatabase` retry loops, `RangeQuery`, `MappedRangeQuery`, and `LocalityUtil` rely on it.

## Risks And Edge Cases
`applySafely` catches only `RuntimeException`, not `Error` or checked exceptions thrown through sneaky mechanisms. `getAll` uses `getNow(null)` after `whenAll`, so exceptional inputs propagate through `whenAll`. Empty `whenAny` behavior follows `CompletableFuture.anyOf` with an empty array and may never complete.

## Test Signals
Tests should cover sync and async loop bodies, exceptional futures, iterator collection/mapping, closeable iterator mapping preserving close, compose-handle flattening, empty and failing task collections, and default/custom executor scheduling.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/AsyncUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/Cancellable.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/Cancellable.java

## Purpose
`Cancellable` is a small contract for operations or signals whose outstanding work can be cancelled.

## Important APIs, Types, And Functions
It defines one method, `cancel()`, documented as non-blocking, idempotent, and non-throwing for non-fatal conditions.

## Control Flow
Implementations are expected to stop work and notify all consumers that no result will be returned. `AsyncIterator` uses the same cancellation shape directly rather than extending this interface.

## State And Persistence Behavior
The interface stores no state. Implementations typically maintain cancellation flags and cancel outstanding futures.

## Dependencies And Integration Points
It belongs to the async support package and documents a cancellation model shared conceptually by range iterators and closeable async iterators.

## Risks And Edge Cases
The interface cannot enforce idempotence or non-throwing behavior. Shared operations should define whether one consumer cancellation cancels all consumers.

## Test Signals
Tests for implementations should verify repeated cancel calls, cancellation before and after completion, and downstream consumer notification.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/Cancellable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/CloneableException.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/CloneableException.java

## Purpose
`CloneableException` marks exceptions that can produce a new exception with a fresh backtrace at the caller site.

## Important APIs, Types, And Functions
It defines `Exception retargetClone()`.

## Control Flow
Code handling asynchronous failures can call `retargetClone` to preserve a more useful call stack when rethrowing or completing futures.

## State And Persistence Behavior
The interface stores no state. Implementations decide what error code/message/cause data is copied into the clone.

## Dependencies And Integration Points
It is part of the async package and is relevant to exception types used with asynchronous FoundationDB APIs.

## Risks And Edge Cases
Incorrect implementations may lose original error code, cause, or suppressed exceptions. The interface does not require the clone type to match exactly beyond returning `Exception`.

## Test Signals
Tests should verify cloned exceptions preserve semantic fields and have a new stack trace including the retargeting call.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/CloneableException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/CloseableAsyncIterator.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/CloseableAsyncIterator.java

## Purpose
`CloseableAsyncIterator` combines `AsyncIterator` with `AutoCloseable` for asynchronous streams that own resources and must be closed after use.

## Important APIs, Types, And Functions
It overrides `close()` and provides a default `cancel()` implementation that calls `close()`.

## Control Flow
Consumers can call either `close` or `cancel` to stop work and release resources. `LocalityUtil.BoundaryIterator` implements it for boundary-key scans.

## State And Persistence Behavior
The interface stores no state. Implementations typically own transactions, native futures, file handles, or other closeable resources.

## Dependencies And Integration Points
It extends `AutoCloseable` and `AsyncIterator` and is wrapped by `AsyncUtil.mapIterator(CloseableAsyncIterator, Function)`.

## Risks And Edge Cases
Because `cancel` aliases `close`, implementations should make close idempotent and safe after partial iteration. Users must remember to close these iterators; otherwise resources may leak until finalization or transaction cleanup.

## Test Signals
Tests should cover close idempotence, cancel alias behavior, mapped closeable iterator forwarding, and resource release after early termination.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/async/CloseableAsyncIterator.java -->
