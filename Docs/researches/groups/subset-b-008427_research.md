# subset-b-008427 research

Grouped research report for FoundationDB `fdbcli` command/build files. Each section preserves the source path in the title and is wrapped for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/BulkLoadCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/BulkLoadCommand.cpp

Purpose: Implements the `bulkload` fdbcli command namespace for enabling/disabling bulk-load mode, submitting SST load jobs, reporting progress, cancelling jobs, viewing/clearing history, and issuing hidden range-lock debug operations used by bulk-load workflows.

Important APIs/types/functions: `bulkLoadCommandActor(Database, tokens)` is the command dispatcher and returns the submitted job `UID` for load/history-clear-id paths. It uses `BulkLoadJobState`, `BulkLoadProgress`, `BulkLoadTaskState`, `BulkLoadJobPhase`, `BulkLoadPhase`, `BulkLoadTransportMethod`, `submitBulkLoadJob`, `cancelBulkLoadJob`, `getBulkLoadMode`, `setBulkLoadMode`, `getBulkLoadProgress`, `getBulkLoadJobFromHistory`, `clearBulkLoadJobHistory`, `validateBulkJobId`, and utility renderers such as `formatBytesProgress`, `printProgressMetrics`, and `printStalledTasks`. Debug-only subcommands use range-lock helpers: `registerRangeLockOwner`, `findExclusiveReadLockOnRange`, `getAllRangeLockOwners`, and `releaseExclusiveReadLockByUser`.

Control flow: usage strings are composed into a `CommandHelp` description. `printPastBulkLoadJob` scans terminal history states and formats completed/error/cancelled jobs. `printBulkLoadJobProgress` iterates the job range through `krmGetRanges` under `READ_SYSTEM_KEYS` and `LOCK_AWARE`, aggregates manifest counts by task phase, and retries with transaction `onError`. The main actor branches on `tokens[1]`: `mode` reads or writes the cluster bulk-load mode; `load` verifies mode is enabled, validates token count/job id/range, chooses CP vs blobstore transport from the source URI prefix, creates a job state, and submits it; `status` prints aggregate current progress; `cancel` cancels and reports lock cleanup; `history` lists or clears records; hidden lock commands inspect and manipulate bulk-load range lock metadata.

State and persistence behavior: All durable effects are in FoundationDB metadata managed by `fdbclient/BulkLoading.h` and range-lock management APIs. The command reads system key ranges for task state and history, writes mode/job/cancel/history metadata through management helpers, and does not persist local files. It restricts bulk-load target ranges to `normalKeys` and treats job-root strings as either local-copy or blobstore inputs.

Dependencies and integration points: Depends on fdbcli command registration, `ManagementAPI`, bulk-loading client helpers, key-range-map system metadata, Flow actors, and fdbcli progress-formatting utilities. The returned `UID` integrates with higher-level CLI execution/testing paths that observe command results.

Risks: Operational risk is high because it injects external SST content into normal keyspace and toggles cluster-level bulk-load behavior. Input validation is mostly token/range/job-id based; root path/blobstore validity is delegated to bulk-load execution. Progress aggregation assumes task metadata remains decodable and that `rangeResult.back()` is available while scanning. Hidden lock commands can disrupt range-lock state if used incorrectly.

Test signals: Coverage should include command parsing, mode on/off, invalid ranges, blobstore URI transport selection, history clear variants, status output for no job and mixed phases, cancellation, retry behavior around system-key reads, and hidden range-lock debug paths. Existing fdbcli integration tests in this target are the likely end-to-end signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/BulkLoadCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/CMakeLists.txt -->
# sources/storage-engines/foundationdb/fdbcli/CMakeLists.txt

Purpose: Defines the `fdbcli` executable target, its include path, link dependencies, install behavior, sanitizer-specific link behavior, platform-specific linenoise usage, and fdbcli integration tests.

Important APIs/types/functions: CMake macros/functions include `fdb_find_sources`, `add_flow_target`, `target_include_directories`, `target_link_libraries`, `target_link_options`, `fdb_install`, `add_custom_target`, `add_dependencies`, and `add_fdbclient_test`. It links `fdbcli` against `fdbctl`, `fdbclient`, `SimpleOpt`, and non-Windows `linenoise`.

Control flow: Source files are discovered into `FDBCLI_SRCS`, then `add_flow_target(EXECUTABLE NAME fdbcli ...)` creates the executable. The target includes `fdbcli/include`. If UBSan is enabled, `-rdynamic` is added so typeinfo symbols agree between fdbcli and external `libfdb_c` clients for vptr checks. Non-Windows builds link linenoise. Install behavior differs between debug-package and stripped-package modes. Test registration is enabled only outside Windows and IDE-only builds, depends on `external_client`, and skips all four fdbcli Python test lanes under ASan.

State and persistence behavior: This file controls build graph and installation artifacts only. It persists no runtime state, but it determines whether installed clients use a stripped package binary or direct target output.

Dependencies and integration points: Integrates fdbcli into the broader FoundationDB Flow/CMake build system, package installation, external client build, and `fdbcli/tests/fdbcli_tests.py`. The external-client variants pass `--external-client-library` pointing at `bindings/c/libfdb_c_external.so`.

Risks: Automatic source discovery means new files under the directory are compiled unless excluded by the macro. Test coverage is intentionally absent under ASan because of known failures/timeout; regressions specific to ASan builds may be missed. Install behavior depends on `strip_only_fdbcli` existing when debug packages are disabled.

Test signals: Build success for `fdbcli`, package install generation, UBSan symbol behavior, non-Windows linenoise linking, and four non-ASan fdbclient tests: single/multi-process native and single/multi-process external-client fdbcli tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/CheckMetadataEncodingCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/CheckMetadataEncodingCommand.cpp

Purpose: Implements an audit helper that scans shard metadata encoding state and reports whether key-server/server-key metadata is old format, new format, mixed, or safe for rollback.

Important APIs/types/functions: `checkMetadataEncodingCommandActor(Database, tokens)` scans `keyServersPrefix..keyServersEnd`, `serverKeysPrefix..strinc(serverKeysPrefix)`, and `dataMoveKeys`. It uses `BinaryReader` with `IncludeVersion`, `rd.protocolVersion().hasShardEncodeLocationMetaData()`, constants `serverKeysTrue`, `serverKeysFalse`, `serverKeysTrueEmptyRange`, and transaction options `READ_SYSTEM_KEYS`, `READ_LOCK_AWARE`, and `PRIORITY_SYSTEM_IMMEDIATE`.

Control flow: The actor initializes counters, scans keyServers in 1000-row pages, classifies empty values and old protocol encodings as old, and newer shard-location metadata encodings as new. It separately scans serverKeys and treats legacy constant values as old, anything else as UID-encoded new. It then reads up to `CLIENT_KNOBS->TOO_MANY` data-move rows and prints counts plus a derived migration status. Each scan loop creates/reuses transactions and uses `onError` for retry, except the data-move section performs one retry path if an error was captured.

State and persistence behavior: Read-only against system metadata. No local state or cluster mutation. It reads live metadata, so output is a snapshot-like diagnostic and can change while migration is running.

Dependencies and integration points: Used by audit-storage command paths for metadata encoding validation. Depends on system data layout, binary protocol-version tagging, and key-range constants from fdbclient.

Risks: Classifying unknown non-legacy serverKeys values as new is intentionally broad. The data-move count uses a single `TOO_MANY` bounded read; if invariants are violated and more rows exist than expected, this command does not page the range. It also assumes metadata values are decodable.

Test signals: Tests should exercise all-old, all-new, mixed, rollback-complete with zero data moves, and data-move-present states. Fault injection around transaction retries and malformed metadata would protect the diagnostic path.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/CheckMetadataEncodingCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/ConfigureCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/ConfigureCommand.cpp

Purpose: Implements the `configure` command for creating or changing database configuration, including interactive `auto` recommendations and guarded rejection of backup-worker knobs managed elsewhere.

Important APIs/types/functions: `configureCommandActor(Reference<IDatabase>, Database, tokens, LineNoise*, Future<Void>)`, `configureGenerator`, `ManagementAPI::changeConfig`, `StatusClient::statusFetcher`, `parseConfig`, `ConfigureAutoResult`, `ConfigurationResult`, and command registration via `CommandFactory configureFactory`. It uses `LineNoise` to ask for confirmation in `auto` mode.

Control flow: The actor parses optional `FORCE`, then handles `auto` by fetching status JSON either through a valid multiversion transaction special key (`\xff\xff/status/json`) or native `StatusClient::statusFetcher` fallback. It computes recommended vs current configuration, prints a comparison table, asks for confirmation, and only then proceeds. Before calling `changeConfig`, it rejects `backup_worker_enabled:=` and `range_backup_worker_enabled:=`. The returned `ConfigurationResult` is mapped to user-facing success, warnings, or errors covering invalid configs, region constraints, storage migration settings, unavailable database, experimental storage engines, and restricted backup-worker settings.

State and persistence behavior: Durable changes are performed by `ManagementAPI::changeConfig`, which writes cluster configuration metadata. `auto` mode is read-only until the user confirms. The command itself keeps only transient state and cancels warning futures once it proceeds.

Dependencies and integration points: Integrates fdbcli parsing/help/completion, status JSON schema, management configuration validation, Flow actor futures, and interactive input. Configuration text maps to core cluster configuration, TSS, proxy/log/resolver counts, storage migration, and exclusion bootstrap parameters.

Risks: This is a high-impact operational command. The `FORCE` path bypasses availability/safety checks delegated to `ManagementAPI`. `auto` relies on status JSON completeness and parse advice; manual settings can block automatic changes. Parsing uses token prefix checks for restricted backup knobs, so equivalent formatting must remain covered by tests.

Test signals: Command tests should cover no options, `FORCE`, `auto` accept/decline, unavailable status fallback, all `ConfigurationResult` mappings, restricted backup knobs, generator completions, and representative valid/invalid configuration mutations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/ConfigureCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/ConsistencyCheckCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/ConsistencyCheckCommand.cpp

Purpose: Implements `consistencycheck [on|off]`, a small command that toggles whether consistency-checking processes are allowed to run.

Important APIs/types/functions: `consistencyCheckCommandActor(Reference<ITransaction>, tokens, bool intrans)`, `consistencyCheckSpecialKey`, `SPECIAL_KEY_SPACE_ENABLE_WRITES`, and `CommandFactory consistencyCheckFactory`.

Control flow: The actor enables special-key writes on the supplied transaction. With no arguments it reads `\xff\xff/management/consistency_check_suspended` and prints `off` when the key is present, `on` otherwise. `off` sets the key to an empty value; `on` clears it. If not already inside an fdbcli transaction (`intrans == false`), the actor commits immediately. Invalid tokens print command usage and return false.

State and persistence behavior: The persisted state is one special key. Presence means suspended/off; absence means allowed/on. In transaction mode it participates in the caller's transaction rather than committing by itself.

Dependencies and integration points: Depends on special-key-space management semantics and fdbcli transaction execution. The consistency-checking role observes this management key.

Risks: The command does not loop on retry; comments state outer fdbcli error handling is expected to print errors. This keeps behavior simple but means callers must preserve that contract. Because the toggle is inverted by key presence, future maintainers must avoid misreading the empty value as enabled.

Test signals: Tests should verify status display for present/absent key, immediate commit vs in-transaction behavior, special-key write option use, and invalid argument handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/ConsistencyCheckCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/ConsistencyScanCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/ConsistencyScanCommand.cpp

Purpose: Implements `consistencyscan`, which reads or changes configuration for the Consistency Scan role and exposes current/lifetime scan statistics.

Important APIs/types/functions: `consistencyScanCommandActor(Database, tokens)`, `dumpStats`, `ConsistencyScanState`, `ConsistencyScanState::Config`, `ReadYourWritesTransaction`, `SystemDBWriteLockedNow`, and options `on`, `off`, `restart`, `stats`, `clearstats`, `maxRate`, and `targetInterval`.

Control flow: Tokens after the command are placed in a list. The command creates a RYW transaction, applies system DB write-lock options, reads scan config, and either prints JSON when no args are supplied or walks arguments sequentially. Boolean toggles mutate `config.enabled`; `restart` sets `minStartVersion` from the transaction read version; `stats` prints current/lifetime JSON stats; `clearstats` clears stats; numeric options parse the next argument with `boost::lexical_cast<int>`. The updated config is written and committed with normal `onError` retry.

State and persistence behavior: Configuration and stats live in system metadata managed by `ConsistencyScanState`. The command mutates persisted config/stats; output is JSON generated from current state.

Dependencies and integration points: Depends on fdbclient consistency-scan state abstractions, RYW transaction semantics, system database lock-aware options, JSON serialization, and status JSON conventions documented in the help text.

Risks: Invalid numeric conversions are not explicitly caught by this actor, so lexical-cast exceptions may escape rather than becoming clean usage output. `tokens[2]` is not accessed directly, but option parsing accepts unknown trailing tokens silently if they are not matched and do not set `error`, so tests should pin intended behavior. Stats operations and config writes share one transaction.

Test signals: Exercise no-arg JSON, enable/disable, restart version update, stats and clearstats, numeric options, missing numeric values, retry on transaction errors, and unknown-token behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/ConsistencyScanCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/CoordinatorsCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/CoordinatorsCommand.cpp

Purpose: Implements `coordinators`, allowing users to display cluster coordinator information or change coordinator processes and cluster description.

Important APIs/types/functions: `coordinatorsCommandActor`, private `printCoordinatorsInfo`, `changeCoordinators`, special keys `clusterDescriptionSpecialKey`, `coordinatorsAutoSpecialKey`, `coordinatorsProcessSpecialKey`, `NetworkAddress`, `Hostname`, `ManagementAPI::generateErrorMessage`, and `CoordinatorsResult`.

Control flow: With no arguments, `printCoordinatorsInfo` reads cluster description and coordinator process special keys, splits the comma-delimited process list, and prints summary information. With arguments, `changeCoordinators` extracts a single `description=` token, detects `auto`, enables special-key writes, optionally writes the description, reads auto coordinator recommendations if needed, or validates and deduplicates supplied hostnames/network addresses before writing the process list. Commit is expected to fail with `commit_unknown_result` after coordinator change; special-key failures are decoded into user-facing management errors. `NOT_ENOUGH_MACHINES` is tolerated once with a retry.

State and persistence behavior: Writes special-key-backed coordination configuration. No local persistence. The command may change the cluster file description and coordinator set, which affects cluster availability and future client connection strings.

Dependencies and integration points: Relies on special-key management API, hostname/address parsing, boost string splitting/joining, and shared coordinator keys also read by status/exclude logic.

Risks: Coordinator changes are operationally sensitive. Successful commit semantics are unusual: the code asserts if commit succeeds because coordinator changes are expected to produce unknown commit result. Duplicate detection is separated for hostnames and addresses, so semantically equivalent hostname/address pairs are not resolved. Description validation is delegated to management.

Test signals: Cover display, auto mode, manual hostnames and IP:port addresses, duplicate detection, invalid endpoint errors, description extraction, same-network no-op, not-enough-machines retry, and special-key failure message propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/CoordinatorsCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/DataDistributionCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/DataDistributionCommand.cpp

Purpose: Implements hidden `datadistribution` controls for enabling/disabling all data distribution or selected data-distribution subfunctions such as storage-server failure handling and rebalance modes.

Important APIs/types/functions: `dataDistributionCommandActor`, `setDDMode`, `setDDIgnoreRebalanceSwitch`, `setDDIgnoreRebalanceOn`, `setDDIgnoreRebalanceOff`, special keys `ddModeSpecialKey` and `ddIgnoreRebalanceSpecialKey`, `rebalanceDDIgnoreKey`, `DDIgnore` masks, plus maintenance helpers `setHealthyZone` and `clearHealthyZone`.

Control flow: The actor accepts `on`, `off`, `disable <ssfailure|rebalance|rebalance_disk|rebalance_read>`, and matching `enable` forms. `setDDMode` writes the mode special key and, when enabling, clears global storage-failure maintenance state and rebalance-ignore state. Rebalance switches read the old mask, treating empty legacy values as `DDIgnore::ALL`, set or clear the masked bits, and remove the key when the mask becomes zero. Storage-server failure disable is implemented through maintenance state with `IgnoreSSFailures`; enable clears that state.

State and persistence behavior: Persists cluster-wide management special keys under `\xff\xff/management/data_distribution/...` and maintenance keys. The hidden command modifies live DD behavior and can leave the cluster unable to rebalance or react to failures until re-enabled.

Dependencies and integration points: Integrates with maintenance command state, DD ignore masks, special key space, `CLIENT_KNOBS->TOO_MANY`, Flow retry loops, and status warnings that surface DD disabled states.

Risks: High operational blast radius. Legacy empty-value handling must remain correct during upgrades. `tokens[2]` is used in the `disable/enable` branches after a broad size check that permits size 2; if a user enters only `datadistribution disable`, this can index past the token vector. Tests should catch this parser hazard.

Test signals: Cover `on/off`, each disable/enable submode, legacy empty mask upgrade, clearing DD side effects, invalid argument handling including missing third token, and status JSON warnings.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/DataDistributionCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/DebugCommands.cpp -->
# sources/storage-engines/foundationdb/fdbcli/DebugCommands.cpp

Purpose: Provides hidden debugging commands for locating storage replicas, reading all replica values for a key, and comparing all replicas over a key range for inconsistency diagnostics.

Important APIs/types/functions: `toHex`, `getVersion`, `getKeyServers`, `getLocationCommandActor`, `getallCommandActor`, `printStorageServerMachineInfo`, `printAllStorageServerMachineInfo`, `checkResults`, `doCheckAll`, and `checkallCommandActor`. It uses `CommitProxyInterface::getKeyServersLocations`, `GetKeyServerLocationsRequest`, `StorageServerInterface::getValue`, `StorageServerInterface::getKeyValues`, `getKeyLocation_internal`, `GetKeyValuesRequest`, and `CLIENT_KNOBS->KRM_GET_RANGE_LIMIT*`.

Control flow: `getlocation` asks commit proxies for shard-to-storage-server mappings over a key or range and prints server addresses. `getall` resolves a key at a supplied version and sends parallel `GetValueRequest`s to every replica location. `checkall` parses begin/end, optional DCID and `all`, then `doCheckAll` repeatedly resolves shard locations, queries all replica storage servers at the same read version, determines a comparison window from returned keys and `more` flags, and calls `checkResults` to log unique-key or mismatched-value inconsistencies. A recursive sub-check avoids getting stuck when paginated replies end at the current begin key.

State and persistence behavior: Read-only diagnostics. It bypasses ordinary transactional range reads and contacts commit proxies/storage servers directly, using retry delays and transaction `onError` only for read-version/backoff support.

Dependencies and integration points: Depends on NativeAPI internals, commit proxy and storage server interfaces, Flow `race`, `waitForAll`, `CoroUtils`, and hidden `CommandFactory` registrations for `getlocation`, `getall`, and `checkall`.

Risks: Intended for small ranges; `checkall` can be expensive and noisy. Direct server RPCs expose failures differently from transaction reads. DCID filtering only excludes servers with a different present dcid; if cluster/server dcid is absent, the filter is ignored. Comparison logic is subtle around pagination and clear operations.

Test signals: Unit tests should target `checkResults` mismatch cases and pagination invariants. Integration tests should cover location lookup, replica value reads, DCID filtering, recursive progress when `begin == claimEndKey`, stop-on-first vs `all`, and server RPC error retry.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/DebugCommands.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/ExcludeCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/ExcludeCommand.cpp

Purpose: Implements `exclude`, allowing operators to exclude or mark failed servers/localities, list current exclusions and in-progress exclusions, wait for safe data movement, and warn about coordinators or missing workers.

Important APIs/types/functions: `excludeCommandActor`, private helpers `excludeServersAndLocalities`, `getExcludedServers`, `getExcludedLocalities`, `getFailedServers`, `getFailedLocalities`, `getInProgressExclusion`, `checkForExcludingServers`, and `checkForCoordinators`. Special ranges include `excludedServersSpecialKeyRange`, `failedServersSpecialKeyRange`, `excludedLocalitySpecialKeyRange`, `failedLocalitySpecialKeyRange`, force-option keys, and `exclusionInProgressSpecialKeyRange`.

Control flow: With no arguments, the actor lists excluded servers/localities, failed servers/localities, and in-progress process exclusions. With arguments, it fetches workers and storage-server interfaces, parses `FORCE`, `no_wait`, `failed`, locality selectors, and `AddressExclusion`s, expands localities to address exclusions for wait/warning logic, writes requested exclusion/failed keys with optional force marker, optionally waits until in-progress exclusions no longer overlap the requested set, then prints per-address success/in-progress/missing warnings and coordinator warnings.

State and persistence behavior: Persists special-key-backed exclusion and failed metadata. `failed` semantics can cause the cluster to forget state and restore lost ranges to empty, so it can be data-loss inducing. No local persistence.

Dependencies and integration points: Integrates with worker discovery (`getWorkers`), storage server interfaces, locality expansion helpers, coordinator special keys, management special-key failure messages, and data distribution movement that clears in-progress exclusions.

Risks: High operational risk, especially `failed` and `FORCE`. Locality selectors with no matches are still written and warned afterward. Safety depends on special-key API checks unless forced. The in-progress wait polls rather than watches. Coordinator parsing only handles network addresses from the coordinator process key, not hostnames.

Test signals: Cover list output for all four exclusion classes, address/locality parsing, TLS suffix warning, force markers, failed mode, no-wait, missing worker warnings, in-progress wait and overlap logic, coordinator warnings, no-match locality warnings, and special-key failure message customization.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/ExcludeCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/ExpensiveDataCheckCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/ExpensiveDataCheckCommand.cpp

Purpose: Implements hidden `expensive_data_check`, which triggers process reboot with the check flag enabled so selected processes perform expensive data checking on restart.

Important APIs/types/functions: `expensiveDataCheckCommandActor(Reference<IDatabase>, Reference<ITransaction>, tokens, address_interface)`, `getWorkerInterfaces`, `db->rebootWorker(addresses, true, 0)`, and the cached `address_interface` map from process address key to worker interface metadata.

Control flow: With no arguments, the command refreshes the process-address map and lists checkable addresses. `list` prints the cached map. `all` requires a populated cache, joins all cached addresses with commas, and calls `rebootWorker` once so requests are sent in parallel. Explicit address arguments are validated against the cached map before joining and sending one reboot/check request. Errors instruct users to refresh the list.

State and persistence behavior: The command itself keeps transient state in the caller-owned `address_interface` cache across invocations. It does not write FoundationDB keys, but it sends reboot requests to cluster workers, causing process restarts and subsequent data checking.

Dependencies and integration points: Shares cache behavior with `kill`/`suspend`, depends on worker interface discovery through special keys, and uses the database client API reboot path.

Risks: Operationally disruptive: it kills processes. Cached addresses can become stale; validation intentionally requires an earlier list refresh. Curly apostrophes in some error strings are harmless but worth preserving/normalizing consistently if CLI output tests are strict. `all` can affect every known process at once.

Test signals: Cover initial listing, empty cache errors, stale/unknown address validation, `all` batching, explicit address batching, zero requests sent, and integration with worker-interface verification.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/ExpensiveDataCheckCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/FileConfigureCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/FileConfigureCommand.cpp

Purpose: Implements `fileconfigure`, which reads a JSON configuration file, validates it against the cluster configuration schema, converts it to a configure string, and applies it through the management API.

Important APIs/types/functions: `fileConfigureCommandActor(Reference<IDatabase>, filePath, isNewDatabase, force)`, `readFileBytes`, `json_spirit::read_string`, `JSONSchemas::clusterConfigurationSchema`, `schemaMatch`, `DatabaseConfiguration::configureStringFromJSON`, `ManagementAPI::changeConfig`, and `ConfigurationResult`.

Control flow: The actor reads up to 100000 bytes from the file, parses JSON, requires a top-level object, loads and applies the schema, converts the JSON to a configure string, prepends `new` for new database creation or removes the leading space otherwise, rejects restricted backup-worker settings, then calls `changeConfig`. It maps configuration result variants to fileconfigure-specific errors/warnings and success messages.

State and persistence behavior: Local file input is read only. Persistent changes are cluster configuration changes made through `ManagementAPI`. The command has no local output files or cache.

Dependencies and integration points: Integrates fdbcli command help, fdbclient schema validation, database configuration serialization, and the same management configuration machinery used by `configure`.

Risks: The 100000-byte read limit must be sufficient for supported config JSON. Restricted setting detection uses substring search on serialized configure text and may depend on formatting. Some newer `ConfigurationResult` variants handled by `configure` are not present here, so enum expansion can hit `ASSERT(false)` until updated.

Test signals: Cover invalid JSON, non-object JSON, schema mismatch messages, conversion exceptions, `new` vs existing config string construction, restricted backup-worker settings, force/unavailable failures, and every handled `ConfigurationResult`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/FileConfigureCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/FlowLineNoise.cpp -->
# sources/storage-engines/foundationdb/fdbcli/FlowLineNoise.cpp

Purpose: Provides asynchronous line input, completion, hints, history, and keyboard-interrupt handling for fdbcli using linenoise on Unix-like platforms and stdin fallback elsewhere.

Important APIs/types/functions: `LineNoiseReader` implements `IThreadPoolReceiver`; nested `Read` actions carry a prompt and `ThreadReturnPromise<Optional<std::string>>`; `LineNoise::LineNoise`, destructor, `read`, `onKeyboardInterrupt`, `historyAdd`, `historyLoad`, and `historySave`; helper `waitKeyboardInterrupt`. It uses linenoise callbacks when `HAVE_LINENOISE` is true and Boost.Asio signal handling for SIGINT.

Control flow: The constructor creates a generic thread pool, installs a `LineNoiseReader`, configures linenoise max history, multiline mode, completion callback, hints callback, and free callback. Linenoise callbacks run in the reader thread but call `onMainThread(...).getBlocking()` to safely invoke fdbcli completion/hint functions on the main Flow thread. `read` posts an action to the thread pool and returns a future. The reader turns Ctrl-C/EAGAIN into an empty string, EOF into absent optional, and exceptions into errors.

State and persistence behavior: Maintains a thread pool and linenoise global callback functions. History is persisted only when `historyLoad`/`historySave` are called with a filename; this file just delegates to linenoise.

Dependencies and integration points: Integrates Flow thread pools, `onMainThread`, network global ASIO service, linenoise, Boost.Asio, and fdbcli interactive command handling.

Risks: Linenoise callback storage uses static function objects, so multiple `LineNoise` instances would overwrite callbacks. Completion captures `line` and a local vector across synchronous `getBlocking`, which relies on callback execution remaining synchronous. Non-Unix fallback lacks completion/history behavior.

Test signals: Interactive behavior is hard to automate, but tests can cover fallback reads, future completion, Ctrl-C handling, callback invocation via `onMainThread`, history load/save error propagation, and clean thread-pool shutdown.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/FlowLineNoise.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/ForceRecoveryWithDataLossCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/ForceRecoveryWithDataLossCommand.cpp

Purpose: Implements `force_recovery_with_data_loss <DCID>`, an emergency command that forces recovery into a specified datacenter and accepts potential committed mutation loss.

Important APIs/types/functions: `forceRecoveryWithDataLossCommandActor(Reference<IDatabase>, tokens)`, `db->forceRecoveryWithDataLoss(tokens[1])`, `safeThreadFutureToFuture`, and `CommandFactory forceRecoveryWithDataLossFactory`.

Control flow: The actor requires exactly two tokens. Invalid usage prints help and returns false. Valid usage forwards the DCID token to the database API and returns true after the future completes. It does not catch errors locally; fdbcli outer handling is expected to report them.

State and persistence behavior: The command delegates all durable behavior to the database management API. Per help text, it changes region configuration priorities, sets `usable_regions` to 1, and does nothing if the database has already recovered. No local state is written.

Dependencies and integration points: Depends on multiversion database interface support for force recovery and fdbcli command registration. Operationally tied to multi-region disaster recovery configuration.

Risks: Data-loss inducing by design. There is no interactive confirmation in this file; any confirmation must be enforced by higher-level command dispatch if desired. Validation of the DCID and recovery conditions is delegated to the database API.

Test signals: Cover token-count validation, successful delegation, propagated API errors, already-recovered no-op behavior at integration level, and documentation/confirmation expectations in the command dispatcher.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/ForceRecoveryWithDataLossCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/GetAuditStatusCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/GetAuditStatusCommand.cpp

Purpose: Implements `get_audit_status`, a diagnostic command for fetching audit records, recent/phase-filtered audit states, and progress for multiple audit types.

Important APIs/types/functions: `getAuditStatusCommandActor`, `getAuditProgress`, `getAuditProgressByRange`, `getStorageServers`, `getAuditProgressByServer`, fdbclient audit APIs `getAuditState`, `getAuditStates`, `getAuditStateByRange`, and `getAuditStateByServer`, plus `AuditStorageState`, `AuditType`, and `AuditPhase`.

Control flow: The command maps type tokens (`ha`, `replica`, `locationmetadata`, `ssshard`, `validate_restore`, `metadata_encoding`) to `AuditType`, then branches on `id`, `progress`, `recent`, and `phase`. `id` fetches one audit state by UID. `recent` fetches newest states with optional count. `phase` filters by parsed phase and optional count. `progress` fetches the audit state, and if running, delegates to progress helpers. Range-based audit progress pages through audit state ranges, printing ongoing/error ranges and count of finished ranges. Storage-server-shard progress lists storage servers, skips TSSes, and classifies each server as complete/ongoing/error/partial.

State and persistence behavior: Read-only diagnostic against audit metadata and server list system keys. No local state.

Dependencies and integration points: Depends on audit metadata layout, audit utility functions, server list decoding, system-key reads, `CLIENT_KNOBS->TOO_MANY`, and fdbcli output formatting.

Risks: `getAuditStatusCommandActor` checks `tokens.size() < 2 || > 5` but then accesses `tokens[2]`; a two-token invocation with only a type can index past the vector. Progress loops call `auditStates.back()` and assume non-empty range results. Retry counters are shared across pages and can end progress early after repeated transient failures.

Test signals: Cover all action forms, invalid type/action/phase, missing action token parser safety, count parsing, range progress with ongoing/error/complete states, storage-server-shard progress including TSS skip, empty audit-state result handling, and retry exhaustion.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/GetAuditStatusCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/HotRangeCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/HotRangeCommand.cpp

Purpose: Implements `hotrange`, a storage-server diagnostic command that queries read hot-range metrics from one selected storage server and prints JSON ranges with metrics.

Important APIs/types/functions: `hotRangeCommandActor(Database localdb, Reference<IDatabase> db, tokens, storage_interface)`, private `parseSplitType`, `getStorageServerInterfaces`, `ReadHotSubRangeRequest::SplitType`, `ReadHotRangeWithMetrics`, and `localdb->getHotRangeMetrics`.

Control flow: With no arguments, the command refreshes the caller-owned `storage_interface` map and prints queryable storage server addresses. With exactly six tokens, it requires a non-empty cache, validates the address exists, parses `splitCount` with `boost::lexical_cast<int>`, maps split type from `bytes`, `readBytes`, or `readOps` with fallback to bytes for unknown strings, builds a key range from begin/end tokens, queries hot range metrics through the native local database, and serializes each metric object to pretty JSON. Other token counts print usage.

State and persistence behavior: Read-only against storage-server metrics. The only state is transient cached storage interfaces maintained outside this actor.

Dependencies and integration points: Depends on fdbcli utility discovery of storage interfaces, storage-server metric RPCs, JSON output, and native database access because the code notes multiversion support is not yet refactored.

Risks: Requires a prior cache-populating invocation; stale cache can reject valid servers or target old interfaces. Unknown split type logs an error but still runs with bytes, which may surprise users. It does not validate `begin < end` or `splitCount > 0` locally.

Test signals: Cover listing, empty/stale cache handling, split type parsing, invalid split count, unknown split type fallback, JSON output shape, range validation expectations, and storage-server RPC errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/HotRangeCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/IdempotencyIdsCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/IdempotencyIdsCommand.cpp

Purpose: Implements `idempotencyids`, exposing status for idempotency-id metadata and a cleanup action for reclaiming space used by old idempotency IDs.

Important APIs/types/functions: `idempotencyIdsCommandActor(Database, tokens)`, private `parseAgeValue`, `getIdmpKeyStatus`, `cleanIdempotencyIds`, `JsonBuilderObject`, and command registration `idempotencyIdsCommandFactory`.

Control flow: The actor requires two or three tokens. `status` requires no additional argument, awaits `getIdmpKeyStatus`, and prints JSON. `clear <min_age_seconds>` parses the age using `std::stod`, rejects parse failures, calls `cleanIdempotencyIds`, and prints success. Unknown actions or wrong arity print usage and return false.

State and persistence behavior: `status` is read-only; `clear` mutates idempotency ID metadata through fdbclient helpers and can expire transaction versions older than the specified age. No local state is persisted.

Dependencies and integration points: Depends on fdbclient `IdempotencyId` helpers, JSON builder, fdbcli parsing/help, and cluster idempotency metadata.

Risks: `std::stod` accepts some partial strings unless position is checked; `parseAgeValue` does not validate full-token consumption, finite values, or non-negative ages. Cleanup has potentially broad historical transaction-version effects, so input validation matters.

Test signals: Cover status JSON, valid clear, invalid age, partial numeric age, negative/NaN/infinite age behavior, wrong arity, unknown actions, and helper error propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/IdempotencyIdsCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/IncludeCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/IncludeCommand.cpp

Purpose: Implements `include`, clearing prior excluded or failed server/locality entries so processes or localities may rejoin the database.

Important APIs/types/functions: `includeCommandActor`, private `include`, `includeServers`, `includeLocalities`, `AddressExclusion`, `LocalityData::ExcludeLocalityPrefix`, and the special-key ranges exported by `ExcludeCommand.cpp`.

Control flow: The actor requires at least one argument after `include`. The helper parses `all`, `failed`, locality selectors, and address exclusions. `all` constructs an invalid `AddressExclusion` sentinel to clear the entire failed or excluded server range and clears the whole locality range. Otherwise it clears specific address keys and/or locality keys. Whole-machine address inclusion also clears port-level exclusions for that IP using the `IP:` to `IP;` key range. Errors for invalid tokens include a TLS suffix hint.

State and persistence behavior: Persists by clearing special keys under excluded/failed server and locality ranges. It does not validate that cleared entries existed. No local state.

Dependencies and integration points: Shares exclusion special key contracts with `ExcludeCommand.cpp` and affects data distribution recruitment behavior. Uses special-key writes and normal transaction retry loops.

Risks: `all` plus `failed` clears all failed entries, which may reintroduce processes intended to remain failed. The local `versionKey` variables are unused. Clearing whole-machine port ranges relies on string ordering around `:` and `;`, which is documented in comments and should remain tested.

Test signals: Cover clearing specific IP, IP:port, whole-machine plus port-level entries, localities, all, failed variants, invalid token/TLS suffix handling, idempotent clears, and transaction retry.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/IncludeCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/KillCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/KillCommand.cpp

Purpose: Implements `kill`, allowing operators to list killable processes from cached worker interfaces and send reboot-worker kill requests to selected or all processes.

Important APIs/types/functions: `killCommandActor(Reference<IDatabase>, Reference<ITransaction>, tokens, address_interface)`, `getWorkerInterfaces`, `db->rebootWorker(addresses, false, 0)`, `killGenerator`, and `CommandFactory killFactory`.

Control flow: With only `kill`, the command refreshes the address cache from worker interfaces. With `kill` or `kill list`, it prints cached addresses. `kill all` requires a populated cache, joins all addresses, and sends one reboot request. Explicit addresses are validated against the cache before sending one request. After a successful explicit kill, the actor waits three seconds so the network queue can flush before the client exits.

State and persistence behavior: No cluster metadata is written by this file, but it sends kill/reboot requests to live processes. The address map is transient state owned by the caller and must be refreshed before use.

Dependencies and integration points: Integrates with worker interface special keys, database reboot API, boost string join, fdbcli completion generator, and command help.

Risks: Operationally disruptive. Cache staleness can cause false rejections or missed processes. `kill all` can terminate every known process. The command relies on the reboot API returning a nonzero count to indicate request dispatch.

Test signals: Cover cache population/listing, empty-cache `all` error, explicit unknown address error, all/explicit successful batching, zero requests sent, three-second delay behavior under test control, and completion suggestions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/KillCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/LocationMetadataCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/LocationMetadataCommand.cpp

Purpose: Implements `location_metadata`, a diagnostic command for inspecting shard metadata, physical shard counts, range resolution, per-server shard assignments, and random shard samples.

Important APIs/types/functions: `locationMetadataCommandActor`, private helpers `describeServers`, `printKeyServersEntry`, `printRandomShards`, `printPhysicalShardCount`, `printServerShards`, and `resolveRange`. It uses `ReadYourWritesTransaction`, `serverListKeyFor`, `decodeServerListValue`, `decodeKeyServersValue`, `decodeServerKeysValue`, `serverTagKeys`, `keyServersPrefix`, `serverKeysPrefixFor`, `krmGetRanges`, `anonymousShardId`, and `DataMoveType`.

Control flow: `physicalshards` scans all key-server ranges and counts ranges whose decoded source shard id is not anonymous. `resolve` prints keyServers entries for a single key or range, including source/destination server descriptions resolved from server list entries. `servershards` scans a server's serverKeys prefix and prints assigned ranges and shard ids. `listshards <n> [physical]` scans keyServers ranges from `allKeys.begin`, printing the first `n` physical or non-physical shards encountered.

State and persistence behavior: Read-only against system key metadata. No local state or mutations.

Dependencies and integration points: Depends on the new location metadata encoding, server tag maps, server list decoding, key-range-map helpers, and lock-aware system reads. It complements audit commands that validate location metadata.

Risks: Several helper paths assume system metadata values are present and decodable, including `describeServers` calling `v.get()`. `std::stoi` and `UID::fromString` exceptions are not caught locally. Long scans over all keys can be expensive on large clusters.

Test signals: Cover each subcommand, physical vs non-physical filtering, server ID parsing, single key vs range resolution, empty or malformed server list entries, paging over keyServers/serverKeys, and invalid argument handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/LocationMetadataCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/LockCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/LockCommand.cpp

Purpose: Implements database `lock` and `unlock` support using a special key that stores a lock UID.

Important APIs/types/functions: `lockCommandActor`, private `lockDatabase`, exported `unlockDatabaseActor`, `lockSpecialKey`, `deterministicRandom()->randomUniqueID`, and `CommandFactory` registrations for `lock` and `unlock`.

Control flow: `lock` requires no extra tokens, generates a random UID, prints it, and calls `lockDatabase`. `lockDatabase` enables special-key writes, sets `\xff\xff/management/db_locked` to the UID string, commits with retry, returns special-key failure messages, and rethrows `database_locked`. `unlockDatabaseActor` reads the lock key, returns true if absent, compares the stored UID with the provided UID, clears the key on match, commits, and handles special-key failures.

State and persistence behavior: The lock state is a persisted management special key containing the UID string. Unlock requires exact UID match. No local state is persisted.

Dependencies and integration points: Depends on special-key-space lock management and fdbcli higher-level confirmation for unlock, as implied by help text. Locking affects database operations beyond fdbcli.

Risks: Losing the printed UID prevents normal unlock through this command. The file does not itself prompt for unlock confirmation; that must be enforced by dispatch. `UID::fromString` on stored values assumes valid lock metadata.

Test signals: Cover lock success, already-locked error propagation, special-key failure message, unlock absent key, wrong UID, correct UID, malformed stored UID, and retry behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/LockCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/MaintenanceCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/MaintenanceCommand.cpp

Purpose: Implements `maintenance`, marking one zone as under maintenance for a duration, clearing maintenance, or reporting current maintenance state.

Important APIs/types/functions: `maintenanceCommandActor`, private `printHealthyZone`, exported `setHealthyZone`, `clearHealthyZone`, `maintenanceSpecialKeyRange`, and `ignoreSSFailureSpecialKey`.

Control flow: With no args, `printHealthyZone` reads the maintenance range and prints either global storage-failure DD disable, no ongoing maintenance, or zone/duration remaining. `maintenance off` clears maintenance. `maintenance on <ZONEID> <SECONDS>` parses seconds with `sscanf` requiring full-token consumption and writes the zone key with seconds. Both set/clear helpers reject normal maintenance operations while `IgnoreSSFailures` is present unless explicitly clearing that state for data-distribution enablement.

State and persistence behavior: Persists one special-key range entry under `\xff\xff/management/maintenance/`. A key named `IgnoreSSFailures` represents data distribution disabled for storage-server failures rather than ordinary maintenance. No local state.

Dependencies and integration points: Shared with `DataDistributionCommand.cpp`, status warnings, and data distribution's interpretation of maintenance metadata. Uses special-key writes and retry loops.

Risks: Only one maintenance zone is supported and enforced by assumptions (`ASSERT(res.size() <= 1)`). Seconds are stored as a string/double and displayed as integer seconds; negative or zero durations are not rejected at parse time. Confusion between maintenance mode and `IgnoreSSFailures` can leave DD failure response disabled.

Test signals: Cover report states, on/off, invalid seconds, zero/negative duration policy, rejection when storage-failure DD disable is active, clearing with `clearSSFailureZoneString`, and transaction retry.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/MaintenanceCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/ProfileCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/ProfileCommand.cpp

Purpose: Implements `profile` commands for client transaction profiling settings and listing worker process addresses.

Important APIs/types/functions: `profileCommandActor(Database, Reference<ITransaction>, tokens, intrans)`, `db->globalConfig`, global config keys `fdbClientInfoTxnSampleRate` and `fdbClientInfoTxnSizeLimit`, `GlobalConfig::prefixedKey`, `Tuple::makeTuple`, `parse_with_suffix`, and worker-interface range reads.

Control flow: `profile client get` waits for global config initialization, reads sample rate and size limit from the in-memory global config with sentinel defaults, and prints current settings. `profile client set <RATE|default> <SIZE|default>` parses rate with `strtod` or infinity sentinel, parses size with suffix parser or `-1`, enables special-key writes, writes packed tuple values to global config keys, and commits if not inside a transaction. `profile list` scans worker interface special keys and prints IP:port addresses with `:tls` stripped. Invalid type/action/arity prints errors.

State and persistence behavior: Client profiling settings are persisted through global configuration special keys. `profile list` is read-only. In transaction mode, writes are staged but not committed by this actor.

Dependencies and integration points: Depends on global config, tuple encoding, fdbcli transaction mode, worker-interface special keys, and client profiling consumers that observe the global keys.

Risks: `strtod` validation checks for whitespace after the parsed rate; tokens may not be null-terminated in all contexts, so this parsing pattern merits scrutiny. It does not check sample-rate range or size-limit overflow beyond helper behavior. `profile list` asserts no `more` result.

Test signals: Cover get defaults and explicit values, set defaults, numeric rate/size suffix parsing, invalid rate/size, in-transaction staging, worker list TLS stripping, and malformed worker-interface range size.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/ProfileCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/RangeConfigCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/RangeConfigCommand.cpp

Purpose: Implements `rangeconfig`, exposing per-key-range data distribution configuration hints such as replication factor and team ID.

Important APIs/types/functions: `rangeConfigCommandActor(Database, tokens)`, `rangeConfigGenerator`, `DDConfiguration().userRangeConfig()`, `DDRangeConfig`, `DDConfiguration::toJSON`, `SystemDBWriteLockedNow`, `RangeConfigMapSnapshot`, and boost lexical integer parsing.

Control flow: The actor wraps usage/error handling in a local `fail` lambda, then consumes arguments from a list. `show [includeDefault]` reads a snapshot for all keys and prints JSON, optionally including default ranges. `update` and `set` require begin/end plus options, validate `end > begin`, construct a `DDRangeConfig`, parse option pairs (`replication <N>`, `teamID <N>`) or `default`, and call `updateRange` with a boolean indicating exact set vs incremental update. A generator supplies context-sensitive completion hints.

State and persistence behavior: Mutates persisted user range configuration through system DB write-locked DD configuration abstractions. The settings are hints consumed by DataDistribution and do not directly rewrite shard maps.

Dependencies and integration points: Integrates with fdbclient data-distribution configuration, system database write-lock wrappers, JSON rendering, and fdbcli help/completion.

Risks: The `updateRange` call is inside the option loop, so multiple options cause multiple writes as the config object accumulates. If that is intentional it still increases partial-progress considerations if a later option fails before subsequent writes. It does not validate range is within normal keys. Integer option validation is delegated to DD config layers.

Test signals: Cover show with/without defaults, update vs set semantics, default reset, multiple options, missing/invalid option arguments, inverted ranges, unknown commands/options, completion output, and DD config persistence.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/RangeConfigCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/RangeLockCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/RangeLockCommand.cpp

Purpose: Implements `rangelock`, a user-facing range lock management command for registering owners, taking/releasing exclusive read locks, releasing all locks for an owner, and listing locks.

Important APIs/types/functions: `rangeLockCommandActor(Database, tokens)`, `printKnobReminder`, `parseNormalKeyRange`, `reportRangeLockError`, `registerRangeLockOwner`, `removeRangeLockOwner`, `getAllRangeLockOwners`, `takeExclusiveReadLockOnRange`, `releaseExclusiveReadLockOnRange`, `releaseExclusiveReadLockByUser`, `findExclusiveReadLockOnRange`, `RangeLockOwner`, and `RangeLockState`.

Control flow: The actor dispatches on subcommands. `register` and `unregister` validate non-empty owner IDs/descriptions and call owner management APIs. `owners` lists all owners. `take` and `release` validate owner ID and a strict non-empty range within `normalKeys`, then call the range lock API. `release-all` releases every lock by owner. `list` scans either `normalKeys` or a supplied normal range and prints locks. Range-lock API errors are mapped to tailored messages; actor cancellation is rethrown.

State and persistence behavior: Persists owner and lock metadata through fdbclient range-lock management APIs. Lock enforcement depends on commit proxies being started with `knob_enable_read_lock_on_range=true`; the command prints a reminder after taking a lock because metadata alone may not reject writes.

Dependencies and integration points: Depends on `fdbclient/RangeLock.h`, `ManagementAPI`, normal keyspace constants, and fdbcli command registration. Bulk-load debug paths also use related range-lock helpers.

Risks: Enforcement knob cannot be probed by the client, so users can get persisted but unenforced locks. Release requires matching range/owner semantics, which may be surprising. All operations have high coordination impact if lock metadata is wrong.

Test signals: Cover every subcommand, invalid arity, empty owner/description, invalid and system key ranges, overlapping lock errors, unlock reject errors, owner lifecycle, list filtering, knob reminder text, and actor-cancelled propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/RangeLockCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/SetClassCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/SetClassCommand.cpp

Purpose: Implements `setclass`, listing process classes or changing the class type for a registered process address.

Important APIs/types/functions: `setClassCommandActor`, private `printProcessClass`, `setProcessClass`, special ranges `processClassSourceSpecialKeyRange` and `processClassTypeSpecialKeyRange`, `getSpecialKeysFailureErrorMessage`, and `CommandFactory setClassFactory`.

Control flow: No arguments lists all registered process class types and sources by scanning both special-key ranges, asserting they align by size and address order. Two arguments look up the requested address under class type keys, reject if absent, set the class type value, and commit. Invalid arity prints usage.

State and persistence behavior: Process class type changes are persisted via special keys under `\xff\xff/configuration/process/class_type/`. Source metadata is read only. No local state.

Dependencies and integration points: Depends on fdbclient process-class configuration keys, special-key writes, and cluster recruitment/role assignment behavior that consumes process classes.

Risks: The list path assumes type/source ranges are sorted identically and have equal cardinality. Class type strings are not locally validated against the documented enum; invalid values are expected to be rejected by special-key API or downstream validation. Changing process classes can alter role recruitment and performance.

Test signals: Cover listing empty/non-empty process maps, mismatched source/type range detection, unknown address, valid class set, invalid class special-key error, retry behavior, and documented class names.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/SetClassCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/SnapshotCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/SnapshotCommand.cpp

Purpose: Implements hidden `snapshot`, which sends a snapshot command string to all relevant processes through the database API and reports a generated UID for cleanup correlation.

Important APIs/types/functions: `snapshotCommandActor(Reference<IDatabase>, tokens)`, `deterministicRandom()->randomUniqueID`, `Standalone<StringRef>`, `db->createSnapshot(uid, snap_cmd)`, and `CommandFactory snapshotFactory`.

Control flow: The actor requires at least one argument after `snapshot`. It generates a UID string, concatenates all remaining tokens with spaces into `snap_cmd`, calls `createSnapshot`, and prints success with the UID. Errors are caught locally, printed with error code/name and cleanup guidance referencing the UID, and return false.

State and persistence behavior: No local persistence. Snapshot side effects occur on cluster/process storage as implemented by the database API. The generated UID is not stored locally but is essential for manual cleanup if partial snapshots were created.

Dependencies and integration points: Depends on fdbclient snapshot API and hidden fdbcli command dispatch. Operationally tied to instance-level snapshot implementations.

Risks: Hidden but potentially disruptive. Token concatenation preserves spaces between tokens but not original quoting details. Failure may leave external snapshots requiring manual cleanup. Validation of snapshot subcommand semantics is delegated to server-side API.

Test signals: Cover missing args, command string construction, success UID output, API error output including cleanup UID, and quoted/multi-token snapshot command behavior in the top-level parser.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/SnapshotCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/StatusCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/StatusCommand.cpp

Purpose: Implements `status`, rendering FoundationDB cluster status in normal, detailed, minimal, or JSON form from status JSON.

Important APIs/types/functions: Helpers include `getCoordinatorsInfoString`, `lineWrap`, `getNumOfNonExcludedProcessAndZones`, `getNumofNonExcludedMachines`, `logEpochsMayBeLosingData`, `getDateInfoString`, `getProcessAddressByServerID`, `getWorkloadRates`, `getBackupDRTags`, and `logBackupDR`. Public functions include `toBytesString`, `printStatus`, `statusCommandActor`, `statusGenerator`, and `CommandFactory statusFactory`. It uses `StatusObjectReader`, `StatusClient::StatusLevel`, `StatusClient::statusFetcher`, and the special key `\xff\xff/status/json`.

Control flow: `statusCommandActor` selects the output level from tokens, reads status JSON via the multiversion transaction special key when valid or native `StatusClient::statusFetcher` fallback otherwise, parses it, and calls `printStatus`. `printStatus` first handles incompatible outgoing connections, then branches by level. Normal/detailed mode builds one large output string: client/coordination messages, fatal recovery diagnostics, configuration, cluster counts/fault tolerance/server time, data health/size/movement, storage wiggle, operating space, workload, backup/DR, and detailed per-process performance/coordination sections. Minimal mode prints availability/health and cluster-file freshness. JSON mode pretty-prints the raw object.

State and persistence behavior: Read-only. All state is derived from live status JSON and Flow transport compatibility flags. No local or cluster writes.

Dependencies and integration points: Deeply coupled to status JSON schema paths from cluster, client, process, machine, workload, backup, DR, fault tolerance, and QoS subsystems. Also integrates with fdbcli exec mode formatting and command completion.

Risks: Large schema-dependent renderer with many try/catch blocks; missing fields generally degrade to "unknown" or section failure, but some paths can still assume objects exist, such as later use of `processesMap.obj()`. `getNumofNonExcludedMachines` appears to count machines where `excluded` exists and is false, not machines without an excluded field, which may undercount depending on schema. `getDateInfoString` uses localtime and is not timezone-stable in tests. Normal mode can hide messages during fatal recovery based on skip lists.

Test signals: Golden-output tests should cover minimal healthy/unavailable/issues, JSON output, normal and detailed status with unreachable coordinators, fatal recovery states, exclusions, regions/TSS, data loss warnings, DD disabled warnings, backup/DR tags, process performance details, missing/malformed sections, and cluster-file freshness warnings.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/StatusCommand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/SuspendCommand.cpp -->
# sources/storage-engines/foundationdb/fdbcli/SuspendCommand.cpp

Purpose: Implements `suspend`, allowing operators to ask selected processes to suspend for a duration and then die.

Important APIs/types/functions: `suspendCommandActor(Reference<IDatabase>, Reference<ITransaction>, tokens, address_interface)`, `getWorkerInterfaces`, `db->rebootWorker(addresses, false, seconds)`, and `CommandFactory suspendFactory`.

Control flow: With no args, the command refreshes and prints suspendable process addresses. With only a duration token, usage is printed. With duration plus addresses, it validates every address against the cached map, parses seconds using `sscanf` with full-token validation, joins addresses with commas, and sends a reboot-worker request with the suspend duration. It prints attempted count on success or an error suggesting the list be refreshed if no requests were sent.

State and persistence behavior: No metadata is persisted by the command. It uses a transient caller-owned address cache and sends process-control requests that affect live workers.

Dependencies and integration points: Shares worker interface cache behavior with `kill` and `expensive_data_check`, uses boost join and the database reboot API, and depends on fdbcli command dispatch.

Risks: Operationally disruptive. Requires a populated, current address cache; stale cache can reject valid targets or send to outdated addresses. Seconds are cast to `int`, so fractional values are truncated and very large values may overflow. Negative durations are not explicitly rejected.

Test signals: Cover list population, missing address cache, invalid/negative/fractional/large seconds, unknown addresses, successful batching, zero requests sent, and process-control integration behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbcli/SuspendCommand.cpp -->
