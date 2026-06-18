# Research Group subset-b-008953

Grouped research for the requested TiKV integration-test files and WiredTiger build/benchmark support files. Each section is bounded for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/server/raft_client.rs -->
# sources/storage-engines/tikv/tests/integrations/server/raft_client.rs

## Purpose
This integration test validates TiKV raft-client transport behavior around gRPC streaming, batching fallback, reconnects, PD-backed store resolution, store block/allow lists, and network-inspection latency bookkeeping. It uses a mock `Tikv` gRPC service to count received raft messages without starting a full TiKV cluster for the basic transport cases.

## Important APIs, Types, and Functions
`get_raft_client` builds a `RaftClient` from a `ConnectionBuilder`, `VersionTrack<Config>`, `SecurityManager`, resolver, router, lazy worker scheduler, and `ThreadLoadPool`. `MockKvForRaft` implements `Tikv::raft` and `Tikv::batch_raft`, counting individual messages and batch envelopes; when `allow_batch` is false, `batch_raft` returns `UNIMPLEMENTED` to exercise fallback. `create_mock_server`, `create_mock_server_on`, and `check_msg_count` provide local test infrastructure.

## Control Flow
The first tests establish a mock server, send `RaftMessage`s through `RaftClient::send`, call `flush`, and assert counter changes. Reconnect coverage shuts down the mock server, waits for router notification, queues more sends, restarts the server on the same port, and verifies later delivery. PD resolver tests add stores to the mock PD handler, then test tombstone block-listing and explicit allow-list filtering. Async tests start network inspection after creating store connections and query `get_max_latency` / `get_all_max_latencies`.

## State, Persistence, and Dependencies
State is mostly in-memory: atomic counters, worker queues, raft-client connection state, PD mock store records, and health-checker latency maps. Dependencies include `grpcio`, `kvproto`, `raftstore`, TiKV server connection builder/resolver types, failpoints, and Tokio for async latency tests. No on-disk persistence is intentional.

## Integration Points, Risks, and Test Signals
The tests exercise compatibility between single-message and batch raft RPCs, resolver reactions to tombstone stores, reconnect backoff, and health checker lifecycle. Risks include timing sensitivity from sleeps, fixed port ranges, and async inspection tests that may pass without proving recovery after final connection failure. Strong signals are exact message counts, discarded-send assertions, and latency map presence checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/server/raft_client.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/server/security.rs -->
# sources/storage-engines/tikv/tests/integrations/server/security.rs

## Purpose
This file verifies TiKV server-side TLS common-name filtering for gRPC clients. It starts a one-node server cluster with generated test security credentials and checks that a client certificate whose CN is allowed can issue a `kv_get`, while an unapproved CN is rejected.

## Important APIs, Types, and Functions
The tests use `new_server_cluster`, `test_util::new_security_cfg`, `test_util::new_channel_cred`, `grpcio::ChannelBuilder::secure_connect`, and `kvproto::tikvpb::TikvClient`. `HashSet<String>` configures allowed CNs on `cluster.cfg.security`.

## Control Flow
Each test creates a cluster, sets `security` config, runs the cluster, finds the leader store address from the simulator registry, constructs a secure gRPC channel, and calls `TikvClient::kv_get`. The success case unwraps the response; the failure case asserts the RPC returns an error.

## State, Persistence, and Dependencies
State is limited to the temporary server cluster and in-memory security configuration. It depends on test certificates matching the expected `"tikv-server"` CN and on the test raftstore simulator exposing store addresses.

## Integration Points, Risks, and Test Signals
The integration point is the full gRPC server credential path rather than a unit-level security manager call. Test signal is binary RPC success/failure. The failure case uses the misspelled string `"invaild-server"`, which is harmless but should not be copied into documentation as a canonical name.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/server/security.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/server/server.rs -->
# sources/storage-engines/tikv/tests/integrations/server/server.rs

## Purpose
This integration test validates that TiKV's top-level server process can pause and resume its gRPC service via `ServiceEvent` control messages while health checks reflect availability changes.

## Important APIs, Types, and Functions
The main function is `test_restart_grpc_service`. It uses `server::server::run_tikv`, `TikvConfig`, mock PD `test_pd::Server`, `tikv_util::mpsc::unbounded`, `grpcio_health::HealthClient`, and `ServiceEvent::{PauseGrpc, ResumeGrpc, Exit}`. A helper closure retries health checks until `ServingStatus::Serving` appears.

## Control Flow
The test spawns a TiKV server thread with a temp data directory, mock PD endpoint, critical log level, and a selected listen address. The main thread connects a health client, waits for serving status, sends `PauseGrpc`, loops until the health RPC fails with `UNAVAILABLE`, sends `ResumeGrpc`, waits for serving again, then sends `Exit` and joins the server thread.

## State, Persistence, and Dependencies
Persistent state is a temp storage data directory cleaned by test utilities. Runtime state flows through the service-event channel and gRPC health service. The failpoint `mock_force_uninitial_logger` avoids logger initialization conflicts in test context.

## Integration Points, Risks, and Test Signals
This is a process-level integration signal covering server startup, PD binding, health service exposure, control-plane events, and graceful exit. Risks are timeout sensitivity and reliance on local port allocation. The assertions directly check serving, unavailable during pause, and serving after resume.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/server/server.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/server/status_server.rs -->
# sources/storage-engines/tikv/tests/integrations/server/status_server.rs

## Purpose
This test validates the HTTP status server's `/region/{id}` endpoint. It checks that a real cluster region can be fetched from the raft extension and serialized as JSON `RegionMeta`.

## Important APIs, Types, and Functions
`check` builds a Hyper HTTP GET request and validates status, content type, and JSON deserialization. `test_region_meta_endpoint` uses `new_server_cluster`, `StatusServer::new`, `ConfigController::default`, `SecurityConfig::default`, `GrpcServiceManager::dummy`, and the store's `raft_extension`.

## Control Flow
The cluster runs, the test discovers the initial region and peer store, constructs a status server with that store's router, starts it on a free local address, and runs the async `check` future in a Tokio runtime. The server is stopped after validation.

## State, Persistence, and Dependencies
State comes from the live raftstore region metadata and status server listener. Dependencies include Hyper, serde JSON, TiKV status server internals, and raftstore `RegionMeta`.

## Integration Points, Risks, and Test Signals
This exercises the endpoint through HTTP rather than internal calls. Test signals are `200 OK`, `application/json`, and successful `RegionMeta` parsing. It does not assert fields inside `RegionMeta`, so schema validity is covered more than semantic freshness.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/server/status_server.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/server_encryption.rs -->
# sources/storage-engines/tikv/tests/integrations/server_encryption.rs

## Purpose
This file verifies encrypted snapshot transfer for both node and server cluster simulators. It ensures data from default, write, and lock column families survives learner addition and peer promotion when encryption is enabled.

## Important APIs, Types, and Functions
`test_snapshot_encryption<T: Simulator>` is the shared scenario. It calls `configure_for_encryption`, disables default PD operators, uses `run_conf_change`, `must_put`, `must_put_cf`, `must_add_peer`, `new_learner_peer`, `new_peer`, and `must_get_*_equal` helpers.

## Control Flow
The test enables encryption, writes ten keys into three CFs, adds store 2 first as learner and then as voter, writes an extra key to force replication progress, and checks that store 2 has representative default/lock/write CF values. Two test functions instantiate the scenario with `new_node_cluster` and `new_server_cluster`.

## State, Persistence, and Dependencies
Persistent state is cluster data and generated encrypted snapshot files under temporary paths. The tests call `take_path` before drop so cleanup order can occur after cluster shutdown.

## Integration Points, Risks, and Test Signals
The integration point is raft snapshot generation, encryption, transfer, ingestion, and CF-level retrieval. Signals are successful peer addition plus exact value reads on the target store. The scenario does not inspect encrypted bytes directly; it infers encryption compatibility from snapshot application success.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/server_encryption.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/storage/mod.rs -->
# sources/storage-engines/tikv/tests/integrations/storage/mod.rs

## Purpose
This module file wires the TiKV storage integration-test suite into Rust's test module tree. It has no runtime logic of its own, but controls which sibling test files are compiled and run.

## Important APIs, Types, and Functions
It declares `mod test_raft_storage;`, `mod test_raftkv;`, `mod test_region_info_accessor;`, `mod test_storage;`, and `mod test_titan;`.

## Control Flow
Compilation includes each listed submodule, allowing their `#[test]` and `#[bench]` items to register with the Rust harness.

## State, Persistence, Dependencies, Risks, and Test Signals
There is no state or persistence. The dependency is purely module inclusion. The main risk is omission: adding a new storage integration file without updating this module would leave tests uncompiled. The signal is indirect through the included modules' tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/storage/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/storage/test_raft_storage.rs -->
# sources/storage-engines/tikv/tests/integrations/storage/test_raft_storage.rs

## Purpose
This file tests TiKV's transactional and raw storage APIs when backed by raftstore. It covers basic MVCC operations, leader lease reads, stale/wrong region and store errors, leader-term validation, automatic GC across split regions, and raw atomic operations.

## Important APIs, Types, and Functions
`new_raft_storage` creates a one-store `SyncTestStorageApiV1<SimulateEngine>` and request `Context`. `write_test_data` and `check_data` help auto-GC validation across leaders and regions. Tests call storage APIs such as `get`, `prewrite`, `commit`, `rollback`, `scan`, `scan_locks`, `raw_get`, `raw_put`, `raw_batch_put_atomic`, `raw_compare_and_swap_atomic`, and `raw_batch_delete_atomic`.

## Control Flow
The basic tests write MVCC values, commit them, then mutate context fields to assert region/store mismatch errors. Leader-change tests capture a term, move leadership twice, and verify not-leader/stale-command behavior. Auto-GC builds per-store storage handles, starts auto GC with callbacks, writes three timestamp generations, splits regions, advances the PD safe point, waits for one GC round per store, and checks old versions are gone while newer versions remain. Atomic tests write raw values and exercise compare-and-swap success, failure, delete, and batch delete.

## State, Persistence, and Dependencies
State spans raftstore region metadata, peer/store IDs, MVCC CF contents, PD safe point, and GC worker state. It depends on `test_raftstore`, `test_storage`, TiKV storage error types, `AutoGcConfig`, and error-code matching for stale commands.

## Integration Points, Risks, and Test Signals
The tests integrate storage API calls with raft routing, leader lease, region splits, PD safe point, GC workers, and raw atomic raft commands. Signals include exact returned values, expected structured errors (`store_not_match`, `stale_command`), callback counts, and absence/presence of old MVCC versions. Risks are timing sensitivity in GC and leader lease sleeps.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/storage/test_raft_storage.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/storage/test_raftkv.rs -->
# sources/storage-engines/tikv/tests/integrations/storage/test_raftkv.rs

## Purpose
This integration test validates the lower-level raft-backed `kv::Engine` interface: snapshots, writes, deletes, CF access, cursor seek behavior, replica reads, read-index behavior, in-memory lock checking, and write prechecks on followers or isolated leaders.

## Important APIs, Types, and Functions
The file uses `Engine`, `SnapContext`, `WriteData`, `Modify`, `Cursor`, `IterOptions`, `CfStatistics`, and helpers such as `must_put`, `assert_has`, `assert_seek`, `near_seek`, `cf`, `empty_write`, and `wrong_context`. It also uses raftstore packet filters and `read_index_on_peer`.

## Control Flow
`test_raftkv` starts a one-node server cluster, obtains the leader storage, builds a region `Context`, and runs basic get/put, batch write, seek, near-seek, CF, empty-write, and wrong-context checks. Multi-node tests validate leader lease reads after isolating the leader, follower read-index responses, replica snapshot reads with `replica_read`, catch-up after follower restart, memory-lock detection for replica reads, not-leader read-index errors when heartbeats/appends are delayed, and `precheck_write_with_ctx` failures on followers or isolated leaders.

## State, Persistence, and Dependencies
State includes raft region membership, current leader, local storage handles, RocksDB CF data, memory lock entries in the concurrency manager, and simulator packet filters. Dependencies include `kvproto::Context`, raft message types, `test_raftstore`, and TiKV storage `kv` abstractions.

## Integration Points, Risks, and Test Signals
The file checks the boundary between raftstore leadership/read-index semantics and storage snapshots. It has strong signals for encoded key ordering, CF isolation, lock error equality, and not-leader headers. Risks include sleeps for election/catch-up and reliance on exact simulator timing.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/storage/test_raftkv.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/storage/test_region_info_accessor.rs -->
# sources/storage-engines/tikv/tests/integrations/storage/test_region_info_accessor.rs

## Purpose
This file tests raftstore's `RegionInfoAccessor` and `RegionInfoProvider` query behavior over a cluster whose keyspace is split into known contiguous regions.

## Important APIs, Types, and Functions
`prepare_cluster` writes keys, splits at `k1`, `k3`, `k5`, `k7`, and `k9`, and returns the expected region list. Tests create accessors through `post_create_coprocessor_host` and call `seek_region`, `get_regions_in_range`, `get_top_regions`, `find_region_by_key`, scheduler `RegionInfoQuery::RaftStoreEvent`, and `RegionActivity`.

## Control Flow
Each test starts a three-node cluster, captures one accessor per node from the coprocessor host creation hook, prepares the split layout, then queries every node's accessor. Seek tests verify traversal from empty, boundary, interior, and high keys. Range tests cover unbounded and bounded ranges. Top-region tests inject coprocessor write stats for each region and validate leader-side top-region population. Find-by-key tests check boundary and tail lookup.

## State, Persistence, and Dependencies
State is the accessor's in-memory region collection, raftstore leader tracking, and injected region activity metrics. It depends on PD/client region stat types, coprocessor hooks, and `HandyRwLock` for checking leader sets.

## Integration Points, Risks, and Test Signals
The tests integrate region metadata updates from raftstore with query APIs used by GC, scheduling, and diagnostics. Signals are exact region vector equality for deterministic ranges and non-empty top regions on leaders. Risk is the fixed sleep used to wait for raftstore updates after splits.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/storage/test_region_info_accessor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/storage/test_storage.rs -->
# sources/storage-engines/tikv/tests/integrations/storage/test_storage.rs

## Purpose
This is the broadest TiKV storage integration suite for MVCC transaction semantics and raw KV APIs. It validates reads, writes, deletes, prewrite/commit/rollback/cleanup, forward and reverse scans, lock scanning/resolution, GC, API version validation, raw CF operations, raw atomic APIs, checksums, and concurrent isolation behavior.

## Important APIs, Types, and Functions
Most tests use `AssertionStorage` and `AssertionStorageApiV1` helpers from `test_storage`. Core TiKV APIs include `Mutation`, `Key`, `TimeStamp`, `Context`, `KeyRange`, `ApiVersion`, `dispatch_api_version!`, `checksum_crc64_xor`, `DEFAULT_GC_BATCH_KEYS`, `MAX_TXN_WRITE_SIZE`, and `RESOLVE_LOCK_BATCH_SIZE`. Local helpers include `lock`, `Oracle`, `inc`, `inc_multi`, `backoff`, and benchmark functions.

## Control Flow
Early tests verify MVCC visibility by timestamp for single get, batch get, delete, cleanup, and point-get with primary-key locks. Scan tests build multi-version key layouts and repeatedly check historical snapshots, limits, bounds, reverse bounds, and key-only mode. Lock tests create several prewrites, scan locks by safe point/range/limit, resolve or batch-resolve locks as rollback or commit, and reject illegal TSO ordering. GC tests run both single-engine and raft-cluster storage over small, large, and long-key sets, ensuring old versions disappear after collection. RawKV tests cover get/put/delete/scan, CF selection, key-size errors, API-version rules for V1/V1ttl/V2, raw batch APIs, raw atomic CAS/delete/put, and raw checksum. Isolation tests spawn concurrent increment transactions with retry/backoff and verify every increment observes serializable progress.

## State, Persistence, and Dependencies
State includes MVCC default/write/lock CF entries, raw CF values, locks, rollback records, GC-safe regions, request API version, and in-memory oracle timestamps. Dependencies are the test storage harness, engine traits, kvproto request types, TiKV GC constants, random jitter, and CRC64 checksum logic.

## Integration Points, Risks, and Test Signals
This suite is a primary behavioral contract for transaction storage and raw API validation. Signals are exact visibility assertions, expected errors, lock-info equality, absence after GC, checksum tuple equality, and concurrent punch-card uniqueness. Risks include large stress cases near batch/write-size constants and benchmarks compiled only under bench harness; API-version matrices are dense and should be updated with any key-format change.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/storage/test_storage.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/storage/test_titan.rs -->
# sources/storage-engines/tikv/tests/integrations/storage/test_titan.rs

## Purpose
This file tests TiKV behavior when RocksDB Titan blob storage is enabled, disabled, garbage-collected, and used during snapshot/range deletion flows. It focuses on safe Titan shutdown and avoiding missing-blob or key resurrection problems.

## Important APIs, Types, and Functions
`test_turnoff_titan` uses raftstore cluster helpers, `configure_for_enable_titan`, `configure_for_disable_titan`, RocksDB properties, CF option updates, compaction, and `pre_start_check`. The ignored `test_delete_files_in_range_for_titan` constructs `Engines`, writes raw MVCC keys, ingests an external SST delete, triggers Titan GC, calls `delete_ranges_cfs` with `DeleteFiles`, `DeleteByKey`, and `DeleteBlobs`, builds SST snapshot files, ingests them into another DB, and scans with `ScannerBuilder`.

## Control Flow
The first test writes values into a Titan-enabled cluster, flushes twice, checks L0/blob-file counts, shuts down, verifies startup fails when Titan is disabled prematurely, reopens with Titan, switches `blob_run_mode` to fallback, compacts until blob files are removed, shuts down, and then verifies Titan-disabled startup succeeds after purge. The ignored test creates an overlapped LSM/Titan layout, deletes a range by multiple strategies, builds snapshot SSTs, applies them to a fresh engine, and asserts only key `b` remains visible.

## State, Persistence, and Dependencies
Persistent state is Rocks/Titan data directories, blob files, SST levels, ingested external files, and snapshot SSTs. Dependencies include `engine_rocks`, `engine_traits`, raftstore snapshot helpers, TiKV config builders, and MVCC scanner types.

## Integration Points, Risks, and Test Signals
The tests integrate Titan file lifecycle with TiKV startup checks, compaction, range deletion, snapshot generation, and ingestion. Signals are RocksDB property counts, `pre_start_check` success/failure, and scanner output. The ignored test is valuable but not normally run; it is timing- and storage-layout-sensitive.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/storage/test_titan.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/.devcontainer/Dockerfile -->
# sources/storage-engines/wiredtiger/.devcontainer/Dockerfile

## Purpose
This Dockerfile defines a VS Code devcontainer base image for WiredTiger development on Ubuntu 26.04. It installs compilers, CMake/Ninja, debugging tools, compression/security libraries, Python/SWIG tooling, and formatting/static-analysis utilities.

## Important APIs, Types, and Functions
The file uses Docker build instructions `FROM`, `RUN`, `USER`, `ENV`, and `WORKDIR`. It creates a non-root `wiredtiger` user and a Python virtual environment at `/home/wiredtiger/venv`.

## Control Flow, State, and Dependencies
Build flow updates apt metadata, installs packages without recommended extras, removes apt lists, creates the user, switches to that user, creates a venv, prepends it to `PATH`, and installs pinned Python packages (`find_libpython`, `gcovr`, `psutil`, `ruff`, `uv`). State is baked into the container image.

## Integration Points, Risks, and Test Signals
It supports the paired `devcontainer.json` and local CMake/Python/SWIG workflows. Risks include Ubuntu 26.04 package availability and pinned Python versions aging. Test signal is successful image build and ability to configure WiredTiger inside `/workdir`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/.devcontainer/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/.devcontainer/devcontainer.json -->
# sources/storage-engines/wiredtiger/.devcontainer/devcontainer.json

## Purpose
This VS Code devcontainer descriptor names the WiredTiger development container and points the container build at the local Dockerfile.

## Important APIs, Types, and Functions
It configures `"build": {"dockerfile": "Dockerfile"}` and VS Code customizations: clangd, Python, CMake Tools, C/C++, and YAML extensions. Settings disable the Microsoft C/C++ IntelliSense engine and select `clangd`.

## Control Flow, State, and Dependencies
The file is declarative; the devcontainer runtime builds the Dockerfile and applies editor extensions/settings. It depends on VS Code Remote Containers and the Dockerfile in the same directory.

## Integration Points, Risks, and Test Signals
It integrates editor tooling with the repository's CMake compile database and clangd workflow. Risk is extension/settings drift. Signal is a devcontainer opening successfully with clangd and CMake tooling available.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/.devcontainer/devcontainer.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/.github/workflows/pr_checklist.yml -->
# sources/storage-engines/wiredtiger/.github/workflows/pr_checklist.yml

## Purpose
This GitHub Actions workflow posts a structured review checklist comment when a pull request is opened. It is process automation rather than build/test execution.

## Important APIs, Types, and Functions
The workflow triggers on `pull_request` type `opened`, runs one `ubuntu-latest` job, and uses `actions/github-script@v7` to call `github.rest.issues.createComment`.

## Control Flow, State, and Dependencies
On PR open, the script builds a Markdown comment with review readiness, safety, compatibility, test coverage, risk, and change-type questions, then posts it to the PR issue thread. State is stored as a GitHub comment.

## Integration Points, Risks, and Test Signals
It integrates with GitHub Issues/PR comments and links repository risk/testing docs. Risks include duplicate comments on reopen only if workflow trigger changes, and reliance on `GITHUB_TOKEN` permissions. Signal is the comment appearing on new PRs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/.github/workflows/pr_checklist.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/.github/workflows/pr_title_checker.yml -->
# sources/storage-engines/wiredtiger/.github/workflows/pr_title_checker.yml

## Purpose
This workflow enforces WiredTiger PR title policy on opened, edited, and synchronized pull requests.

## Important APIs, Types, and Functions
It runs `thehanimo/pr-title-checker@v1.4.3` with `GITHUB_TOKEN`, `pass_on_octokit_error: false`, and a configuration file path `.github/workflows/pr_title_checker_config.json`.

## Control Flow, State, and Dependencies
Each trigger starts a single `ubuntu-latest` job. The action reads the JSON config and fails the job if the title does not match policy. No repository state is modified.

## Integration Points, Risks, and Test Signals
It integrates with GitHub branch protection/status checks. Risks are third-party action availability and config regex mistakes. Signal is pass/fail status on the PR.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/.github/workflows/pr_title_checker.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/.github/workflows/pr_title_checker_config.json -->
# sources/storage-engines/wiredtiger/.github/workflows/pr_title_checker_config.json

## Purpose
This JSON file configures the PR title checker workflow. It requires titles to start with a WiredTiger ticket number or a `Revert "` prefix followed by a ticket.

## Important APIs, Types, and Functions
`CHECKS.regexp` is `^(Revert \")?WT-[0-9]+ [ -~]+$`, constraining titles to `WT-<digits> ` plus printable ASCII. `MESSAGES` define success and failure text.

## Control Flow, State, and Dependencies
The file is read by `thehanimo/pr-title-checker`; it has no independent execution. Policy state is versioned in the repository.

## Integration Points, Risks, and Test Signals
It integrates with `.github/workflows/pr_title_checker.yml`. Risk is rejecting valid non-ASCII titles or non-WT maintenance PRs. Signal is the title-check workflow result.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/.github/workflows/pr_title_checker_config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/.mcp.json -->
# sources/storage-engines/wiredtiger/.mcp.json

## Purpose
This file declares a repository-local MCP server named `wt` for WiredTiger tooling.

## Important APIs, Types, and Functions
The server uses `"type": "stdio"`, command `uv`, and arguments `--directory ./tools/wt-mcp run server.py`.

## Control Flow, State, and Dependencies
An MCP-capable client reads this JSON and starts the server process with `uv`. Runtime state belongs to the Python server under `tools/wt-mcp`; this file only describes launch configuration.

## Integration Points, Risks, and Test Signals
It integrates AI/editor tooling with WiredTiger-specific helpers. Risks are missing `uv`, absent `tools/wt-mcp`, or changed server entrypoint. Signal is successful MCP server startup over stdio.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/.mcp.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/CMakeLists.txt

## Purpose
This is WiredTiger's top-level CMake build definition. It configures platform detection, third-party libraries, build modes, generated headers, static/shared library targets, Python/workgen bindings, test suites, benchmarks, examples, and tools.

## Important APIs, Types, and Functions
Key CMake helpers include `parse_filelist_source`, `define_wiredtiger_library`, `configure_file`, `FetchContent_Declare/MakeAvailable`, `enable_testing`, `add_subdirectory`, and `setup_gdb_autoloader`. Important variables include `WT_ARCH`, `WT_OS`, `ENABLE_STATIC`, `ENABLE_SHARED`, `WITH_PIC`, `ENABLE_PYTHON`, `HAVE_BUILTIN_EXTENSION_*`, `ENABLE_STRICT`, and `ENABLE_LLVM`.

## Control Flow
CMake detects target architecture/OS, includes platform files, sets ccache if available, loads third-party discovery and base config, enforces at least one library flavor, applies compiler standard and strict/color options, optionally fetches Catch2, parses the `dist/filelist`, builds builtin extension object lists, generates `wiredtiger.h` and `wiredtiger_config.h`, creates object/static/shared library targets, aliases `wt::wiredtiger`, then descends into utilities, install rules, Python/workgen, benchmark/test/example/tool directories.

## State, Persistence, and Dependencies
Build state is CMake cache, generated headers under the binary directory, object libraries, and install/export metadata. Dependencies include platform config modules, third-party compression/crypto/memkind/IAA/lazyfs/voidstar/sqlite discovery, Python3/SWIG for bindings, and Catch2 for unit tests.

## Integration Points, Risks, and Test Signals
This file is the central integration point for all compiled WiredTiger artifacts. Risks include feature-toggle interactions, PIC requirements for shared/SWIG consumers, typo-prone variable names, and network dependency when fetching Catch2. Signals are successful configure/generate/build across presets and the existence of expected benchmark/test targets.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/CMakePresets.json -->
# sources/storage-engines/wiredtiger/CMakePresets.json

## Purpose
This file defines CMake presets for common WiredTiger configure/build environments, especially MongoDB toolchain compiler selections on Linux.

## Important APIs, Types, and Functions
It uses CMake Presets version 3. Configure presets include `default`, hidden `linux`, hidden `linux-v4`, `linux-gcc`, `linux-clang`, and `linux-v4-gcc`. Build preset `default` references configure preset `default` and uses `jobs: 0`.

## Control Flow, State, and Dependencies
Preset selection injects environment variable `MONGODBTOOLCHAIN_BIN` and compiler cache variables for GCC or Clang. Conditions restrict Linux-specific presets to Linux hosts. State is CMake cache generated from selected preset.

## Integration Points, Risks, and Test Signals
It integrates local/CI configure commands with expected toolchain paths. Risks are hard-coded `/opt/mongodbtoolchain` availability and no explicit binary directory. Signal is successful `cmake --preset <name>` configure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/CMakePresets.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/dhandle/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/bench/dhandle/CMakeLists.txt

## Purpose
This CMake file registers the data-handle benchmark executable when building on POSIX platforms.

## Important APIs, Types, and Functions
It calls `project(C)`, includes `test/ctest_helpers.cmake`, gates on `WT_POSIX`, and invokes `create_test_executable(bench_dhandle SOURCES bench_dhandle.c bench_timer.c)`.

## Control Flow, State, and Dependencies
During configure, non-POSIX builds skip the target. POSIX builds create a benchmark/test executable linked according to repository helper rules. Dependencies are the benchmark C files and test utility infrastructure.

## Integration Points, Risks, and Test Signals
It integrates the dhandle benchmark into the top-level `add_subdirectory(bench/dhandle)`. Risk is no target on Windows by design. Signal is generated `bench_dhandle` target in POSIX builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/dhandle/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/dhandle/bench_dhandle.c -->
# sources/storage-engines/wiredtiger/bench/dhandle/bench_dhandle.c

## Purpose
This benchmark stresses WiredTiger data-handle lifecycle behavior under dynamic table creation, dropping, checkpoints, reads, and updates. It grows to a target table count, keeps a configured active window, drops older tables, and measures operation latencies.

## Important APIs, Types, and Functions
Core types are `SHARED`, `THREAD_ARGS`, and `WORK_ITEM`. Key functions are `main`, `bench_dhandle`, `bench_dhandle_run`, `creator`, `queuer`, `worker`, `checkpointer`, and `shuffle`. It uses WiredTiger `WT_CONNECTION`, `WT_SESSION`, `WT_CURSOR`, test utility allocation/parsing helpers, `TAILQ`, pthreads, and `BENCH_TIMER` macros/functions.

## Control Flow
`main` parses benchmark options and defaults. `bench_dhandle` recreates/open the home and runs the workload. `bench_dhandle_run` starts N worker threads plus creator, queuer, and checkpointer, then periodically aggregates per-thread timers and prints deltas/minute summaries until runtime or active-table completion. The creator creates tables to a time-based target high watermark, inserts first records, advances low/exists/high watermarks, drops obsolete tables, and throttles to creation-time percent. The queuer waits for initial tables, builds work items over active table numbers, marks about 10% as updates, and pushes them under a rwlock. Workers pop work items, open cursors, search or update table key 0, and reset sessions. The checkpointer periodically calls `session->checkpoint`.

## State, Persistence, and Dependencies
Persistent state is the WiredTiger home with thousands of table files and statistics logs. Shared state includes table watermarks, queue length, done/started/checkpoint flags, checkpoint number, and per-thread shared timers updated with memory barriers. Dependencies are POSIX pthreads, WiredTiger internal/test utilities, queue macros, and `bench_timer`.

## Integration Points, Risks, and Test Signals
The benchmark integrates schema churn, dhandle open/close, checkpointing, and concurrent table operations. Test signals are printed operation counts and per-op times; the queue overflow path fails by setting `done`. A notable risk is `shuffle`: the loop initializes `i = n - 1` but tests `i < 0`, so it appears never to shuffle. This can bias queue order and weaken randomization.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/dhandle/bench_dhandle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/dhandle/bench_timer.c -->
# sources/storage-engines/wiredtiger/bench/dhandle/bench_timer.c

## Purpose
This file implements a small timing accumulator used by the dhandle benchmark to measure operation counts and elapsed time per operation.

## Important APIs, Types, and Functions
Functions include `bench_timer_init`, `bench_timer_start`, `bench_timer_stop`, `bench_timer_add`, `bench_timer_add_to_shared`, `bench_timer_add_to_shared_2`, `bench_timer_add_from_shared`, internal `__bench_timer_format`, and `bench_timer_show_change`.

## Control Flow
Callers initialize a `BENCH_TIMER`, start it before an operation using `__wt_epoch`, stop it after the operation, and aggregate totals/counts either locally or into shared timers using WiredTiger release/acquire barriers. `bench_timer_show_change` compares a previous snapshot with a new snapshot and prints delta operation count plus formatted per-operation latency.

## State, Persistence, and Dependencies
Timer state is `name`, `total_nsec`, `count`, and `start_nsec`. There is no persistence. Dependencies include `WT_SESSION_IMPL`, `WT_BILLION/MILLION/THOUSAND`, memory barrier macros, asserts, and test utility formatting assertions.

## Integration Points, Risks, and Test Signals
It integrates with `bench_dhandle.c` through macros in `bench_timer.h`. Risks include asserts if start/stop are mispaired and no reset of `start_nsec` after stop, which means a single timer object is expected to be initialized before reuse. Signal is printed timing rows when counts advance.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/dhandle/bench_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/dhandle/bench_timer.h -->
# sources/storage-engines/wiredtiger/bench/dhandle/bench_timer.h

## Purpose
This header declares the `BENCH_TIMER` struct, timing functions, and convenience macros for measuring single and cumulative benchmark operations.

## Important APIs, Types, and Functions
`BENCH_TIMER` stores `name`, `total_nsec`, `count`, and `start_nsec`. Macros `BENCH_TIME_SINGLE` and `BENCH_TIME_CUMULATIVE` wrap statements with timer start/stop and aggregation.

## Control Flow, State, and Dependencies
Callers include the header, allocate timers, and use macros around WiredTiger operations. The cumulative macro creates a stack timer then adds its result to a shared timer. Dependencies are `WT_SESSION`, `uint64_t`, and the implementation in `bench_timer.c`.

## Integration Points, Risks, and Test Signals
The header is tightly coupled to the dhandle benchmark and WiredTiger timing/barrier primitives. Risk is macro statement side effects and required semicolon/block discipline. Signal is successful compilation and consistent operation counts in benchmark output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/dhandle/bench_timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/perf_run_py/aggregate_perf_stat.py -->
# sources/storage-engines/wiredtiger/bench/perf_run_py/aggregate_perf_stat.py

## Purpose
This script aggregates multiple Evergreen-style performance JSON files into a simple CSV named `all_stats.csv`.

## Important APIs, Types, and Functions
`main` uses `glob.glob('perf_stats/*.json')`, `json.load`, and writes columns `Test Name, Metric Name, Value`.

## Control Flow, State, and Dependencies
The script opens `all_stats.csv`, iterates every JSON file under `perf_stats`, expects each file to contain a list with a first element having `info.test_name` and `metrics`, and writes one CSV row per metric. State is the output CSV file.

## Integration Points, Risks, and Test Signals
It integrates with `perf_run.py` brief output or similar Evergreen-compatible files. Risks include no CSV escaping for metric names containing commas, no context manager for the output file, and failure on detailed Atlas-style JSON. Signal is a populated `all_stats.csv`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/perf_run_py/aggregate_perf_stat.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/perf_run_py/perf_config.py -->
# sources/storage-engines/wiredtiger/bench/perf_run_py/perf_config.py

## Purpose
This module holds configuration objects for the WiredTiger Python performance runner.

## Important APIs, Types, and Functions
`TestType` records whether a run is `wtperf` or `workgen` and maps home/test arguments to the proper CLI shape (`-h`/`-O` for wtperf, `--home`/positional for workgen). `PerfConfig` stores executable path, home directory, test path, batch file, extra arguments, requested operations, run count, verbosity, and improved-accuracy flag.

## Control Flow, State, and Dependencies
The module is passive. `PerfConfig.to_value_dict` serializes config fields into report metadata. State is in object attributes. It has no external dependencies beyond Python basics.

## Integration Points, Risks, and Test Signals
It integrates with `perf_run.py` command construction and output reporting. Risks include `TestType.get_home_arg/get_test_arg` returning `None` if both booleans are false, so callers must enforce mutual exclusivity. Signal is correct command lines for wtperf/workgen tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/perf_run_py/perf_config.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/perf_run_py/perf_json_converter_for_atlas_evergreen.py -->
# sources/storage-engines/wiredtiger/bench/perf_run_py/perf_json_converter_for_atlas_evergreen.py

## Purpose
This utility converts a flat JSON mapping of metric names to values into both Atlas-compatible and Evergreen-compatible performance output JSON files.

## Important APIs, Types, and Functions
Functions are `parse_input_file`, `generate_output_atlas`, `generate_output_evg`, and `main`. CLI options are `--test_name`, `--input_file`, and `--output_path`.

## Control Flow, State, and Dependencies
The script reads the input JSON, builds an Atlas object with `"Test Name"`, `"metrics"`, and `"config"`, builds an Evergreen list containing `info.test_name` and `metrics`, then writes `atlas_out_<test>.json` and `evergreen_out_<test>.json`. State is only the generated files.

## Integration Points, Risks, and Test Signals
It integrates external benchmark metric producers with WiredTiger/Atlas/Evergreen perf consumers. Risks include assuming output directory exists and metric values are JSON-serializable numbers. Signal is two valid JSON files.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/perf_run_py/perf_json_converter_for_atlas_evergreen.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/perf_run_py/perf_run.py -->
# sources/storage-engines/wiredtiger/bench/perf_run_py/perf_run.py

## Purpose
This is the main Python harness for running WiredTiger wtperf/workgen performance tests, collecting selected metrics, and writing brief Evergreen-compatible or detailed Atlas-compatible JSON output.

## Important APIs, Types, and Functions
Important functions include `create_test_home_path`, `construct_command_line`, `configure_for_extra_accuracy`, `run_test_wrapper`, `run_test`, `process_results`, `parse_args`, `parse_json_args`, `validate_operations`, `run_perf_tests`, `report_results`, and `main`. It uses `PerfConfig`, `TestType`, `PerfStat`, and `PerfStatCollection`.

## Control Flow
`main` parses CLI flags, converts JSON arguments/operations, validates duplicate/unknown operations, runs one or more tests unless `--reuse` is set, processes stat files from generated home directories, and writes/prints JSON results. Batch mode reads a JSON list of argument/operation sets and processes each with an index-specific home prefix. Extra accuracy mode forces `run_max = 5` and tries to inject `run_time=240`.

## State, Persistence, and Dependencies
Persistent state includes per-run home directories, `stdout_file.txt`, and the output JSON path. Dependencies include `argparse`, `subprocess`, `psutil`, `platform`, local perf modules, and test executables. It captures stdout/stderr together and exits on subprocess failure.

## Integration Points, Risks, and Test Signals
It bridges executable workloads, stat extraction, and CI performance formats. Risks include JSON argument quoting, batch mode mutating `config.run_max` for later entries, `configure_for_extra_accuracy` returning `None` on one branch, use of `list.index` for duplicate batch entries, and overwriting `stdout_file.txt`. Signals are subprocess success and populated metrics matching requested operation labels.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/perf_run_py/perf_run.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/perf_run_py/perf_stat.py -->
# sources/storage-engines/wiredtiger/bench/perf_run_py/perf_stat.py

## Purpose
This module defines metric extractors and aggregators for the performance runner. It turns stat-file text or JSON records into values suitable for Evergreen/Atlas output.

## Important APIs, Types, and Functions
`PerfStat` performs regex matching, conversion, trimmed-average aggregation, and output formatting. Subclasses implement special behavior: `PerfStatMinMax`, `PerfStatCount`, `PerfStatLatency`, `PerfStatLatencyWorkgen`, and `PerfStatDBSize`.

## Control Flow
Each stat object searches one or more files for matching values, `add_values` converts and stores them, and `get_value_list` formats one or more report metrics. Latency classes parse `monitor.json` JSON lines or workgen stdout latencies. DB size sums files in the test home directory.

## State, Persistence, and Dependencies
State is the `values` list on each metric object. Dependencies include `glob`, `json`, `os`, `re`, stat-file naming conventions, and monitor JSON schemas.

## Integration Points, Risks, and Test Signals
It integrates with `PerfStatCollection.find_stats` and `perf_run.py` reports. Risks include empty `values` causing divide-by-zero, `PerfStatDBSize` passing a `DirEntry` to `os.path.getsize`, first-match-only glob behavior in count stats, and schema assumptions for wtperf/workgen JSON. Signals are extracted metric values and value lists.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/perf_run_py/perf_stat.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/perf_run_py/perf_stat_collection.py -->
# sources/storage-engines/wiredtiger/bench/perf_run_py/perf_stat_collection.py

## Purpose
This module declares the catalog of supported performance metric labels and coordinates extraction of requested stats from test home directories.

## Important APIs, Types, and Functions
`create_test_stat_path` joins a home path and stat filename. `PerfStatCollection.__init__` filters `all_stats()` by requested operation short labels. `find_stats` searches each candidate stat file and adds values. Static methods `cache_eviction_stats`, `latency_stats`, and `all_stats` define the supported metrics.

## Control Flow
Callers construct a collection with operation names, run tests, then call `find_stats` for each home. For each configured stat, it searches its ordered `stat_files`; if two files match for one metric, it raises a runtime error, otherwise it appends found values to the metric.

## State, Persistence, and Dependencies
State is `to_report`, a list of `PerfStat` instances that accumulate values across runs. Dependencies are local stat classes and output files such as `test.stat`, `workload.stat`, `latency.stat`, `monitor.json`, `cache_eviction.stat`, `prefetch_stats.out`, `WiredTigerStat*`, and `stdout_file.txt`.

## Integration Points, Risks, and Test Signals
This is the central stat registry used by `validate_operations` and `process_results`. Risks include regex/input-offset coupling to exact stat text, duplicate short labels not being guarded except by caller validation, and empty requested operations producing no metrics. Signal is a non-empty `to_report` with populated values.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/perf_run_py/perf_stat_collection.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/perf_run_py/validate_expected_stats.py -->
# sources/storage-engines/wiredtiger/bench/perf_run_py/validate_expected_stats.py

## Purpose
This CLI validates expected metric values against an Evergreen-style `evergreen_out*.json` performance output file.

## Important APIs, Types, and Functions
`main` parses positional arguments `stat_file`, `comparison_op`, and `expected_stats`, validates filename shape, loads JSON, builds a metric-name/value map, and compares expected values using `eq`, `gt`, or `lt`.

## Control Flow, State, and Dependencies
The script rejects non-matching filenames, decodes the expected-stats JSON object, accumulates errors for missing or mismatched metrics, prints all errors and exits 1 if any exist, otherwise prints success. It depends on the Evergreen output schema used by `perf_run.py` brief mode.

## Integration Points, Risks, and Test Signals
It integrates performance tests with CI threshold checks. Risks include continuing after an invalid comparison operator message without immediate exit and exact equality on potentially noisy numeric metrics. Signals are process exit code and error messages.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/perf_run_py/validate_expected_stats.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/tiered/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/bench/tiered/CMakeLists.txt

## Purpose
This CMake file registers the tiered-storage push/pull benchmark executable.

## Important APIs, Types, and Functions
It calls `create_test_executable(test_push_pull SOURCES push_pull.c)`.

## Control Flow, State, and Dependencies
During configure, the repository test helper creates a `test_push_pull` target from `push_pull.c`. It depends on the top-level inclusion of ctest helpers and WiredTiger test utility link rules.

## Integration Points, Risks, and Test Signals
It integrates the tiered benchmark into the top-level benchmark suite. Risk is minimal; build failure indicates missing helper setup or source compile problems. Signal is the generated executable target.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/tiered/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/tiered/push_pull.c -->
# sources/storage-engines/wiredtiger/bench/tiered/push_pull.c

## Purpose
This benchmark measures tiered-storage checkpoint push/pull behavior for different logical table sizes, comparing checkpoint with and without `flush_tier`, and validating recovered data.

## Important APIs, Types, and Functions
Key functions are `main`, `run_test_clean`, `run_test`, `populate`, `recover_validate`, `get_file_size`, `compute_tiered_file_size`, `compute_wt_file_size`, `fill_random_data`, `difftime_msecs`, `difftime_sec`, and `calculate_std_deviation`. It uses `TEST_OPTS`, `WT_CONNECTION`, `WT_SESSION`, `WT_CURSOR`, `WT_ITEM`, WiredTiger random helpers, and test utility filesystem functions.

## Control Flow
`main` parses test options and runs each size twice: first without flush, then with flush enabled when tiered storage is active. `run_test_clean` repeats each size `MAX_RUN` times, cleaning homes and averaging write/read time, throughput, file size, and standard deviation. `run_test` opens a home, creates a table, populates deterministic random records, checkpoints with optional `flush_tier`, computes file size after close, and optionally calls `recover_validate`. Recovery reopens the home, regenerates the same random sequence, scans all records, and verifies keys and values.

## State, Persistence, and Dependencies
Persistent state is per-run WiredTiger homes, local `.wt` files or tiered `.wtobj` files, copied debug data, and table contents. Dependencies include tiered-storage test options, directory-store support, POSIX stat/getcwd/chdir, math library, and WiredTiger test utilities.

## Integration Points, Risks, and Test Signals
It integrates table population, checkpoint, tiered flush, recovery, file-size accounting, and throughput reporting. Signals are assertions during recovery and printed averages. Risks include fixed `MAX_TIERED_FILES`, sleep-based file visibility, global arrays reused per run, and dependence on deterministic random seeding.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/tiered/push_pull.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/bench/workgen/CMakeLists.txt

## Purpose
This CMake file builds the Python workgen extension and supporting C++ library for POSIX WiredTiger builds when Python support is enabled.

## Important APIs, Types, and Functions
It selects `wiredtiger_static` with PIC or `wiredtiger_shared`, builds `workgen_cpp` from `workgen.cpp` and `workgen_func.c`, sets include directories and link libraries, configures SWIG flags, calls `swig_add_library(workgen TYPE ${share_state} LANGUAGE python SOURCES workgen.i)`, links generated module, and applies compiler/linker options.

## Control Flow
Non-POSIX builds return early. POSIX builds choose a link target, create a PIC static C++ helper library, hide libstdc++ symbols via `--exclude-libs`, configure SWIG interface name `_workgen`, include generated headers/configs, compile the Python extension, suppress SWIG wrapper warnings, and force `.so` suffix on Darwin.

## State, Persistence, and Dependencies
Build state includes `workgen_cpp`, `_workgen` Python extension, generated SWIG wrappers, and compiler flags. Dependencies include Python3, SWIG, WiredTiger library targets, `test_util`, generated headers, and POSIX support.

## Integration Points, Risks, and Test Signals
It integrates C++ workgen APIs with Python workloads under `bench/workgen/runner`. Risks include requiring PIC/shared builds, possible typo in `message(STATIC ...)`, and platform-specific dynamic-loading quirks. Signal is successful import of the generated `workgen` module.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/latency_metric.py -->
# sources/storage-engines/wiredtiger/bench/workgen/latency_metric.py

## Purpose
This script computes latency summary metrics from workgen `monitor.json` files, especially comparing read latency during checkpoint intervals versus normal intervals.

## Important APIs, Types, and Functions
`Digest` accumulates entries, operations, weighted average latency, raw/weighted 99th percentile latency, max latency, and elapsed seconds. `Metric` stores report metadata. `FileMetrics` parses one file and calculates `Average latency reads us`, `Max latency reads us`, `Max vs average latency`, `Checkpoint vs normal 99%`, and `Proportion of ckpt time`. Helper functions format a table.

## Control Flow
The script parses argv for `--raw` and filenames. Each `FileMetrics.calculate` wraps JSON lines into a synthetic `{"ts": [...]}` array and calls `calculate_using_json`. Iteration tracks checkpoint active transitions, skips the first entry for elapsed-time calculation, splits read stats into checkpoint or normal digests, validates that there are entries/ops and at least two checkpoints, computes metrics, and prints a table across files. Raw mode dumps digest internals.

## State, Persistence, and Dependencies
State is in per-file metric/digest objects. Dependencies include `json`, `datetime`, monitor entries with `localTime`, `workgen.checkpoint.active`, and `workgen.read` latency fields.

## Integration Points, Risks, and Test Signals
It integrates with workgen runs that emit monitor JSON. Risks include loading entire files into memory, strict timestamp format, exceptions when checkpoint coverage is insufficient, and weighted/raw 99th percentile semantics that should be understood before thresholding. Signal is tabular output or detailed raw diagnostics.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/latency_metric.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/cache-stuck-disagg.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/cache-stuck-disagg.py

## Purpose
This workgen runner creates a heavy disaggregated-storage workload intended to reproduce or measure cache-stuck behavior with layered/disagg block management, timestamped transactions, and periodic checkpoints.

## Important APIs, Types, and Functions
It imports `runner`, `wiredtiger`, and `workgen`, creates a `Context`, opens a WiredTiger connection with disaggregated/palite extension config, defines a layered table, constructs `Operation`, `Thread`, and `Workload` objects, uses `txn`, and writes latency output through `latency.workload_latency`.

## Control Flow
The script opens a leader disaggregated connection, creates one table, runs an initial populate workload with eight insert threads plus checkpoint threads for about ten million rows, then builds a 900-second run workload with 24 update threads, 8 insert threads, 8 timestamp-lagged read threads, and one checkpoint thread. It sets timestamp advancement/lags, report interval, runs the workload, records elapsed time, writes latency output, and closes the connection.

## State, Persistence, and Dependencies
Persistent state is the workgen home, palite page-log/disaggregated files, populated table data, and `latency.out`. Dependencies include `WT_BUILDDIR` for the palite extension path, the built `workgen` Python module, and substantial disk/time resources.

## Integration Points, Risks, and Test Signals
It integrates disaggregated storage, precise checkpoints, timestamp management, and workload latency reporting. Risks include very large runtime/resource needs, no explicit guard for missing `WT_BUILDDIR`, and assertion-only failure handling. Signals are workload return code zero, elapsed-time prints, and generated latency file.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/cache-stuck-disagg.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/cache_workload_dirty_trigger.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/cache_workload_dirty_trigger.py

## Purpose
This workgen runner creates a cache dirty-trigger workload with mixed table updates, reads, log-like traffic, and bursty operation storms. It is adapted from a generated wtperf workload and tuned to pressure eviction/update triggers.

## Important APIs, Types, and Functions
It uses `Context`, `Table`, `Operation`, `Thread`, `Workload`, `op_multi_table`, `op_log_like`, `txn`, `get_cache_eviction_stats`, and `latency.workload_latency`. Connection config sets cache size, eviction threads, logging, session max, fast statistics, statistics logging, and IO capacity.

## Control Flow
The script opens a WiredTiger connection, creates ten file tables, populates one million records across them, creates a logged table, defines throttled log update/read threads, defines transactional multi-table update and read storm threads with sleep cycles, computes 128 total workload threads split by read percentage, runs for 200 seconds with latency sampling, then writes cache eviction stats and latency stats under the test home.

## State, Persistence, and Dependencies
Persistent state includes the workload home, tables, log table, statistics log, `cache_eviction.stat`, and `latency.stat`. Dependencies include built workgen bindings, WiredTiger Python module, and runner helper functions.

## Integration Points, Risks, and Test Signals
It integrates cache pressure, eviction stats, latency sampling, logging, and multi-table transactional operations. Risks include high thread/resource demand, a likely typo assigning `"Search"` to `thread_upd10k_sleep10.options.name` instead of the read thread, and no CLI-level parameterization. Signals are workload return code zero and generated stat/latency files.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/cache_workload_dirty_trigger.py -->
