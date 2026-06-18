# subset-b-008439 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/S3Client.cpp -->
# sources/storage-engines/foundationdb/fdbclient/S3Client.cpp

## Purpose
`S3Client.cpp` implements FoundationDB's asynchronous file/object transfer helpers for `blobstore://` S3-compatible backup URLs. It supplies the public helpers declared in `fdbclient/S3Client.h`: upload/download of files and directories, deletion, listing, bulk dump file-set upload, and local file checksum calculation. The implementation sits above `S3BlobStoreEndpoint`, `IAsyncFile`, Flow actors, and FoundationDB client knobs, so callers can use a single API for backup, bulk load/dump, CLI, and simulation workload paths without owning HTTP request details.

## Important APIs, types, and functions
`PartState` tracks one multipart transfer part: part number, file offset, size, ETag, per-part MD5 or SHA256 checksum, completion state, and uploaded bytes retained for ordered whole-object checksum calculation. `PartConfig` centralizes multipart size, retry delays, retry counts, retry cap, and checksum-validation enablement, mostly sourced from `CLIENT_KNOBS`.

`calculateFileChecksum()` streams an `IAsyncFile` in 64 KiB reads and returns a hex XXH64 digest. It validates short reads and frees the native xxhash state on both success and `Error` exceptions. `getEndpoint()` parses the `blobstore://` URL through `S3BlobStoreEndpoint::fromString`, applies the global proxy from `g_network`, validates that the `bucket` parameter exists, and restricts resource characters to alnum, `_`, `-`, `.`, and `/`.

Transfer helpers include `uploadPart()`, `copyUpFile(endpoint, bucket, object, filepath)`, public `copyUpFile(filepath, s3url)`, `copyUpDirectory()`, `copyUpBulkDumpFileSet()`, `downloadPart()`, `copyDownFile(endpoint, bucket, object, filepath)`, public `copyDownFile(s3url, filepath)`, `copyDownDirectory()`, `deleteResource()`, `listFiles()`, and `listFiles_impl()`. Checksum helpers prefer S3 object tags named `xxhash64` and fall back to a companion object with suffix `.checksum`.

## Control flow
Uploads parse a URL, open the local file uncached/no-AIO, start a multipart upload, and schedule `uploadPart()` actors in batches bounded by `BLOBSTORE_CONCURRENT_WRITES_PER_FILE`. Each part reads its byte range, computes SHA256/base64 when object integrity checking is enabled or MD5 otherwise, writes the part via `endpoint->uploadPart`, and retries retryable transport/storage errors with exponential delay. After all active futures complete, `copyUpFile()` finishes the multipart upload with the part ETags/checksums, then computes the whole-file XXH64 in part-number order from stored `partData`, writes the checksum tag or sidecar, and logs completion.

Downloads query object size, create the local parent directory, open an atomic read/write file, truncate it to the remote size, and schedule `downloadPart()` actors bounded by `BLOBSTORE_CONCURRENT_READS_PER_FILE`. Each part repeatedly calls ranged `readObject()` until its byte count is satisfied, optionally checks a per-part MD5 if populated, and writes to the local file offset. After all parts complete, the file is synced and the whole-file XXH64 is compared against the tag/sidecar checksum when present. Failure paths close/delete local files or abort multipart uploads where possible, then either retry file-level operations or rethrow.

Listing uses `S3BlobStoreEndpoint::listObjects()` for user-facing output and a lower-level `listFiles_impl()` that performs a list-type=2 GET and parses `ListBucketResult` XML through rapidxml.

## State and persistence behavior
The durable state touched here is outside FoundationDB key-value storage: S3 objects, S3 multipart upload sessions, optional object tags, optional checksum companion objects, and local files. `copyUpBulkDumpFileSet()` deletes an existing destination batch directory before uploading manifest/data/sample files. `copyDownFile()` writes through an atomic local file mode and deletes the partial file on terminal failure. No database transaction state is persisted by this file.

## Dependencies and integration points
The file depends on `S3BlobStoreEndpoint`, HTTP checksum helpers, `IAsyncFileSystem`, Flow actors/futures, `TraceEvent`, `CLIENT_KNOBS`, `platform::findFilesRecursively`, rapidxml, OpenSSL SHA256, libb64, and xxhash. It is used by the `s3client` CLI, bulk load/dump utilities, backup tests, `S3ClientWorkload`, and the `fdbclient/tests/s3client_test.sh` CTest targets. The public wrapper functions are the main integration surface.

## Risks and edge cases
`copyUpFile()` retains every uploaded part's data until after multipart completion so it can compute the ordered XXH64 digest; this avoids concurrent hash-state races but can scale memory usage up to the full file size. Empty remote objects are treated as `file_not_found()` on download because `objectSize <= 0` is rejected. The upload path appears to begin multipart upload even for a zero-length local file, leaving behavior dependent on endpoint handling of an empty ETag map. URL resource character validation is conservative and may reject object names that S3 itself accepts. Checksum validation is best effort for legacy objects: absence of tag and companion file logs `S3ClientNoChecksumFound` and allows download success. Retryable errors are explicitly enumerated, so new endpoint error codes may not retry until added.

## Test signals
Primary signals are `fdbclient/tests/s3client_test.sh`, `gcs_client_test`, bulkload tests that invoke `bin/s3client`, and simulation workloads `S3Client.toml` and `S3ClientWorkloadWithChaos.toml`. Useful assertions include multipart upload/download round trips, checksum tag and sidecar fallback, no-integrity-check knob behavior, listing depth/recursive output, nonexistent bucket/key errors, directory transfer path handling, and injected connection/HTTP failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/S3Client.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/S3Client_cli.cpp -->
# sources/storage-engines/foundationdb/fdbclient/S3Client_cli.cpp

## Purpose
`S3Client_cli.cpp` builds the standalone `s3client` executable around the library helpers in `S3Client.cpp`. It provides command-line `cp`, `ls`, and `rm` operations for FoundationDB `blobstore://` URLs, initializes the Flow network, TLS/blob credentials, knobs, proxy state, and optional tracing, then runs the selected asynchronous S3 operation to completion.

## Important APIs, types, and functions
The `s3client_cli` namespace defines SimpleOpt option IDs and the `Options[]` table for trace flags, blob credentials, TLS options, build flags, knobs, proxy, help, and recursive listing. `Params` is the parsed command model: proxy, tracing fields, `BackupTLSConfig`, knob overrides, source/target, command, URL-side marker, default integrity-check knob name, and `ls_recursive`.

`printUsage()` documents commands and URL format. `parseCommandLine()` validates command arity and whether source or target is a blobstore URL. `Params::updateKnobs()` adds `blobstore_enable_object_integrity_check=true` unless overridden, applies knob overrides with `setupClientKnobs()`, then reinitializes client knobs. `run()` dispatches to `copyUpDirectory`, `copyUpFile`, `copyDownDirectory`, `copyDownFile`, `deleteResource`, or `listFiles`. `main()` owns process setup and error-to-exit-code mapping.

## Control flow
`main()` reconstructs the command line for tracing, parses arguments with `CSimpleOpt`, prints usage on parse/build/help non-success, configures trace output if enabled, sets up TLS, calls `platformInit()`, `Error::init()`, and `setupNetwork()`, then applies knob updates. If no `--proxy` was passed, it reads `FDB_PROXY`; a valid proxy is stored in `g_network->global(INetwork::enProxy)` for `S3Client.cpp` endpoint construction.

After emitting a `ProgramStart` trace event and opening trace files, `main()` loads blob credentials, wraps `run(params)` in `stopAfter`, starts `runNetwork()`, and maps failed futures/exceptions to FoundationDB exit codes. `run()` chooses upload versus download based on which argument starts with `BLOBSTORE_PREFIX`; local directory tests are performed with `std::filesystem::is_directory`.

## State and persistence behavior
The CLI itself persists no database state. It mutates process-global runtime state: network options, trace-file settings, client knobs, TLS/blob-credential configuration, and the global proxy optional. The underlying command may write S3 objects, delete S3 resources, or write local files through the library helpers. Trace files are written when enabled.

## Dependencies and integration points
This executable is declared separately in `fdbclient/CMakeLists.txt` after removing `S3Client_cli.cpp` from library sources. It links Flow, fdbclient, TLS, SimpleOpt, and the S3 client implementation. Shell tests under `fdbclient/tests/s3client_test.sh`, backup test helpers, and bulkload tests invoke `bin/s3client`. The CLI accepts the same blob credential format as backup tooling through `BackupTLSConfig`.

## Risks and edge cases
`--help` and `--build-flags` return `FDB_EXIT_ERROR` after printing, so callers expecting zero for informational commands need to account for current behavior. The usage says `--recursive` is only valid with `ls`, but parsing does not reject it for other commands; it is simply ignored outside `ls`. If a blobstore source is copied to a non-directory target, the path is treated as a file target rather than forcing directory semantics. The default integrity-check knob is enabled by CLI policy, which can differ from library callers unless they set the knob explicitly. Proxy validation only accepts hostname or parsed network address strings.

## Test signals
`s3client_test.sh` is the main behavioral test: upload/download, directory copy, listing, recursive listing, errors for nonexistent resources, empty buckets, credentials, TLS CA handling, and integrity-check knob combinations. Build and smoke coverage also comes from CMake `s3client_test`, `gcs_client_test`, backup tests, and bulkload tests that shell out to the executable.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/S3Client_cli.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/Schemas.cpp -->
# sources/storage-engines/foundationdb/fdbclient/Schemas.cpp

## Purpose
`Schemas.cpp` defines the static JSON schema/example payloads exposed by `JSONSchemas` in `fdbclient/Schemas.h`. These strings describe the expected shape of FoundationDB status JSON, configuration JSON, latency band configuration, management API errors, health snippets, data-distribution stats, and fault-tolerance status. They are used by CLI tools and simulation workloads as validation contracts rather than runtime parsers.

## Important APIs, types, and functions
The file has no functions. It initializes `const KeyRef` members with raw string literals: `statusSchema`, `clusterConfigurationSchema`, `latencyBandConfigurationSchema`, `dataDistributionStatsSchema`, `logHealthSchema`, `storageHealthSchema`, `aggregateHealthSchema`, `managementApiErrorSchema`, and `faultToleranceStatusSchema`.

The large `statusSchema` includes cluster storage wiggler state, layers, processes and roles, logs, fault tolerance, QoS throttling, lag, lock state, gray failure, latency probes, clients, cache stats, messages, recovery state, workload counters, configuration, consistency scan, data distribution, machines, idempotency ids, version epoch, and client/coordinator status. `clusterConfigurationSchema` focuses on configurable redundancy, regions, storage/log engines, workers, proxies, and backup/range backup worker flags. The fault-tolerance schema is a reduced status view centered on logs, fault tolerance, QoS, recovery, maintenance, data, and client coordinator reachability.

## Control flow
There is no executable control flow beyond static initialization of `KeyRef` constants from string literals using the `_sr` suffix. All validation and interpretation happens in consumers that parse these strings with `json_spirit` or custom schema comparison logic.

## State and persistence behavior
No persistent state is read or written. The constants are compiled into the binary and serve as in-memory references. Any schema drift affects validation behavior in downstream tooling and workloads but not stored data directly.

## Dependencies and integration points
Consumers include `StatusWorkload`, `ChangeConfig`, `Throttling`, `DataDistributionMetrics`, `SpecialKeySpaceCorrectness`, `SpecialKeySpaceRobustness`, `fdbcli/Util.cpp`, `fdbcli/FileConfigureCommand.cpp`, `fdbctl/ControlCommands.cpp`, and `fdbserver/core/LatencyBandConfig.cpp`. `managementApiErrorSchema` is used to validate JSON error messages returned through special-key management APIs. A source comment notes that `mr-status-json-schemas.rst.inc` should be updated alongside the status schema, making documentation synchronization an explicit integration point.

## Risks and edge cases
The schemas use a FoundationDB-specific example/schema convention with markers such as `$enum` and `$map`, so generic JSON Schema tooling will not interpret them as standard JSON Schema. The raw strings must remain syntactically valid JSON despite their size; small formatting mistakes can break consumers at runtime. Because many enum lists mirror live status and configuration strings from other modules, drift can create false test failures or allow incomplete coverage. Some fields are examples rather than exhaustive machine-checkable constraints, so passing validation does not prove all production payload invariants.

## Test signals
Schema consumers are the test signals. `StatusWorkload` parses status schema, `ChangeConfig` and file configuration paths validate configuration and management API error shapes, `Throttling` validates health schemas, `DataDistributionMetrics` validates data distribution stats, and special-key-space workloads validate management errors and fault-tolerance status. A useful guard is to parse every constant as strict JSON and run the existing simulation workloads that compare live JSON to these examples.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/Schemas.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/SpecialKeySpace.cpp -->
# sources/storage-engines/foundationdb/fdbclient/SpecialKeySpace.cpp

## Purpose
`SpecialKeySpace.cpp` implements FoundationDB's virtual `\xff\xff/...` key space on the client side. It routes special-key reads to synthetic data sources, records special-key writes in the `ReadYourWritesTransaction` write map, and commits selected writes as management/configuration operations against real system keys or external cluster APIs. It is the client bridge between normal transaction syntax and features such as conflict-range inspection, status/metrics, exclusions, process classes, coordinators, global config, tracing, actor lineage, maintenance mode, and data-distribution controls.

## Important APIs, types, and functions
Static maps define module boundaries (`TRANSACTION`, `WORKERINTERFACE`, `STATUSJSON`, `CONNECTIONSTRING`, `CLUSTERFILEPATH`, `METRICS`, `MANAGEMENT`, `ERRORMSG`, `CONFIGURATION`, `GLOBALCONFIG`, `TRACING`, `ACTORLINEAGE`, `ACTOR_PROFILER_CONF`, `CLUSTERID`), management command subranges, actor-lineage subranges, management options, and tracing options. `SpecialKeySpace::registerKeyRange()` registers read-only or read-write implementations inside module boundaries and validates snake-case key names.

The core read machinery is `getRange()`, `checkRYWValid()`, `getRangeAggregationActor()`, `normalizeKeySelectorActor()`, and `moveKeySelectorOverRangeActor()`. These normalize key selectors, enforce cross-module restrictions unless relaxed mode is enabled, aggregate registered implementation ranges, honor reverse and limit behavior, and cache first async reads where selector normalization and final result filtering would otherwise repeat RPC work. `get()` is implemented through a one-key `getRange()`.

Write machinery is `set()`, `clear(key/range)`, `decode()`, and `commitActor()`. Writes require `specialKeySpaceChangeConfiguration`; range clears cannot cross write modules. `commitActor()` scans the transaction's special-key write map, deduplicates touched write modules, calls each module's `commit()`, stores JSON error text in the transaction on failure, and throws `special_keys_api_failure()`.

Important module implementations include conflict range readers, data-distribution metrics, management options, excluded/failed server and locality ranges, exclusion-in-progress status, process class/source, database lock, consistency check suspension, global config, tracing options, coordinators and auto coordinators, advance version, version epoch, client profiling, actor lineage, actor profiler config, maintenance mode, data distribution mode/rebalance ignore, worker interfaces, fault tolerance metrics, and simulation-only subrange validation.

## Control flow
Reads enter from `ReadYourWrites.actor.cpp` when a transaction reads special keys. Selectors are converted to first-greater-or-equal form, the module boundary is selected, and every intersecting registered implementation contributes sorted `RangeResult` entries. `rywGetRange()` overlays local special-key writes onto read results unless read-your-writes is disabled, matching normal RYW behavior for sets and clears.

Writes enter from transaction `set`/`clear` calls. The selected write implementation records an entry in `specialKeySpaceWriteMap`; most values are validated only during commit. On transaction commit, `ReadYourWrites` calls `DatabaseContext::specialKeySpace->commit()`, which dispatches to each touched module. Commit actors then translate virtual operations into real actions: setting system keys, clearing configuration keys, invoking management helpers like `excludeServers`, `excludeLocalities`, `changeQuorumChecker`, or `GlobalConfig::applyChanges`, or returning a `ManagementAPIError` JSON string.

Several readers issue RPCs or system-key reads: actor lineage opens a process interface for the requested host and asks for actor lineage samples; worker interface reads can optionally verify connectivity; fault-tolerance metrics calls `getJSON`; exclusion-in-progress combines excluded servers/localities, server list, and logs; DD metrics waits for the data distributor metrics list.

## State and persistence behavior
Special-key reads are virtual, but many commits persist to real system state. Exclusion modules map management keys to `\xff/conf/` excluded/failed server/locality keys and version keys. Locking writes `databaseLockedKey`; consistency check writes `fdbShouldConsistencyCheckBeSuspended`; global config writes through `GlobalConfig::applyChanges` and trims recent history; coordinator changes update the cluster connection record through quorum-change machinery; advance version writes `minRequiredCommitVersionKey`; version epoch writes `versionEpochKey`; client profiling writes global config keys; maintenance writes `healthyZoneKey`; data distribution writes `dataDistributionModeKey`, `rebalanceDDIgnoreKey`, and move-keys lock owner/write keys. Actor profiler configuration is process-local via `ProfilerConfig::instance().reset(config)`.

## Dependencies and integration points
`DatabaseContext` constructs `SpecialKeySpace` and registers concrete implementations. `ReadYourWrites.actor.cpp` routes reads, writes, clears, relaxed-mode reads, change-configuration commits, and error-message handling through this file. Management API helpers build special-key transactions for exclusions and localities. Consumers include fdbcli/fdbctl management commands, simulation workloads `SpecialKeySpaceCorrectness` and `SpecialKeySpaceRobustness`, status/fault-tolerance tooling, actor lineage/profiler code, `GlobalConfig`, `StatusClient`, and cluster connection/coordinator code.

## Risks and edge cases
Selector normalization is subtle: it may query implementation ranges while moving offsets across sparse virtual ranges, and bugs here can create off-by-one, reverse-read, or limit/`more` inconsistencies. Cross-module reads and clears are intentionally rejected in normal mode, so callers must use precise ranges or relaxed mode. Commit ordering is by first appearance of touched ranges after deduplication, not by an explicit dependency graph; modules that rely on options written in another range must read the shared write map carefully.

Exclusion safety depends on status JSON fields and can fail closed when status is incomplete. In the locality exclusion path inside `checkExclusion()`, the code condition for appending `addrExclusion` appears inverted (`find(...) != end()` before `push_back`), which risks not adding new addresses for failed locality safety checks. `DataDistributionImpl::commit()` computes a management error for invalid `rebalance_ignored` values but does not assign it to `msg`, so invalid non-integer input may not surface as intended. `ActorProfilerConf::set()` mutates the in-memory config before commit succeeds, so failed transactions may still have process-local side effects until reset. Actor lineage keys embed a user-supplied host and open a well-known endpoint on every read, so malformed ranges and unavailable processes turn reads into API failures.

## Test signals
The most direct coverage is `fdbserver/workloads/SpecialKeySpaceCorrectness.cpp` and `SpecialKeySpaceRobustness.cpp`, including read normalization, management error schema validation, options, invalid address handling, and fault-tolerance reads. `ChangeConfig`, `DataDistributionMetrics`, `Throttling`, fdbcli/fdbctl management commands, actor lineage/profiler tests, and status workloads are integration signals. High-value tests include cross-module read/clear rejection, RYW overlay behavior, reverse reads with byte/count limits, exclusion safety with force options, localities with failed mode, coordinator validation, global config history trimming, and failure propagation through `\xff\xff/error_message`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/SpecialKeySpace.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/StackLineage.cpp -->
# sources/storage-engines/foundationdb/fdbclient/StackLineage.cpp

## Purpose
`StackLineage.cpp` exposes a small helper for retrieving the current Flow actor stack lineage as a vector of actor-name `StringRef`s. It is part of the actor lineage/profiling support used to report or inspect where execution is within nested actor contexts.

## Important APIs, types, and functions
The file includes `fdbclient/StackLineage.h` and defines `getActorStackTrace()`. The function dereferences the thread-local `currentLineage` pointer and calls `stack(&StackLineage::actorName)`, returning the lineage stack for the `StackLineage` property. A `StackLineageCollector` instantiation is present only as commented-out code in an anonymous namespace.

## Control flow
There is no asynchronous control flow. Callers synchronously invoke `getActorStackTrace()`, which walks the current lineage object through the Flow lineage API and returns the collected actor-name stack.

## State and persistence behavior
No persistent state is written. The function reads the thread-local lineage maintained by Flow (`currentLineage`) and returns references owned by lineage data. The commented collector means this translation unit currently does not register an additional collector at static initialization.

## Dependencies and integration points
The helper depends on Flow lineage primitives declared in `flow/flow.h` and the `StackLineage` property declared in `StackLineage.h`. `fdbserver/SigStack.cpp` calls `getActorStackTrace()` when producing signal stack diagnostics. Flow actor/coroutine code updates `currentLineage`, while actor lineage profiler code can use related lineage references.

## Risks and edge cases
Correctness relies on `currentLineage` being initialized for the calling thread and on lineage entries remaining valid for the returned `StringRef` vector. If actor compiler lineage annotation is disabled or not populated, the returned stack may be empty or less useful. Because the collector is commented out, any expected automatic collection behavior must come from other registration paths, not this file.

## Test signals
Useful checks are signal-stack diagnostics that include actor names, unit or integration tests that run nested Flow actors and assert `getActorStackTrace()` returns the expected order, and actor-lineage/profiler smoke tests that verify lineage remains available across coroutine boundaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/StackLineage.cpp -->
