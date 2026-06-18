# subset-b-008390 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/AsyncStackTester.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/AsyncStackTester.java

Purpose: asynchronous cross-binding stack-machine executor for the Java binding. It consumes tuple-encoded instructions from FoundationDB keys under a prefix and executes API operations through `CompletableFuture` chains so the async API can be compared with the synchronous stack tester and other language bindings.

Important APIs and flow: `processInstruction` dispatches `StackOperation` values for stack manipulation, transaction lifecycle, mutations, reads, range reads, key selectors, conflict ranges, tuple packing/unpacking, versionstamps, option smoke tests, and stack logging. `AsynchronousContext` extends `Context`, pages instructions with `db.readAsync`, delegates `DIRECTORY_` operations to `AsyncDirectoryExtension`, and releases transaction references after every operation. Helpers flatten futures into stack values, convert FDB exceptions into packed `ERROR` tuples, filter `getKey` results by prefix, and log stack entries in batches.

State and persistence: state lives in the shared `Context.stack`, static named transaction map, per-context instruction cursor, and `lastVersion`. Database writes include tested mutations plus `LOG_STACK` output under a caller-provided prefix. Risks are high around async reference counting, mixed `join()` calls in some operations, prefix filter boundary behavior, and keeping operation semantics aligned with `StackTester`. Test signal is strongest when driven by binding tester workloads that exercise future completion, retry, directory, tuple, watch, and locality operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/AsyncStackTester.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/BlockingBenchmark.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/BlockingBenchmark.java

Purpose: microbenchmark for Java future blocking overhead on a transaction with a fixed read version, intended to measure client-side future completion costs without depending on real database contact.

Important APIs and flow: `main` selects `TestApiVersion.CURRENT`, opens a database and transaction, sets the read version, then times several blocking strategies over `tr.getReadVersion()`: `join`, `get`, one async identity callback, ten chained async callbacks, and repeated `get`. `runTests` measures both serial and `PARALLEL` batched future blocking.

State and persistence: no intended database persistence; the transaction read version is set explicitly and only read-version futures are created. Dependencies are `FDB`, `Database`, `Transaction`, `CompletableFuture`, and `FDB.DEFAULT_EXECUTOR`. Risks include coarse millisecond timing, ignored exceptions, and reliance on an openable cluster file/database object even though reads should not contact storage. Test signal is performance-only stdout, not assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/BlockingBenchmark.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/ConcurrentGetSetGet.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/ConcurrentGetSetGet.java

Purpose: simple async concurrency stress program that runs many get/set/get transactions to expose callback, retry, or semaphore-leak failures in `Database.runAsync`.

Important APIs and flow: `apply` uses a `Semaphore` to cap outstanding transactions at `CONCURRENCY`, creates random `test:<int>` keys with `SecureRandom`, and launches `db.runAsync` transactions that get the key, set it to `value`, then read it again. Atomic counters record attempts, completed second gets, and errors; a background status thread prints progress.

State and persistence: writes random user-space keys prefixed `test:` and leaves them unless external cleanup occurs. Integration points are `Database.runAsync`, transaction read-your-writes behavior, `FDB.DEFAULT_EXECUTOR`, and semaphore coordination. Risks include `System.exit`, one-shot status thread, random key accumulation, and possible deadlock if a failure path misses semaphore release. Signal is final throughput and counter consistency.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/ConcurrentGetSetGet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/Context.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/Context.java

Purpose: shared execution context for the Java stack-machine testers. It owns the instruction range, shared stack, child contexts, named transaction registry, and asynchronous parameter popping semantics used by both synchronous and asynchronous runners.

Important APIs and flow: the constructor derives the instruction scan range from `Tuple.from(prefix).range()` and opens a current transaction. `run` calls subclass `executeOperations` and joins child threads. Static transaction maps implement `newTransaction`, `replaceTransaction`, `releaseTransaction`, and `getTransaction` with reference counts so pending futures can safely outlive an instruction. `popParams` recursively pops stack entries and resolves futures on `FDB.DEFAULT_EXECUTOR`, converting FDB failures to packed error bytes.

State and persistence: static maps are process-wide and keyed by printable transaction names, so thread tests share named transactions. `lastVersion` stores read/commit version data for later `SET_READ_VERSION`. Risks include global state across contexts, assert-dependent null checks, reference leaks on unexpected future paths, and process termination on runner exceptions. Integration is central to `Instruction`, `StackTester`, `AsyncStackTester`, and directory extensions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/Context.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/ContinuousSample.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/ContinuousSample.java

Purpose: small reservoir sampler for benchmark latency summaries. It retains up to `sampleSize` comparable numeric samples while tracking population size, min, max, mean, median, and percentiles.

Important APIs and flow: `addSample` updates min/max, appends initial samples, then probabilistically replaces a random retained slot with probability `sampleSize / populationSize`. `percentile` lazily sorts retained samples and indexes by floor of percentile position. `toString` reports mean, median, 90th, and 98th percentile.

State and persistence: all state is in memory: `samples`, `populationSize`, `sorted`, and min/max. It has no FoundationDB dependency and is used by `ParallelRandomScan`. Risks include non-thread-safe internal mutation, approximate percentile accuracy, and a subtle reservoir issue where `samples.add(randomIndex, sample)` inserts instead of replacing after capacity. Callers synchronize externally when sharing it.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/ContinuousSample.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/DirectoryExtension.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/DirectoryExtension.java

Purpose: synchronous directory-layer extension for the stack tester. It interprets `DIRECTORY_` stack operations and exposes Java directory/subspace behavior to cross-binding directory tests.

Important APIs and flow: `dirList` stores `DirectoryLayer`, `Directory`, `DirectorySubspace`, `Subspace`, or null handles addressed by stack-supplied indexes. `processInstruction` creates subspaces/layers, changes current handle, creates/opens/moves/removes directories, lists and checks existence, packs/unpacks/ranges subspace keys, logs directory metadata, and strips prefixes. It uses `DirectoryUtil` to pop tuple paths and pushes encoded results back onto the instruction stack.

State and persistence: directory metadata is persisted through `DirectoryLayer` under the configured node/content subspaces, and logging operations write to the active transaction. Error handling pushes `DIRECTORY_ERROR` and appends null for operations that would have produced a directory handle. Risks include blocking `.get()` calls, null handle fallback through `errorIndex`, compatibility hacks around `exists` read versions, and preserving handle order exactly for cross-binding scripts.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/DirectoryExtension.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/DirectoryOperation.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/DirectoryOperation.java

Purpose: enum listing every stack-machine directory operation understood by the Java directory extensions.

Important APIs and flow: constants cover directory/subspace/layer creation, current handle switching, error index selection, create/open/move/remove/list/exists, layer checks, subspace pack/unpack/range/contains/open, logging, and prefix stripping. The `createsDirectory` flag marks operations that append a directory-like handle and therefore need a null placeholder on error.

State and persistence: no runtime state beyond enum metadata. Integration is direct with `DirectoryExtension`, `AsyncDirectoryExtension`, and `DirectoryUtil.pushError`. Risks are contract drift: adding an operation in one binding or extension without updating this enum breaks `valueOf(inst.op)` dispatch. Test signal comes from cross-binding directory workloads that expect handle list alignment after both success and failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/DirectoryOperation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/DirectoryUtil.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/DirectoryUtil.java

Purpose: helper methods for converting stack entries into directory-layer tuples and paths, plus common directory error reporting.

Important APIs and flow: `TuplePopper` repeatedly pops a tuple length followed by that many items and builds `Tuple.fromItems`. `popTuples`, `popTuple`, `popPaths`, and `popPath` expose async helpers returning tuples or `List<String>` paths. `pushError` pushes `DIRECTORY_ERROR` and appends null to the directory list when the operation's enum says it creates a directory.

State and persistence: only transient local lists. It depends on `Instruction.popParam/popParams`, `AsyncUtil.whileTrue`, `Tuple`, and `StackUtils`. Risks include assuming path tuple elements are strings, asynchronous executor ordering, and the handle-list side effect in error paths. Signal is indirect through directory stack tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/DirectoryUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/Example.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/Example.java

Purpose: minimal Java binding example demonstrating API version selection, database open, transaction retry wrapper, tuple key/value packing, and reading a value back.

Important APIs and flow: `main` selects `ApiVersion.LATEST`, opens the default database, runs one transaction that sets `Tuple.from("hello").pack()` to `Tuple.from("world").pack()`, then runs a read transaction and prints `Hello world`.

State and persistence: writes one user-space key named by the tuple encoding of `hello`. Dependencies are `FDB`, `Database`, and `Tuple`. Risks are limited but include mutating a shared cluster when run manually and using latest API rather than the repository's `TestApiVersion.CURRENT`. Test signal is the printed greeting and absence of exceptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/Example.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/Instruction.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/Instruction.java

Purpose: per-operation facade for stack-machine execution. It parses operation suffixes, binds the proper transaction/read context, and forwards stack operations to the owning `Context`.

Important APIs and flow: constructor interprets `_DATABASE` to use `Database` contexts and no transaction, `_SNAPSHOT` to use `tr.snapshot()` for reads, or normal operations to use the current transaction. It exposes `tcx` and `readTcx` for mutation/read wrappers, `replaceTransaction` overloads for `ON_ERROR`, `releaseTransaction`, and stack push/pop/swap/clear helpers. When pushing a `CompletableFuture` tied to a transaction, it increments the transaction reference count until completion.

State and persistence: holds immutable references for one tuple instruction and mutates the shared `Context.stack`. Risks include suffix parsing contract drift, future reference leaks, use of database-level operations where transaction replacement is impossible, and preserving snapshot/non-snapshot conflict semantics. Integration is central to stack testers and directory extensions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/Instruction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/IterableTest.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/IterableTest.java

Purpose: small manual test for iterating a range with Java's enhanced-for syntax over `AsyncIterable<KeyValue>` inside `TransactionContext.run`.

Important APIs and flow: `main` selects `TestApiVersion.CURRENT`, opens the default database, and calls `runTests`. The test transaction iterates `tr.getRange("vcount", "zz")`, printing each key/value. It then prints timing counters and exits.

State and persistence: read-only over the specified key range; no writes. Dependencies are `FDB`, `Database`, `TransactionContext`, and `KeyValue`. Risks include `System.exit`, unused `reps`/`lastcount`, lack of assertions, and reliance on existing database contents. Signal is only stdout and exception absence.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/IterableTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/LocalityTests.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/LocalityTests.java

Purpose: manual smoke test for Java locality APIs: storage server addresses for a key and boundary key iteration.

Important APIs and flow: `main` opens the cluster file from `args[0]`, calls `LocalityUtil.getAddressesForKey` for key `a`, then uses `LocalityUtil.getBoundaryKeys(database, begin, end)` over the user-space range. `AsyncUtil.collectRemaining` collects boundary keys from a `CloseableAsyncIterator`, which is closed by try-with-resources.

State and persistence: read-only metadata/locality access; no user data writes. Dependencies include locality APIs, async iterator collection, and printable byte utility. Risks include requiring a running cluster, system-key/locality permissions varying by configuration, potentially large boundary key output, and no assertions beyond exceptions. Signal is elapsed time, boundary count, printed addresses, and iterator closure behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/LocalityTests.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/ParallelRandomScan.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/ParallelRandomScan.java

Purpose: range-read latency/throughput benchmark that launches random point-sized range scans at varying parallelism against a preloaded integer-key space.

Important APIs and flow: `main` opens `args[0]` and runs `runTest` for parallelism 10 through 100. `runTest` disables read-your-writes in a single transaction, obtains a read version once, then for a fixed duration uses a semaphore to cap outstanding async range reads. Each read chooses a random 4-byte key, calls `tr.getRange(key, Integer.MAX_VALUE, 1, false, StreamingMode.ITERATOR).iterator().onHasNext()`, records latency in `ContinuousSample`, and prints throughput and percentile stats.

State and persistence: read-only benchmark, but it assumes a database populated with integer keys, likely by `SerialInsertion`. Risks include using one long-lived transaction for all reads, semaphore coordination, approximate sampler correctness, and time-window races. Signal is stdout metrics and error counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/ParallelRandomScan.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/PerformanceTester.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/PerformanceTester.java

Purpose: configurable Java binding performance suite for core Completable API operations, producing KPI JSON through `AbstractTester`/`TestResult`.

Important APIs and flow: constructor registers enum `Tests` to benchmark methods for future latency, set/clear/clear range, parallel and serial get, range reads, key selectors, single-key ranges, alternating get/set, and write transactions. `testPerformance` loads data, selects requested tests from `TesterArgs`, sleeps for quiescence, runs each test multiple times, and records the median keys/sec. `insertData` clears the configured subspace and fills deterministic fixed-width keys using concurrent `runAsync` actors.

State and persistence: actively clears and repopulates either user space or a configured subspace, then may perform canceled mutations or committed write transactions. Dependencies include `AbstractTester`, `TesterArgs`, `TestResult`, `AsyncUtil`, `ByteArrayUtil`, and transaction retry APIs. Risks include destructive clears without a subspace, benchmark sensitivity to cluster load, large sleeps, and tests that use canceled transactions as client-side mutation benchmarks. Signal is KPI output plus captured errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/PerformanceTester.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/RYWBenchmark.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/RYWBenchmark.java

Purpose: benchmark read-your-writes cache behavior within one Java transaction.

Important APIs and flow: a single transaction is created in `testPerformance`, seeded with deterministic keys by `insertData`, and reused for requested enum tests. Tests measure repeated cached gets of one key, sequential cached gets, full range reads from the transaction cache, range reads after point clears, range reads after clear ranges, and interleaved set/get increments on one key. Median results are written as KPIs.

State and persistence: `insertData` clears user space, sets keys in the transaction, and the transaction is canceled at the end, so the benchmark targets in-memory RYW behavior rather than committed storage state. It still mutates transaction state heavily. Risks include destructive clear staged in a transaction, cache growth, tests interacting through one reused transaction, and argument subspace inconsistencies in clear calls. Signal is KPI output and errors captured by `AbstractTester`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/RYWBenchmark.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/RangeTest.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/RangeTest.java

Purpose: manual integration smoke test for basic range reads, cancellation behavior, clear ranges, and `Range.equals/hashCode`.

Important APIs and flow: `main` writes `apple1` through `apple6`, calls `checkRange`, verifies canceled transactions return FDB error 1025 on a subsequent get, clears `apple3` through `apple6`, checks the range again, and compares several `Range` instances including null endpoints. `checkRange` reads a value, obtains a limited selector range as a list, then iterates the same `AsyncIterable`.

State and persistence: writes and clears user-space `apple*` keys. Dependencies include `FDB`, `Database.run`, `Transaction`, `KeySelector`, `Range`, and `AsyncIterable`. Risks include non-isolated test keys, stdout-based validation for range contents, and direct assumptions about cancellation error codes. Signal is exceptions for hard failures and printed diagnostics for range equality.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/RangeTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/SerialInsertion.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/SerialInsertion.java

Purpose: data loader benchmark that inserts one million 4-byte integer keys from multiple threads in batched transactions.

Important APIs and flow: `main` starts `THREAD_COUNT` `InsertionThread`s, dividing key ranges among them. Each thread reuses a `ByteBuffer` for big-endian integer keys, stages up to `BATCH_SIZE` sets per transaction, commits, then creates a new transaction. Runtime exceptions are passed to `tr.onError(e).join()` for retry handling.

State and persistence: writes keys from `0` to `NODES - 1` with value `....` into user space and does not clear first. Dependencies are `FDB`, `Database`, `Transaction`, and Java threads. Risks include duplicate/incorrect ranges if node division changes, committing large batches near transaction limits, no cleanup, and broad `RuntimeException` retry handling. Signal is elapsed time and absence of uncaught thread failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/SerialInsertion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/SerialIteration.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/SerialIteration.java

Purpose: scan throughput benchmark for iterating a large contiguous key range with configurable thread count.

Important APIs and flow: `main` opens a supplied cluster file and runs `runThreadedTest`. Each `IterationThread` performs `RUNS` scans with a randomized start delay, discarding the first run from averages. `scanDatabase` creates a transaction, disables read-your-writes, reads from empty key to `Integer.MAX_VALUE` with unlimited row limit and `StreamingMode.WANT_ALL`, and counts rows through a for-each iterator.

State and persistence: read-only, but assumes prior data loading, commonly by `SerialInsertion`. Risks include one transaction per full scan, unlimited row reads, no timeout/retry, hard-coded `THREAD_COUNT = 1`, and exception swallowing inside scan iteration. Signal is rows/sec printed per thread group.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/SerialIteration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/SerialTest.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/SerialTest.java

Purpose: simple serial transaction throughput smoke test for repeated get/set increments of a `count` key.

Important APIs and flow: `runTests` loops `reps` times calling `db.run`; each transaction reads `count`, parses it as an integer, writes incremented text, and records the prior value. It prints total time and transactions per second, then exits.

State and persistence: mutates the user-space `count` key and requires it to already contain a parseable integer; no initialization is present. Dependencies are `FDB`, `Database`, `TransactionContext`, and retry wrappers. Risks include `NumberFormatException` on missing data, non-isolated key use, `System.exit`, and no assertions. Signal is throughput output and exception traces.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/SerialTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/SnapshotTransactionTest.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/SnapshotTransactionTest.java

Purpose: integration tests for snapshot read conflict behavior and snapshot transaction identity semantics.

Important APIs and flow: `addUUIDConflicts` adds random read/write conflict keys so commits participate in conflict resolution. `snapshotReadShouldNotConflict` verifies snapshot key/range reads do not conflict while normal reads do. `snapshotShouldNotAddConflictRange` checks `addReadConflictRangeIfNotSnapshot` and `addReadConflictKeyIfNotSnapshot` return false on snapshots and true on normal transactions. `snapshotOnSnapshot` checks `isSnapshot`, pointer inequality for `tr.snapshot()`, and idempotence of snapshot-on-snapshot.

State and persistence: uses a `Subspace` under `("test","conflict_ranges")` only for conflict keys; no intentional data writes except conflict ranges. Risks include reliance on conflict code 1020, timeout sensitivity, and careful transaction ordering. Signal is strong because failures throw runtime exceptions after validating exception causes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/SnapshotTransactionTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/Stack.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/Stack.java

Purpose: thin wrapper around `java.util.Stack<StackEntry>` for the stack-machine test harness.

Important APIs and flow: exposes `push(int,Object)`, `push(StackEntry)`, `pop`, `swap`, `size`, and `clear`. `swap(index)` treats index as distance from top, validates bounds, and swaps the selected entry with the top entry.

State and persistence: in-memory stack only, shared through `Context.stack`. Dependencies are `StackEntry` and callers in `Instruction`, `Context`, and stack testers. Risks include synchronized legacy `java.util.Stack` semantics not guaranteeing higher-level thread safety, unchecked empty pops, and operation-index preservation depending on callers. Signal is indirect through stack-machine workloads.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/Stack.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/StackEntry.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/StackEntry.java

Purpose: data holder for one stack-machine entry, preserving both the instruction index that produced the value and the value itself.

Important APIs and flow: constructor stores `idx` and `value`; fields are package-private and mutable for direct harness access. Values can be bytes, strings, numbers, tuples, futures, errors, or other objects accepted by tuple serialization helpers.

State and persistence: no persistence; entries live in `Stack` until popped or logged. Integration points are stack push/pop, `WAIT_FUTURE`, `DUP`, `LOG_STACK`, and async flattening. Risks are limited but include mutable public package state and values whose lifetime is tied to transaction futures. Test signal is preserving correct original instruction indexes in logged stack output.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/StackEntry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/StackOperation.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/StackOperation.java

Purpose: enum contract for non-directory operations in the Java binding stack-machine tests.

Important APIs and flow: constants cover stack commands, waits/threads, transaction lifecycle, mutation commands, explicit conflict range/key operations, reads/ranges/key selectors, version APIs, error retry, arithmetic/concat, tuple and versionstamp packing, float/double encoding, unit-test smoke operations, and stack logging. `StackTester` and `AsyncStackTester` dispatch with `StackOperation.valueOf(inst.op)`.

State and persistence: no runtime state. Dependencies are semantic rather than code-level: tuple-encoded test instructions must match these names exactly after suffix removal by `Instruction`. Risks are compatibility drift across bindings and unimplemented operations causing hard failures. Signal comes from cross-binding generated stack workloads.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/StackOperation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/StackTester.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/StackTester.java

Purpose: synchronous cross-binding stack-machine executor for the Java binding. It is the blocking counterpart to `AsyncStackTester` and exercises broad FoundationDB API behavior from tuple-encoded instructions stored in the database.

Important APIs and flow: `processInstruction` dispatches stack, transaction, mutation, read, range, key selector, version, tuple, error, and unit-test operations, usually blocking with `join`/`get`. `SynchronousContext` scans instruction keys under the prefix and delegates `DIRECTORY_` commands to `DirectoryExtension`. Helpers execute retry-wrapped mutations, filter `getKey` results, read ranges by iterator or `asList`, log stack state, and run watch/locality smoke tests during `UNIT_TESTS`.

State and persistence: uses `Context` for shared stack, transaction registry, child contexts, and `lastVersion`. It persists tested mutations and stack logs; unit tests may set options and exercise watches/locality. Risks include broad `catch` converting only FDB failures to stack errors, random choice between iterator and list range paths, blocking waits that can hang on unresolved futures, and destructive operations driven by input scripts. Test signal is high for cross-binding parity, especially synchronous behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/StackTester.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/StackUtils.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/StackUtils.java

Purpose: shared conversion and error helpers for the stack-machine harness.

Important APIs and flow: `pushError` and `getErrorBytes` encode FDB errors as a tuple containing `ERROR` and the numeric code. `serializeFuture` waits on a future, maps null to `RESULT_NOT_PRESENT`, and converts FDB completion failures to error bytes. Numeric and boolean coercion helpers normalize stack operands, `createSelector` builds `KeySelector`, and `getRootFDBException` walks exception causes.

State and persistence: stateless utility class. Dependencies include `FDBException`, `KeySelector`, `Tuple`, `CompletableFuture`, and `CompletionException`. Risks include unchecked casts from generic `Object`, blocking joins in serialization, swallowing only FDB exceptions, and code-zero errors not being pushed. Signal is indirect through correctness of stack result encoding.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/StackUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/TestApiVersion.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/TestApiVersion.java

Purpose: single source for the API version used by standalone Java tests and benchmarks that are not part of normal CI.

Important APIs and flow: exposes `public static final int CURRENT = 800`. Comments note that these tests should be manually retested when the version changes.

State and persistence: no runtime state or persistence. Integration points are many manual test `main` methods that call `FDB.selectAPIVersion(TestApiVersion.CURRENT)`. Risks are version skew with generated bindings or cluster support; stale values can hide or create compatibility failures. Test signal is indirect because all dependent tests use this constant to select the binding API contract.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/TestApiVersion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/TestResult.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/TestResult.java

Purpose: lightweight result collector for Java performance tests, writing KPI and error data to a JSON-like file.

Important APIs and flow: constructor generates a random positive id, `addKpi` stores value and units under a name, `addError` records throwables, and `save` writes `javaresult-<id>.json` in the requested directory. Output is built manually with sorted KPI maps and escaped stack traces.

State and persistence: in-memory KPI/error maps become a filesystem artifact. Dependencies are standard Java IO and collections. Risks include manual JSON construction, partial escaping, no directory creation, random id collision possibility, and throwing on write failure after printing a message. Signal is the persisted result file consumed by benchmark automation or humans.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/TestResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/TesterArgs.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/TesterArgs.java

Purpose: command-line parser and immutable-ish configuration holder for Java performance test runners.

Important APIs and flow: `parseArgs` recognizes output directory, subspace, disabling multiversion API, enabling callbacks on external threads, using external client, and a list of tests to run. It prints usage and throws on malformed or unknown arguments. Accessors expose parsed booleans, `Subspace`, output directory, and test names.

State and persistence: stores configuration in object fields; no database or filesystem writes. Dependencies include `Subspace` and `Tuple`. Integration is with `AbstractTester`, `PerformanceTester`, and `RYWBenchmark`. Risks include returning null on help, typo in one error message, no quoting support beyond shell argv, and parsing tests until the next dash-prefixed token. Signal is argument validation before benchmarks run.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/TesterArgs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/TuplePerformanceTest.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/TuplePerformanceTest.java

Purpose: CPU microbenchmark and correctness stress for Java tuple packing, unpacking, equality, hashing, packed size, and subspace pack/unpack behavior.

Important APIs and flow: tuple generators create random mixed-type, integer, floating-point, or string-like tuples including nulls, byte arrays, strings, booleans, UUIDs, versionstamps, and nested tuples. `run` warms up, then for millions of iterations serializes a random tuple, deserializes it, verifies equality both with copied items and packed representations, checks packed size, validates subspace concatenation and unpacking, and measures hash timings. It prints aggregate timing statistics.

State and persistence: no database persistence; all work is in memory. Dependencies are tuple, subspace, versionstamp, UUID, random, and byte-array utilities. Risks include very long default runtime, random coverage without deterministic seed, Unicode generation edge cases, and stdout-only metrics. Signal is strong for tuple invariants because mismatches throw runtime exceptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/TuplePerformanceTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/TupleTest.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/TupleTest.java

Purpose: small tuple smoke test with a legacy helper for incomplete versionstamp encoding behavior under older API versions.

Important APIs and flow: `incompleteVersionstamps300` verifies incomplete versionstamps do not compare equal to complete tuple values despite matching packed representations, checks encoded position suffixes, verifies subspace prefix position adjustment, and asserts oversized versionstamp offsets throw. `runTests` currently creates a tuple inside a transaction and prints timing data.

State and persistence: no intentional database writes. Dependencies are `FDB`, `Database`, `TransactionContext`, `Tuple`, `Subspace`, `Versionstamp`, `ByteBuffer`, and byte comparisons. Risks include the main path not invoking `incompleteVersionstamps300`, comments requiring API < 520 while `TestApiVersion.CURRENT` is higher, `System.exit`, and minimal active assertions. Signal is weak in current main flow, stronger if the legacy helper is explicitly invoked under a compatible API.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/TupleTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/VersionstampSmokeTest.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/VersionstampSmokeTest.java

Purpose: smoke test for `SET_VERSIONSTAMPED_KEY` and transaction versionstamp retrieval in the Java tuple API.

Important APIs and flow: clears the tuple range for `prefix`, then runs a transaction that mutates a key packed with `Tuple.from("prefix", Versionstamp.incomplete()).packWithVersionstamp()` and returns `tr.getVersionstamp()`. A follow-up transaction reads the first key in the prefix subspace, unpacks it, and compares the embedded `Versionstamp` with `Versionstamp.complete(trVersion)`.

State and persistence: clears and writes keys under tuple prefix `prefix`. Dependencies include `MutationType.SET_VERSIONSTAMPED_KEY`, `Subspace`, `Tuple`, and `Versionstamp`. Risks include Java `assert` being disabled unless enabled with `-ea`, non-isolated prefix cleanup, and assuming one result key. Signal is printed versionstamps and assertion/equality when assertions are active.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/VersionstampSmokeTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/WatchTest.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/WatchTest.java

Purpose: manual watch API test covering cancellation and a repeated race between canceling and joining watch futures.

Important APIs and flow: `main` opens `args[0]`, sets a database option, starts a watch on key `a`, commits the transaction, cancels the watch, and expects cancellation error code 1101 when joining. `raceTest` creates a transaction and for 10,000 iterations watches key `hello`, then schedules cancel and join tasks in random order on a cached thread pool, waiting until both complete.

State and persistence: mostly read/watch state; it does not modify the watched key in this file. Dependencies include watch futures, `FDBException`, executor services, and transaction lifecycle. Risks include not shutting down the executor, verbose stderr/stdout, relying on watch cancellation code 1101, and using one transaction for many watch creations. Signal is absence of unexpected errors across race iterations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/WatchTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/WhileTrueTest.java -->
# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/WhileTrueTest.java

Purpose: placeholder/manual test class for async loop behavior that currently contains only an empty `main`.

Important APIs and flow: selects no API version and runs no logic; the file imports no FoundationDB APIs beyond package context. There are no functions besides `main`.

State and persistence: none. Dependencies are standard Java only. Risks are mainly stale test inventory: a named test class may imply coverage that does not exist. Test signal is effectively absent unless future logic is added.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/WhileTrueTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/tests.cmake -->
# sources/storage-engines/foundationdb/bindings/java/src/tests.cmake

Purpose: CMake include file that centralizes Java test source lists so the main build logic can consume test inventory without embedding file names inline.

Important APIs and flow: defines `JAVA_JUNIT_TESTS`, `JUNIT_RESOURCES`, `JAVA_INTEGRATION_TESTS`, and `JAVA_INTEGRATION_RESOURCES`. Unit tests are expected under `src/junit`; integration tests under `src/integration`; resource lists include helper classes such as fake transactions, library rules, database requirements, and multi-client helpers.

State and persistence: build-system variables only; no runtime state. Integration is with higher-level CMake logic for compiling/running Java binding tests. Risks include stale lists when files are added/removed, path assumptions, and this file not listing the standalone manual test classes researched in this subset. Test signal is build configuration coverage: missing entries mean tests may not compile or run in intended lanes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/tests.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/suppressions.xml -->
# sources/storage-engines/foundationdb/bindings/java/suppressions.xml

Purpose: Checkstyle suppression configuration for generated Java binding files.

Important APIs and flow: XML declares the Checkstyle suppressions DTD and suppresses all checks for files matching generated option and enum/error classes: `Options.java`, `ConflictRangeType.java`, `FDBException.java`, `MutationType.java`, and `StreamingMode.java`.

State and persistence: no runtime state; it affects static analysis behavior. Integration is with Java Checkstyle tooling in the binding build. Risks include regexes that are broad enough to match unintended generated-looking paths, stale generated file names, or hiding style issues if hand-written files match. Test signal is style-check stability for generated code while keeping hand-written sources checked.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/suppressions.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/CMakeLists.txt -->
# sources/storage-engines/foundationdb/bindings/python/CMakeLists.txt

Purpose: CMake packaging pipeline for the pure-Python FoundationDB binding.

Important APIs and flow: `SRCS` lists Python sources, metadata, README, manifest, and platform-specific `.pth` library pointer files. A copy loop mirrors sources into the build tree and creates `python_binding`. `vexillographer_compile` generates `fdboptions.py`; API version data is included from `FDB_API_VERSION_FILE` and configured into `fdb/apiversion.py`. The file optionally adds a `pycodestyle` check, configures release suffixes, creates a venv, installs `build`, and runs `python -m build` to produce sdist and py3-none-any wheel package artifacts.

State and persistence: creates build-tree files, generated option/version modules, virtualenv, dist outputs, and package copies under `${CMAKE_BINARY_DIR}/packages`. Dependencies include CMake, Python3, pip/build, vexillographer, version variables, and platform library path files. Risks include network/tool availability for pip, missing API version definitions, stale source list, and platform-specific `.pth` TODO for Windows. Signal is successful `python_binding`, style target, and package artifacts.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/MANIFEST.in -->
# sources/storage-engines/foundationdb/bindings/python/MANIFEST.in

Purpose: Python source distribution manifest additions.

Important APIs and flow: includes `README.rst` and `LICENSE` in the packaged sdist. It is consumed by Python build tooling invoked from the binding CMake packaging flow.

State and persistence: no runtime state; affects packaged file contents. Risks are omissions if additional non-Python runtime files become required, and duplication with packaging metadata in `pyproject.toml`. Test signal is package inspection or install tests confirming README/license presence.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/MANIFEST.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/fdb/__init__.py -->
# sources/storage-engines/foundationdb/bindings/python/fdb/__init__.py

Purpose: public entry point and API-version gate for the FoundationDB Python binding.

Important APIs and flow: before `api_version`, `open`, `init`, and `transactional` raise clear runtime errors. `api_version(ver)` validates one-time selection, enforces supported version bounds, imports `fdb.impl`, calls the C API selector, improves error messages for unsupported C library versions, initializes the C API, then injects public symbols from `impl`, directory, and subspace modules. It also handles compatibility paths for older API versions, including v13 method aliases and pre-610 cluster/open symbols.

State and persistence: module globals hold `__version__`, `LATEST_API_VERSION`, injected symbols, and `_version`. No database state changes occur until users call injected APIs. Dependencies include generated `fdb.apiversion`, `fdb.impl`, `fdb.locality`, `fdb.directory_impl`, and `fdb.subspace_impl`. Risks include global one-shot version state, dynamic symbol injection obscuring static analysis, and compatibility branches that must remain aligned with impl behavior. Signal is import/version selection behavior and downstream binding tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/fdb/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/fdb/apiversion.py.cmake -->
# sources/storage-engines/foundationdb/bindings/python/fdb/apiversion.py.cmake

Purpose: CMake template for the generated Python module containing binding API and package versions.

Important APIs and flow: emits `LATEST_API_VERSION = @FDB_AV_LATEST_BINDINGS_VERSION@` and `FDB_VERSION = "@FDB_VERSION@"`; CMake `configure_file` substitutes these placeholders during the Python binding build.

State and persistence: generated output becomes `fdb/apiversion.py` in the build tree and is imported by `fdb.__init__`. Dependencies are CMake variables loaded from `FDB_API_VERSION_FILE` and project version configuration. Risks include missing or stale substitutions causing import/version selection failures. Test signal is successful package import and `api_version` bound checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/fdb/apiversion.py.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/fdb/directory_impl.py -->
# sources/storage-engines/foundationdb/bindings/python/fdb/directory_impl.py

Purpose: Python implementation of FoundationDB's directory layer, including high-contention prefix allocation, directory metadata management, subspace wrappers, and partitions.

Important APIs and flow: `HighContentionAllocator.allocate` uses transactional counters/recent windows, snapshot reads, no-conflict writes, and write conflict keys to allocate compact unique tuple prefixes. `Directory` provides relative operations that route through a backing `DirectoryLayer`. `DirectoryLayer` implements create/open/create_or_open, move, remove/remove_if_exists, list, exists, version checks, prefix-free validation, metadata traversal, recursive removal, and partition delegation. `_to_unicode_path` normalizes byte/string/tuple paths. `DirectorySubspace` combines `Subspace` and `Directory`; `DirectoryPartition` creates a nested layer and forbids treating the partition root as a normal subspace. `_Node` caches node metadata and detects partition boundaries.

State and persistence: metadata is stored under `node_subspace` with root version and subdirectory maps; directory contents use allocated prefixes in `content_subspace`; partition metadata lives under nested node subspaces. Transaction-local allocator state is attached to transactions with a private attribute and guarded by locks. Dependencies include `fdb.impl.transactional`, tuple packing, `Subspace`, random, struct, and threading. Risks include path type compatibility, manual prefix conflicts, partition move/remove boundaries, allocator contention/window advancement correctness, and Python dynamic transaction attributes. Test signal comes from directory layer integration and cross-binding directory tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/python/fdb/directory_impl.py -->
