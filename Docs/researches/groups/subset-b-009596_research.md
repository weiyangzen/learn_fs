# Group Research: subset-b-009596

Grouped research for gcsfuse integration test sources. Each section preserves the exact source path and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/concurrent_operations/concurrent_read_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/concurrent_operations/concurrent_read_test.go

Purpose: defines the `concurrent_operations` read stress suite for gcsfuse mounts. It validates large-file concurrent read correctness under sequential reads, random chunk reads, shared-handle `ReadAt`, and concurrent write-then-read workloads.
Important APIs and functions: `concurrentReadTest` embeds `suite.Suite`; `SetupSuite`, `SetupTest`, `TearDownSuite`, and `TearDownTest` mount/unmount and prepare `testEnv.testDirPath`; tests use `operations.CreateFileOfSize`, `ReadFileSequentially`, `ReadChunkFromFile`, `CalculateCRC32`, and GCS storage `Object.Attrs`.
Control flow: `TestConcurrentRead` either runs once against a pre-mounted GKE directory or iterates `setup.BuildFlagSets`. Each scenario launches goroutines with a `sync.WaitGroup`, waits through a timeout channel, and fails fast on suspected deadlock or performance regressions.
State and persistence: source state is in mounted files under `testEnv.testDirPath` and backing GCS objects in the configured test bucket. The tests compare mounted reads against GCS CRC32C or object chunk contents, so persistence is validated across the FUSE/GCS boundary.
Dependencies and integration points: depends on shared setup/client/operations utilities, Cloud Storage client, static/dynamic config from `setup_test.go`, `syscall.O_DIRECT`, and `testify` assertions. It is integrated into e2e package selection through the `TestConcurrentRead` run name.
Risks and edge cases: goroutine assertions call `require` from worker goroutines, which can obscure failures if not synchronized by `testify`; global `math/rand` is used after constructing but not using a local RNG. Timeouts are intentionally broad but can still be environment-sensitive for 100 MiB files.
Test signals: success means all concurrent paths finish within 300 seconds and CRC/chunk comparisons match GCS. Failures indicate deadlocks, corrupted reads, broken shared-handle `ReadAt`, direct-IO issues, or upload/read consistency regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/concurrent_operations/concurrent_read_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/concurrent_operations/setup_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/concurrent_operations/setup_test.go

Purpose: package-level setup for concurrent operation integration tests. It loads test configuration, creates the shared storage client, selects bucket type, configures default flag matrices, and chooses static mounting for package execution.
Important APIs and types: constants `testDirName`, `GKETempDir`, `onlyDirMounted`; global `testEnv`, `mountFunc`, `mountDir`, `rootDir`; `env` holds storage client, context, test directory, `TestConfig`, and bucket type; `TestMain` owns process-wide setup.
Control flow: `TestMain` parses setup flags, reads `test_config.yaml`, populates fallback `ConcurrentOperations` config when absent, initializes environment and storage client, handles mounted-directory mode separately, otherwise prepares the test bucket directory and runs the test binary.
State and persistence: persistent test data is under `TestConcurrentOperations` in the selected bucket. Config flags may rewrite cache directories under `/gcsfuse-tmp`; cleanup removes the GCS test directory after test execution.
Dependencies and integration points: integrates `test_suite.ReadConfigFile`, `setup.TestEnvironment`, `client.CreateStorageClientWithCancel`, `static_mounting.MountGcsfuseWithStaticMountingWithConfigFile`, and `setup.BuildFlagSets` consumed by individual test files.
Risks and edge cases: fallback config hard-codes run names for both read and listing tests, so renaming tests can silently skip cases. Mounted-directory mode requires both `GKEMountedDirectory` and `TestBucket`; cache path overrides must stay aligned with GKE/GCE paths.
Test signals: correct setup is visible through successful mount selection, generated flag subtests, created test directories, and final cleanup without leaked bucket prefixes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/concurrent_operations/setup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/create_package_runtime_table.sh -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/create_package_runtime_table.sh

Purpose: renders e2e package runtime statistics as a Rich terminal table. It is invoked by the improved e2e runner after package execution to visualize package attempts, wait time, run time, and pass/fail/flaked status.
Important APIs/functions: shell `main` validates one input file, creates a temp venv, writes an embedded Python script, installs `python3-dev`, `python3-venv`, and `rich`, then executes the Python visualizer. Python groups lines by package and bucket type and renders `Table` columns for package, bucket, time, timeline, and status.
Control flow: the shell validates arguments and file existence before venv setup. Python parses space-separated records with fields package, bucket type, exit code, start seconds, and end seconds; invalid short rows are ignored. Runtime bars are built from sorted attempts using wait and run segments.
State and persistence: only temporary venv/script state is persisted during execution and removed by `trap`. Input data is read-only; no test logs are modified.
Dependencies and integration points: depends on repo `perfmetrics/scripts/os_utils.sh`, Python 3 venv support, pip/PyPI access, terminal width detection, and the runtime stats file produced by `improved_run_e2e_tests.sh`.
Risks and edge cases: installing system packages and pip dependencies during reporting can fail or slow CI; failures intentionally print warnings and skip visualization. Input parsing assumes package names and bucket types have no spaces.
Test signals: useful output is a table where green pass, yellow flake, red failure, and timeline bars reflect the stats file. Exit 0 on prerequisite failure means report rendering is non-critical.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/create_package_runtime_table.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/dentry_cache/delete_operation_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/dentry_cache/delete_operation_test.go

Purpose: verifies delete behavior when a cached dentry points to an object whose GCS generation/content has changed behind gcsfuse. It checks that removing a clobbered file through the mount succeeds rather than returning stale-handle errors.
Important APIs/types/functions: `deleteOperationTest` suite stores flags, storage client, context, and `suite.Suite`; lifecycle methods mount and create a fresh test directory; `TestDeleteFileWhenFileIsClobbered` is the core scenario.
Control flow: setup creates the test dir directly on GCS, stats the mounted file to populate dentry/kernel metadata cache, overwrites the backing object via the storage client, then calls `os.Remove` on the mounted path and asserts no error.
State and persistence: initial and updated object contents live in GCS under `testDirName/testName`; mounted path state is intentionally stale until deletion. The test is about reconciling cached metadata with backend object mutation.
Dependencies and integration points: uses dentry cache flags from `setup_test.go`, `client.SetupFileInTestDirectory`, `client.WriteToObject`, `operations.GenerateRandomData`, Cloud Storage `storage.Conditions{}`, and `testify`.
Risks and edge cases: it validates only successful delete, not the final absence from GCS. It assumes the preceding `os.Stat` is enough to populate the relevant cache and that direct GCS overwrite changes the generation observed by gcsfuse.
Test signals: failure means dentry-cache delete paths mishandle clobbered objects, potentially surfacing unnecessary ESTALE or unlink failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/dentry_cache/delete_operation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/dentry_cache/notifier_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/dentry_cache/notifier_test.go

Purpose: tests dentry-cache notifier behavior after stale read/write/delete errors. It ensures the first operation detects an externally changed or deleted object, invalidates cached kernel metadata, and allows the next operation to observe fresh state before TTL expiry.
Important APIs/types/functions: `notifierTest` suite lifecycle mirrors other dentry tests. Core tests are `TestWriteFileWithDentryCacheEnabled`, `TestReadFileWithDentryCacheEnabled`, and `TestDeleteFileWithDentryCacheEnabled`.
Control flow: each test creates or deletes GCS state behind the mounted path after an initial `os.Stat` warms cache. The first read/write is expected to raise ESTALE; the second read/write should succeed after notifier invalidation. Delete case expects a later `os.Stat` to report missing.
State and persistence: GCS is the source of truth while kernel and metadata caches are intentionally stale. Notifier side effects are transient cache invalidations, not persistent object changes except for test writes.
Dependencies and integration points: uses `client.SetupFileInTestDirectory`, `WriteToObject`, `DeleteObjectOnGCS`, `operations.WriteFile`, `ReadFile`, and `ValidateESTALEError`. It relies on high TTL fallback config so success is attributable to notifier behavior rather than expiry.
Risks and edge cases: ordering assumes immediate notifier invalidation after the first failed operation. Log-based confirmation is absent; behavior is inferred from the second operation and stat result.
Test signals: ESTALE on the first clobbered access plus success/fresh not-found on the next access validates notifier-driven dentry invalidation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/dentry_cache/notifier_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/dentry_cache/setup_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/dentry_cache/setup_test.go

Purpose: process-wide setup for dentry-cache integration tests. It configures fallback flag sets for stat, delete, and notifier suites and establishes the common storage client, mount function, mount dir, and root dir.
Important APIs/types/functions: constants `testDirName`, `initialContentSize`, `updatedContentSize`; global `testEnv`, `mountFunc`, `mountDir`, `rootDir`; `env`; helper `mountGCSFuseAndSetupTestDir`; and `TestMain`.
Control flow: `TestMain` parses flags, reads config, populates fallback `DentryCache` config with `--implicit-dirs --experimental-enable-dentry-cache` and TTL variants, detects bucket type, creates a storage client, handles mounted-directory mode, and otherwise runs static mounting tests.
State and persistence: setup creates test directories under `testDirForDentryCache` and stores config-derived mount/log state. Unlike some packages, there is no final explicit GCS cleanup in this file beyond per-test directory setup.
Dependencies and integration points: integrates `test_suite`, `setup`, `client`, and `static_mounting`. Test files call `setup.BuildFlagSets` using run names configured here.
Risks and edge cases: fallback run names must match exported test functions. TTL differences are critical: stat tests need short expiry, delete/notifier tests need long expiry to prove invalidation rather than natural timeout.
Test signals: successful setup yields separate flag-driven suite runs across compatible bucket types with dentry cache enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/dentry_cache/setup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/dentry_cache/stat_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/dentry_cache/stat_test.go

Purpose: validates stat behavior with dentry cache enabled when backing GCS objects are updated or deleted outside the mount. It checks both cached stale attributes and refresh after TTL expiry.
Important APIs/types/functions: `statWithDentryCacheEnabledTest` suite, lifecycle methods, `TestStatWithDentryCacheEnabled`, and `TestStatWhenFileIsDeletedDirectlyFromGCS`.
Control flow: tests create an object, `os.Stat` the mounted file to cache the entry, mutate or delete the object directly on GCS, then stat immediately and after sleeping just over the configured two-second TTL.
State and persistence: backend object content/absence persists in GCS. Mounted stat results are expected to reflect cached state first, then refreshed GCS state after TTL expiry.
Dependencies and integration points: uses dentry setup fallback flags, Cloud Storage client helpers, `operations.GenerateRandomData`, `client.WriteToObject`, `client.DeleteObjectOnGCS`, and `time.Sleep`.
Risks and edge cases: fixed `2100ms` sleep is close to TTL and can be flaky on slow environments or if cache expiration uses coarse scheduling. It does not inspect logs, relying on observed sizes and errors.
Test signals: immediate stat returns initial size despite backend mutation/deletion; post-TTL stat returns updated size or not-found. Failures isolate stale/expiry behavior in metadata/dentry cache.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/dentry_cache/stat_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/config.yaml -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/config.yaml

Purpose: minimal proxy-server configuration for emulator tests that need a pass-through target to the storage testbench JSON endpoint.
Important keys: `targetHost: http://localhost:9000`, matching the storage-testbench HTTP endpoint started by `emulator_tests.sh`.
Control flow: no executable logic; the proxy server consumes this YAML to route requests to the emulator without injected retry, stall, or validation behavior.
State and persistence: holds endpoint configuration only. Persistent test state remains in the storage testbench bucket and mounted files.
Dependencies and integration points: used by proxy-server tooling under `tools/integration_tests/proxy_server` and by tests/util helpers that launch the proxy with `--config-path`.
Risks and edge cases: assumes the emulator is listening on localhost port 9000 and that tests run with host networking. Port mismatch causes proxy startup or request failures.
Test signals: success is indirect: proxy starts, logs listening port/PID, and storage clients using `STORAGE_EMULATOR_HOST` reach the emulator.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/empty_gcs_file_2nd_chunk_upload_returns412.yaml -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/empty_gcs_file_2nd_chunk_upload_returns412.yaml

Purpose: proxy fault-injection config for streaming-write failure tests against an existing empty GCS object. It forces a 412 response during the second chunk upload path.
Important keys: `targetHost` points to the HTTP testbench; `retryConfig` targets `JsonCreate`, uses `retryInstruction: return-412`, `retryCount: 1`, and `skipCount: 4`.
Control flow: the proxy ignores the first four matching calls because they create the test directory, create the empty object, create the resumable upload URI, and upload the first chunk. The next eligible `JsonCreate` returns 412.
State and persistence: no persisted state beyond proxy counters. It is designed so the original empty GCS object remains unchanged after write failure.
Dependencies and integration points: consumed by `empty_gcs_file_failure_test.go` through `commonFailureTestSuite.setupTest` and `StartProxyServer`.
Risks and edge cases: the skip count is tightly coupled to the storage client's request sequence. SDK/protocol changes can shift call counts and make the injected failure hit the wrong request.
Test signals: streaming-write tests should see write/sync/close failures while GCS validation still finds an empty object.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/empty_gcs_file_2nd_chunk_upload_returns412.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/grpc_header_validation.yaml -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/grpc_header_validation.yaml

Purpose: configures the proxy server as a gRPC metadata validator for DirectPath header behavior against storage-testbench's gRPC endpoint.
Important keys: `proxyType: grpc`, `targetHost: localhost:8888`, and two `headerValidation` rules for `x-goog-request-params` matching `force_direct_connectivity=ENFORCED` and `direct_connectivity_diagnostic`.
Control flow: for matching gRPC calls, the proxy inspects metadata and fails on mismatch. Tests later scan proxy logs for validation success and expected method names.
State and persistence: stores validation rules only. Runtime state is proxy log content and the emulator bucket.
Dependencies and integration points: used by `grpc_header_validation_test.go`, which starts the proxy and mounts gcsfuse with `--client-protocol=grpc` plus localhost custom endpoint.
Risks and edge cases: depends on Go Storage SDK metadata formatting and DirectPath diagnostic keys. Method counts in tests can change if gcsfuse adds prefetch or extra validation calls.
Test signals: proxy logs contain `Metadata validation passed`, request params, diagnostic metadata, and expected `google.storage.v2.Storage` method paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/grpc_header_validation.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/local_file_2nd_chunk_upload_returns412.yaml -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/local_file_2nd_chunk_upload_returns412.yaml

Purpose: proxy fault-injection config for streaming writes to a new local file. It returns 412 on the second chunk upload without an existing GCS object.
Important keys: `targetHost`, `retryConfig` for `JsonCreate`, `retryInstruction: return-412`, `retryCount: 1`, and `skipCount: 3`.
Control flow: the proxy skips test directory creation, resumable upload session creation, and first chunk upload, then injects the 412 into the next matching JSON create/upload request.
State and persistence: proxy counters are transient. The expected persistent result is that no completed GCS object exists after the failed upload path.
Dependencies and integration points: used by `new_local_file_failure_test.go` through the common failure suite and storage client bound to the proxy endpoint.
Risks and edge cases: skip count is request-sequence-sensitive and may break if gcsfuse creates additional objects or the SDK changes resumable upload flow.
Test signals: failure tests should produce write errors and `ValidateObjectNotFoundErrOnGCS` should pass before block-writer reinitialization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/local_file_2nd_chunk_upload_returns412.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/read_stall_5s.yaml -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/read_stall_5s.yaml

Purpose: injects a controlled XML read stall for read-stall retry tests. It makes the first eligible read hang for five seconds immediately after zero kilobytes.
Important keys: `targetHost`, `retryConfig` method `XmlRead`, `retryInstruction: stall-for-5s-after-0K`, `retryCount: 1`, and `skipCount: 0`.
Control flow: the proxy stalls the first read, allowing tests to verify that gcsfuse's read-stall retry timeout cancels/retries before the full stall elapses.
State and persistence: no persistent state beyond proxy counters/logs. File data is created in the emulator bucket by the test.
Dependencies and integration points: consumed by `read_stall_test.go` through `StartProxyServer` and `AppendProxyEndpointToFlagSet`.
Risks and edge cases: timing assertions depend on scheduler and emulator responsiveness; if stall injection moves to a different protocol path the test may not exercise retry logic.
Test signals: first-byte read elapsed time should exceed configured minimum timeout but stay below the forced five-second stall.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/read_stall_5s.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/write_stall_40s.yaml -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/write_stall_40s.yaml

Purpose: injects a single 40-second stall during resumable JSON write upload after 15 MiB, for chunk-transfer timeout and infinite-timeout tests.
Important keys: `targetHost`, `retryConfig` method `JsonCreate`, `retryInstruction: stall-for-40s-after-15360K`, `retryCount: 1`, and `skipCount: 2`.
Control flow: the proxy skips initial file creation and resumable upload session creation, then stalls the first actual upload request matching the threshold.
State and persistence: proxy tracks injected count; test file data persists in the emulator bucket if retries succeed.
Dependencies and integration points: used by `writes_stall_on_sync_test.go` scenarios `SingleStall` and `chunkTransferTimeoutInfinity`.
Risks and edge cases: relies on a 50 MiB file and upload chunking crossing the 15 MiB point. Upload block size changes can alter where the stall is triggered.
Test signals: sync duration is at least 40 seconds for infinite timeout, or bounded near configured timeout for retry-enabled scenarios.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/write_stall_40s.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/write_stall_twice_40s.yaml -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/write_stall_twice_40s.yaml

Purpose: injects two 40-second resumable upload stalls to validate accumulated chunk transfer timeout behavior across multiple retry attempts.
Important keys: same `JsonCreate` and `stall-for-40s-after-15360K` instruction as the single-stall config, with `retryCount: 2` and `skipCount: 2`.
Control flow: after the initial skipped setup calls, two eligible upload requests are stalled. The test expects total elapsed time to reflect two configured chunk-transfer timeouts.
State and persistence: transient proxy counters determine how many upload attempts stall. Completed object state is validated through successful write/sync.
Dependencies and integration points: used by the `MultipleStalls` subcase in `TestChunkTransferTimeout`.
Risks and edge cases: exact elapsed assertions are sensitive to retry scheduling and fixed five-second slack. Any SDK retry/backoff changes may require tolerance adjustment.
Test signals: elapsed sync time should be greater or equal to twice the chunk transfer timeout and less than that plus the slack window.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/write_stall_twice_40s.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/write_stalls_four_times_60s.yaml -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/write_stalls_four_times_60s.yaml

Purpose: injects four long resumable upload stalls to validate `--chunk-retry-deadline-secs` success and failure boundaries.
Important keys: `JsonCreate`, `stall-for-60s-after-15360K`, `retryCount: 4`, and `skipCount: 2`.
Control flow: first four eligible upload attempts stall. Tests combine this with a 10-second chunk transfer timeout so the client accumulates about 40 seconds of failed attempts before the next attempt can succeed, unless the retry deadline is shorter.
State and persistence: proxy counters are runtime-only. The outcome is either a completed object after retries or an error before completion.
Dependencies and integration points: consumed by `TestChunkRetryDeadline`.
Risks and edge cases: assumes transfer timeout, retry deadline, and proxy stall durations interact deterministically. Slow hosts may blur elapsed-time expectations.
Test signals: deadline 120s should succeed after the induced retry sequence; deadline 32s should fail with a sync/write error.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/write_stalls_four_times_60s.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/emulator_tests.sh -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/emulator_tests.sh

Purpose: orchestration script for all emulator-backed integration tests. It installs/validates Docker, starts storage-testbench HTTP and gRPC endpoints, creates `test-bucket`, and runs `go test` for `./tools/integration_tests/emulator_tests/...`.
Important functions and variables: `log_info`, `log_error`, `wait_for_emulator`, `cleanup`, `TEST_INSTALLED_PACKAGE`, `GCSFUSE_PREBUILT_DIR`, `STORAGE_EMULATOR_HOST`, `STORAGE_EMULATOR_HOST_GRPC`, docker image/name variables, and final `args` passed to Go tests.
Control flow: validates mutually exclusive package/prebuilt modes, skips arm64 and old Go, installs Docker/lsof if needed, pulls/runs storage-testbench with host networking and extended Gunicorn timeout, waits for readiness, creates bucket, starts gRPC on port 8888, then runs tests serially with `-p 1`.
State and persistence: creates a Docker container, `emulator_container.log`, temporary `test.json`, and environment variables. Cleanup stops the container, unsets emulator env vars, prints logs, and removes temp JSON.
Dependencies and integration points: depends on Linux host networking, sudo Docker, curl, Go tooling, storage-testbench image, and optional built gcsfuse path from the parent e2e runner.
Risks and edge cases: host networking and fixed ports can conflict with other local services. Docker installation mutates the host. Serial package execution reduces CPU pressure but can lengthen CI time.
Test signals: readiness curl, successful bucket creation, HTTP 200 from `/start_grpc`, and passing `go test` establish emulator infrastructure health.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/emulator_tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/grpc_header_validation/grpc_header_validation_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/grpc_header_validation/grpc_header_validation_test.go

Purpose: verifies that gcsfuse's gRPC client sends DirectPath-related metadata headers through a proxy to the emulator gRPC testbench.
Important APIs/types/functions: `grpcHeaderValidation` suite with proxy port/PID/log/config/flags fields; `SetupTest`, `TearDownTest`, `TestGRPCClientSendsExpectedHeaders`, `TestGRPCHeadersInMultipleOperations`, and `TestGRPCHeaderValidation`.
Control flow: setup starts the gRPC validation proxy, appends `--custom-endpoint` and `--anonymous-access`, then mounts with `--client-protocol=grpc`. Tests either rely on mount-triggered DirectPath calls or perform write/read/stat/list operations and inspect proxy logs.
State and persistence: mounted file operations create test data in the emulator bucket. Validation state is proxy log text, including metadata validation markers and method names.
Dependencies and integration points: integrates emulator util `StartProxyServer`, static mount setup, config `grpc_header_validation.yaml`, and storage-testbench gRPC server from `emulator_tests.sh`.
Risks and edge cases: method count assertions are brittle if gcsfuse adds extra `GetObject`, prefetch, or validation calls. The localhost gRPC endpoint requires anonymous access.
Test signals: logs must include DirectPath metadata patterns, diagnostic value `no_auth`, `Metadata validation passed`, and expected counts for GetObject/BidiWriteObject/ReadObject/ListObjects.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/grpc_header_validation/grpc_header_validation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/grpc_header_validation/setup_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/grpc_header_validation/setup_test.go

Purpose: package-level setup for emulator gRPC header validation tests. It prepares a static mounting function and root mount directory for tests that run only against the emulator-created test bucket.
Important APIs and state: globals `mountFunc` and `rootDir`; `TestMain` parses setup flags, rejects mounted-directory mode, calls `setup.SetUpTestDirForTestBucketFlag`, sets `rootDir = setup.MntDir()`, and selects `static_mounting.MountGcsfuseWithStaticMounting`.
Control flow: if `--mountedDirectory` is set, the package logs and returns without running tests. Otherwise it prepares test-dir state and executes the package tests.
State and persistence: no storage client is created here; state is limited to mount root and setup flags. Actual file/object state is managed in test methods through mounted paths and emulator config.
Dependencies and integration points: consumed by `grpc_header_validation_test.go`, which calls `setup.MountGCSFuseWithGivenMountFunc(g.flags, mountFunc)` and unmounts `rootDir`.
Risks and edge cases: returning from `TestMain` instead of `os.Exit(0)` for mounted-directory mode may be surprising but effectively skips. Fixed static mounting means dynamic/only-dir modes are not covered.
Test signals: successful setup lets tests start proxy and mount using the configured static mount function.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/grpc_header_validation/setup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/read_stall/read_stall_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/read_stall/read_stall_test.go

Purpose: validates read-stall retry behavior by forcing the proxy to stall the first read and asserting gcsfuse retries fast enough to complete before the full stall duration.
Important APIs/types/functions: constants `fileSize`, `forcedStallTime`, `minReqTimeout`; `readStall` suite; lifecycle methods; `TestReadFirstByteStallInducedShouldCompleteInLessThanStallTime`; and package entry `TestReadStall`.
Control flow: setup starts the `read_stall_5s.yaml` proxy, appends endpoint flags, mounts, and creates a per-test directory. The test writes a 5 MiB file, reads the first byte through `emulator_tests.ReadFirstByte`, and asserts elapsed time is greater than minimum timeout but less than the five-second injected stall.
State and persistence: the test file is created in the mounted emulator bucket and read through the proxy. Proxy logs are saved on failure.
Dependencies and integration points: depends on emulator util, setup operations, static mount setup, and read-stall flags `--enable-read-stall-retry`, `--read-stall-min-req-timeout`, and `--read-stall-initial-req-timeout`.
Risks and edge cases: timing windows are environment-sensitive; the lower bound proves the stall path was likely hit, while the upper bound proves retry behavior.
Test signals: elapsed time in `[minReqTimeout, forcedStallTime)` plus no read error indicates read-stall retry is active and bounded.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/read_stall/read_stall_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/read_stall/setup_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/read_stall/setup_test.go

Purpose: package setup for read-stall emulator tests. It defines shared mount/test directory variables and chooses static mounting against the emulator test bucket.
Important APIs and state: globals `testDirPath`, `mountFunc`, and `rootDir`; `TestMain` parses setup flags, skips mounted-directory mode, sets up the test bucket flag, records `rootDir`, and assigns `static_mounting.MountGcsfuseWithStaticMounting`.
Control flow: mounted-directory mode logs and returns. Normal mode initializes test directory support, runs all tests, and exits with their status.
State and persistence: state is process-global and consumed by `read_stall_test.go`; test-created files persist only for the lifetime of the emulator bucket.
Dependencies and integration points: integrates with `emulator_tests.sh` environment variables and `setup.SetUpTestDirForTestBucketFlag`.
Risks and edge cases: static-only coverage misses dynamic mount behavior. The package assumes the parent script created `test-bucket`.
Test signals: setup succeeds when tests can mount using a proxy endpoint and unmount `rootDir` during teardown.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/read_stall/setup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/streaming_writes_failure/common_failure_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/streaming_writes_failure/common_failure_test.go

Purpose: shared streaming-write failure suite for cases where a second chunk upload or finalize operation fails through the proxy. It verifies error propagation, block writer reset, and recovery with a new write handle.
Important APIs/types/functions: `commonFailureTestSuite`, `gcsObjectValidator`, `SetupSuite`, `setupTest`, `TearDownTest`, `writingWithNewFileHandleAlsoFails`, `writingAfterBwhReinitializationSucceeds`, and multiple `TestStreamingWrites...` methods.
Control flow: suite setup configures small write blocks and 5 MiB data. Per-test setup starts the configured proxy, appends endpoint flags, creates a storage client, mounts, and creates a random test directory. Test methods perform `WriteAt`, `Sync`, `Truncate`, `Close`, and read-handle scenarios around injected upload/finalize failures.
State and persistence: state includes open file handles, block writer error state, proxy process/log, storage client, and GCS object state validated by scenario-specific implementations. Recovery is tested by closing failed write handles and writing the full data again.
Dependencies and integration points: used by empty-existing-object and new-local-file suites. Depends on operations/client/setup utilities, storage emulator proxy configs, and static mounting from package setup.
Risks and edge cases: tests rely on precise buffering comments and write-block-size behavior. Some write calls intentionally ignore intermediate errors because async upload timing can vary.
Test signals: expected write/sync/close errors, failed writes from new handles before reset, successful writes after block-writer reinitialization, and final GCS content validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/streaming_writes_failure/common_failure_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/streaming_writes_failure/empty_gcs_file_failure_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/streaming_writes_failure/empty_gcs_file_failure_test.go

Purpose: specializes the common streaming-write failure suite for an existing empty GCS file. It validates that failed streaming writes do not corrupt or replace the original empty object.
Important APIs/types/functions: `emptyGcsFileFailureTestSuite` embeds `commonFailureTestSuite`; `SetupTest`; `validateGcsObject`; and `TestEmptyGcsFileFailureTestSuite`.
Control flow: setup selects `empty_gcs_file_2nd_chunk_upload_returns412.yaml`, runs common proxy/mount setup, creates an empty object in GCS, validates it, opens the mounted file, and then inherits all common failure tests.
State and persistence: the scenario's baseline persistent state is an empty GCS object at `testDirName/FileName1`; `validateGcsObject` asserts that state remains empty after failure/reset boundaries.
Dependencies and integration points: depends on dot-imported client helpers, operations open-file helper, the common suite's `gcsObjectValidator`, and proxy skip counts tailored to an existing object.
Risks and edge cases: if setup request counts change, the 412 may no longer land on the intended upload. The scenario assumes empty-object preservation is the correct failure semantics.
Test signals: inherited failure tests pass only if write failures surface and the original empty GCS object remains intact until a later successful rewrite.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/streaming_writes_failure/empty_gcs_file_failure_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/streaming_writes_failure/new_local_file_failure_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/streaming_writes_failure/new_local_file_failure_test.go

Purpose: specializes the streaming-write failure suite for a newly created local file with no prior GCS object. It validates object non-existence after failed upload and recovery after block-writer reset.
Important APIs/types/functions: `newLocalFileFailureTestSuite`, `SetupTest`, `validateGcsObject`, and `TestNewLocalFileFailureTestSuite`.
Control flow: setup selects `local_file_2nd_chunk_upload_returns412.yaml`, starts common proxy/mount/storage setup, creates a local file in the mounted test directory, and delegates all failure scenarios to the embedded common suite.
State and persistence: baseline persistent state is absence of `FileName1` in GCS. `validateGcsObject` asserts not-found after failure before a later successful write.
Dependencies and integration points: uses dot-imported client helpers and common failure suite. It relies on proxy skip count for the new-file resumable upload sequence.
Risks and edge cases: local file creation may create unfinalized or placeholder state on zonal/emulator implementations if semantics change. The test assumes non-existence is the correct post-failure state.
Test signals: common tests pass when failures prevent GCS object creation until a fresh handle writes and closes successfully.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/streaming_writes_failure/new_local_file_failure_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/streaming_writes_failure/streaming_writes_failure_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/streaming_writes_failure/streaming_writes_failure_test.go

Purpose: package-level setup for streaming-writes failure emulator tests. It configures static mounting and shared root/test directory state used by the specialized suites.
Important APIs and state: constant `testDirNamePrefix`; globals `mountFunc`, `rootDir`, `testDirName`; and `TestMain`.
Control flow: setup parses flags, skips mounted-directory mode, prepares the emulator test bucket directory, sets `rootDir`, logs the test log path, assigns static mounting, runs tests, and exits.
State and persistence: `testDirName` is later randomized per test in `commonFailureTestSuite.setupTest`. Persistent object state is managed by child suites and the emulator bucket.
Dependencies and integration points: works under `emulator_tests.sh`, which sets emulator env vars and creates `test-bucket`; child suites call `setup.MountGCSFuseWithGivenMountFunc` through `mountFunc`.
Risks and edge cases: mounted-directory mode returns without explicit exit; static-only coverage excludes other mount modes. Randomized directory names reduce collision risk.
Test signals: setup health is indicated by successful static mount, proxy use, and teardown unmount through `rootDir`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/streaming_writes_failure/streaming_writes_failure_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/util/test_helper.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/util/test_helper.go

Purpose: shared emulator test helper library for starting proxy servers, killing them, timing write sync/read operations, and parsing timeout flags.
Important APIs/functions: `StartProxyServer`, `KillProxyServerProcess`, `WriteFileAndSync`, `ReadFirstByte`, `GetChunkTransferTimeoutFromFlags`, `GetChunkRetryDeadlineFromFlags`, and private `getPortAndProcessInfoFromLogFile`. Constant `PortAndProxyProcessIdInfoRegex` parses proxy log output.
Control flow: `StartProxyServer` runs the proxy with `go run`, polls its log for listening port/PID, and sets `STORAGE_EMULATOR_HOST` to the proxy. Kill unsets the env var and sends SIGINT. Timing helpers create/read files and measure only `Sync` or first `Read`. Flag parsers scan string flags with defaults.
State and persistence: mutates process environment, starts a background process, reads proxy log files, and creates mounted files. Random data is generated for write tests.
Dependencies and integration points: imported by read/write stall, gRPC header, and streaming-write failure tests. Depends on `operations` helpers, OS process APIs, regex polling, and expected proxy log format.
Risks and edge cases: `STORAGE_EMULATOR_HOST` lacks `http://` when set to localhost port, matching Go storage client expectations but easy to misuse. `go run` startup polling can fail if logs are delayed.
Test signals: helper success returns port/PID, elapsed durations, and parsed timeout values; failures usually indicate proxy startup/log-format/environment issues.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/util/test_helper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/write_stall/write_stall_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/write_stall/write_stall_test.go

Purpose: package setup for write-stall emulator tests. It declares shared mount directory state and configures static mounting against the emulator bucket.
Important APIs and state: globals `testDirPath`, `mountFunc`, and `rootDir`; `TestMain` parses setup flags, skips mounted-directory mode, prepares the test bucket flag, sets `rootDir`, and assigns static mounting.
Control flow: normal mode runs tests after static mount function setup; tests themselves mount per scenario with proxy endpoints and unmount using `rootDir`.
State and persistence: this file stores only package-global mount/test path state. Per-test file data and proxy process state are handled in `writes_stall_on_sync_test.go`.
Dependencies and integration points: depends on `setup` and `static_mounting`, and on `emulator_tests.sh` for emulator env vars and bucket creation.
Risks and edge cases: no dynamic/only-dir coverage; mounted-directory mode simply logs and returns. Fixed root dir is shared across tests but each test mounts/unmounts serially in package execution.
Test signals: successful setup means write-stall scenarios can call `setup.MountGCSFuseWithGivenMountFunc` and unmount cleanly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/write_stall/write_stall_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/write_stall/writes_stall_on_sync_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/write_stall/writes_stall_on_sync_test.go

Purpose: validates write stall handling, chunk transfer timeout, and chunk retry deadline behavior when resumable uploads stall through the emulator proxy.
Important APIs/types/functions: constants `fileSize` and `stallTime`; suite `chunkTransferTimeoutInfinity`; tests `TestWriteStallCausesDelay`, `TestChunkTransferTimeout`, and `TestChunkRetryDeadline`.
Control flow: suite setup starts a proxy with single 40s stall, mounts with `--chunk-transfer-timeout-secs=0`, writes a 50 MiB file, and asserts `Sync` waits at least 40s. Table-driven tests start proxies for single/multiple stall configs, append proxy endpoint flags, mount, write/sync, and compare elapsed time against parsed flag defaults/overrides. Retry-deadline tests assert success or failure based on deadline.
State and persistence: test files are created in random directories in the emulator bucket. Proxy process/log and mounted state are created and cleaned per subtest.
Dependencies and integration points: uses emulator helper `WriteFileAndSync`, timeout flag parsers, YAML stall configs, setup mount utilities, and `testify`.
Risks and edge cases: mutating `flags` with appended proxy endpoint inside nested loops can leak endpoints across scenarios if reused. Time-based assertions require stable scheduling and emulator behavior.
Test signals: durations near configured timeout windows, success under long deadline, and errors under short deadline validate retry logic.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/write_stall/writes_stall_on_sync_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/explicit_dir/explicit_dir_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/explicit_dir/explicit_dir_test.go

Purpose: process-wide setup for tests where implicit directories are disabled and only explicit directory objects should be surfaced.
Important APIs/types/functions: constant `DirForExplicitDirTests`; `env` with storage client and context; global `testEnv`; `TestMain`.
Control flow: `TestMain` parses flags, reads config, populates fallback `ExplicitDir` config with `--implicit-dirs=false` and gRPC variant for compatible flat buckets, creates storage client, builds flag sets, and delegates execution to `implicit_and_explicit_dir_setup.RunTestsForExplicitAndImplicitDir`.
State and persistence: test data is created under `dirForExplicitDirTests`; setup itself stores context/client only. Mount lifecycle is delegated to the shared implicit/explicit directory setup helper.
Dependencies and integration points: integrates `test_suite`, `setup`, `client`, and `implicit_and_explicit_dir_setup`. Test files rely on `testEnv` and the shared directory constants.
Risks and edge cases: compatibility marks HNS/zonal false in fallback config, so coverage depends on external config for other bucket types. The package name uses `_test`, so it exercises public utility APIs only.
Test signals: successful setup yields flag-specific runs where explicit-only listing/stat behavior can be asserted.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/explicit_dir/explicit_dir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/explicit_dir/list_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/explicit_dir/list_test.go

Purpose: verifies listing behavior when implicit directories are disabled. It ensures only explicit directory objects and files are visible, and statting an implicit directory after list returns not-exist.
Important APIs/functions: `TestListOnlyExplicitObjectsFromBucket` and `TestStatImplicitDirAfterList`.
Control flow: tests create a mixed implicit/explicit directory structure using either storage-client helpers for zonal runs or mounted/object helpers for other runs. `filepath.WalkDir` reads directories and checks expected names, ordering, directory flags, and counts.
State and persistence: backing GCS contains both implicit object prefixes and explicit directory marker/file objects. Mounted listing should filter out implicit-only directories in this package configuration.
Dependencies and integration points: depends on shared constants in `implicit_and_explicit_dir_setup`, `setup.SetupTestDirectory`, storage client in `testEnv`, and explicit-dir package setup flags.
Risks and edge cases: assertions rely on deterministic `os.ReadDir` lexical ordering. TODOs show zonal bucket setup path differs from non-zonal, which can hide behavior differences.
Test signals: root listing contains only explicit dir/file, explicit dir contains its files, and stat of implicit directory yields `os.ErrNotExist` after list.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/explicit_dir/list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/explicit_dir/rename_sym_link_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/explicit_dir/rename_sym_link_test.go

Purpose: validates renaming a symlink whose target is an explicit directory in a mounted gcsfuse filesystem.
Important APIs/functions: single test `TestRenameSymlinkToExplicitDir` uses `os.Mkdir`, `os.Symlink`, `os.Rename`, `os.Lstat`, `os.Readlink`, and `os.Stat`.
Control flow: creates an explicit target directory under the test dir, creates an old symlink pointing to it, renames the symlink path, then verifies the old symlink is gone, the new path is still a symlink, the link target is preserved, and following the link stats as a directory.
State and persistence: symlink metadata and explicit directory are stored through the mount; the target directory remains unchanged while only the symlink object/name changes.
Dependencies and integration points: relies on explicit-dir package setup and gcsfuse symlink support. Uses `testify` assertions and setup path helpers.
Risks and edge cases: does not verify GCS object representation directly. Absolute target path is used, so behavior can differ from relative symlink handling.
Test signals: rename success plus preserved link mode/target confirms symlink rename semantics for explicit directory targets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/explicit_dir/rename_sym_link_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/flag_optimizations/mount_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/flag_optimizations/mount_test.go

Purpose: validates negative mount behavior for flag optimization profiles, primarily unknown profiles that should reject mounting.
Important APIs/functions: `tearDownMountTest` saves logs and unmounts only if mount unexpectedly succeeded; `TestMountFails` iterates configured flag sets and asserts `mountGCSFuseAndSetupTestDir` returns an error.
Control flow: mounted-directory mode is invalid and fails immediately. Otherwise each flag set gets a sanitized subtest name, attempts mount/setup, defers conditional teardown, and expects an error.
State and persistence: on failed mount there should be no mounted state; if mount succeeds, teardown unmounts and logs are saved. No persistent test objects are required beyond setup attempts.
Dependencies and integration points: uses flag optimization config from `setup_test.go`, `setup.BuildFlagSets`, shared mount helper, and `testify`.
Risks and edge cases: if a formerly unknown profile becomes valid, this test must move to a different negative flag. Teardown depends on the returned error accurately reflecting mount state.
Test signals: passing means invalid optimization profile/config combinations fail before usable mount state is established.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/flag_optimizations/mount_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/flag_optimizations/optimization_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/flag_optimizations/optimization_test.go

Purpose: tests profile and machine-type flag optimizations that implicitly enable/disable features such as implicit directories and rename directory limits.
Important APIs/functions: `tearDownOptimizationTest`, `TestImplicitDirsNotEnabled`, `TestRenameDirLimitNotSet`, `TestImplicitDirsEnabled`, and `TestRenameDirLimitSet`.
Control flow: each test iterates `setup.BuildFlagSets`, mounts with selected flags, creates GCS implicit directories or source directories with files, performs `os.Stat` or `os.Rename`, and asserts expected failure/success. Cleanup deletes created prefixes.
State and persistence: state includes GCS directory markers/files and mounted views. Tests distinguish implicit-dir visibility and rename-dir-limit behavior based on flag-derived optimized defaults.
Dependencies and integration points: uses `client.CreateImplicitDir`, `CreateGcsDir`, `CreateNFilesInDir`, `DeleteAllObjectsWithPrefix`, shared setup config, and `testify`.
Risks and edge cases: optimization behavior is encoded indirectly through config run names and flag sets, so changes in profile defaults can flip expectations. Flat/HNS/zonal compatibility matters.
Test signals: implicit dirs hidden or visible and directory rename rejected or accepted according to selected optimized profile settings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/flag_optimizations/optimization_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/flag_optimizations/setup_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/flag_optimizations/setup_test.go

Purpose: package-level orchestration for flag optimization tests. It defines fallback config for machine-type/profile/zonal/kernel-reader scenarios and runs the package across static, dynamic, and only-dir mounting modes.
Important APIs/types/functions: constants `testDirName`, `onlyDirMounted`, `GKETempDir`; `env` with mount function/dirs/client/context/config; `mountGCSFuseAndSetupTestDir`, `mustMountGCSFuseAndSetupTestDir`, and `TestMain`.
Control flow: setup parses flags, builds fallback `FlagOptimizations` config with 12 run-specific items, initializes storage client/environment, validates bucket/mounted-directory flags, prepares test bucket and path overrides, runs static tests, then dynamic tests, then only-dir tests if prior modes pass.
State and persistence: creates test directories under `FlagOptimizationsTests` and optional only-dir prefix. Config and mount dirs change between mount modes. Cleanup removes bucket prefixes and saves logs on failure.
Dependencies and integration points: integrates static/dynamic/only-dir mounting helpers, `setup.BuildFlagSets`, `client` helpers, and config consumed by mount, optimization, and zonal kernel-reader tests.
Risks and edge cases: sequential reruns of `m.Run()` depend on package globals being reset by tests. Fallback run names must stay synchronized with test functions. Only-dir cleanup targets a nested prefix.
Test signals: successful pass across mount modes demonstrates optimized flags behave consistently under different mount topologies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/flag_optimizations/setup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/flag_optimizations/zonal_bucket_optimization_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/flag_optimizations/zonal_bucket_optimization_test.go

Purpose: validates zonal bucket optimizations for kernel parameters and read strategy precedence. It checks optimized FUSE kernel settings, kernel reader default behavior, and fallback to file cache or buffered reader when kernel reader is disabled.
Important APIs/types/functions: constants for expected log messages; `KernelReaderParamsSuite` with `verifyKernelParam` and `TestKernelParamVerification`; `ReadStrategySuite` with `validateParallelReads` and `TestKernelReaderBehavior`; `createAndReadFile`; and tests for default, explicit override, dynamic mount, and read strategy cases.
Control flow: kernel-param tests stat the mount to derive device major/minor, resolve `/sys` parameter paths via `kernelparams.PathForParam`, and compare values to optimized defaults or explicit overrides. Read strategy tests create/read a 10 MiB file, truncate logs first, then inspect log messages and parallel ReadFile overlap.
State and persistence: state spans mounted files, gcsfuse logs, `/sys` FUSE connection parameters, and configured cache dirs under `/gcsfuse-tmp`. Test files are removed with cleanup callbacks.
Dependencies and integration points: imports `cfg.DefaultMaxBackground`, `DefaultCongestionThreshold`, `kernelparams`, `unix.Stat`, setup helpers, and operations. Config entries are defined in `setup_test.go`.
Risks and edge cases: log-string assertions are brittle against logging changes. `/sys` parameter availability depends on platform privileges. Dynamic mount intentionally expects optimized values not to apply.
Test signals: correct kernel params, kernel reader initialization/parallel reads by default, and absence of kernel reader logs when explicitly disabled prove zonal optimization behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/flag_optimizations/zonal_bucket_optimization_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/grpc_validation/grpc_validation_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/grpc_validation/grpc_validation_test.go

Purpose: validates gRPC DirectPath connectivity logging for buckets located in same/different regions and multi-regions relative to the test VM.
Important APIs/types/functions: `gRPCValidation` suite with four bucket name fields; `SetupSuite` creates success/failure buckets; `TearDownSuite` deletes them; `TestGRPCDirectPathConnections` mounts each bucket with gRPC and checks logs.
Control flow: setup chooses single-region and multi-region success/failure locations from helper functions in `setup_test.go`, creates unique buckets, then each subtest creates a temp mountpoint/log, runs `mounting.MountGcsfuse` with `--client-protocol=grpc --log-severity=TRACE`, and searches for expected DirectPath log substring.
State and persistence: creates real GCS buckets in project `gcs-fuse-test`; temp mount dirs and logs are removed on success, preserved on failure. Bucket cleanup is best-effort.
Dependencies and integration points: depends on Cloud Storage client, region detection, mount binary path, log polling helper, and actual GCP DirectPath support.
Risks and edge cases: high-impact external integration test: bucket creation quotas, IAM, region availability, and DirectPath infrastructure can all fail. Expected failure cases may still mount but log unavailable reasons.
Test signals: success cases log `Successfully connected over gRPC DirectPath`; failure cases log `Direct path connectivity unavailable ... reason:` for target buckets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/grpc_validation/grpc_validation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/grpc_validation/setup_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/grpc_validation/setup_test.go

Purpose: environment and helper setup for live gRPC DirectPath validation. It detects the VM region, skips unsupported contexts, creates a storage client, and provides bucket-region selection helpers.
Important APIs/functions: region lists `singleRegions`, `multiRegions`; globals `gcpProject`, `ctx`, `client`, `testRegion`; `findTestExecutionEnvironment`, `findSingleRegionForGRPCDirectPathSuccessCase`, `findMultiRegionForGRPCDirectPathSuccessCase`, `pickFailureRegionFromListOfRegions`, `createTestBucketName`, `createTestBucket`, and `TestMain`.
Control flow: `TestMain` parses flags, skips presubmit, prepares test bucket flags, creates storage client, detects GCE/cloudtop environment using OpenTelemetry GCP detector, skips cloudtop, then runs tests.
State and persistence: persistent state is the storage client and dynamically created buckets later owned by the suite. Helper-generated bucket names include region and nanosecond suffix.
Dependencies and integration points: uses OpenTelemetry resource detector, Cloud Storage API, setup flags, and project `gcs-fuse-test`.
Risks and edge cases: if region detection returns empty, helper functions can produce empty bucket locations. Cloudtop and presubmit skips avoid unsupported direct path but reduce coverage.
Test signals: setup success means a usable non-cloudtop GCE zone was detected and storage client creation succeeded.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/grpc_validation/setup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/gzip/gzip_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/gzip/gzip_test.go

Purpose: package setup and fixture generation for gzip object integration tests. It creates combinations of gzip-encoded content, content-encoding headers, and cache-control no-transform metadata.
Important APIs/functions: constants naming read and overwrite fixtures; globals `gcsObjectsToBeDeletedEventually`, `storageClient`, `ctx`; `setup_testdata`, `destroy_testdata`, `createContentOfSize`, and `TestMain`.
Control flow: setup builds deterministic large text content, optionally gzip-compresses local temp files, uploads objects with or without `Content-Encoding: gzip`, optionally clears cache-control no-transform, records object paths for cleanup, then mounts/runs configured gzip tests.
State and persistence: creates many objects under `gzip/` in the test bucket and deletes them after tests. Local temp files are removed immediately after upload. Mounted state is managed by static mounting helper.
Dependencies and integration points: uses storage client helpers for upload/delete/cache-control, static mounting with config file, setup/test_suite config, and operations temp-file generation.
Risks and edge cases: fixture size is large enough for sequential/ranged reads and may slow CI. The misspelled log `destoy` is cosmetic. Cleanup aborts on first delete error.
Test signals: downstream read and overwrite tests depend on all fixture variants existing with precise metadata combinations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/gzip/gzip_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/gzip/read_gzip_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/gzip/read_gzip_test.go

Purpose: verifies full-file and ranged reads of gzip-related GCS objects through gcsfuse preserve compressed bytes and object size semantics across content-encoding/no-transform variants.
Important APIs/functions: `verifyFileSizeAndFullFileRead`, `verifyRangedRead`, `downloadGzipGcsObjectAsCompressed`, and ten exported tests covering text/gzip content with/without content encoding and no-transform.
Control flow: full-read tests stat the mounted file, compare mounted size to GCS object size, download the same object using `ReadCompressed(true)`, and compare bytes. Ranged tests compute offsets/sizes, read chunks from mounted and downloaded compressed files, and compare buffers.
State and persistence: reads fixture objects under `gzip/` created by `gzip_test.go`; creates local temp compressed downloads for comparison and removes them.
Dependencies and integration points: uses Cloud Storage client `ReadCompressed(true)` because gcloud/gsutil decompress content-encoded gzip by default. Depends on operations read/stat/compare helpers.
Risks and edge cases: ranged read uses several fixed offset multipliers and assumes object size supports them. It opens a file handle `f` in `verifyRangedRead` but does not use/close it, which can leak descriptors in long runs.
Test signals: mounted bytes and sizes must exactly match compressed GCS object bytes for full and ranged reads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/gzip/read_gzip_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/gzip/write_gzip_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/gzip/write_gzip_test.go

Purpose: verifies overwriting gzip-related objects through the mounted filesystem writes the new raw content and updates GCS object size as expected.
Important APIs/functions: constant `overwrittenFileSize`; helper `verifyFullFileOverwrite`; five tests covering content-encoding/no-transform fixture variants.
Control flow: helper confirms the initial mounted file size matches the GCS object size, creates a 1000-byte temp file, copies it over the mounted object path with overwrite allowed, then re-queries GCS object size and expects exactly 1000 bytes.
State and persistence: mutates the overwrite-specific fixture objects under `gzip/`. Temp overwrite file is local and removed after use.
Dependencies and integration points: uses `client.GetGcsObjectSize`, `operations.StatFile`, `createContentOfSize`, `CreateLocalTempFile`, and `CopyFileAllowOverwrite`.
Risks and edge cases: validates size but not content or metadata after overwrite. Tests operate on separate `ToOverwrite` fixtures to avoid interfering with read tests.
Test signals: object size changes to `overwrittenFileSize` after mounted copy, confirming overwrite path is not preserving stale gzip metadata sizing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/gzip/write_gzip_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/implicit_dir/delete_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/implicit_dir/delete_test.go

Purpose: tests recursive deletion semantics for implicit directories, including nested implicit subdirectories and mixtures with explicit directories.
Important APIs/functions: `TestDeleteNonEmptyImplicitDir`, `TestDeleteNonEmptyImplicitSubDir`, `TestDeleteImplicitDirWithExplicitSubDir`, `TestDeleteImplicitDirWithImplicitSubDirContainingExplicitDir`, `TestDeleteImplicitDirInExplicitDir`, and `TestDeleteExplicitDirContainingImplicitSubDir`.
Control flow: each test creates a directory topology under a unique subdir using storage-client helpers for zonal runs or shared setup helpers otherwise, optionally adds explicit subdirectories/files through mounted operations, then calls `RemoveAndCheckIfDirIsDeleted`.
State and persistence: backing GCS contains implicit prefixes represented by child objects and explicit directory objects. Deletion through the mount should remove all relevant child objects/prefixes.
Dependencies and integration points: depends on `setupTestDir`, constants from `implicit_dir_test.go`, `operations.CreateDirectoryWithNFiles`, and `implicit_and_explicit_dir_setup` helpers.
Risks and edge cases: behavior differs for zonal bucket setup paths, tracked by TODOs. Tests rely on helper correctness for both creation and deletion validation.
Test signals: successful removal and absence checks for target directory names across implicit/explicit mixtures validate recursive delete behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/implicit_dir/delete_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/implicit_dir/implicit_dir_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/implicit_dir/implicit_dir_test.go

Purpose: process-wide setup for tests with `--implicit-dirs` enabled. It defines constants used by deletion/list/local-file tests and drives execution through shared implicit/explicit directory setup.
Important APIs/types/functions: constants for explicit dirs inside implicit dirs, file prefixes/counts, and `DirForImplicitDirTests`; `env`; global `testEnv`; `setupTestDir`; and `TestMain`.
Control flow: setup parses flags, reads config, populates fallback `ImplicitDir` config with HTTP and gRPC variants, creates storage client, builds compatible flag sets, runs tests with `RunTestsForExplicitAndImplicitDir`, saves logs on failure, and cleans up GCS test prefix.
State and persistence: test data lives under `dirForImplicitDirTests` and additional local-file test prefixes. `setupTestDir` creates a mounted subdirectory under the package root test dir.
Dependencies and integration points: integrates setup/test_suite/client helpers and shared implicit/explicit setup utilities. Other files depend on constants and `testEnv`.
Risks and edge cases: cleanup path references `testDirName`, a constant declared in `local_file_test.go` in the same package; this cross-file dependency is legal but non-obvious. gRPC variant excludes zonal buckets.
Test signals: setup success enables implicit directory visibility, deletion, symlink, and local-file behavior to be tested across configured bucket types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/implicit_dir/implicit_dir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/implicit_dir/list_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/implicit_dir/list_test.go

Purpose: verifies listing and stat behavior when implicit directories are enabled. It ensures implicit prefixes appear as directories alongside explicit objects.
Important APIs/functions: `TestListImplicitObjectsFromBucket` and `TestStatImplicitDirAfterList`.
Control flow: creates mixed implicit and explicit structures under a test subdir, walks directories with `filepath.WalkDir`, calls `os.ReadDir`, and checks counts, lexical names, and directory/file flags at root, explicit dir, implicit dir, and implicit subdir. Stat-after-list asserts the implicit dir is stattable and is a directory.
State and persistence: GCS has explicit directory markers/files and implicit-prefix child objects. Mounted state should synthesize directory entries for implicit prefixes.
Dependencies and integration points: uses `implicit_and_explicit_dir_setup`, package `testEnv`, and setup helpers. Zonal runs use storage-client creation due to bucket semantics.
Risks and edge cases: relies on ordering from `os.ReadDir`. Typo in one error string is cosmetic. The walk callback returns nil after validating target dirs, so nested traversal still depends on `WalkDir` ordering.
Test signals: root shows three entries including implicit dir; child listings match expected files/subdirs; stat of implicit dir succeeds after listing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/implicit_dir/list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/implicit_dir/local_file_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/implicit_dir/local_file_test.go

Purpose: tests interactions between local unclosed files and implicit directories. It verifies visibility before close/sync and directory listing behavior with local plus GCS-backed entries.
Important APIs/functions: constant `testDirName`; tests `TestNewFileUnderImplicitDirectoryShouldNotGetSyncedToGCSTillClose`, `TestReadDirForImplicitDirWithLocalFile`, and `TestRecursiveListingWithLocalFiles`.
Control flow: tests create recursive base dirs and implicit GCS dirs, create local files under implicit/explicit/root paths, optionally write without close, list directories, verify entry counts/sizes, then close handles and validate final GCS content.
State and persistence: distinguishes unfinalized/local write state from persisted GCS objects. Zonal buckets expose unfinalized zero-size objects before sync, while non-zonal buckets should not show objects until close.
Dependencies and integration points: dot-imports client helpers, uses operations directory/read/write helpers, setup bucket-mode checks, and package setup storage client/context.
Risks and edge cases: assertions differ by bucket type, so zonal behavior is explicitly special-cased. Recursive listing compares `walkPath == setup.MntDir()` even though walking starts at `testEnv.testDirPath`, which may depend on path relationships in setup.
Test signals: local files appear in directory listings with zero size, persisted GCS entries coexist, and final close validates object contents.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/implicit_dir/local_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/implicit_dir/rename_sym_link_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/implicit_dir/rename_sym_link_test.go

Purpose: validates renaming a symlink whose target is an implicit directory synthesized from a GCS object prefix.
Important APIs/functions: `TestRenameSymlinkToImplicitDir` uses `client.CreateObjectOnGCS`, `os.Symlink`, `os.Rename`, `os.Lstat`, `os.Readlink`, and `os.Stat`.
Control flow: creates a placeholder object under `implicit_dir/` to define the implicit directory, creates a symlink to the mounted implicit directory, renames the symlink, then verifies old path absence, new symlink type, preserved target, and target directory stat.
State and persistence: persistent state is the placeholder GCS object defining the implicit prefix plus symlink metadata written through the mount.
Dependencies and integration points: depends on implicit-dir setup with implicit dirs enabled, package storage client/context, and symlink support in gcsfuse.
Risks and edge cases: uses absolute symlink target. It does not inspect the underlying GCS representation of the symlink after rename.
Test signals: successful rename and preserved symlink target confirm symlink operations work even when the target directory is implicit, not explicit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/implicit_dir/rename_sym_link_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/improved_run_e2e_tests.sh -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/improved_run_e2e_tests.sh

Purpose: full e2e runner for gcsfuse integration tests. It installs prerequisites, optionally builds or installs gcsfuse, creates per-package test buckets, runs packages in parallel by bucket type with retries, captures logs/artifacts, prints runtime tables, and cleans up buckets.
Important APIs/functions: `usage`, logging helpers, bash-version self-upgrade block, option parsing, `validate_option_value`, `create_file_helper`, `filter_array`, lock helpers, log organization, `create_bucket`, `cleanup_created_buckets`, `safe_kill`, `clean_up`, `run_package_parallel`, `create_bucket_and_run_package`, `test_package`, `generate_test_log_artifacts`, `install_package_from_path`, `build_gcsfuse_once`, `install_packages`, `run_test_group`, `run_e2e_tests_for_emulator`, and `main`.
Control flow: parses long options, determines GCE project/location metadata, validates zonal/TPC/package choices, creates output/lock/stat files, defines package lists, installs dependencies, chooses package install/build mode, optionally tracks resources, then launches HNS/flat/emulator, zonal, or TPC groups. It waits for all pids, prints runtime table, stops resource tracking, and exits aggregate status.
State and persistence: creates output directories with running/success/failed logs, package runtime stats, resource usage, bucket creation logs, and bucket ledger. It creates real GCS buckets and deletes them in batches on cleanup. It may install system packages, Go, gcloud, and built binaries.
Dependencies and integration points: depends on GCE metadata server, gcloud, Docker only through emulator script, Go, Bash 5.1+, `flock`, Kokoro env vars, `go-junit-report`, perfmetrics install scripts, and integration test package config.
Risks and edge cases: high blast radius script: installs tools, creates buckets in parallel, uses `eval` for quoted command strings, and relies on metadata server. Bucket quota throttling is mitigated by locks and delays. Package retry status is aggregated per group.
Test signals: logs organized by status/bucket, runtime stats table, JUnit artifacts in Kokoro, zero aggregate exit, and cleaned bucket ledger indicate a healthy e2e run.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/improved_run_e2e_tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/inactive_stream_timeout/setup_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/inactive_stream_timeout/setup_test.go

Purpose: package setup and log parsing helpers for inactive read stream timeout tests. It configures enabled/disabled timeout flag sets and runs across static, dynamic, and only-dir mounts.
Important APIs/types/functions: constants for test dir, only-dir prefix, file/chunk sizes, default timeout, log paths, retry timing; `env`; globals `testEnv`, `mountFunc`, `mountDir`, `rootDir`; `mountGCSFuseAndSetupTestDir`; `doesNotHaveInactiveReaderClosedLogLineInLogFile`; `hasInactiveReaderClosedLogLineInLogFile`; and `TestMain`.
Control flow: setup reads config or populates default enabled/disabled timeout configs with JSON log files, initializes storage client/environment, handles mounted-directory mode, otherwise sets up test bucket, overrides paths, runs static tests, then dynamic, then only-dir if successful, and cleans up GCS prefixes.
State and persistence: test state includes JSON gcsfuse log files, GCS objects under `inactiveReadTimeout`, mounted directories, and only-dir prefix. Log helpers parse timestamps to detect close-reader messages within time windows.
Dependencies and integration points: uses `read_logs.ParseJsonLogLineIntoLogEntryStruct`, storage client helpers, static/dynamic/only-dir mounting, and operations retry helper in tests.
Risks and edge cases: log assertions depend on JSON log format and timestamp bounds. Fixed sleeps and retry windows can be flaky under slow logging. Only enabled suite is in this work item, but config also references disabled suite in another file.
Test signals: setup supports log-file path rewriting and mount-mode coverage; helper success/failure indicates whether inactive-reader close messages appear in the expected window.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/inactive_stream_timeout/setup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/inactive_stream_timeout/with_timeout_test.go -->
# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/inactive_stream_timeout/with_timeout_test.go

Purpose: tests active behavior when `--read-inactive-stream-timeout` is enabled. It verifies idle readers are closed after timeout and remain open when accessed within timeout.
Important APIs/types/functions: `timeoutEnabledSuite` with flags/storage/context/base test name; lifecycle methods; `TestReaderCloses`; `TestReaderStaysOpenWithinTimeout`; and `TestTimeoutEnabledSuite`.
Control flow: suite setup configures log file path and mounts. `TestReaderCloses` creates a 10 MiB object, opens it, reads a 128 KiB chunk, waits over twice the timeout, polls logs for the inactive-reader close message, then reads again to prove a new reader can be created. `TestReaderStaysOpenWithinTimeout` reads, sleeps half the timeout, reads again, and asserts no close log occurred in between.
State and persistence: state includes open file handles, backing GCS object, gcsfuse JSON log file, and reader lifecycle inside gcsfuse. File handles are closed by defer.
Dependencies and integration points: depends on setup helpers in `setup_test.go`, `client.SetupFileInTestDirectory`, `operations.OpenFileAsReadonly`, `operations.RetryUntil`, and package config flag sets for HTTP and gRPC.
Risks and edge cases: log timing windows use `time.Now()` around reads/sleeps, so clock skew with log timestamps or delayed flushing can affect results. Sleeps intentionally include buffers to reduce flake.
Test signals: close log found after idle interval, absent before timeout, and subsequent read success validate inactive stream cleanup without breaking file handles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/inactive_stream_timeout/with_timeout_test.go -->
