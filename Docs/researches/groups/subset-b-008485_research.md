# subset-b-008485 Research

Grouped research report for the FoundationDB Swift interop tests and fdbserver tester/tlog build sources in this work item. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/swift/tests/Rainbow.swift -->
# sources/storage-engines/foundationdb/fdbserver/swift/tests/Rainbow.swift

Purpose: Provides a tiny ANSI color helper for Swift test output. `RainbowColor` maps named colors to terminal escape sequences and `String` extensions expose `.red`, `.green`, `.yellow`, etc. for readable pass/fail/skip logging.

Important APIs/types/functions: `RainbowColor: String` defines the color escape codes plus `name()`. `String.colored(as:)` wraps the receiver in the selected color and resets to `.default`; computed properties call it for each color.

Control flow: There is no asynchronous or branching runtime flow beyond the enum switch in `name()`. Test code calls the computed properties while printing status lines.

State and persistence behavior: Stateless. It only constructs temporary strings; it does not mutate global state or persist output.

Dependencies and integration points: Pure Swift standard library. Used by `SimpleSwiftTestSuite.swift` and `swift_tests.swift` logging to distinguish skipped, passing, and failing tests. It assumes ANSI-capable stdout/stderr.

Risks: Escape sequences may pollute logs or non-terminal consumers. Color helpers always reset to default, which avoids most bleed-through risk. The file header name appears copied from `swift_test_streams.swift`, a documentation-only mismatch.

Test signals: Indirectly exercised whenever Swift tests print colored status. No explicit assertions are needed beyond ensuring colored output remains valid strings.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/swift/tests/Rainbow.swift -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/swift/tests/SimpleSwiftTestSuite.swift -->
# sources/storage-engines/foundationdb/fdbserver/swift/tests/SimpleSwiftTestSuite.swift

Purpose: Defines the minimal Swift async test harness used by fdbserver Swift/Flow interop tests. It gives tests a result-builder syntax, metadata, filtering, and a runner that executes all suites registered by `SimpleSwiftTestSuites`.

Important APIs/types/functions: `SimpleSwiftTestSuite` requires `init()` and a builder-backed `tests` list. `TestCasesBuilder.buildBlock` collects `TestCase` values. `TestCase` stores name, file, line, and an async throwing block, with `run()` invoking the block. `SimpleSwiftTestRunner.TestFilter` parses `--test-filter` and matches suite or test names. `SimpleSwiftTestRunner.run()` iterates registered suites and logs skip/test/pass/fail. `allTestsForSuite` and `findTestCase` locate tests by suite/name.

Control flow: The runner parses command-line arguments, iterates `SimpleSwiftTestSuites`, expands each suite by instantiating it, filters each test, and awaits `TestCase.run()`. Failures are caught and logged per test; the current implementation does not rethrow after a failed case, so the outer runner can still complete and signal its promise.

State and persistence behavior: Test metadata is immutable except `_testSuiteName`, which is currently unused. Runtime state is transient. No persistent storage is touched.

Dependencies and integration points: Depends on `SimpleSwiftTestSuites` from `swift_tests.swift` and color helpers from `Rainbow.swift`. The C++/Swift bridge entry point calls `SimpleSwiftTestRunner().run()` from a Swift `Task`.

Risks: Catching errors without propagating them can let a failing test suite complete successfully from the C++ promise perspective unless the failure is detected through logs or precondition crashes. The filter parser uses `fatalError` for missing values. The suite lookup uses stringification of type names, which is simple but brittle if module-qualified names change.

Test signals: Test signal is primarily console/trace text: `[skip]`, `[test]`, `[pass]`, `[fail]`. `findTestCase` offers a focused lookup path for future harness tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/swift/tests/SimpleSwiftTestSuite.swift -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/swift/tests/swift_test_streams.swift -->
# sources/storage-engines/foundationdb/fdbserver/swift/tests/swift_test_streams.swift

Purpose: Exercises Swift async integration with Flow `PromiseStream`/`FutureStream`, including direct `waitNext`, `AsyncSequence` iteration, a Swift task-group equivalent of Flow `loop choose`, and actor/task fanout from multiple streams.

Important APIs/types/functions: `StreamTests: SimpleSwiftTestSuite` contributes four `TestCase`s. The tests use generated C++ bridge types `PromiseStreamCInt`, `FutureStreamCInt`, `PromiseVoid`, `FlowClock`, and `end_of_stream()`. `sleepALittleBit()` uses the Flow clock for deterministic sleeps.

Control flow: The first test sends values into a promise stream, checks immediate readiness/pop behavior, then awaits `waitNext`. The second test starts a producer task, sends three integers, terminates with `end_of_stream`, and consumes the stream through `for try await`. The task-group test races a sleep task and a future-wait task, repeats sleep notifications until the promise completes, cancels outstanding tasks, and verifies the ready value. The final test starts two stream-consumer tasks, each spawning child tasks into a Swift `actor Cook`; a promise completes when all expected cook calls finish.

State and persistence behavior: All state is in-memory: stream queues, task-local variables, the `Cook` actor counters, and a promise used as a completion latch. No database or file state is touched.

Dependencies and integration points: Imports `Flow` and `flow_swift`. It validates generated Swift conformances from Flow stream bridging and the custom Flow clock/executor behavior used by FoundationDB's Swift interop layer.

Risks: Cancellation of stream-consuming tasks is explicitly noted as incomplete, so deferred task cancellation may not interrupt a blocked stream await. Nested unstructured `Task` creation can outlive local scope if completion accounting regresses. The tests rely on deterministic single-threaded Flow scheduling assumptions.

Test signals: Uses `precondition` assertions for values and actor results, plus end-of-stream termination and completion promise fulfillment. Failures manifest as thrown async errors, precondition traps, or hangs.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/swift/tests/swift_test_streams.swift -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/swift/tests/swift_test_task.swift -->
# sources/storage-engines/foundationdb/fdbserver/swift/tests/swift_test_task.swift

Purpose: Verifies Swift async/await behavior for Flow futures and FoundationDB's Swift executor integration, especially resumption on the Net2 event loop and mapping Flow priorities into Swift `Task.priority`.

Important APIs/types/functions: `TaskTests: SimpleSwiftTestSuite` defines tests for `FutureVoid`, `FutureCInt`, broader promise/future await behavior, and Flow task priority. It uses `PromiseVoid`, `PromiseCInt`, `FutureCInt.value()`, `__getUnsafe()`, `Task(priority: .Worker)`, and `assertOnNet2EventLoop()`.

Control flow: The simple tests send into promises before awaiting the future value. The broader test validates not-ready/ready transitions, sends one value before await, sends another from a spawned Swift task, and asserts resumption on the Net2 thread after awaits. The priority test executes a normal child task and a `.Worker` priority task, checking priority raw value and executor location.

State and persistence behavior: State is transient promises/futures and local integers. No database state or durable state is touched.

Dependencies and integration points: Imports `Flow` and `flow_swift`; relies on `_mainThreadID` and `assertOnNet2EventLoop` from `swift_tests.swift`. It tests generated Swift wrappers for Flow futures.

Risks: Uses `try!`, forced unwraps, and `precondition`, so regressions crash rather than produce structured test failures. The test assumes single-threaded Net2 execution and a stable raw priority value of 60 for `.Worker`.

Test signals: Preconditions verify future readiness, returned values, priority values, and executor thread. Printed `pprint` messages provide ordering diagnostics.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/swift/tests/swift_test_task.swift -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/swift/tests/swift_tests.swift -->
# sources/storage-engines/foundationdb/fdbserver/swift/tests/swift_tests.swift

Purpose: Provides the Swift test-suite registration and C++-visible entry point for the Swift/Flow interop tests.

Important APIs/types/functions: `_mainThreadID` captures `_tid()` at load time. `SimpleSwiftTestSuites` registers `TaskTests` and `StreamTests`. `@_expose(Cxx) public func swiftyTestRunner(p: PromiseVoid)` launches the Swift harness and signals a Flow promise. `assertOnNet2EventLoop()` checks the current thread matches `_mainThreadID`.

Control flow: C++ calls `swiftyTestRunner` with a promise. The function starts a Swift `Task`, awaits `SimpleSwiftTestRunner().run()`, logs any caught error in red, and sends `Flow.Void()` to unblock the caller. Tests call `assertOnNet2EventLoop` after awaits/tasks.

State and persistence behavior: Uses one unsynchronized global `_mainThreadID`; comments state this is safe because tests run single-threaded on Net2. No persistence.

Dependencies and integration points: Imports `Flow` and `flow_swift`, uses `PromiseVoid` and `Flow.Void`, and exposes the function to C++ via Swift interop. Depends on `Rainbow.swift`, `SimpleSwiftTestSuite.swift`, `TaskTests`, and `StreamTests`.

Risks: The promise is sent even after caught runner errors, so callers may see completion rather than failure unless the error crashes or logs are checked. Thread assertion is deliberately tied to single-thread Net2 behavior. The registered suite list must be updated manually when new Swift suites are added.

Test signals: C++ integration observes promise completion; Swift tests emit pass/fail logs and `precondition` traps. `assertOnNet2EventLoop` is a direct executor correctness signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/swift/tests/swift_tests.swift -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/swift_fdbserver_collections.swift -->
# sources/storage-engines/foundationdb/fdbserver/swift_fdbserver_collections.swift

Purpose: Holds disabled experimental Swift C++ interop conformances for FoundationDB map iterator types. It is currently a placeholder for future toolchain support.

Important APIs/types/functions: Under `#if NOTNEEDED`, it would conform `Map_UID_CommitProxyVersionReplies.const_iterator` and `MAP_UInt64_GetCommitVersionReply.const_iterator` to `UnsafeCxxInputIterator`, and their map types to `CxxSequence`, with equality operators.

Control flow: No active runtime control flow because the whole implementation is compile-time disabled.

State and persistence behavior: None. If enabled, it would only affect iteration semantics for imported C++ containers.

Dependencies and integration points: Imports `Flow`, `FDBServer`, and `Cxx`. The comments tie it to Swift toolchain limitations around C++ map interop.

Risks: Equality implementations currently return `true`, which would be incorrect if enabled as-is and could break sequence iteration. Any future activation must replace placeholders with real iterator comparison.

Test signals: No active tests. Build coverage confirms the disabled block stays excluded; future enabling would require Swift iteration tests over the bridged map types.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/swift_fdbserver_collections.swift -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/swift_fdbserver_cxx_swift_value_conformance.swift -->
# sources/storage-engines/foundationdb/fdbserver/swift_fdbserver_cxx_swift_value_conformance.swift

Purpose: Forces Swift value witness/conformance exposure for selected FDBServer/FDBClient request types so C++ can use them in generated Swift interop contexts.

Important APIs/types/functions: `@_expose(Cxx) public struct ExposeTypeConf<T>` is a generic carrier. Four `@_expose(Cxx)` functions accept `ExposeTypeConf<UpdateRecoveryDataRequest>`, `ExposeTypeConf<GetCommitVersionRequest>`, `ExposeTypeConf<GetRawCommittedVersionRequest>`, and `ExposeTypeConf<ReportRawCommittedVersionRequest>`.

Control flow: Functions are no-op markers; the effect happens at compile/header generation time, not runtime.

State and persistence behavior: No state. The functions do not read or mutate values.

Dependencies and integration points: Imports `FDBClient`, `FDBServer`, and `flow_swift`. Integrated with Swift/C++ generated headers where these request types otherwise cannot be used in Swift generic contexts from C++.

Risks: Manual maintenance burden: every additional bridged type with the same generic-context error needs a matching expose function. The file uses underscored Swift attributes, so it is sensitive to Swift interop evolution.

Test signals: Build success is the primary signal. Failures appear as C++/Swift interop compile errors involving missing value witness exposure for request types.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/swift_fdbserver_cxx_swift_value_conformance.swift -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/swift_fdbserver_stream_support.swift -->
# sources/storage-engines/foundationdb/fdbserver/swift_fdbserver_stream_support.swift

Purpose: Adds Swift `FlowStreamOps` and callback protocol conformances for FDBServer request `FutureStream` types, enabling Swift async iteration over C++ Flow streams.

Important APIs/types/functions: Extensions cover `FutureStream_UpdateRecoveryDataRequest`, `FutureStream_GetRawCommittedVersionRequest`, `FutureStream_GetCommitVersionRequest`, and `FutureStream_ReportRawCommittedVersionRequest`. Each sets `Element`, `SingleCB`, and `AsyncIterator = FlowStreamOpsAsyncIteratorAsyncIterator<Self>`. Matching `FlowSingleCallbackForSwiftContinuation_*` types conform to `FlowSingleCallbackForSwiftContinuationProtocol` and define `AssociatedFutureStream`.

Control flow: No direct runtime flow; these conformances enable generic async-stream code paths in `flow_swift` to subscribe callbacks and produce async iterators.

State and persistence behavior: No stored state in this file. State lives in the underlying Flow streams and continuation callback objects.

Dependencies and integration points: Imports `Flow`, `flow_swift`, `FDBClient`, `FDBServer`, and `Cxx`. It is the FDBServer-specific stream bridge companion to generic Flow Swift support and is validated by Swift stream tests.

Risks: Every C++ stream type requires exact pairing between the future stream and callback type. A mismatched associated stream would compile incorrectly or fail at interop boundaries. The file name in the header comment contains a typo (`strem`), documentation-only.

Test signals: Build checks conformance completeness. Runtime signal comes from Swift tests that await/iterate Flow streams and from any FDBServer Swift actor code consuming these request streams.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/swift_fdbserver_stream_support.swift -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/CMakeLists.txt -->
# sources/storage-engines/foundationdb/fdbserver/tester/CMakeLists.txt

Purpose: Defines the `fdbserver_tester` static library build target and link test.

Important APIs/types/functions: Uses `fdb_find_sources(FDBSERVER_TESTER_SRCS)`, `add_flow_target(STATIC_LIBRARY NAME fdbserver_tester ...)`, `add_fdbserver_link_test(fdbserver_testerlinktest fdbserver_tester fdbserver_core)`, `configure_fdbserver_common_includes`, `target_include_directories(.../include)`, `target_link_libraries(... fdbclient fdbserver_core toml11::toml11)`, and conditional `add_dependencies(fdbserver_tester toml11Project)`.

Control flow: CMake discovers sources, creates a static library, configures public include paths, links dependencies, and ensures vendored `toml11` builds first when not found as a package.

State and persistence behavior: Build-system state only: target graph, include paths, dependencies. No runtime state.

Dependencies and integration points: Pulls together tester orchestration, workload utilities, parser, maintenance, and consistency checker sources. Links to `fdbclient`, `fdbserver_core`, and TOML parsing.

Risks: `fdb_find_sources` makes source inclusion broad; accidental files in the directory can enter the target. TOML dependency handling must match external project naming. Missing public include configuration would break `fdbserver/tester/...` includes.

Test signals: `fdbserver_testerlinktest` verifies link completeness. Build failures around TOML or core symbols indicate integration drift.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/ConsistencyChecker.cpp -->
# sources/storage-engines/foundationdb/fdbserver/tester/ConsistencyChecker.cpp

Purpose: Implements tester-side consistency verification paths: storage audit triggering/waiting, normal `ConsistencyCheck` workload orchestration, and urgent consistency checks that divide key-server shards across testers.

Important APIs/types/functions: `auditStorageCorrectness` triggers audit storage through the data distributor and polls `getAuditState`. `checkConsistency` builds a `TestSpec` for the `ConsistencyCheck` workload and retries with repair. `runUrgentConsistencyCheckWorkload` recruits tester workloads and triggers their start endpoints. `getConsistencyCheckShards` reads key-server metadata. `getTesters` recruits tester-class workers. `getKeyFromString` and `loadRangesToCheckFromKnob` parse knob-provided `\xNN` key ranges. `makeTaskAssignment` batches shards across testers with shuffled tester IDs. `runConsistencyCheckerUrgentCore`, `runConsistencyCheckerUrgentHolder`, and `checkConsistencyUrgentSim` drive the urgent checker.

Control flow: Normal consistency checks optionally disable simulated connection failures, run a generated workload, retry until success or soft time limit, and call `repairDeadDatacenter` between failures. Audits wait for recovery/distributor readiness, trigger an audit, then poll until complete/error/failure or bounded retries. Urgent checks build an in-memory `KeyRangeMap<bool>` of incomplete ranges, recruit testers, map ranges to actual shards, assign shard batches, run tester workloads, mark completed clients' assigned ranges done, and repeat with backoff until no incomplete ranges remain.

State and persistence behavior: Urgent progress is in-memory only and resets if the actor restarts. It reads key-server metadata under system-key, immediate-priority, lock-aware transactions. Simulation state is mutated by disabling/restoring connection failures and setting `fdbSimulationPolicyState().isConsistencyChecked`. Audit state is persisted in cluster audit metadata owned by the management/audit subsystem.

Dependencies and integration points: Uses Flow coroutines, simulator APIs, FDB management/native APIs, system key ranges, data distributor audit endpoints, worker recruitment, `TesterInterface`, `WorkloadRequest`, `runWorkload`, `quietDatabase`, and knobs under `SERVER_KNOBS`/`CLIENT_KNOBS`.

Risks: Urgent checker progress is not durable; repeated actor failures can restart all work. Knob range parsing is strict and logs errors for malformed `\xNN` strings. If no testers can be recruited for a day, it escalates with severe trace. Task assignment intentionally randomizes tester selection to avoid retrying the same failing tester edge cases. Audit polling breaks after a retry cap even if still running, so callers rely on trace state and timeout wrappers.

Test signals: Trace events cover every phase (`AuditStorageCorrectness*`, `ConsistencyCheckUrgent_*`). Simulation injects random operation failures to validate retry behavior. `checkConsistencyUrgentSim` is called from the main test orchestrator before regular consistency checks when quiescent.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/ConsistencyChecker.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/ConsistencyChecker.h -->
# sources/storage-engines/foundationdb/fdbserver/tester/ConsistencyChecker.h

Purpose: Declares the consistency and audit entry points used by the tester orchestrator.

Important APIs/types/functions: Forward declares `AuditType`, `ClusterControllerFullInterface`, and `ServerDBInfo`. Declares `checkConsistency`, `auditStorageCorrectness`, `checkConsistencyUrgentSim`, and `runConsistencyCheckerUrgentHolder`.

Control flow: Header-only declarations; runtime flow is in `ConsistencyChecker.cpp`.

State and persistence behavior: No state in the header. Function signatures expose the stateful dependencies: `Database`, tester interfaces, server DB info async vars, and optional tester vectors.

Dependencies and integration points: Includes `fdbclient/NativeAPI.actor.h` and `fdbserver/tester/WorkloadUtils.h` for `Database`, `Future`, `TesterInterface`, and `TestSpec`-related types. Used by `test.cpp` to run post-workload checks and urgent checker modes.

Risks: The broad `checkConsistency` signature must stay aligned with call sites in `test.cpp`. Forward declarations reduce compile coupling but require complete types in implementation.

Test signals: Compile/link coverage ensures implementation matches declarations; functional signals come through tester runs.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/ConsistencyChecker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/CustomShardConfigWorkload.cpp -->
# sources/storage-engines/foundationdb/fdbserver/tester/CustomShardConfigWorkload.cpp

Purpose: Randomly exercises data-distribution user range configuration map behavior during simulation tests, including default ranges, overlapping updates, snapshots, and per-key lookup verification.

Important APIs/types/functions: `customShardConfigWorkload(Database const& cxUnsafe)` constructs a `ReadYourWritesTransaction`, uses `DDConfiguration().userRangeConfig()`, calls `updateRange`, `getSnapshot`, and `getRangeForKey`, and verifies expected `DDRangeConfig` values.

Control flow: The actor loops until commit succeeds. Each attempt sets system-key and lock-aware options, optionally initializes the all-keys default range, optionally applies fixed test ranges, verifies a table of query keys against both database-backed map lookups and the full snapshot, commits, and retries through `tr.onError` on failure.

State and persistence behavior: Mutates system-key backed data-distribution range configuration when enabled by random choices. The `RangeConfigMap` is optional because state variables need default construction around non-default-constructible versioned map internals.

Dependencies and integration points: Depends on `DataDistributionConfig`, `FDBTypes`, deterministic random, transaction options, and `customShardConfigWorkload` declaration in `tester.h`. `runTests7` invokes it with 25% probability in simulated database tests.

Risks: It writes system configuration during tests, so failures can affect subsequent test setup if not isolated by simulation cleanup. It uses `ASSERT` for verification, causing hard failures. Random branches mean any single run may skip parts of the behavior.

Test signals: `CODE_PROBE` and trace events (`KeyRangeConfigSetDefault`, `KeyRangeConfigSetTestRanges`, `KeyRangeConfigCommitted`, `KeyRangeConfigCommitError`) show which branches ran. Assertions validate lookup and snapshot consistency.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/CustomShardConfigWorkload.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/DatabaseMaintenance.cpp -->
# sources/storage-engines/foundationdb/fdbserver/tester/DatabaseMaintenance.cpp

Purpose: Provides database cleanup, HTML dumping, metric aggregation/logging, and post-test consistency-scan control for tester runs.

Important APIs/types/functions: `clearData` clears `normalKeys` and verifies emptiness. `toHTML` escapes binary keys/values for dumps. `dumpDatabase` scans a key range into an HTML file at a consistent read version. `aggregateMetrics` groups `PerfMetric`s by name and sums or averages them. `logMetrics` writes metrics as trace events. `checkConsistencyScanAfterTest` enables/disables simulated consistency scans based on `TesterConsistencyScanState`.

Control flow: `clearData` uses one transaction to clear and commit, then a second RAW_ACCESS transaction to verify no normal keys remain, retrying both loops through `onError`. `dumpDatabase` opens output, gets a read version, paginates `getRange` in batches of 1000, writes escaped rows, and retries on transaction errors. Metric aggregation is synchronous. Consistency-scan handling disables repeat execution by clearing `enabled`, optionally enables the scan, then disables it with optional wait-for-complete.

State and persistence behavior: `clearData` durably removes user data under `normalKeys`. `dumpDatabase` writes a local HTML file. Consistency-scan helpers mutate simulation/management state. Metrics are not persisted except trace output.

Dependencies and integration points: Uses native transactions, system key constants, management APIs, `PerfMetric`, `TraceEvent`, `fdbrpc/sim_validation.h`, and `QuietDatabase` support. Called by `runTest` in `test.cpp`.

Risks: `clearData` asserts if any key remains, so bugs or tenant/system-key misunderstandings become hard failures. `dumpDatabase` writes a file named from test title and can expose raw test data in HTML. `aggregateMetrics` assumes same-named metrics have compatible averaging/format metadata.

Test signals: Trace events include clear phases, database dumped filename, metric traces, and consistency-scan progress. `TesterClearFailure` is the critical failure signal for cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/DatabaseMaintenance.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/DatabaseMaintenance.h -->
# sources/storage-engines/foundationdb/fdbserver/tester/DatabaseMaintenance.h

Purpose: Declares tester maintenance helpers and the consistency-scan state struct shared with the main orchestrator.

Important APIs/types/functions: `TesterConsistencyScanState` contains `enabled`, `enableAfter`, and `waitForComplete`. Declares `clearData`, `dumpDatabase`, `aggregateMetrics`, and `checkConsistencyScanAfterTest`.

Control flow: No implementation flow in the header; the struct flags drive the conditional flow in `DatabaseMaintenance.cpp` and `test.cpp`.

State and persistence behavior: The struct is transient in-memory state carried across a test run. The declared functions can mutate database contents, write dump files, and alter simulated scan state.

Dependencies and integration points: Includes `fdbclient/NativeAPI.actor.h` for `Database`, `Future`, `KeyRange`, and `PerfMetric`. Used by `test.cpp` and the tester library.

Risks: `TesterConsistencyScanState*` is passed raw to async functions; callers must ensure lifetime across suspension points. Defaults keep scans disabled unless the orchestrator enables them.

Test signals: Compile/link coverage plus runtime traces from the implementation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/DatabaseMaintenance.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/KnobProtectiveGroups.cpp -->
# sources/storage-engines/foundationdb/fdbserver/tester/KnobProtectiveGroups.cpp

Purpose: Implements scoped knob overrides for tests, restoring original knob values when the scope ends.

Important APIs/types/functions: `KnobKeyValuePairs::set` inserts unique parsed knob values. `getKnobs` exposes the map. `KnobProtectiveGroup` constructor snapshots current values and assigns overrides. Destructor restores originals. `snapshotOriginalKnobs` searches client, server, then flow knobs. `assignKnobs` converts parsed values to `KnobValueRef` and calls `trySetServerKnob`.

Control flow: Construction snapshots every knob named in the override set, then applies override values. Destruction applies the saved original set. Missing knobs assert. Assignment traces and asserts on failure.

State and persistence behavior: Mutates process-global knob state for the lifetime of the protective group. Original values are held in memory only and restored by RAII.

Dependencies and integration points: Depends on `flow/Knobs.h`, `fdbclient/Knobs.h`, `fdbserver/core/Knobs.h`, parsed knob variants, and trace logging. Used by `TestSpecParser` and `test.cpp` for global and per-test TOML knob overrides.

Risks: Duplicate knob names assert in `set`. RAII restoration depends on destructor execution; process aborts skip restoration. `trySetServerKnob` is used for all knob categories after resolving values, so cross-category behavior depends on that helper recognizing the name.

Test signals: Trace events `SnapshotKnobValue`, `AssignKnobValue`, and `FailedToAssignKnob`. TOML tests with `[knobs]` exercise the path.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/KnobProtectiveGroups.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/TestSpecParser.cpp -->
# sources/storage-engines/foundationdb/fdbserver/tester/TestSpecParser.cpp

Purpose: Parses legacy text test specs and TOML test specs into `TestSpec`/`TestSet`, including workload options and scoped knob overrides.

Important APIs/types/functions: `testSpecGlobalKeys` accepts harness-level keys and side effects such as client info logging. `testSpecTestKeys` maps test-level attributes into `TestSpec` fields. `toml_to_string` normalizes TOML values. `readTests` parses legacy `key=value` text. `getOverriddenKnobKeyValues` parses TOML `knobs` arrays through client/server/flow knob parsers. `readTOMLTests_` parses `[[test]]`, nested workloads, and test-level knobs. `readTOMLTests` catches `std::exception` and converts to Flow `unknown_error`.

Control flow: Legacy parsing reads line by line, strips whitespace, routes recognized test/global keys, starts a new workload option group on `testName`, flushes option groups on new test titles, and returns specs with titles/options. TOML parsing reads global knobs, iterates tests, applies test-level fields, converts each `workload` table into a `VectorRef<KeyValueRef>`, then attaches per-test knobs.

State and persistence behavior: Produces in-memory `TestSpec` and `KnobKeyValuePairs`. It may set network options for client statistics logging. No file writes.

Dependencies and integration points: Uses `toml11`, Flow platform helpers, trace logging, native API types, knobs, `TestSpecParser.h`, and `KnobProtectiveGroups`. `runTests` calls it for `.txt` and `.toml` files.

Risks: Unknown legacy keys become workload options, so typos may only be caught later by option-consumption checks. TOML unknown test parameters log severe errors but parsing continues. Numeric parsing uses `sscanf`/asserts. TOML `workload` is required for each test via `toml::find`.

Test signals: Trace events `TestParserTest`, `TestParserOption`, `TestSpecUnrecognizedKnob`, `TestSpecUnrecognizedTestParam`, and `TOMLParseError`. Invalid specs surface later as `test_specification_invalid`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/TestSpecParser.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/TestSpecParser.h -->
# sources/storage-engines/foundationdb/fdbserver/tester/TestSpecParser.h

Purpose: Declares parser outputs and entry points for tester spec files.

Important APIs/types/functions: `TestSet` groups global `KnobKeyValuePairs overrideKnobs` with `std::vector<TestSpec> testSpecs`. Declares `readTests(std::ifstream&)` for legacy text and `readTOMLTests(std::string)` for TOML.

Control flow: Header only; parsing flow is in `TestSpecParser.cpp`.

State and persistence behavior: `TestSet` carries in-memory parsed configuration and knob overrides. No durable state.

Dependencies and integration points: Includes `WorkloadUtils.h` for `TestSpec` and `KnobKeyValuePairs`. Used by `test.cpp` to materialize test runs from file names.

Risks: Header couples parser users to workload utilities and knob protective types. API returns full vectors by value, which is appropriate for parsed spec ownership.

Test signals: Compile/link coverage and parser trace events in implementation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/TestSpecParser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/TesterServer.cpp -->
# sources/storage-engines/foundationdb/fdbserver/tester/TesterServer.cpp

Purpose: Implements the tester worker service that receives workload recruitment requests, constructs workload objects, executes setup/start/check/metrics phases, monitors database liveness, and handles special urgent consistency-check workloads.

Important APIs/types/functions: `checkAllOptionsConsumed` validates workload option use. `getWorkloadIface` builds a single or compound workload through `IWorkloadFactory`. `printSimulatedTopology` prints grouped simulator process topology. `databaseWarmer`, `pingDatabase`, and `testDatabaseLiveness` keep database liveness checks active. `runWorkloadAsync` serves workload interface requests. `testerServerWorkload` handles normal workload recruitment. `testerServerConsistencyCheckerUrgentWorkload` and helpers handle the one-at-a-time urgent checker path. `testerServerCore` is the long-running recruitment loop.

Control flow: On recruitment, the server validates expected workload title, constructs workload(s), sends back a `WorkloadInterface`, and runs an actor that listens for setup/start/check/metrics/stop requests. Normal workloads are sent into an actor collection. Urgent consistency checker requests bypass normal compound handling and are limited to one active checker per tester, with duplicate/conflicting request detection by `sharedRandomNumber`.

State and persistence behavior: Holds active workload actors, phase result caches (`setupResult`, `startResult`, `checkResult`) to make repeated phase requests idempotent, and one `consistencyCheckerUrgentTester` pair. Database state is mutated by workloads, not by the server wrapper except liveness ping transactions.

Dependencies and integration points: Uses `TesterInterface`, `WorkloadRequest`, `WorkloadInterface`, `WorkloadFactory`, `CompoundWorkload`, `ServerDBInfo`, simulator topology, role tracing, and native database creation. `test.cpp` recruits testers through these interfaces.

Risks: Workload option validation relies on `getOption` blanking consumed values. A workload that forgets to consume options causes `test_specification_invalid`. Normal workload stop is cooperative and not guaranteed to cancel all work immediately. Urgent checker conflict handling intentionally lets a newer checker replace an older one, producing broken promises for the older workload.

Test signals: Trace events include `WorkloadReceived`, `TestBeginAsync`, `TestSetupComplete`, `TestComplete`, `TestCheckComplete`, `WorkloadSendMetrics`, and `ConsistencyCheckUrgent_Tester*`. Liveness failures are severe trace events.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/TesterServer.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/TesterServer.h -->
# sources/storage-engines/foundationdb/fdbserver/tester/TesterServer.h

Purpose: Declares tester-server utilities exposed outside `TesterServer.cpp`.

Important APIs/types/functions: Declares `testDatabaseLiveness(Database cx, double databasePingDelay, std::string context, double startDelay = 0.0)` and `printSimulatedTopology()`.

Control flow: No header implementation. The declarations are used by the main test orchestrator for pre/post quiescence liveness checks and topology diagnostics.

State and persistence behavior: No header state. The declared liveness function performs repeated transaction pings; topology printing reads simulator process state.

Dependencies and integration points: Includes `fdbclient/NativeAPI.actor.h`. `testerServerCore` itself is declared in `include/fdbserver/tester/tester.h`, not this private header.

Risks: Minimal. Callers must understand `testDatabaseLiveness` is an infinite actor until cancelled or failed.

Test signals: Runtime traces from implementation; compile coverage ensures signature alignment.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/TesterServer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/WorkloadUtils.cpp -->
# sources/storage-engines/foundationdb/fdbserver/tester/WorkloadUtils.cpp

Purpose: Implements shared workload utilities: option parsing, key generation for key-value workloads, timing distributions, compound workload orchestration, and failure-injection workload behavior.

Important APIs/types/functions: `emplaceIndex` writes hex IDs into key buffers. `KVWorkload` key helpers generate random/present/absent keys and reverse indexes. `poisson` and `uniform` schedule operations. `getOption` overloads parse and consume options by blanking values. `hasOption` checks presence. `CompoundWorkload` implements description, setup/start/check/metrics aggregation, check timeout, and failure-injection insertion. `FailureInjectionWorkload` implements default injection probability and hold-while wrappers.

Control flow: Compound setup starts all primary setup futures, then either returns their completion or runs failure-injection setup held until primary setup completes. Start/check run primaries plus injected workloads in parallel, logging counts and aggregating with `waitForAll`/`allTrue`. Failure injection iterates registered factories, skips disabled names, and repeatedly injects according to deterministic random probability.

State and persistence behavior: `getOption` mutates option vectors in-place to mark consumed entries. `CompoundWorkload` stores primary and failure-injection workload references. `KVWorkload` stores key/value generation parameters. No durable state is written here.

Dependencies and integration points: Uses Flow coroutine utilities, deterministic random, trace, `fmt::join`, `ServerDBInfo`, and declarations in `workloads.h`. `TesterServer.cpp` depends on consumed-option behavior for spec validation.

Risks: `getOption(double)` parses into `float`, losing precision. `getOption(bool)` asserts on any non-`true`/`false` string. `indexForKey` assumes key layout generated by `keyForIndex`. Failure injection is probabilistic, so coverage varies unless seeds are controlled.

Test signals: Workload traces `WorkloadRunStatus`, `WorkloadCheckStatus`, and `AddFailureInjectionWorkload`. Invalid options produce `InvalidTestOption` and `test_specification_invalid`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/WorkloadUtils.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/include/fdbserver/tester/KnobProtectiveGroups.h -->
# sources/storage-engines/foundationdb/fdbserver/tester/include/fdbserver/tester/KnobProtectiveGroups.h

Purpose: Declares RAII types for collecting and applying temporary knob overrides in tester runs.

Important APIs/types/functions: `KnobKeyValuePairs` owns an `unordered_map<std::string, ParsedKnobValue>` and provides `set`/`getKnobs`. `KnobProtectiveGroup` stores original and overridden knob sets and declares constructor, destructor, `snapshotOriginalKnobs`, and `assignKnobs`.

Control flow: Header expresses the RAII contract: constructing a protective group applies overrides; destroying it restores originals.

State and persistence behavior: Holds knob values in memory and indirectly mutates global knob state through implementation.

Dependencies and integration points: Includes `flow/Knobs.h` for `ParsedKnobValue`. Used by TOML parser and main test orchestrator to apply global/per-test knobs.

Risks: Header exposes mutable global side effects through an apparently small utility. Copy/move behavior is not explicitly disabled for `KnobProtectiveGroup`, so usage should remain via `unique_ptr`/stack non-copy patterns.

Test signals: Compile coverage plus implementation trace events. TOML knob override tests exercise the declarations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/include/fdbserver/tester/KnobProtectiveGroups.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/include/fdbserver/tester/TestEncryptionUtils.h -->
# sources/storage-engines/foundationdb/fdbserver/tester/include/fdbserver/tester/TestEncryptionUtils.h

Purpose: Declares a tester helper for locating or naming test encryption material.

Important APIs/types/functions: `std::string getTestEncryptionFileName();`.

Control flow: Header only; implementation is elsewhere in the tester/library tree.

State and persistence behavior: The declaration suggests filesystem interaction by name, but this header has no state. Callers should expect a string path/name.

Dependencies and integration points: Includes `<string>`. It is part of the public tester include tree so workloads or utilities can share a consistent encryption test filename provider.

Risks: Without the implementation in this work item, behavior such as temporary path selection, environment dependence, and cleanup cannot be assessed here. The minimal API has no error channel.

Test signals: Compile/link coverage when consumers call the function; runtime signals depend on the implementation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/include/fdbserver/tester/TestEncryptionUtils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/include/fdbserver/tester/WorkloadUtils.h -->
# sources/storage-engines/foundationdb/fdbserver/tester/include/fdbserver/tester/WorkloadUtils.h

Purpose: Declares tester-wide workload result/spec structures and utility actors used by orchestration and workloads.

Important APIs/types/functions: `DistributedTestResults` holds metrics, successes, failures, and `ok()`. `TestSpec` stores title, phase flags, options, timeouts, database use, consistency-check flags, simulation agent modes, knob overrides, and disabled failure-injection workload names. Declares `runWorkload`, `logMetrics`, `databaseWarmer`, and `testExpectedError`.

Control flow: Constructors initialize defaults based on simulation status: simulated tests default to database clearing and consistency checks, different timeout/ping defaults, and all workload phases. `ok()` requires at least one success and zero failures.

State and persistence behavior: `TestSpec` is an in-memory execution contract. It carries `Standalone` Flow refs and knob overrides but does not persist anything itself.

Dependencies and integration points: Includes native API, simulation policy, knob protective groups, tester interfaces, workload declarations, perf metrics, and simulator. Central to `TestSpecParser`, `test.cpp`, `TesterServer.cpp`, and workload implementations.

Risks: Defaults are environment-sensitive through `g_network->isSimulated()`, so constructing specs before network initialization would be risky. `DistributedTestResults` default constructor leaves integer fields uninitialized until assigned by callers.

Test signals: Widespread compile/runtime coverage through all tester runs. `testExpectedError` is a reusable assertion actor for negative async tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/include/fdbserver/tester/WorkloadUtils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/include/fdbserver/tester/tester.h -->
# sources/storage-engines/foundationdb/fdbserver/tester/include/fdbserver/tester/tester.h

Purpose: Public tester API header declaring the tester server, top-level test runner, mode enums, and custom shard config workload.

Important APIs/types/functions: `testerServerCore`, `test_location_t` (`TEST_HERE`, `TEST_ON_SERVERS`, `TEST_ON_TESTERS`), `test_type_t` (`FROM_FILE`, `CONSISTENCY_CHECK`, `UNIT_TESTS`, `CONSISTENCY_CHECK_URGENT`), `runTests`, and `customShardConfigWorkload`.

Control flow: Header only; the enums steer `runTests` in `test.cpp`, selecting file parsing, generated consistency check, unit tests, or repeating urgent consistency checker, and selecting local/server/tester execution locations.

State and persistence behavior: No state in the header. Function signatures expose cluster connection, locality, unit test parameters, and restart flag state.

Dependencies and integration points: Includes locality, `TesterInterface`, and `UnitTest`. It is the include used by fdbserver/tester consumers and by `CustomShardConfigWorkload.cpp`.

Risks: `runTests` uses many const-reference parameters with defaults; implementation explicitly copies them for C++20 coroutine safety. Callers must choose correct enum combinations for the intended topology.

Test signals: Compile/link coverage and top-level tester execution. Invalid modes are generally asserted in implementation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/include/fdbserver/tester/tester.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/include/fdbserver/tester/workloads.h -->
# sources/storage-engines/foundationdb/fdbserver/tester/include/fdbserver/tester/workloads.h

Purpose: Defines the core workload abstraction, factories, option helpers, key-value workload base class, compound workload container, failure-injection support, and `quietDatabase` declaration.

Important APIs/types/functions: `WorkloadContext` carries options, client IDs, shared random number, DB info, connection record, and urgent-check ranges. `getOption` overloads, `poisson`, `uniform`, and `emplaceIndex` are shared helpers. `TestWorkload` defines `initialized`, `description`, `setup`, `start`, `check`, `getMetrics`, and phase bits. `TestWorkloadImpl` supplies descriptions from `Workload::NAME`. `FailureInjectionWorkload`, `IFailureInjectorFactory`, `FailureInjectorFactory`, `CompoundWorkload`, `ClientWorkload`, `KVWorkload`, `IWorkloadFactory`, `WorkloadFactory`, `REGISTER_WORKLOAD`, and `quietDatabase` form the registration/execution framework.

Control flow: Workload factories register statically by name. `IWorkloadFactory::create` looks up the requested `testName`. `WorkloadFactory` may wrap workloads in `ClientWorkload` for untrusted simulated clients. `TestWorkload` constructor consumes `runSetup` and initializes phase flags. Compound/failure-injection runtime flow is implemented in `WorkloadUtils.cpp`.

State and persistence behavior: `WorkloadContext` and workload objects hold per-client in-memory state. `KVWorkload` generates deterministic key/value content based on configured ranges. Actual database persistence is performed by concrete workload implementations, not this header.

Dependencies and integration points: Includes native API, database context clone support, simulation policy, tester interface, workload key definitions, and STL containers. Used by nearly every workload and by `TesterServer.cpp`.

Risks: Static registration order and duplicate workload names are guarded by asserts. Option consumption mutates `VectorRef<KeyValueRef>` values, so copies/ownership must be understood. `KVWorkload::randomValue` returns a `StringRef` over string memory passed into Flow's string wrapper; this relies on correct `StringRef`/`Value` ownership behavior in the constructor path.

Test signals: Workload creation failures emit `TestCreationError`; invalid options surface through option parsers. Concrete workload tests validate the framework indirectly.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/include/fdbserver/tester/workloads.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/test.cpp -->
# sources/storage-engines/foundationdb/fdbserver/tester/test.cpp

Purpose: Implements the top-level FoundationDB tester orchestrator: parses/generates test specs, recruits testers, runs workload phases, prepares/quiesces the database, runs consistency/audit checks, manages simulation policies, applies knob scopes, and records pass/fail counts.

Important APIs/types/functions: Global `passCount`/`failCount`. `throwIfError` unwraps `ErrorOr` future vectors. `runWorkload` recruits tester workloads and drives setup/start/check/metrics. `changeConfiguration` runs `ChangeConfig`. `runTest` wraps one `TestSpec` with timeout, metrics, dump, consistency checks, audits, and clearing. `monitorServerDBInfo` tracks cluster controller DB info. `initializeSimConfig` updates simulation failure policies from database configuration. `disableConnectionFailuresAfter` schedules simulation failure-disable behavior. `runTests7` is the core suite orchestrator. `runTests8` recruits enough workers and delegates to `runTests7`. `runTests` is the public entry point. `testExpectedError` validates expected async failures.

Control flow: `runTests` copies coroutine parameters, starts leader/interface monitors, builds a `TestSet` from mode/file/options, applies global knobs, then chooses urgent checker, local tester, or remote tester execution. `runTests8` waits for enough workers. `runTests7` derives suite-level needs, opens DB if needed, configures simulation agents and connection failures, optionally applies starting configuration, runs pre-test quiescence, then iterates specs with per-test knob protection and `runTest`. `runTest` runs workload phases, logs metrics, handles timeout as failure, performs optional dump/consistency scan/urgent check/regular check/audits, updates counts, and optionally clears data.

State and persistence behavior: Mutates global pass/fail counters, simulation policy state, connection-failure settings, backup/DR agent choices, database configuration, custom shard config, consistency scan state, and potentially database contents. It may write HTML dump files and clears `normalKeys` after tests. Server DB info is maintained in an `AsyncVar`.

Dependencies and integration points: Integrates Flow actors, cluster controller/worker interfaces, management APIs, data-distribution config, simulation validation, quiet database, consistency checker, maintenance helpers, parser, tester server, workload framework, and knob protection.

Risks: Global pass/fail counters persist across invocations in-process. Many operations use hard timeouts; simulated slowness can produce false failures. Comments call out coroutine lifetime hazards, mitigated by copying parameters/state to function scope. Stop requests to workloads are best-effort. Consistency/audit checks can dominate runtime and introduce complex failure modes after workload success.

Test signals: Primary traces include `TestRunning`, `TestSetupStart/Complete`, `TestComplete`, `TestCheckComplete`, `TestResults`, `TestProgress`, `TestsExpectedToPass`, timeout `ProcessEvents`, and audit/consistency traces. Final stdout prints counts passed/failed.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tester/test.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tlog/CMakeLists.txt -->
# sources/storage-engines/foundationdb/fdbserver/tlog/CMakeLists.txt

Purpose: Defines the `fdbserver_tlog` static library, link test, and unit test target for transaction-log server components.

Important APIs/types/functions: Uses `fdb_find_sources(FDBSERVER_TLOG_SRCS)`, `add_flow_target(STATIC_LIBRARY NAME fdbserver_tlog ...)`, `add_fdbserver_link_test(fdbserver_tloglinktest fdbserver_tlog fdbserver_logsystem fdbserver_core)`, `add_fdbserver_unit_test(fdbserver_tlog_test tlog ...)`, `configure_fdbserver_common_includes`, public/private include directories, and private links to `fdbserver_core`, `fdbserver_kvstore`, and `fdbserver_logsystem`.

Control flow: CMake discovers tlog sources, creates the library, configures tests and includes, and links the required internal libraries.

State and persistence behavior: Build graph only; no runtime state. The linked components themselves handle transaction-log persistence outside this file.

Dependencies and integration points: Integrates tlog sources with core, kvstore, and logsystem libraries. The unit test target gives a focused test lane named `tlog`.

Risks: Source discovery via `fdb_find_sources` can include unintended files. Missing private include for the current directory would break internal headers. Link target changes in core/logsystem/kvstore must be mirrored here.

Test signals: `fdbserver_tloglinktest` verifies link closure; `fdbserver_tlog_test` runs tlog unit tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/tlog/CMakeLists.txt -->
