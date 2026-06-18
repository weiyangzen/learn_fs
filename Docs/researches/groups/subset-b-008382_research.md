# subset-b-008382 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterTestSpec.cpp -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterTestSpec.cpp

## Purpose
Parses C API tester TOML files into the in-memory `TestSpec` and `WorkloadSpec` model consumed by `fdb_c_api_tester.cpp`. It is the boundary between declarative test scenarios and runtime options such as threading, buggify, database pooling, TLS cluster settings, and workload definitions.

## Important APIs, types, and functions
`readTomlTestSpec` loads one `[[test]]` table, maps known scalar keys through `testSpecTestKeys`, gathers optional `[[knobs]]`, and converts each `[[test.workload]]` table into a named `WorkloadSpec`. `processIntOption` validates bounded integer fields, while `toml_to_string` normalizes TOML strings and primitive values for the all-string workload option map.

## Control flow
The parser rejects missing or multiple `test` sections, rejects unknown test-level keys, then iterates workloads and requires each workload to contain `name`. Workload attributes are copied verbatim as strings so individual workload classes own deeper option validation.

## State and persistence behavior
No persisted state is written. The only state is the returned `TestSpec`, including knob pairs later applied as FDB network options. The empty `getOverriddenKnobKeyValues` stub is currently inert.

## Dependencies and integration points
Depends on `toml.hpp`, `fmt`, `TesterUtil::TesterError`, and the structs in `TesterTestSpec.h`. Its output feeds option randomization, network setup, transaction executor selection, and workload factory creation.

## Risks and test signals
Boolean parsing treats only literal `"true"` as true and anything else as false, so malformed booleans can silently disable settings if TOML accepts them. Exact parser errors are a useful signal for invalid test files; successful scenarios are exercised by every `apitester/tests/*.toml` run.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterTestSpec.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterTestSpec.h -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterTestSpec.h

## Purpose
Defines the declarative test model for the FoundationDB C API tester. The header keeps TOML-derived suite-level options separate from per-workload option maps.

## Important APIs, types, and functions
`WorkloadSpec` stores a workload `name` and string option map. `TestSpec` stores title, future mode, multi-threading, buggify, callbacks-on-external-threads, database-per-transaction, cluster-file tampering, FDB/client/database/client-count ranges, disable-client-bypass, run-loop profiling, knob overrides, and workload list. `readTomlTestSpec` is the parser entry point. `FDB_API_VERSION` is fixed to `FDB_LATEST_API_VERSION`.

## Control flow
This header has no runtime control flow, but its defaults define behavior when TOML omits a field: one FDB thread, one client thread, one database, up to ten clients, no buggify, callback futures, and no special network options.

## State and persistence behavior
The structs are transient configuration containers. They do not own FDB handles or files and are copied into `TesterOptions`, `TransactionExecutorOptions`, and `WorkloadConfig`.

## Dependencies and integration points
Includes generated API version information from `foundationdb/fdb_c_apiversion.g.h` and is consumed by the TOML parser, main tester executable, and test scenario files.

## Risks and test signals
Changing defaults changes the meaning of many TOML files that intentionally omit options. Range fields are later randomized, so tests should validate both lower and upper bounds by repeated runner invocations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterTestSpec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterTransactionExecutor.cpp -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterTransactionExecutor.cpp

## Purpose
Implements the C API tester transaction lifecycle: database selection, transaction creation, future continuation handling, retry/on-error behavior, timeout restarts, and cluster-file/database-creation fault injection.

## Important APIs, types, and functions
`TransactionContextBase` implements `ITransactionContext` with a `TxState` state machine, `commit`, `done`, `onError`, `makeSelfConflicting`, retry accounting, transaction recreation, and cleanup. `BlockingTransactionContext` schedules blocking waits on tester scheduler threads. `AsyncTransactionContext` registers FDB callbacks and tracks pending futures in `callbackMap`. `TransactionExecutorBase` initializes temp cluster-file variants, applies tamper behavior, and creates contexts. `DBPoolTransactionExecutor` reuses a pool of databases; `DBPerTransactionExecutor` creates a database per transaction.

## Control flow
`execute` builds a context, starts the user operation, and completes through either success `done`/`commit` or error `onError`. Retryable transactional errors flow through `tx.onError`; non-transactional retryable errors restart directly. Injected database-create failures and transaction timeouts can recreate the database/transaction before restart. Completed transactions cancel pending futures and call the workload continuation exactly once.

## State and persistence behavior
State is mostly in-memory: FDB database/transaction wrappers, callback maps, retry history, temp cluster files, and a tamper thread. Temp files are created under `tmpDir` and deleted by `TmpFile` unless process termination bypasses destructors. Tampering rewrites a synthetic cluster file from unreachable to invalid to valid copied contents.

## Dependencies and integration points
Depends on `test/fdb_api.hpp`, `TesterScheduler`, `TesterUtil`, FDB error codes, random helpers, and filesystem/threading. It is called by `WorkloadBase` and supplies all workload access to FDB.

## Risks and test signals
The highest risks are callback lifetime races, scheduler destruction after workload completion, deadlock in blocking mode, swallowed late callbacks, and retry loops hiding real failures. Signals include retry-limit logs, long-future wait logs, cancellation behavior in `CancelTransaction` workloads, timeout scenarios, DB-per-transaction tests, and tampered cluster-file tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterTransactionExecutor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterTransactionExecutor.h -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterTransactionExecutor.h

## Purpose
Declares the transaction execution abstraction used by all C API tester workloads. It hides FDB database/transaction ownership, continuation style, retry handling, and database selection policy behind stable interfaces.

## Important APIs, types, and functions
`ITransactionContext` exposes `db`, `dbOps`, `tx`, `continueAfter`, `continueAfterAll`, `commit`, `onError`, `done`, and `makeSelfConflicting`. `TransactionExecutorOptions` configures blocking futures, database-per-transaction, injected database create failures, tampered cluster files, database pool size, retry limit, and temp directory. `ITransactionExecutor` exposes `init`, `execute`, `selectDatabase`, `getClusterFileForErrorInjection`, and `getOptions`. `createTransactionExecutor` chooses the implementation.

## Control flow
Workloads pass a start lambda and final continuation into `execute`. During operations, they attach continuations to FDB futures through `ITransactionContext` rather than directly deciding blocking versus callback mode.

## State and persistence behavior
The header defines only configuration and interfaces. Runtime implementations persist no database data beyond normal FDB transaction effects; temp file behavior is implementation-owned.

## Dependencies and integration points
Depends on `test/fdb_api.hpp`, `TesterOptions`, `TesterScheduler`, and C++ functional/memory types. It is the main integration point between workload code and FoundationDB C API wrappers.

## Risks and test signals
Interface misuse is possible if workloads call `done` before all futures are accounted for or forget `makeSelfConflicting` when using timeout restarts. Compile-time signals catch signature drift; runtime signals come from correctness, cancel, timeout, and blocking/callback TOML suites.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterTransactionExecutor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterUtil.cpp -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterUtil.cpp

## Purpose
Provides concrete utility implementations for random generation, byte-copy helpers, assertion reporting, and temporary file management used by the API tester harness.

## Important APIs, types, and functions
`lowerCase` copies and lowercases byte strings. `Random` seeds a thread-local Mersenne generator and provides integer and probability helpers. `copyValueRef`, `copyKeyValueArray`, and `copyKeyRangeArray` copy FDB future-owned references into owned C++ containers. `TmpFile::create`, `write`, and `remove` manage temporary cluster-file variants.

## Control flow
Temporary file creation loops until it finds a non-existing randomized name, creates an empty file, and later rewrites/removes it. Array-copy helpers iterate native FDB result arrays and preserve `more` flags for range reads.

## State and persistence behavior
`Random::get` is thread-local mutable state. `TmpFile` persists a real filesystem file for the object lifetime and removes it in the destructor, logging removal failure to stderr.

## Dependencies and integration points
Depends on `test/fdb_api.hpp`, C++ filesystem/streams, `fmt`, and generated FDB error definitions. It supports `TesterTransactionExecutor`, workload implementations, and TOML parsing.

## Risks and test signals
The utilities assume little-endian layout through companion header checks. Temporary-file removal failure is non-fatal, so leaked files can be a signal of abnormal termination or platform behavior. Data-copy helpers are important for avoiding use-after-free of FDB future buffers.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterUtil.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterUtil.h -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterUtil.h

## Purpose
Declares shared API tester primitives: random data generation, assertion/error handling, time helpers, FDB result-copy helpers, integer byte encoding, and RAII temp files.

## Important APIs, types, and functions
`Random` supplies thread-local random strings/bytes, integers, and booleans. `TesterError` is the harness exception type. `ASSERT` aborts after `print_internal_error`. Time helpers use `steady_clock` and microsecond durations. `copyValueRef`, `copyKeyValueArray`, and `copyKeyRangeArray` copy FDB references. `toInteger` and `toByteString` convert little-endian integral payloads. `TmpFile` wraps a named temporary file.

## Control flow
Most helpers are inline. Random string generation reserves a selected length and appends lowercase ASCII bytes. Integral conversion asserts exact byte width before `memcpy`.

## State and persistence behavior
The only persistent behavior is `TmpFile` writing/removing files. `Random` state is per thread and intentionally nondeterministic because it seeds from `std::random_device`.

## Dependencies and integration points
Includes `test/fdb_api.hpp`, `fmt`, `flow/error_definitions.h`, and standard random/chrono/optional support. It is included throughout the API tester and transaction executor.

## Risks and test signals
Nondeterministic random seeding can make failures hard to reproduce. The endian static assertion prevents unsupported platforms from silently misencoding atomic-operation values. Assertion failures abort, which is expected for internal invariants rather than user input errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterUtil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterWatchAndWaitWorkload.cpp -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterWatchAndWaitWorkload.cpp

## Purpose
Defines the `WatchAndWait` API workload, which verifies that an FDB watch future triggers after a watched key changes.

## Important APIs, types, and functions
`WatchAndWaitWorkload` derives from `ApiWorkload`, overrides `getMaxSelfBlockingFutures`, and implements `randomOperation`. It uses transaction `set`, `get`, `watch`, `commit`, and `continueAfterAll`.

## Control flow
Each operation writes an initial value, then starts a transaction that reads the key. If the key already equals the new value it finishes; otherwise it creates a watch and commit future and waits for both. A scheduled sibling transaction writes the new value, causing the watch to fire.

## State and persistence behavior
The workload persists random keys and values in the test database. It deliberately ensures the new value differs from the initial value so the watch has a meaningful state transition.

## Dependencies and integration points
Depends on `TesterApiWorkload.h`, `test/fdb_api.hpp`, `WorkloadFactory`, and the transaction executor. TOML correctness suites include it alongside API and atomic-operation workloads.

## Risks and test signals
The workload has one self-blocking future, so blocking mode must allocate enough scheduler threads. Failures expose watch registration, commit ordering, callback scheduling, and cancellation issues.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterWatchAndWaitWorkload.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterWorkload.cpp -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterWorkload.cpp

## Purpose
Implements the generic workload framework for the C API tester: option parsing, task scheduling, transaction execution wrappers, workload lifecycle management, control pipes, progress checks, stats scheduling, and factory lookup.

## Important APIs, types, and functions
`WorkloadConfig::getIntOption`, `getFloatOption`, and `getBoolOption` validate string options. `WorkloadBase` tracks scheduled tasks, transaction counts, errors, and completion. `execTransaction` and `execOperation` delegate to `ITransactionExecutor`. `WorkloadManager` owns active workloads, starts/stops the scheduler, handles `STOP`/`CHECK` pipe commands, and emits `DONE`/`CHECK_OK`. `IWorkloadFactory::create` resolves registered workload names.

## Control flow
`WorkloadManager::run` initializes all workloads, starts them, joins the scheduler, then closes control output. `WorkloadBase::schedule` and `doExecute` increment task counters and call `scheduledTaskDone` after continuations. When the last workload finishes, the manager cancels stats timers and stops the scheduler.

## State and persistence behavior
State is in-memory counters, active-workload maps, control pipe streams, and optional stats timer. Database persistence is delegated to workload transactions.

## Dependencies and integration points
Depends on `TesterScheduler`, `TesterTransactionExecutor`, FDB transaction options, `fmt`, and workload factories registered in individual workload translation units.

## Risks and test signals
Races around `workloadDone`, scheduler stop, and control-pipe threads can hang tests. `tasksScheduled` must balance every scheduled unit. Test signals include `All workloads successfully completed`, per-workload error logs, `CHECK_OK`, `DONE`, and nonzero failure counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterWorkload.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterWorkload.h -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterWorkload.h

## Purpose
Declares the workload abstraction and manager used by the C API tester. It lets individual workload implementations focus on database operations while shared code handles scheduling, transactions, errors, and lifecycle.

## Important APIs, types, and functions
`IWorkloadControlIfc` supports external stop/progress checks. `IWorkload` defines `init`, `start`, `getWorkloadId`, `getControlIfc`, `printStats`, and `getMaxSelfBlockingFutures`. `WorkloadConfig` carries client identity, API version, tenant placeholder, and option map. `WorkloadBase` supplies `schedule`, `execTransaction`, `execOperation`, logging, and progress confirmation. `WorkloadManager` owns active workloads and control pipes. `IWorkloadFactory` and `WorkloadFactory<T>` provide registry-based creation.

## Control flow
Derived workloads schedule tasks and transactions through protected helpers. The manager initializes workloads, waits for task counters to drain, and stops the scheduler when the active map becomes empty.

## State and persistence behavior
Workload state includes atomics for task counts, errors, transaction starts/completions, and in-progress/failure flags. No direct persistence is declared; database writes happen through transaction contexts.

## Dependencies and integration points
Depends on transaction executor, scheduler, `TesterUtil`, threading, atomics, mutexes, and file streams. TOML workload names must match registered factories.

## Risks and test signals
The tenant field is intentionally retained but disabled, which reduces accidental test breakage. Risks include unregistered workload names, self-blocking workloads under-provisioning blocking scheduler threads, and missing control-interface progress acknowledgments.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterWorkload.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/fdb_c_api_tester.cpp -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/fdb_c_api_tester.cpp

## Purpose
Main executable for the FoundationDB C API tester. It parses command-line options, reads a TOML test spec, configures the FDB network, starts the network thread, creates scheduler/transaction/workload components, and returns success based on workload outcomes.

## Important APIs, types, and functions
`parseArgs` and `processArg` use SimpleOpt for cluster file, trace, external clients, temp dir, pipes, API version, retry limit, stats interval, TLS files, and retained client-copy flags. `applyNetworkOptions` maps `TesterOptions` and `TestSpec` flags to FDB network options. `randomizeOptions` chooses concrete thread/database/client counts. `runWorkloads` creates `TransactionExecutorOptions`, workloads via `IWorkloadFactory`, scheduler, executor, and `WorkloadManager`.

## Control flow
`main` parses, randomizes, selects capped API version, applies network options, sets up/runs FDB network on a thread, executes workloads, optionally flushes ASAN deferred cleanup, stops the network, and joins. Workload execution can open control pipes and periodically print stats.

## State and persistence behavior
The executable writes trace logs when enabled, may create temporary files through the executor, and writes workload data to the cluster. Network options are process-global and must be set before `fdb::network::setup`.

## Dependencies and integration points
Integrates `TesterOptions`, `TesterTestSpec`, `TesterScheduler`, `TesterTransactionExecutor`, `TesterWorkload`, FDB C API wrappers, TLS config, external client libraries, and TOML scenario files. It is launched by `run_c_api_tests.py` and shim upgrade scripts.

## Risks and test signals
Option ordering is critical because FDB network options become immutable after setup. Randomized concurrency broadens coverage but complicates reproduction. Signals include exit code, workload stderr summaries, trace files, stats output, and ASAN-specific cleanup behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/fdb_c_api_tester.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/run_c_api_tests.py -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/run_c_api_tests.py

## Purpose
Python runner for C API tester TOML scenarios. It creates a temporary FoundationDB cluster per test, derives TLS/server process settings from TOML, launches the compiled tester, and reports failures with client logs.

## Important APIs, types, and functions
`TestConfig` reads `[server]` settings including TLS, certificate chain lengths, and process-count range. `run_tester` constructs the tester command with cluster file, test file, stats interval, tmp dir, trace logging, external client library, TLS files, and knob overrides. `run_test` wraps `TempCluster`, and `run_tests` iterates either one file or all `.toml` files in a directory.

## Control flow
Argument parsing configures build/test paths and timeout. For each selected TOML file, the script creates a cluster, runs the tester with a timeout, kills it on timeout, checks cluster logs, and increments failure count on any nonzero result.

## State and persistence behavior
Temporary cluster directories and client trace logs are created through `TempCluster`. On failure, trace log contents are dumped unless disabled. No persistent repository files are modified.

## Dependencies and integration points
Depends on `fdb_test_runner.tmp_cluster.TempCluster`, `TLSConfig`, Python `toml`, and the built `fdb_c_api_tester` binary. It is the CI-facing adapter for `apitester/tests`.

## Risks and test signals
The `--knob` loop currently builds `--knob-*` arguments, while the C++ tester expects TOML `[[knobs]]`; mismatches may leave CLI knobs ineffective. Signals include tester exit code, timeout reason, cluster log health, and dumped client traces.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/run_c_api_tests.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCancelTransactionBlocking.toml -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCancelTransactionBlocking.toml

## Purpose
Defines a randomized multi-threaded cancel-transaction scenario using blocking future waits.

## Important APIs, types, and functions
The `[[test]]` section enables `multiThreaded`, `buggify`, and `blockOnFutures`, with randomized FDB threads, databases, client threads, and clients. The workload is `CancelTransaction` with random key/value sizes, `maxKeysPerTransaction`, initial data, operation count, and existing-key read ratio.

## Control flow
The runner randomizes configured ranges, starts a temporary cluster, and the tester exercises cancellation while futures consume scheduler threads by blocking.

## State and persistence behavior
The workload seeds and mutates test key space in FDB. No TLS or special server state is requested.

## Dependencies and integration points
Parsed by `TesterTestSpec.cpp`, executed by `run_c_api_tests.py`, and stresses `BlockingTransactionContext` plus cancel workload implementation.

## Risks and test signals
Blocking mode can deadlock if client threads are insufficient for self-blocking futures. Success is a zero tester exit with workload completion; failures expose cancellation, retry, or scheduler starvation defects.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCancelTransactionBlocking.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCancelTransactionCB.toml -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCancelTransactionCB.toml

## Purpose
Defines the callback-based counterpart to the blocking cancel-transaction test.

## Important APIs, types, and functions
The test enables `multiThreaded` and `buggify` but leaves `blockOnFutures` false, so `AsyncTransactionContext` uses FDB future callbacks. It configures one `CancelTransaction` workload with randomized key/value sizes, initial size, random operation count, and read-existing ratio.

## Control flow
The tester randomizes thread/database/client counts and runs cancel operations through callback continuations. Cancellation callbacks may arrive after transaction cleanup and must be ignored safely.

## State and persistence behavior
Database state is the workload key space populated and modified during the run. No server or TLS table is present.

## Dependencies and integration points
Exercises TOML parsing, async transaction executor callback maps, workload cancellation logic, and multi-version client buggify injection.

## Risks and test signals
Primary risks are callback lifetime races, double completion, and late cancelled futures. Success is normal workload completion under randomized concurrency and buggified client errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCancelTransactionCB.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCancelTransactionDBPerTX.toml -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCancelTransactionDBPerTX.toml

## Purpose
Tests cancel-transaction behavior when every transaction uses a fresh database handle.

## Important APIs, types, and functions
The test enables `databasePerTransaction`, `multiThreaded`, and `buggify`. The workload remains `CancelTransaction` with the standard randomized key/value and operation parameters.

## Control flow
Each transaction calls `DBPerTransactionExecutor::selectDatabase`, increasing database create/destroy pressure while cancel operations run concurrently.

## State and persistence behavior
The FDB cluster stores workload keys; client-side state includes many short-lived database objects and future callbacks. No TLS settings are present.

## Dependencies and integration points
Stresses `DBPerTransactionExecutor`, the FDB C API database lifecycle, and cancellation cleanup paths.

## Risks and test signals
Risks include database handle leaks, delayed cleanup callbacks, and cancellation interacting with database destruction. The signal is a successful tester exit under buggified multi-threaded execution.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCancelTransactionDBPerTX.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCancelTransactionDBPerTX_TLS.toml -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCancelTransactionDBPerTX_TLS.toml

## Purpose
Runs the database-per-transaction cancel workload against a TLS-enabled temporary cluster.

## Important APIs, types, and functions
The test enables `databasePerTransaction`, `multiThreaded`, and `buggify`; `[server]` sets `tls_enabled = true` and `max_num_processes = 1`. The workload is `CancelTransaction` with standard random operation settings.

## Control flow
`run_c_api_tests.py` provisions TLS certificates and passes TLS paths to the tester. The transaction executor repeatedly creates database handles and cancels transactions over TLS.

## State and persistence behavior
Persists workload keys in the TLS cluster and creates temporary TLS material through the test runner.

## Dependencies and integration points
Integrates the TLS branch of `TempCluster`, tester TLS network options, database-per-transaction execution, and cancellation workload.

## Risks and test signals
Combines TLS connection setup cost with database-handle churn, so failures can reveal TLS option ordering, client certificate configuration, cleanup, or timeout issues.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCancelTransactionDBPerTX_TLS.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCancelTransactionWithTimeout.toml -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCancelTransactionWithTimeout.toml

## Purpose
Adds transaction timeouts to the randomized cancel-transaction workload.

## Important APIs, types, and functions
The `CancelTransaction` workload sets `minTxTimeoutMs = 10` and `maxTxTimeoutMs = 10000`, causing `WorkloadBase` to apply `FDB_TR_OPTION_TIMEOUT` to transactions and enable restart-on-timeout behavior.

## Control flow
Transactions may time out while cancellation and buggified errors are being exercised. The transaction executor can recreate/self-conflict transactions when configured for timeout restarts.

## State and persistence behavior
The workload mutates normal test keys. Timeout state is client-side transaction option state and retry history.

## Dependencies and integration points
Stresses `WorkloadBase::doExecute`, `TransactionContextBase::makeSelfConflicting`, `onError`, and cancel workload paths.

## Risks and test signals
Risks include treating expected timeouts as fatal, retrying non-idempotent writes without conflict protection, or leaking pending callbacks after timeout cancellation. Passing runs indicate cancellation remains robust under timeout churn.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCancelTransactionWithTimeout.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCorrectnessBlocking.toml -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCorrectnessBlocking.toml

## Purpose
Runs core API, atomic operation, and watch correctness workloads using blocking future waits.

## Important APIs, types, and functions
The test enables `blockOnFutures`, `multiThreaded`, and `buggify`, with randomized thread/database/client ranges. Workloads are `ApiCorrectness`, `AtomicOpsCorrectness`, and `WatchAndWait`.

## Control flow
The tester adjusts client thread count if blocking waits plus self-blocking watch futures require more lanes. Workloads run concurrently over randomized key/value sizes and operation counts.

## State and persistence behavior
Persists correctness key spaces, atomic-operation keys, and watch keys. No server-specific state is requested.

## Dependencies and integration points
Exercises `BlockingTransactionContext`, workload factory registration, API wrapper methods for reads/writes/ranges/atomic ops/watches, and retry-on-error behavior.

## Risks and test signals
Deadlock, incorrect atomic encodings, watch non-delivery, and blocking wait error handling are the main risks. Zero exit and workload success logs are the primary signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCorrectnessBlocking.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCorrectnessCallbacksOnExtThr.toml -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCorrectnessCallbacksOnExtThr.toml

## Purpose
Validates core API correctness while FDB future callbacks execute on external client threads.

## Important APIs, types, and functions
The test enables `fdbCallbacksOnExternalThreads`, `multiThreaded`, and `buggify`, with the same three correctness workloads: `ApiCorrectness`, `AtomicOpsCorrectness`, and `WatchAndWait`.

## Control flow
`fdb_c_api_tester.cpp` maps the flag to `FDB_NET_OPTION_CALLBACKS_ON_EXTERNAL_THREADS`. The async transaction context must safely receive callbacks from external FDB threads and schedule workload continuations locally.

## State and persistence behavior
Database state is normal correctness workload data. Threading state crosses the FDB external client callback boundary.

## Dependencies and integration points
Touches multi-version client callback options, `AsyncTransactionContext::futureReadyCallback`, scheduler handoff, and workload invariants.

## Risks and test signals
Race conditions are more likely because callbacks can arrive on threads not owned by the local scheduler. Passing tests signal thread-safe callback maps, state transitions, and scheduler lifetime handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCorrectnessCallbacksOnExtThr.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCorrectnessDBPerTX.toml -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCorrectnessDBPerTX.toml

## Purpose
Runs the API, atomic, and watch correctness workloads while creating a separate database handle for each transaction.

## Important APIs, types, and functions
The test enables `databasePerTransaction`, `multiThreaded`, and `buggify`. Workloads are `ApiCorrectness`, `AtomicOpsCorrectness`, and `WatchAndWait` with standard randomized parameters.

## Control flow
Every workload transaction selects a fresh `fdb::Database`, increasing churn around database creation, transaction creation, commit, cancellation, and destruction.

## State and persistence behavior
FDB stores workload keys. Client persistence is limited to short-lived database wrappers and transaction futures.

## Dependencies and integration points
Stresses `DBPerTransactionExecutor`, wrapper RAII in `fdb_api.hpp`, executor retry behavior, and the correctness workloads.

## Risks and test signals
Risks include database lifetime bugs, excessive creation failures, and callbacks referencing destroyed transactions. Passing under buggify is a strong lifecycle signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCorrectnessDBPerTX.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCorrectnessDisableBypass.toml -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCorrectnessDisableBypass.toml

## Purpose
Runs single-threaded API correctness with multi-version client bypass disabled.

## Important APIs, types, and functions
The test sets `multiThreaded = false`, `disableClientBypass = true`, `minClients = 1`, `maxClients = 3`, and database range 1 to 3. Workloads are `ApiCorrectness`, `AtomicOpsCorrectness`, and `WatchAndWait`.

## Control flow
`fdb_c_api_tester.cpp` applies `FDB_NET_OPTION_DISABLE_CLIENT_BYPASS` for supported API versions, forcing requests through the multi-version client path even without external clients.

## State and persistence behavior
Normal correctness workload keys are persisted. The important state is process-global client bypass configuration before network setup.

## Dependencies and integration points
Tests network option parsing/application, single-threaded scheduler behavior, and correctness workloads without buggify.

## Risks and test signals
Changing API version gates or bypass behavior can invalidate the test. Passing indicates the non-bypass client path preserves API correctness.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCorrectnessDisableBypass.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCorrectnessMultiThr.toml -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCorrectnessMultiThr.toml

## Purpose
Default broad C API correctness scenario for multi-threaded, buggified client execution.

## Important APIs, types, and functions
Enables `multiThreaded` and `buggify`, randomizes FDB/client/database/client counts, and runs `ApiCorrectness`, `AtomicOpsCorrectness`, and `WatchAndWait`.

## Control flow
The runner starts a temporary cluster, the tester randomizes ranges, configures FDB client threads per version, enables client buggify, and executes all workloads concurrently.

## State and persistence behavior
Persists random correctness data and watch keys in the cluster. No TLS or special cluster settings are present.

## Dependencies and integration points
This is used by shim tests as the default workload and covers the core API tester stack end to end.

## Risks and test signals
Because it is broad and randomized, it catches integration regressions across wrappers, scheduler, executor, and workloads but may need reruns for reproducibility. Success is a clean tester exit with no workload failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCorrectnessMultiThr.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCorrectnessSingleThr.toml -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCorrectnessSingleThr.toml

## Purpose
Runs the core correctness workloads in non-multithreaded mode with a small randomized client count.

## Important APIs, types, and functions
Sets `multiThreaded = false`, `minClients = 1`, `maxClients = 3`, and includes `ApiCorrectness`, `AtomicOpsCorrectness`, and `WatchAndWait`.

## Control flow
The tester avoids multi-threaded FDB client configuration and executes workloads through the normal scheduler/executor path.

## State and persistence behavior
Only normal workload data is persisted in the cluster. Client state is intentionally simpler than the multi-threaded cases.

## Dependencies and integration points
Validates the baseline API tester path, workload factory creation, and correctness operations without buggify or client-thread randomization.

## Risks and test signals
This catches regressions hidden by concurrency while offering a simpler reproduction path. Watch workloads still require enough scheduler progress to avoid self-blocking issues.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCorrectnessSingleThr.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCorrectnessTLS.toml -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCorrectnessTLS.toml

## Purpose
Runs the core multi-threaded buggified API correctness suite against a TLS-enabled cluster.

## Important APIs, types, and functions
Enables `multiThreaded`, `buggify`, randomized thread/database/client ranges, and `[server] tls_enabled = true` with one process. Workloads are `ApiCorrectness`, `AtomicOpsCorrectness`, and `WatchAndWait`.

## Control flow
`run_c_api_tests.py` creates TLS material and passes CA/key/cert paths. The tester applies TLS network options before setup and then executes the standard correctness workload mix.

## State and persistence behavior
Persists workload data over TLS connections. Temporary certificate files are owned by the cluster runner.

## Dependencies and integration points
Covers TLS option application, TempCluster TLS setup, FDB client connectivity, and all core correctness workload operations.

## Risks and test signals
Failures may indicate certificate path issues, TLS/plaintext mismatch, option ordering problems, or correctness regressions exposed by TLS timing.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiCorrectnessTLS.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiRunLoopProfiler.toml -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiRunLoopProfiler.toml

## Purpose
Exercises the C API tester with FDB run-loop profiling enabled under a high-concurrency correctness workload.

## Important APIs, types, and functions
Sets `runLoopProfiler = true`, fixed 8 FDB threads, 8 databases, 16 client threads, 32 clients, and one `ApiCorrectness` workload. The `[[knobs]]` section sets `run_loop_profiling_interval=0.001`.

## Control flow
The tester applies `FDB_NET_OPTION_ENABLE_RUN_LOOP_PROFILING` and the knob before network setup, then runs the workload with large concurrency.

## State and persistence behavior
Persists normal API correctness data and emits profiler/trace-related client state through FDB logging mechanisms when enabled.

## Dependencies and integration points
Connects TOML knob parsing, network option application, run-loop profiling internals, and the API correctness workload.

## Risks and test signals
The TOML formatting has a tight `[[knobs]]` entry, so parser compatibility matters. Signals are successful workload completion and absence of profiler-induced client instability.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiRunLoopProfiler.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiTamperClusterFile.toml -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiTamperClusterFile.toml

## Purpose
Tests client recovery when the cluster file used by the tester changes from unreachable to invalid to valid during execution.

## Important APIs, types, and functions
Sets `tamperClusterFile = true`, `multiThreaded = true`, `buggify = true`, and moderate randomized thread/database/client ranges. The workload is `ApiCorrectness`.

## Control flow
`TransactionExecutorBase` writes a synthetic cluster file, later overwrites it with an invalid connection string, and finally copies the real cluster file while transactions execute and retry.

## State and persistence behavior
Creates and mutates a temporary cluster file under `tmpDir`; workload data persists once connectivity succeeds.

## Dependencies and integration points
Exercises cluster-file monitoring/reload behavior, database-create error injection paths, transaction retry, and API correctness.

## Risks and test signals
Risks include permanent initialization failure, retry storms, and mishandling invalid connection strings. Passing shows the client can tolerate cluster-file tampering and eventual recovery.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiTamperClusterFile.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiTamperClusterFileTLS.toml -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiTamperClusterFileTLS.toml

## Purpose
Runs the cluster-file tampering scenario against a TLS-enabled temporary cluster.

## Important APIs, types, and functions
Combines `tamperClusterFile = true`, `multiThreaded`, `buggify`, randomized moderate concurrency, `[server] tls_enabled = true`, and one `ApiCorrectness` workload.

## Control flow
The runner supplies TLS files, and the transaction executor mutates the temporary cluster file before restoring valid TLS cluster-file contents.

## State and persistence behavior
Persists workload data after recovery and mutates temporary cluster-file state. TLS certificate material is runner-managed.

## Dependencies and integration points
Stresses TLS network options, cluster-file reload/recovery, database creation, and retry behavior together.

## Risks and test signals
Combining TLS with invalid cluster-file windows can expose longer connection delays and option/config mismatch. Success is recovery to normal workload completion without fatal client errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/CApiTamperClusterFileTLS.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/upgrade/MixedApiWorkloadMultiThr.toml -->
# sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/upgrade/MixedApiWorkloadMultiThr.toml

## Purpose
Defines a long-running mixed workload for upgrade tests with a multi-threaded, buggified client.

## Important APIs, types, and functions
Sets `databasePerTransaction = false`, randomized FDB/client/database/client ranges, and four `runUntilStop` workloads: `ApiCorrectness`, `CancelTransaction`, `AtomicOpsCorrectness`, and `WatchAndWait`.

## Control flow
Unlike bounded correctness TOMLs, each workload runs until an external controller sends stop through control pipes. This supports cluster upgrade tests that need ongoing client traffic across version transitions.

## State and persistence behavior
Continuously mutates correctness, cancel, atomic, and watch key spaces. The controlling test observes progress rather than a fixed operation count.

## Dependencies and integration points
Requires workload control support, upgrade harness pipes, transaction executor stability across cluster version changes, and multi-version client compatibility.

## Risks and test signals
Risks include no-progress hangs after upgrade, control-pipe failures, and workload-specific retry bugs. Signals include `CHECK_OK`, `DONE`, continued progress during upgrades, and clean stop.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/apitester/tests/upgrade/MixedApiWorkloadMultiThr.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/client_config_tester.cpp -->
# sources/storage-engines/foundationdb/bindings/c/test/client_config_tester.cpp

## Purpose
Standalone executable for validating FoundationDB client configuration combinations. It applies network options, opens a database, runs a simple transaction, optionally prints client status JSON, and exits according to an expected error code.

## Important APIs, types, and functions
`TesterOptions` stores API version, cluster file, external client library/dir, transaction timeout, trace/tmp settings, expected error, status flag, and arbitrary network options. `extractPrefixedArgument` parses `--network-option-*`. `applyNetworkOptions` maps option names to generated `FDBNetworkOptions::optionInfo`. `testTransaction` performs get/set/commit with timeout and `onError` retry handling. `printDatabaseStatus` emits `getClientStatus`.

## Control flow
`main` parses arguments, selects API version, applies options, sets up/runs the network thread, executes the transaction, stops the network, then compares the final code against `expectedError`. Some exits use `_exit`/`TerminateProcess` to avoid extra shutdown effects.

## State and persistence behavior
Writes one key/value transaction on success, may create trace files, and reads client status from the database. Network configuration is process-global.

## Dependencies and integration points
Uses `test/fdb_api.hpp`, generated option metadata, SimpleOpt, and platform process-exit APIs. It is driven by `fdb_c_client_config_tests.py`.

## Risks and test signals
Expected-error handling is central: tests can pass by observing the configured failure. Risks include unknown network options being logged but still dereferenced, timeout flakiness, and status JSON schema drift.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/client_config_tester.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/client_memory_test.cpp -->
# sources/storage-engines/foundationdb/bindings/c/test/client_memory_test.cpp

## Purpose
Small stress utility for observing client allocator memory return behavior after heavy transaction-side allocation.

## Important APIs, types, and functions
Uses raw C API setup/run/stop plus a helper `fdb_open_database`. Worker threads create `fdb::Transaction` wrappers and perform 10,000 `set` calls with increasingly large zero-filled values, then cancel.

## Control flow
The program expects a cluster file, selects the latest API version, starts the network thread, enables JSON tracing, opens a database, runs 64 allocation-heavy threads, joins them, destroys the database, sleeps 10 seconds for external memory observation, then stops the network.

## State and persistence behavior
Transactions are cancelled, so database mutations are not committed. The relevant state is process memory and trace output; an external monitor is expected to inspect RSS during the sleep.

## Dependencies and integration points
Includes `foundationdb/fdb_c.h` and `unit/fdb_api.hpp`, plus standard threading/vector support. It is likely used by targeted memory/allocator tests rather than TOML workloads.

## Risks and test signals
The program prints usage but does not exit early on wrong argc, so missing arguments can still crash. Test signal is external memory dropping after database destruction and transaction cancellation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/client_memory_test.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/fdb_api.hpp -->
# sources/storage-engines/foundationdb/bindings/c/test/fdb_api.hpp

## Purpose
C++ RAII and typed-future wrapper around the FoundationDB C API for tests. It gives test code safer ownership, typed result extraction, string/byte conversions, and convenience methods for network/database/transaction operations.

## Important APIs, types, and functions
Defines byte aliases, `Error`, future result traits in `future_var`, `Future`, `TypedFuture`, `Result`, `Transaction`, `Database`, `IDatabaseOps`, key selector helpers, network setup/option wrappers, and API version selection helpers. Native C API symbols are isolated under `fdb::native`.

## Control flow
Network methods wrap C calls and throw on error in checked variants. `Future::then` allocates a lambda callback and destroys it after invocation. `Transaction` methods return typed futures or call C mutation APIs. `Database` creates/destroys native handles through shared pointers.

## State and persistence behavior
RAII wrappers own native `FDBFuture`, `FDBTransaction`, `FDBDatabase`, and `FDBResult` handles. Transaction methods persist data only when committed. Atomic load/store helpers allow handles to be swapped safely across executor state transitions.

## Dependencies and integration points
Includes generated FDB options and `foundationdb/fdb_c.h`. Used by the API tester, client-config tester, Mako, shim tests, and memory tests.

## Risks and test signals
Callback allocation must be freed exactly once, result references are only valid while futures/results live, and `intSize` overflow checking is disabled by default. Compile and runtime tests across C API workloads validate wrapper signature compatibility and lifetime behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/fdb_api.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/fdb_c90_test.c -->
# sources/storage-engines/foundationdb/bindings/c/test/fdb_c90_test.c

## Purpose
Minimal C compilation test proving the FoundationDB C header is usable from a C90-style translation unit with a fixed API version.

## Important APIs, types, and functions
Defines `FDB_API_VERSION 800`, includes `foundationdb/fdb_c.h`, and calls `fdb_select_api_version`.

## Control flow
`main` ignores arguments, selects the API version, and exits zero without starting the network or creating a database.

## State and persistence behavior
No persistent state or FDB cluster state is touched.

## Dependencies and integration points
Depends only on the public C API header and C compiler compatibility. It protects build/test compatibility for non-C++ consumers.

## Risks and test signals
Any C++-only constructs or header incompatibility would fail compilation. Runtime behavior is intentionally trivial.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/fdb_c90_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/fdb_c_client_config_tests.py -->
# sources/storage-engines/foundationdb/bindings/c/test/fdb_c_client_config_tests.py

## Purpose
Python unittest suite for FoundationDB C client configuration, multi-version client selection, TLS/plaintext behavior, upgrade waiting, incompatible clients, and tracing.

## Important APIs, types, and functions
`TestCluster` extends `LocalCluster`, manages temp dirs, binary versions, TLS certificates, and upgrades. `ClientConfigTest` builds command lines for `client_config_tester`, creates external client libraries/directories, invalid cluster files, and parses status JSON. `ClientConfigTests`, `ClientConfigPrevVersionTests`, `ClientConfigSeparateCluster`, and `ClientTracingTests` cover scenario groups.

## Control flow
The script downloads previous-version binaries, starts clusters in class or per-test fixtures, executes `client_config_tester` with expected errors, and asserts status fields, available clients, selected protocol, health, trace file count, and trace event fields.

## State and persistence behavior
Creates temp cluster directories, copied client libraries, logs, tmp dirs, trace files, invalid cluster files, and TLS material. Cluster upgrades stop/restart binaries while preserving cluster files and database state.

## Dependencies and integration points
Depends on `FdbBinaryDownloader`, `LocalCluster`, `PortProvider`, `TLSConfig`, `client_config_tester`, generated current/previous version constants, and Python unittest/subprocess/json.

## Risks and test signals
There are duplicate method names in the class, so later definitions override earlier intended tests. Timing-sensitive upgrade and timeout tests may be flaky. Strong signals include exact initialization states, health booleans, current-client matching, expected error codes, and trace filename/event patterns.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/fdb_c_client_config_tests.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/fdb_c_shim_tests.py -->
# sources/storage-engines/foundationdb/bindings/c/test/fdb_c_shim_tests.py

## Purpose
Tests FoundationDB C shim and multi-version client behavior across current and previous binary/client-library versions.

## Important APIs, types, and functions
`TestEnv` extends `LocalCluster`, downloads versioned binaries, copies `libfdb_c` as an external library, and sets library paths. `FdbCShimTests` builds API tester args, runs C API workloads, C unit tests, and shim library tester scenarios. Helper functions convert release versions to API versions.

## Control flow
The suite runs the default C API workload and unit tests for the current version, then exercises local-library discovery via `LD_LIBRARY_PATH`, explicit API calls, environment variables, external-library mode, invalid paths, older API versions, and previous-release compatibility.

## State and persistence behavior
Creates temp cluster directories and copied client libraries, starts local clusters, and cleans them after each environment. Workloads persist normal test data in those clusters.

## Dependencies and integration points
Depends on `FdbBinaryDownloader`, `LocalCluster`, shim/unit/api tester binaries, previous release constants, environment variables such as `FDB_LOCAL_CLIENT_LIBRARY_PATH`, and `CApiCorrectnessMultiThr.toml`.

## Risks and test signals
Expected abort codes for invalid library paths are platform-sensitive. Previous-version downloads can fail externally. Test signals are exact process return codes for compatible, incompatible, invalid-path, and missing-function cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/fdb_c_shim_tests.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/admin_server.cpp -->
# sources/storage-engines/foundationdb/bindings/c/test/mako/admin_server.cpp

## Purpose
Implements Mako's forked admin server process, used to isolate administrative FDB tasks when process-global TLS options make in-process reconfiguration unsafe.

## Important APIs, types, and functions
`AdminServer::start` forks, rebinds the thread-local logger in the child, applies global options, sets up the FDB network, starts a network thread, and handles serialized IPC requests. `AdminServer::~AdminServer` sends `StopRequest` and waits for the child. `getOrCreateDatabase` caches database handles by cluster file, though current request handling only supports ping/stop.

## Control flow
Parent returns after fork with `server_pid`. Child enters a loop reading `Request` variants from `pipe_to_server`, dispatches with `boost::apply_visitor`, returns responses, and exits on stop or fatal exception. An `ExitGuard` stops the network thread on shutdown.

## State and persistence behavior
Maintains child process state, pipes, optional setup error, database cache, and network thread. It does not currently persist database mutations.

## Dependencies and integration points
Uses Boost process pipes, Boost serialization/variant, `fdb_api.hpp`, Mako arguments/logger/time/utils, POSIX `fork`/`waitpid`, and RapidJSON includes.

## Risks and test signals
Forking after complex process setup can be fragile. Pipe serialization failures or setup errors return error responses. Destructor wait status and ping/stop responses are key lifecycle signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/admin_server.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/admin_server.hpp -->
# sources/storage-engines/foundationdb/bindings/c/test/mako/admin_server.hpp

## Purpose
Declares Mako's admin IPC protocol and `AdminServer` wrapper for a forked administrative subprocess.

## Important APIs, types, and functions
`DefaultResponse` carries optional error text. `PingRequest` and `StopRequest` define response types and serialization. `Request` is a Boost variant of supported requests. `AdminServer` owns arguments, child pid, bidirectional pstreams, `sendObject`, `receiveObject`, `sendResponse`, and typed `send`.

## Control flow
Construction initializes pipes and calls `start`; `send` serializes a variant request and waits for the typed response. Copy and move are disabled to avoid duplicating process/pipe ownership.

## State and persistence behavior
State is child process identity and pipes. No file or database persistence is declared in the header.

## Dependencies and integration points
Depends on Boost process/serialization, `fdb_api.hpp`, `logger.hpp`, and `mako.hpp`. It is used by Mako benchmark code needing isolated global option setup.

## Risks and test signals
The protocol is small; adding requests requires variant, serialization, and child dispatch updates. Incorrect parent/child use is guarded by assertions on `server_pid` and logger process kind.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/admin_server.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/async.cpp -->
# sources/storage-engines/foundationdb/bindings/c/test/mako/async.cpp

## Purpose
Implements asynchronous resumable state machines for Mako benchmark population and workload execution without C++ coroutines.

## Important APIs, types, and functions
`ResumableStateForPopulate::runOneTick` inserts generated keys/values, commits every configured count, retries through `onError`, and records latency/statistics. `ResumableStateForRunWorkload::runOneTick` drives operation steps from `opTable`, handles immediate versus future-returning steps, records per-step/op/commit/transaction stats, and retries errors through `tx.onError`. `onTransactionSuccess`, `onIterationEnd`, `updateErrorStats`, and `isExpectedError` manage iteration lifecycle.

## Control flow
Both state machines post themselves back to a Boost.Asio `io_context` and capture `shared_from_this` in callbacks to preserve lifetime. Immediate operations loop locally to reduce context switches; blocking operations register continuations.

## State and persistence behavior
Population persists generated records. Workload execution mutates FDB data according to selected operation mix. State includes transaction handles, keys/values, iterators, latency stopwatches, counters, retry decisions, and stop signals.

## Dependencies and integration points
Depends on Mako operations, stats, time, utils, logger, `future.hpp`, Boost.Asio, and `fdb_api.hpp`.

## Risks and test signals
Risks include callback lifetime bugs, stats skew, retry loops, expected timeout handling, and incorrect transaction reset/commit boundaries. Signals are operation/error/conflict/timeout counts and latency sketches emitted by Mako.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/async.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/async.hpp -->
# sources/storage-engines/foundationdb/bindings/c/test/mako/async.hpp

## Purpose
Declares heap-resident resumable execution state for Mako asynchronous population and benchmark workloads.

## Important APIs, types, and functions
`ResumableStateForPopulate` stores logger, database/transaction, `io_context`, arguments, stats, stop counter, key range/checkpoint, reusable key/value buffers, and stopwatches. `ResumableStateForRunWorkload` stores operation iterator, workload buffers, transaction state, counters, stop signal, and latency watches. Both expose `runOneTick`, `postNextTick`, and `signalEnd`.

## Control flow
Instances are managed by `shared_ptr` aliases and inherit `enable_shared_from_this` so callbacks can safely resume them.

## State and persistence behavior
The structs own transient benchmark execution state. Database persistence is produced by their transaction operations, not by the declarations themselves.

## Dependencies and integration points
Depends on Boost.Asio, Mako `Arguments`, `WorkflowStatistics`, shared memory signal definitions, `future.hpp`, logger, and time helpers.

## Risks and test signals
Because state is reused across callbacks, every field must be reset at transaction/iteration boundaries. Stop counters and signals are the main completion integration points with worker orchestration.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/async.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/ddsketch.hpp -->
# sources/storage-engines/foundationdb/bindings/c/test/mako/ddsketch.hpp

## Purpose
Header-only DDSketch implementations for approximate latency/value distributions in Mako benchmark statistics.

## Important APIs, types, and functions
`fastLogger::fastlog` and `reverseLog` approximate logarithm mappings. `DDSketchBase` tracks buckets, zero count, population, min/max, sum, mean, median, percentile, clear, and merge. `DDSketch<T>` uses fast log for floating values. `DDSketchSlow<T>` uses standard `log`/`pow`. `DDSketchFastUnsigned` provides a fixed-accuracy unsigned integer sketch.

## Control flow
`addSample` routes near-zero samples to a zero counter or maps positive values to buckets. `percentile` scans buckets upward for lower percentiles and downward for upper percentiles. `mergeWith` combines compatible sketches.

## State and persistence behavior
All state is in-memory aggregate statistics: bucket counts, population, sum, min, and max. No serialization is implemented here.

## Dependencies and integration points
Uses standard math, vectors, assertions, endian assumptions, and Mako stats consumers.

## Risks and test signals
Inputs must be non-negative and within supported range; bucket indexes are assertion-guarded. Accuracy depends on mapping constants and endian/compiler intrinsics. Signals are percentile/mean outputs and assertion failures under invalid samples.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/ddsketch.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/future.hpp -->
# sources/storage-engines/foundationdb/bindings/c/test/mako/future.hpp

## Purpose
Shared Mako helpers for waiting on FDB futures and translating success, retry, and abort decisions.

## Important APIs, types, and functions
`FutureRC` enumerates `OK`, `RETRY`, and `ABORT`. `LogContext` and `NoLog` control logging. `waitFuture` blocks and reports block errors. `handleForOnError` evaluates `tx.onError` results and resets transactions on unretryable errors. `waitAndHandleError` waits for an operation future, logs expected/unexpected errors, calls `tx.onError`, and returns a retry decision.

## Control flow
Helpers first block for readiness, then inspect `f.error()`. Successful operation futures return `OK`; retryable/errors flow into `onError`; failed `onError` returns `ABORT`; successful `onError` returns `RETRY`.

## State and persistence behavior
No persistent state is owned. Helpers may reset a transaction after aborting, affecting caller transaction state.

## Dependencies and integration points
Depends on `fdb_api.hpp`, Mako `logger.hpp`, and `force_inline` macro. Used by synchronous and asynchronous Mako operation loops.

## Risks and test signals
Assertions assume `blockUntilReady` errors are not retryable. Timeout logging is downgraded only when expected. Incorrect classification changes benchmark retry/error counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/future.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/limit.hpp -->
# sources/storage-engines/foundationdb/bindings/c/test/mako/limit.hpp

## Purpose
Small portability header that exposes platform path length limits for Mako code.

## Important APIs, types, and functions
Includes `<linux/limits.h>` on Linux, `<sys/syslimits.h>` on Apple platforms, and `<limits.h>` elsewhere.

## Control flow
There is no runtime control flow; preprocessor selection happens at compile time.

## State and persistence behavior
No state or persistence behavior.

## Dependencies and integration points
Used by Mako sources that need `PATH_MAX` or related constants while remaining portable across supported platforms.

## Risks and test signals
Unsupported or unusual platforms fall back to `<limits.h>`, which may lack expected constants. Compile failures are the primary signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/limit.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/logger.hpp -->
# sources/storage-engines/foundationdb/bindings/c/test/mako/logger.hpp

## Purpose
Defines Mako's lightweight formatted logger with process/thread-aware prefixes and verbosity filtering.

## Important APIs, types, and functions
Verbosity constants range from `VERBOSE_NONE` to `VERBOSE_DEBUG`. Process kind aliases select main, stats, worker, and admin prefixes. `Logger` stores process kind, verbosity, process id, and thread id. Methods include `printWithLogLevel`, `error`, `info`, `warn`, `debug`, `imm`, `setVerbosity`, and `isFor`.

## Control flow
Each log call checks verbosity, formats a prefix into an inline buffer, formats the message with `fmt`, and writes errors/immediate output to stderr or other levels to stdout.

## State and persistence behavior
Logger state is per object and often thread-local in Mako. It does not persist logs to files itself; output goes to process streams.

## Dependencies and integration points
Depends on `fmt`, `process.hpp`, assertions, and standard I/O. Used across Mako workers, stats, admin server, and async execution.

## Risks and test signals
Prefix correctness matters for multi-process benchmark diagnostics. Format-string compile checking helps, while verbosity misconfiguration can hide expected-warning context or flood output.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/logger.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/macro.hpp -->
# sources/storage-engines/foundationdb/bindings/c/test/mako/macro.hpp

## Purpose
Provides a portable `force_inline` macro for performance-sensitive Mako helper functions.

## Important APIs, types, and functions
Defines `force_inline` as `inline __attribute__((__always_inline__))` for GNU-compatible compilers and `__forceinline` for MSVC.

## Control flow
Compile-time preprocessor branching selects the compiler-specific inline directive.

## State and persistence behavior
No runtime state or persistence.

## Dependencies and integration points
Included by Mako headers such as `future.hpp` to encourage aggressive inlining in hot error/future handling paths.

## Risks and test signals
Unsupported compilers fail with `#error Missing force inline`. Over-forcing inline can affect debug builds or code size, but failures are compile-time obvious.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/c/test/mako/macro.hpp -->
