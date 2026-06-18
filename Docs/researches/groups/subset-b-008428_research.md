# subset-b-008428 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/ThrottleCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/ThrottleCommand.cpp

## Purpose

`ThrottleCommand.cpp` implements the `fdbcli throttle` command family for viewing and controlling transaction tag throttles. It covers manual tag throttling, unthrottling by filter, automatic throttling enablement, list output, completion suggestions, and inline command hints. The implementation is intentionally thin over `ThrottleApi`, so the file's main local responsibilities are CLI grammar, argument validation, human-readable output, and registering command metadata.

## Important APIs, Types, and Functions

- `throttleCommandActor(Reference<IDatabase>, std::vector<StringRef>)` is the command actor. It handles `list`, `on tag`, `off`, `enable auto`, and `disable auto`.
- `ThrottleApi::getThrottledTags`, `getRecommendedTags`, `throttleTags`, `unthrottleTags`, `unthrottleAll`, and `enableAuto` provide the persistent system-key operations.
- `TagThrottleInfo`, `TagSet`, `TagThrottleType`, `TagThrottledReason`, and `TransactionPriority` are the key domain types.
- `parseDuration`, `transactionPriorityToString`, `tokencmp`, `printUsage`, and `printable` are shared CLI helpers.
- `throttleGenerator` and `throttleHintGenerator` provide shell completion and progressive hints.
- The static `CommandFactory throttleFactory` publishes the public help text and registers the command name.

## Control Flow

The actor first rejects a bare `throttle` by printing usage. `list` validates an optional mode (`throttled`, `recommended`, or `all`) and optional integer limit, fetches matching records through `ThrottleApi`, then prints only unexpired entries. `on tag <TAG>` parses optional TPS rate, duration, and priority, validates nonnegative rate and nonzero duration, builds a single-tag `TagSet`, and persists a manual throttle. `off` scans a flexible set of filters: throttle type, priority, and optional `tag <TAG>`. If no tag is supplied it calls `unthrottleAll`; otherwise it calls `unthrottleTags`. `enable auto` and `disable auto` validate the fixed grammar and toggle the automatic throttling flag.

## State and Persistence Behavior

This command persists all changes through `ThrottleApi`, which writes FoundationDB system metadata for throttled tags and auto-throttling enablement. `throttle list` reads current throttle metadata and filters against `now()` so expired throttles do not appear in the table. Manual throttles are written with `TagThrottleType::MANUAL`; `off all` clears both manual and auto throttles by passing an empty `Optional<TagThrottleType>`.

## Dependencies and Integration Points

The file integrates with `fdbcli.h` command registration, `IClientApi` database handles, tag throttle system data, transaction priority formatting, Flow coroutines, and CLI completion infrastructure. It is dispatched from `fdbcli.cpp` when the first token is `throttle`.

## Risks and Edge Cases

The `list` limit parser accepts `strtol` output without checking negative values or overflow. A negative limit would be passed to `ThrottleApi` and may have surprising behavior depending on downstream validation. The parser uses `tokens.size()` in some checks that are redundant after earlier validation but harmless. Output is exact-text sensitive because integration tests compare CLI strings. Another subtlety is that `list all` can print "There are no throttled tags" even when only recommended tags were requested by a different branch; the wording is selected from `reportThrottled`.

## Test Signals

`fdbcli_tests.py` contains a disabled `throttle()` integration test that checks empty list output and verifies `throttle enable auto` / `disable auto` by reading the system key `\xff\x02/throttledTags/autoThrottlingEnabled`. Useful additional coverage would exercise manual `on tag`, duration parsing, priority-specific unthrottle, `list all`, invalid limit, negative rate, and completion hints.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/ThrottleCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/TriggerDDTeamInfoLogCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/TriggerDDTeamInfoLogCommand.cpp

## Purpose

This file implements the `triggerddteaminfolog` command. The command writes a fresh value to the special system key that the data distributor watches to trigger detailed team information logging.

## Important APIs, Types, and Functions

- `triggerddteaminfologCommandActor(Reference<IDatabase>)` creates a transaction and commits the trigger write.
- `triggerDDTeamInfoPrintKey` is the system key used as the signal.
- `FDBTransactionOptions::ACCESS_SYSTEM_KEYS` and `PRIORITY_SYSTEM_IMMEDIATE` allow writing the system key with high priority.
- `deterministicRandom()->randomUniqueID().toString()` provides a changing value so repeated command invocations produce new writes.
- `CommandFactory triggerddteaminfologFactory` registers help and usage text.

## Control Flow

The actor creates one transaction and retries in a `while (true)` loop. Each attempt sets system-key access and system-immediate priority, generates a unique string, writes it to `triggerDDTeamInfoPrintKey`, commits via `safeThreadFutureToFuture`, prints success, and returns true. Retriable errors go through `tr->onError(err)` before the loop tries again.

## State and Persistence Behavior

The only persistent mutation is the system-key value used as a trigger. The value content is not semantically important beyond changing the key, but using a unique ID avoids idempotent rewrites being invisible to watchers or log logic. The transaction is retried using normal FoundationDB retry semantics.

## Dependencies and Integration Points

The command relies on `SystemData.h` for the trigger key, the client API transaction abstraction, Flow actors, and thread-future conversion. `fdbcli.cpp` dispatches it directly when the token is `triggerddteaminfolog`.

## Risks and Edge Cases

The command takes no arguments, but the actor itself has no token validation; dispatch relies on the command being invoked by name. If extra arguments reach this actor, they are ignored because the signature has no token vector. Any persistent failure from transaction retry semantics will propagate as an error to the main CLI loop.

## Test Signals

`fdbcli_tests.py` includes `triggerddteaminfolog()` and asserts the exact output `Triggered team info logging in data distribution.`. Deeper verification would require checking data distributor logs or a system-key watcher rather than only CLI output.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/TriggerDDTeamInfoLogCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/TssqCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/TssqCommand.cpp

## Purpose

`TssqCommand.cpp` implements `fdbcli tssq`, a command for listing, starting, and stopping quarantine mode for Testing Storage Server (TSS) processes. It is operational tooling for cases where a TSS has incorrect data or needs manual investigation.

## Important APIs, Types, and Functions

- `tssqCommandActor(Reference<IDatabase>, std::vector<StringRef>)` validates grammar and dispatches subcommands.
- `tssQuarantineList` reads `tssQuarantineKeys` and prints quarantined TSS IDs.
- `tssQuarantine` validates a target storage ID, toggles its quarantine key, and updates the TSS mapping.
- `serverListKeyFor`, `decodeServerListValue`, `StorageServerInterface::isTss`, `tssQuarantineKeyFor`, `decodeTssQuarantineKey`, `tssMappingKeys`, and `KeyBackedMap<UID, UID>` are the relevant metadata APIs.
- `CommandFactory tssqFactory` registers the command.

## Control Flow

`tssq list` calls `tssQuarantineList`, which reads the full quarantine key range with system-key access and asserts it is not paginated. `tssq start <StorageUID>` and `tssq stop <StorageUID>` require a 32-hex-character UID. `tssQuarantine` first checks that the UID exists in the server list, then decodes the `StorageServerInterface` and rejects non-TSS storage IDs. It then checks the current quarantine key to avoid duplicate start or invalid stop. Starting sets the quarantine key and removes the TSS pair mapping; stopping clears the quarantine key. The transaction commits and the command prints success.

## State and Persistence Behavior

The command writes system metadata under the TSS quarantine keyspace. Starting quarantine also erases the TSS's pair mapping from `tssMappingKeys`, which disconnects it from the active TSS pairing metadata. Stopping only clears quarantine; the command text notes that removing quarantine can destroy the TSS process, but that operational effect happens elsewhere in the cluster.

## Dependencies and Integration Points

This file integrates with server-list metadata, TSS mapping metadata, key-backed maps, system-key transactions, and fdbcli dispatch. All database operations use `ACCESS_SYSTEM_KEYS` and `PRIORITY_SYSTEM_IMMEDIATE`.

## Risks and Edge Cases

The list path uses `CLIENT_KNOBS->TOO_MANY` and asserts no pagination, which assumes quarantine cardinality stays small. `std::all_of(..., &isxdigit)` passes raw chars to `isxdigit`; this is conventional here but can be unsafe for negative signed chars outside ASCII. `tssQuarantine` relies on `ssi.tssPairID` being present for TSS interfaces when erasing the mapping.

## Test Signals

The listed integration test file does not include an active `tssq` test. Good signals would cover listing empty/non-empty quarantine, rejecting malformed UIDs, rejecting non-TSS storage IDs, duplicate start/stop behavior, and confirming the quarantine key and TSS mapping mutation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/TssqCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/Util.cpp -->
# sources/storage-engines/foundationdb/fdbcli/Util.cpp

## Purpose

`Util.cpp` provides shared fdbcli helpers for token comparison, command usage lookup, special-key error extraction, worker and storage-server discovery, bulk job ID validation, bulk owner display, and bulk load/dump progress analysis formatting.

## Important APIs, Types, and Functions

- `tokencmp`, `printUsage`, and `printLongDesc` are foundational command helpers used across command files.
- `getSpecialKeysFailureErrorMessage` reads `errorMsgSpecialKey`, parses strict JSON, validates it against `JSONSchemas::managementApiErrorSchema`, and returns its `message`.
- `addInterfacesFromKVs` and `getWorkerInterfaces` decode `ClientWorkerInterface` entries from the special worker interface keyspace and optionally request verification.
- `getWorkers` reads process class and worker-list metadata, merges process class overrides, filters tester processes, and returns `ProcessData`.
- `getStorageServerInterfaces` reads the server list and maps storage-server addresses to `StorageServerInterface`.
- `validateBulkJobId`, `getBulkOwnerSuffix`, and the `print*` helpers support bulk dump/load commands.
- `BulkHealthMetrics::analyze`, `BulkErrorAnalysis::analyze`, and `BulkOptimizationRecommendations::generate` implement lightweight CLI diagnostics.

## Control Flow

Most database helpers create or receive a transaction, set system-key read or write options, issue one or more range reads, decode values, and retry through `onError`. `getWorkers` concurrently fetches process class and worker-list ranges, builds a process-ID to class map, then walks worker data and applies class overrides. Bulk display helpers are synchronous formatting functions invoked by bulk command code after status/progress has already been fetched.

## State and Persistence Behavior

This file is primarily read-only. `getWorkerInterfaces` can write and then clear the special verify option key when `verify` is true, which asks the management special key path to validate interfaces. Bulk diagnostics do not persist anything. Returned `ProcessData`, `StorageServerInterface`, and owner suffix strings are transient CLI state.

## Dependencies and Integration Points

The file depends on management API schemas, status/system data, worker and server metadata encoders, bulk dumping/loading metadata APIs, `fmt`, Flow actors, and thread-future conversion. It is included by many fdbcli command actors through `fdbcli.h`.

## Risks and Edge Cases

Several range reads assert the result is below `CLIENT_KNOBS->TOO_MANY`; a very large cluster or corrupted special key output can trip assertions. Worker interface decoding treats parse failure as a CLI-version compatibility problem and returns early, potentially leaving a partial map. The bulk health/error recommendations are heuristic and string-based; case sensitivity in `BulkErrorAnalysis` may miss errors with capitalized keywords. `getSpecialKeysFailureErrorMessage` asserts schema validity, so malformed special-key error JSON is fatal in debug builds.

## Test Signals

Existing tests indirectly exercise `tokencmp`, usage printing, worker discovery through `kill`, `suspend`, `profile list`, coordinator/exclude commands, and integer option parsing. Bulk analysis helpers are not covered by the visible fdbcli integration tests and would benefit from focused unit tests for scoring, formatting, and error categorization.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/Util.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/VersionEpochCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/VersionEpochCommand.cpp

## Purpose

`VersionEpochCommand.cpp` implements `fdbcli versionepoch`, which reads, enables, disables, sets, and commits the cluster version epoch. Version epoch lets assigned versions track wall-clock-derived expected versions and supports a one-time jump through `advanceVersion`.

## Important APIs, Types, and Functions

- `versionEpochSpecialKey` is `\xff\xff/management/version_epoch`, the management special key used for CLI get/set/clear.
- `VersionInfo` holds current read version and expected version.
- `getVersionInfo` reads `versionEpochKey` directly from system data and computes expected version from `g_network->timer() * CLIENT_KNOBS->CORE_VERSIONSPERSECOND - versionEpoch`.
- `getVersionEpoch` reads the management special key and parses the value with `boost::lexical_cast<int64_t>`.
- `versionEpochCommandActor` implements the full command grammar.
- `advanceVersion(cx, expectedVersion)` performs the irreversible version jump for `commit`.

## Control Flow

With no arguments, the actor reports current version, expected version, and their difference, or says the epoch is unset. `get` reads the special key and prints its integer value. `disable` clears the special key if present. `enable` sets epoch `0` if unset; if already set, it prints the commit warning. `set <EPOCH>` parses a signed integer and sets the special key when absent or different. `commit` computes expected version and calls `advanceVersion`; if the epoch is unset it prints a prerequisite message. All mutating paths retry transactions through `onError`.

## State and Persistence Behavior

The command persists the version epoch through the management special keyspace using `SPECIAL_KEY_SPACE_ENABLE_WRITES`. The no-argument reporting path reads `versionEpochKey` directly with `READ_SYSTEM_KEYS`. Committing does not change the epoch key; it advances the database version to the current expected version through the management API.

## Dependencies and Integration Points

This command integrates with management special keys, direct system data, `advanceVersion`, Flow timers, client knobs, and CLI dispatch. The command help emphasizes irreversibility because large version jumps cannot be undone.

## Risks and Edge Cases

`disable` checks presence by creating a separate transaction for `getVersionEpoch`, then clears using another transaction; a concurrent change can race, although retries handle normal conflicts. `enable` uses `getVersionEpoch(tr)` with the same transaction, while `disable` does not. `boost::lexical_cast` parse failures in `getVersionEpoch` are handled by transaction retry even though malformed special-key output may not be retriable. Very large expected-version differences can lead to disruptive version jumps.

## Test Signals

`fdbcli_tests.py` actively tests unset reporting, `get`, `commit` before setup, `enable`, `set 10`, `disable`, re-enable, and `commit` output prefix. It then waits for full recovery because committing can trigger recovery. Additional coverage should check invalid epoch syntax and idempotent set behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/VersionEpochCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/fdbcli.cpp -->
# sources/storage-engines/foundationdb/fdbcli/fdbcli.cpp

## Purpose

`fdbcli.cpp` is the FoundationDB CLI executable. It parses process options, initializes the client API and network, constructs the interactive shell, parses user command lines, dispatches built-in and command-factory commands, manages transaction state, and handles status checks, history, completion, hints, TLS diagnostics, logging, memory limit monitoring, and `--exec` mode.

## Important APIs, Types, and Functions

- `CLIOptions` parses command-line flags with `SimpleOpt`, including cluster file, API version, trace options, TLS options, `--exec`, timeout, status-from-json, knobs, and memory limit.
- `FdbOptions` stores persistent transaction options and applies them to new or active transactions.
- `parseLine` tokenizes semicolon-separated CLI commands with quotes and escape sequences.
- `formatStringRef`, `printProgramUsage`, `initHelp`, `printHelpOverview`, `printHelp`, `printVersion`, and `printBuildInformation` provide display behavior.
- `makeInterruptable`, `commitTransaction`, `checkStatus`, `timeWarning`, and `getTransaction` coordinate Flow futures and transaction lifecycle.
- Completion and hints are implemented by `fdbcliCompCmd`, `arrayGenerator`, and `LineNoise::Hint` logic in `runCli`.
- `cli` is the central async REPL and dispatcher.
- `main` performs platform setup, signal handling, network options, cluster-file resolution, TLS consistency checks, API setup, and network execution.

## Control Flow

`main` initializes platform/error state, ignores SIGINT on Unix, parses `CLIOptions`, sets tracing/TLS/network options, handles early-exit modes, resolves the cluster file, verifies TLS configuration against coordinator addresses, selects the API version, starts network setup, and runs `runCli` through `stopNetworkAfter`. `runCli` constructs `LineNoise`, loads history, calls `cli`, and saves history on exit.

`cli` creates both `Database` and multiversion `IDatabase` handles, performs an initial read-version handshake, optionally prints status and welcome text, then loops over either `--exec` content or interactive input. Each line is parsed into one or more commands. Parse failures insert a synthetic `parse_error` command so partial malformed commands are not executed. For each command it validates known commands against `helpMap` and `hiddenCommands`, handles built-ins directly, dispatches command actors, updates `is_error`, and stops remaining semicolon-separated commands after a failure. In interactive mode it maintains command history and long-delay status warnings; in exec mode it exits with status 1 on command failure.

## State and Persistence Behavior

Persistent database mutation is done by dispatched commands or by built-ins gated by `writemode`: `set`, `clear`, and `clearrange`. The CLI keeps local state for `intrans`, `writeMode`, active/global transaction options, cached worker/storage interface maps, current transaction reference, warning future, and line history. Explicit `begin` switches to an active transaction and copies global options; `commit`, `rollback`, and exception handling leave transaction mode. Autocommit writes call `commitTransaction` immediately.

## Dependencies and Integration Points

This file is the integration point for most `fdbcli` command actors declared in `fdbcli.h`, plus `LineNoise`, `MultiVersionApi`, `DatabaseContext`, status JSON, global config, management API, TLS config, cluster connection files, knobs, and Flow runtime. It also exposes `arrayGenerator` used by command-specific completion code.

## Risks and Edge Cases

`parseLine` mutates the input string while preserving `StringRef` slices; its erase/replace behavior is delicate and explicitly suppresses a clang-tidy false positive. Exact CLI output is test-sensitive. Long dispatch chains make it easy for new commands to be registered in help but omitted from dispatch or vice versa. `--timeout` races `cliFuture` with `timeExit`; when the timeout wins, `main` returns 1. Some interactive-only paths, such as unlock passphrase prompting and history filtering, require subprocess tests. `getrange` limit parsing manually caps at nine digits and accepts only decimal digits.

## Test Signals

`fdbcli_tests.py` covers much of this file indirectly: `--exec`, exact output, transactions, `writemode`, options, `clearrange` prefix mode, `status --json`, `--status-from-json`, TLS coordinator suffix rejection, command sequencing, lock/unlock prompts, and dispatch for many command actors. Parser edge cases for quoting and escapes are mostly implicit and would benefit from focused tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/fdbcli.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/include/fdbcli/FlowLineNoise.h -->
# sources/storage-engines/foundationdb/fdbcli/include/fdbcli/FlowLineNoise.h

## Purpose

`FlowLineNoise.h` declares `LineNoise`, a Flow-friendly wrapper around the linenoise interactive line editor. It allows fdbcli to read terminal input asynchronously while still using linenoise completion, hints, and history.

## Important APIs, Types, and Functions

- `LineNoise::Hint` holds hint text, color, bold flag, and validity.
- The `LineNoise` constructor accepts completion and hint callbacks, maximum history lines, and a multiline flag.
- `read(prompt)` returns a `Future<Optional<std::string>>`; absence means EOF.
- `historyAdd`, `historyLoad`, and `historySave` manage the linenoise history.
- `onKeyboardInterrupt()` returns a future that becomes ready on the next Ctrl-C.
- `threadPool` and `LineNoiseReader* reader` are implementation state owned by the wrapper.

## Control Flow

The header only defines the interface. `fdbcli.cpp` constructs one `LineNoise` in `runCli`, passes completion and hint lambdas, reads lines in the REPL, stores non-dangerous commands in history, and uses `onKeyboardInterrupt` in `makeInterruptable` to cancel long-running futures.

## State and Persistence Behavior

History persists to the user's `.fdbcli_history` when enabled by `runCli`. The wrapper owns thread-pool and reader objects for asynchronous integration. The comment warns that only one wrapper should exist at a time because linenoise itself supports one history, and that reads are not concurrency-safe.

## Dependencies and Integration Points

The type depends on Flow futures, `NonCopyable`, and function callbacks. Its primary integration is with fdbcli interactive mode and the platform-specific linenoise implementation compiled elsewhere.

## Risks and Edge Cases

Concurrent `read` calls or simultaneous reads with other operations are unsupported and can corrupt UI state. Because Ctrl-C is modeled as a future, callers must cancel or handle the raced operation correctly; `makeInterruptable` does this for most command futures. History persistence failures are logged by the caller, not surfaced to the user.

## Test Signals

The Python integration tests exercise `LineNoise` through subprocess interactive sessions for `kill`, `unlock`, transaction flows, and command sequences. They do not directly test completion, hints, EOF behavior, or Ctrl-C cancellation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/include/fdbcli/FlowLineNoise.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/include/fdbcli/fdbcli.h -->
# sources/storage-engines/foundationdb/fdbcli/include/fdbcli/fdbcli.h

## Purpose

`fdbcli.h` is the shared command interface for fdbcli. It declares command registration types, common special keys, shared utility functions, bulk operation formatting/analysis helpers, worker discovery, status printing, and actor prototypes for every CLI command.

## Important APIs, Types, and Functions

- `CommandHelp` stores usage, short description, and long description.
- `CommandFactory` registers visible commands, hidden commands, completion generators, and hint generators in static maps.
- `arrayGenerator`, `tokencmp`, `printUsage`, `printLongDesc`, `getSpecialKeysFailureErrorMessage`, `getWorkers`, `getStorageServerInterfaces`, and `getWorkerInterfaces` are shared command helpers.
- Special-key declarations include management, exclusion, maintenance, process class, lock, and worker-interface keys.
- Bulk utilities include `validateBulkJobId`, `getBulkOwnerSuffix`, `formatBytesProgress`, progress/task breakdown printing, health/error/optimization analysis types, and `printBulkAnalysis`.
- Actor prototypes define the cross-file dispatch contract used by `fdbcli.cpp`.

## Control Flow

Command source files instantiate `CommandFactory` at static initialization time. `fdbcli.cpp` later calls `initHelp` for built-ins, consults `CommandFactory::commands()` for known command validation/help, and dispatches actors based on the first token. Completion and hint generators are looked up through the `CommandFactory` maps.

## State and Persistence Behavior

The header itself does not persist data. It defines process-local static registries for command metadata. The declared actor APIs may mutate cluster state depending on command semantics. Inline special-key constants such as `errorMsgSpecialKey` and `workerInterfacesVerifyOptionSpecialKey` identify system metadata locations used by utility functions.

## Dependencies and Integration Points

The header includes `FlowLineNoise`, bulk loading, coordination, management API, client API, status client, storage server interface, and Flow arena definitions. It is the main coupling point between the monolithic dispatcher and independently implemented command files.

## Risks and Edge Cases

Static registration depends on linked translation units; a command file not linked into the executable will silently omit its `CommandFactory`. Adding a new command requires both a prototype here and a dispatch branch in `fdbcli.cpp` unless the dispatcher is refactored. The visible command registry and hidden command set are mutable global state.

## Test Signals

The integration test suite exercises many declarations indirectly by invoking built-in and registered commands. Help text, completion, and bulk analysis declarations are less directly covered. Compile/link failures are the primary signal for prototype mismatches between this header and command implementations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/include/fdbcli/fdbcli.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/tests/fdbcli_tests.py -->
# sources/storage-engines/foundationdb/fdbcli/tests/fdbcli_tests.py

## Purpose

`fdbcli_tests.py` is an integration test driver for fdbcli. It runs a built `fdbcli` binary against a real test cluster, invokes commands with `--exec` or interactive stdin, and asserts exact output or observable cluster state through status JSON.

## Important APIs, Types, and Functions

- `run_fdbcli_command` and `run_fdbcli_command_and_get_error` wrap `subprocess.run` for stdout/stderr assertions.
- `enable_logging` decorates test functions with per-test logging.
- Command tests include `maintenance`, `setclass`, `lockAndUnlock`, `kill`, `killall`, `suspend`, `versionepoch`, `consistencycheck`, `datadistribution`, `transaction`, `clearrange_prefix`, `coordinators`, `exclude`, `throttle`, `profile`, `triggerddteaminfolog`, `idempotency_ids`, `integer_options`, and `tls_address_suffix`.
- `get_value_from_status_json`, `read_system_key`, `get_fdb_process_addresses`, and `wait_for_database_fully_recovered` are shared helpers.
- The `__main__` block parses build directory, cluster file, process count, and optional external client library.

## Control Flow

The script builds a command template `[build_dir/bin/fdbcli, -C, cluster_file, --exec]`, verifies database availability, then runs a set of tests. Single-process clusters run most command tests; multi-process clusters run coordinator, exclude, and kill-all tests. Several unstable or disruptive tests are intentionally disabled with comments. Some workflows use interactive `Popen` without `--exec` to preserve state across commands or respond to prompts.

## State and Persistence Behavior

The tests mutate the cluster: they lock/unlock, kill or suspend processes, toggle maintenance, data distribution, consistency check, version epoch, transaction keys, coordinator configuration, process exclusion, profiling config, and idempotency ID metadata. Cleanup is embedded in individual tests where practical, and recovery waits are used after disruptive operations.

## Dependencies and Integration Points

The script depends on Python standard libraries, a running FoundationDB cluster, the built fdbcli binary, status JSON schema, and exact CLI output strings. External client testing is supported by setting `FDB_NETWORK_OPTION_DISABLE_LOCAL_CLIENT` and `FDB_NETWORK_OPTION_EXTERNAL_CLIENT_LIBRARY`.

## Risks and Edge Cases

The suite is output-fragile: harmless wording changes break assertions. Many tests assume local `127.0.0.1` addresses and specific process counts. Some actions are disruptive and can race recovery; the script uses sleeps and polling but can still be environment-sensitive. The `enable_logging` decorator adds a new handler on every invocation, which can duplicate logs if tests are rerun in-process.

## Test Signals

The file itself is the test signal for fdbcli behavior. In this subset it directly covers `versionepoch`, `triggerddteaminfolog`, shared transaction parsing/dispatch, status JSON, TLS validation, and much of `fdbcli.cpp`. The throttle test exists but is not active in the default single-process path.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/tests/fdbcli_tests.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/ActorLineageProfiler.cpp -->
# sources/storage-engines/foundationdb/fdbclient/ActorLineageProfiler.cpp

## Purpose

`ActorLineageProfiler.cpp` implements actor-lineage sampling and ingestion. It collects lineage-derived samples, encodes them as msgpack, retains a time window in memory, and optionally ships samples to a configured backend such as FluentD.

## Important APIs, Types, and Functions

- `Packer` wraps `msgpack::packer<msgpack::sbuffer>` and adds overloads for `std::any`, scalar types, strings, maps, and vectors.
- `IALPCollectorBase` registers collectors with `SampleCollector`.
- `SampleCollectorT::collect(ActorLineage*)` and `SampleCollectorT::collect()` gather per-lineage and per-wait-state samples.
- `SampleCollection_t::collect` stores samples, trims the in-memory window, and calls the configured ingestor.
- `sample(LineageReference*)` allocates lineage if needed, annotates actor name, and posts collection to the profiler Asio context.
- `ProfilerImpl` owns `boost::asio::io_context`, timer, work guard, background thread, and sampling frequency.
- `ActorLineageProfilerT` exposes `setFrequency` and `context`.
- `ProfilerConfigT::reset` parses ingestor configuration.
- `samplingProfilerUpdateFrequency` and `samplingProfilerUpdateWindow` are global config callbacks.

## Control Flow

When sampling is enabled, `ProfilerImpl::profileHandler` sets `startSampling` and schedules the next timer based on frequency. Instrumented actors call `sample`, which posts collection into the profiler's Asio context to avoid doing sample work inline. Collection walks registered getters by `WaitState`, asks each collector for named values, msgpack-encodes non-empty vectors, appends the sample to `SampleCollection`, trims old entries, and sends it to the ingestor. Config reset validates backend settings and installs either `NoneIngestor` or `FluentDIngestor`.

## State and Persistence Behavior

State is process-local: sampled data is held in a mutex-protected deque for a configurable window and optionally emitted externally. The profiler owns a background thread for its Asio event loop. Msgpack buffers are released from `sbuffer` as raw `(char*, unsigned)` pairs stored in `Sample::data`.

## Dependencies and Integration Points

The file integrates with Flow network time, actor lineage/name lineage, global config callbacks, `FluentDIngestor`, `NoneIngestor`, msgpack, Boost.Asio, and thread synchronization. It is part of the client profiling infrastructure used by profile-related command paths.

## Risks and Edge Cases

The `Packer` visitor silently logs unsupported `std::any` types instead of throwing, which can produce incomplete samples. The lowercase conversion lambdas in config parsing return `tolower` but do not assign it back to the character, so values may remain case-sensitive. `ProfilerImpl` destructor joins the background thread after resetting the work guard; pending handlers must exit cleanly. `SampleCollection_t::collect` assumes at least one sample remains while trimming.

## Test Signals

The visible fdbcli `profile` integration test exercises profile command state, but not low-level lineage packing or ingestor behavior. Useful tests would cover msgpack encoding of supported `std::any` types, unsupported type logging, frequency/window config callbacks, case-insensitive config parsing, and sample window trimming.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/ActorLineageProfiler.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/AnnotateActor.cpp -->
# sources/storage-engines/foundationdb/fdbclient/AnnotateActor.cpp

## Purpose

`AnnotateActor.cpp` provides the single storage definition for the global `samples` map declared by the actor annotation/profiling headers. It exists to satisfy linkage for code that records sample getters by wait state.

## Important APIs, Types, and Functions

- `samples` is a `std::map<WaitState, std::function<std::vector<Reference<ActorLineage>>()>>`.
- `WaitState` and `ActorLineage` are declared in `fdbclient/AnnotateActor.h`.

## Control Flow

There is no runtime control flow in this file. It includes the header and defines the global object.

## State and Persistence Behavior

The `samples` map is process-local mutable global state. It does not persist to the database or disk. Other translation units can register or read sampling callbacks through the declaration in the header.

## Dependencies and Integration Points

The file links the actor annotation infrastructure with the lineage profiler. It depends entirely on `AnnotateActor.h` for type definitions.

## Risks and Edge Cases

Global mutable state can introduce initialization-order and thread-safety concerns if modified concurrently. The file itself has no locking; synchronization must be provided by users of the map or by initialization discipline.

## Test Signals

There are no direct tests in the visible subset. Compile/link success is the main signal. Runtime profiling tests would indirectly verify that callbacks registered in `samples` are visible across translation units.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/AnnotateActor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/AsyncFileBlobStore.cpp -->
# sources/storage-engines/foundationdb/fdbclient/AsyncFileBlobStore.cpp

## Purpose

`AsyncFileBlobStore.cpp` adapts blob-store objects to an asynchronous file-like read interface and contains a unit test for rate-control throttling used by backup/blob operations.

## Important APIs, Types, and Functions

- `AsyncFileBlobStoreRead::size()` lazily caches object size by calling `m_bstore->objectSize(m_bucket, m_object)`.
- `AsyncFileBlobStoreRead::read(void*, int, int64_t)` delegates to `m_bstore->readObject`.
- `sendStuff` is a test actor that repeatedly requests byte allowances from an `IRateControl`.
- `TEST_CASE("/backup/throttling")` validates `SpeedLimit` throughput in a non-simulated environment.

## Control Flow

`size()` checks whether `m_size` is already a valid future; if not, it starts an object-size request and returns the cached future. `read()` directly returns the blob-store read future. The test creates a `SpeedLimit`, launches several `sendStuff` actors with different byte totals, waits for all, measures aggregate speed, and asserts it is within one percent of the configured limit.

## State and Persistence Behavior

The adapter does not persist data; it reads blob-store objects. The only local state is the cached size future. The test consumes time and rate-control state but avoids simulation because wall-clock timing is required.

## Dependencies and Integration Points

The file depends on `AsyncFileBlobStore.h`, the blob store interface, Flow unit tests, deterministic random, `IRateControl`, and `SpeedLimit`. It bridges blob-store APIs into code that expects asynchronous file reads.

## Risks and Edge Cases

Caching `m_size` means repeated `size()` calls return the first size future, which is correct for immutable objects but can be stale if the underlying object changes. The timing-based unit test can be sensitive to scheduler and system load outside simulation. `sendStuff` may request zero bytes because the random range includes zero, causing extra loop iterations but not incorrect accounting.

## Test Signals

The embedded `/backup/throttling` unit test is the primary signal. Additional tests could mock `IBackupContainer`/blob store reads to verify size caching, offset reads, error propagation, and object mutation assumptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/AsyncFileBlobStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/Atomic.cpp -->
# sources/storage-engines/foundationdb/fdbclient/Atomic.cpp

## Purpose

`Atomic.cpp` currently provides a link anchor for atomic operation tests and a focused unit test for `doAppendIfFits`, the helper behind append-style atomic mutations constrained by FoundationDB value size limits.

## Important APIs, Types, and Functions

- `forceLinkAtomicTests()` is an empty function used to force this translation unit and its tests into the binary.
- `TEST_CASE("/Atomic/DoAppendIfFits")` validates append behavior.
- `doAppendIfFits(existingValue, otherOperand, arena)` is declared in `Atomic.h` and returns either appended bytes or the existing value when the result would exceed `CLIENT_KNOBS->VALUE_SIZE_LIMIT`.

## Control Flow

The test creates an `Arena`, verifies a small append produces `existingother`, then creates a near-limit existing value and a two-byte operand, fills both with random bytes, and asserts that the result remains equal to the original existing value when the appended result would be too large.

## State and Persistence Behavior

There is no database persistence. Memory is allocated in the local `Arena`; returned `Value` references are expected to remain valid for the arena lifetime.

## Dependencies and Integration Points

The file depends on `Atomic.h`, `flow/Arena.h`, `flow/UnitTest.h`, deterministic random, and client knobs. It is part of the fdbclient unit-test surface for atomic mutation helpers.

## Risks and Edge Cases

Only `doAppendIfFits` is tested here; the TODO explicitly calls out missing tests for other atomic operations. Boundary cases such as exactly-at-limit appends, empty operands, and arena ownership are not covered by this file.

## Test Signals

The `/Atomic/DoAppendIfFits` unit test verifies success and overflow fallback. Broader atomic correctness needs additional unit tests for all operation variants and value-size-limit boundaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/Atomic.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/AuditUtils.cpp -->
# sources/storage-engines/foundationdb/fdbclient/AuditUtils.cpp

## Purpose

`AuditUtils.cpp` implements shared data-distribution audit utilities. It manages audit metadata lifecycle, progress persistence, cleanup, cancellation, resume initialization, move-keys lock validation, range comparison helpers, and readers that compare `serverKeys` and `keyServers` metadata for location consistency audits.

## Important APIs, Types, and Functions

- Metadata lifecycle: `persistNewAuditState`, `persistAuditState`, `getAuditState`, `cancelAuditMetadata`, `clearAuditMetadataForType`, and `initAuditMetadata`.
- Progress metadata: `persistAuditStateByRange`, `getAuditStateByRange`, `persistAuditStateByServer`, `getAuditStateByServer`, `checkAuditProgressCompleteByRange`, and `checkAuditProgressCompleteByServer`.
- Cleanup routing: `clearAuditProgressMetadata` chooses range-based or server-based progress keyspaces based on `AuditType`.
- Locking: `checkMoveKeysLockForAudit` validates and optionally takes/touches the move-keys lock using `MoveKeyLockInfo`.
- Query helpers: `getAuditStates`, `checkStorageServerRemoved`, and `stringToAuditPhase`.
- Range/location helpers: `coalesceRangeList`, `rangesSame`, `checkLocationMetadataConsistency`, `buildLocationMetadataMaps`, `buildOwnRangesFromServerKeysResult`, `buildOwnershipMapFromKeyServersResult`, `getThisServerKeysFromServerKeys`, and `getShardMapFromKeyServers`.

## Control Flow

Most functions run retry loops with system-immediate priority, system-key access or reads, and lock-aware transactions. New audit creation takes the move-keys lock, reads the latest audit ID for a type, assigns the next ID, and commits the encoded `AuditStorageState`. Final state persistence verifies the audit was not cancelled, optionally clears progress on complete, and writes the terminal state. Progress persistence first checks the DD-owned audit state, updates DD ID after failover, skips if already complete, rejects failed/cancelled audits, then writes a KRM range under range-based or server-based progress prefixes. Completion checks page through progress ranges until all subranges have non-invalid phases.

`initAuditMetadata` runs when the data distributor starts or recovers: it loads all audit states, updates running states to the current DD ID, clears old complete/failed audits beyond the retention count, keeps failed progress for investigation until selected for cleanup, and returns running audits to resume. Location metadata helpers build normalized maps from `keyServers` and `serverKeys`, coalesce ranges, and report mismatches by server ID and range.

## State and Persistence Behavior

The file persists audit state under `auditKeys`, progress under either range-based or server-based KRM keyspaces, and move-keys lock ownership/write markers under lock keys. Complete audits clear progress metadata; failed/error audits generally retain progress metadata for investigation until cleanup. Running audits are updated with the current DD ID during initialization so resumed work belongs to the active distributor.

## Dependencies and Integration Points

The utilities integrate with `Audit.h` data encoding, `SystemData.h` audit key builders, KRM helpers, `NativeAPI.actor`, `ReadYourWrites`, client knobs, move-keys locking, storage-server metadata, key-server/server-key encoders, and Flow tracing. They are used by data distribution audit actors and CLI audit status/cancel paths.

## Risks and Edge Cases

Audit correctness depends on consistent routing of each `AuditType` to the right progress keyspace; `clearAuditProgressMetadata` uses explicit branches and `UNREACHABLE` for unknown types. Some cleanup is intentionally non-atomic across read and clear. `persistNewAuditState` compares only `UID.first()` for sequencing and assumes no concurrent creator can pass the move-keys lock. Completion checks access `auditStates.back()` after reads; callers rely on KRM reads returning boundary rows. Retry loops often continue until success except for actor cancellation, move-key conflicts, or bounded progress-check retries. Location range comparison assumes sorted, exclusive ranges in simulation and may assert on invalid inputs.

## Test Signals

This file is not directly exercised by `fdbcli_tests.py` except through audit CLI commands elsewhere. Strong test signals would include simulated DD failover/resume, audit cancellation, progress persistence by range/server, complete versus failed cleanup behavior, move-keys lock conflict paths, `rangesSame` mismatch cases, and consistency comparison between synthetic `serverKeys` and `keyServers` KRM results.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/AuditUtils.cpp -->
