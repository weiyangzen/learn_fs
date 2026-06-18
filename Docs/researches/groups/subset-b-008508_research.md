# Group Research: subset-b-008508

Work item `subset-b-008508` covers 206 FoundationDB test-runner and simulation-spec source files. Each section below is wrapped for reconciliation and split into the tree-aligned per-file output path.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/TestRunner.py -->
# Research: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/TestRunner.py

- **Purpose:** Primary simulation/test runner wrapper. It builds fdbserver command lines, launches one or more simulation specs, aggregates trace output, interprets severity/return-code failures, and applies restart-test binary selection rules.
- **Source facts:** 589 lines, 19265 bytes, executable=True.
- **Important APIs/types/functions:** Imports: .TestDirectory.TestDirectory, argparse.ArgumentParser, functools, io, json, logging, os, re, shutil, subprocess, sys, xml.sax; plus 1 more. Classes: LogParser, JSONParser, XMLParser, RestartTestPolicy, XMLHandler, XMLErrorHandler. Top-level functions: init_logging, get_traces, process_traces, run_simulation_test, main, __init__, write, fail, write_header, write_footer, apply_address_to_line, sanitize_backtrace; plus 20 more. Methods: LogParser.__init__, LogParser.write, LogParser.fail, LogParser.write_header, LogParser.write_footer, LogParser.apply_address_to_line, LogParser.sanitize_backtrace, LogParser.process_traces, LogParser.log_trace_parse_error, LogParser.process_return_codes, JSONParser.__init__, JSONParser.process_line; plus 15 more. Constants: none. CLI flags/options observed: --aggregate-traces, --buggify, --builddir, --config, --crash, --keep-logs, --keep-simdirs, --log-format, --logdir, --loglevel, --name, --old-binary; plus 17 more.
- **Control flow:** CLI parsing initializes logging, builds fdbserver arguments, optionally switches binaries across restart-test files, runs each simulation file, parses XML/JSON traces, folds return-code and severity events into pass/fail, and applies log/simdir retention policy.
- **State and persistence:** launches or inspects child processes (3 subprocess call sites) creates, reads, renames, or removes filesystem artifacts (4 filesystem call sites)
- **Dependencies:** Python imports: .TestDirectory.TestDirectory, argparse.ArgumentParser, functools, io, json, logging, os, re, shutil, subprocess, sys, xml.sax; plus 1 more; external FoundationDB binaries and shell tools are invoked through subprocess; XML trace/event parsing is part of the validation path.
- **Integration points:** Integrated as the simulation-test command entry point from CMake/ctest and as the `run-test-runner` console script.
- **Risks:** Failures depend on external FoundationDB binaries, return codes, and trace contents; missing binaries or platform-specific behavior can fail before workload assertions run. The file uses assertions for contract checks, so optimized Python execution would weaken some validation.
- **Test signals:** Observable signals include returncode, assert; failures normally surface as non-zero process exits, failed assertions, missing expected output, or trace severity events.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/TestRunner.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/__init__.py -->
# Research: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/__init__.py

- **Purpose:** Package marker for the fdb_test_runner module namespace. It has no runtime exports, but makes relative imports from the TestRunner helper scripts work under module execution.
- **Source facts:** 1 lines, 55 bytes, executable=False.
- **Important APIs/types/functions:** Imports: none. Classes: none. Top-level functions: none. Methods: none. Constants: none. CLI flags/options observed: none.
- **Control flow:** Library-style helpers are called by neighboring test-runner modules; control flow is direct function or context-manager execution.
- **State and persistence:** keeps no durable state beyond function-local values
- **Dependencies:** Python imports: none.
- **Integration points:** Used by neighboring FoundationDB test harness modules through package-relative imports or direct script execution.
- **Risks:** Risk is mainly integration drift with the surrounding test harness.
- **Test signals:** Observable signals include none; failures normally surface as non-zero process exits, failed assertions, missing expected output, or trace severity events.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/authz_util.py -->
# Research: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/authz_util.py

- **Purpose:** JWT/JWK helper utilities for temporary-cluster authorization tests. It creates EC/RSA keys, public key sets, and short-lived tenant authorization claims.
- **Source facts:** 67 lines, 1785 bytes, executable=False.
- **Important APIs/types/functions:** Imports: .test_util.random_alphanum_string, authlib.jose.JsonWebKey, authlib.jose.KeySet, authlib.jose.jwt, base64, json, time, typing.List, typing.Union. Classes: none. Top-level functions: to_str, private_key_gen, public_keyset_from_keys, alg_from_kty, token_gen, token_claim_1h. Methods: none. Constants: none. CLI flags/options observed: none.
- **Control flow:** Library-style helpers are called by neighboring test-runner modules; control flow is direct function or context-manager execution.
- **State and persistence:** keeps no durable state beyond function-local values
- **Dependencies:** Python imports: .test_util.random_alphanum_string, authlib.jose.JsonWebKey, authlib.jose.KeySet, authlib.jose.jwt, base64, json, time, typing.List, typing.Union; authlib.jose supplies JWK/JWT primitives.
- **Integration points:** Used by neighboring FoundationDB test harness modules through package-relative imports or direct script execution.
- **Risks:** The file uses assertions for contract checks, so optimized Python execution would weaken some validation. Randomized names, ports, or workflow choices make collision avoidance and reproducibility dependent on surrounding seed/control logic.
- **Test signals:** Observable signals include assert; failures normally surface as non-zero process exits, failed assertions, missing expected output, or trace severity events.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/authz_util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/binary_download.py -->
# Research: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/binary_download.py

- **Purpose:** Upgrade-test binary resolver/downloader. It chooses current/future build outputs, local old-binary repositories, or GitHub release downloads and validates SHA-256 checksums before use.
- **Source facts:** 180 lines, 7001 bytes, executable=False.
- **Important APIs/types/functions:** Imports: .fdb_version.CURRENT_VERSION, .fdb_version.FUTURE_VERSION, .test_util.random_alphanum_string, hashlib, os, pathlib.Path, platform, shutil, stat, urllib.request. Classes: FdbBinaryDownloader. Top-level functions: make_executable_path, compute_sha256, read_to_str, is_local_build_version, __init__, version_in_local_repo, binary_path, lib_dir, lib_path, download_old_binary, copy_clientlib_from_local_repo, download_old_binaries. Methods: FdbBinaryDownloader.__init__, FdbBinaryDownloader.version_in_local_repo, FdbBinaryDownloader.binary_path, FdbBinaryDownloader.lib_dir, FdbBinaryDownloader.lib_path, FdbBinaryDownloader.download_old_binary, FdbBinaryDownloader.copy_clientlib_from_local_repo, FdbBinaryDownloader.download_old_binaries. Constants: FDB_DOWNLOAD_ROOT, LOCAL_OLD_BINARY_REPO, MAX_DOWNLOAD_ATTEMPTS, SUPPORTED_PLATFORMS. CLI flags/options observed: none.
- **Control flow:** Library-style helpers are called by neighboring test-runner modules; control flow is direct function or context-manager execution.
- **State and persistence:** creates, reads, renames, or removes filesystem artifacts (5 filesystem call sites) downloads remote release artifacts
- **Dependencies:** Python imports: .fdb_version.CURRENT_VERSION, .fdb_version.FUTURE_VERSION, .test_util.random_alphanum_string, hashlib, os, pathlib.Path, platform, shutil, stat, urllib.request; GitHub FoundationDB release URLs are used for old binary download.
- **Integration points:** Used by upgrade and temporary-cluster tests to bridge Python orchestration with built FoundationDB binaries, local config files, and simulation/tester workloads.
- **Risks:** Release download paths and checksums are external dependencies; retry and atomic rename logic reduce but do not remove network/cache risk. The file uses assertions for contract checks, so optimized Python execution would weaken some validation. Randomized names, ports, or workflow choices make collision avoidance and reproducibility dependent on surrounding seed/control logic.
- **Test signals:** Observable signals include assert; failures normally surface as non-zero process exits, failed assertions, missing expected output, or trace severity events.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/binary_download.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/cluster_args.py -->
# Research: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/cluster_args.py

- **Purpose:** Shared argparse construction for temporary cluster wrappers. It centralizes build-dir, process count, TLS, authorization, blob granule, and cleanup options.
- **Source facts:** 71 lines, 2473 bytes, executable=False.
- **Important APIs/types/functions:** Imports: argparse.ArgumentParser, argparse.RawDescriptionHelpFormatter. Classes: none. Top-level functions: CreateTmpFdbClusterArgParser. Methods: none. Constants: none. CLI flags/options observed: --authorization-keypair-id, --authorization-kty, --blob-granules-enabled, --build-dir, --client-cert-chain-len, --no-remove-at-exit, --process-number, --server-cert-chain-len, --tls-enabled, --tls-verify-peer, -b, -p.
- **Control flow:** Library-style helpers are called by neighboring test-runner modules; control flow is direct function or context-manager execution.
- **State and persistence:** keeps no durable state beyond function-local values
- **Dependencies:** Python imports: argparse.ArgumentParser, argparse.RawDescriptionHelpFormatter.
- **Integration points:** Used by neighboring FoundationDB test harness modules through package-relative imports or direct script execution.
- **Risks:** Risk is mainly integration drift with the surrounding test harness.
- **Test signals:** Observable signals include none; failures normally surface as non-zero process exits, failed assertions, missing expected output, or trace severity events.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/cluster_args.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/fake_cluster.py -->
# Research: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/fake_cluster.py

- **Purpose:** Command wrapper that creates a disposable fake fdb.cluster file for tests that only need cluster-file argument plumbing, not a live database.
- **Source facts:** 88 lines, 2762 bytes, executable=True.
- **Important APIs/types/functions:** Imports: .test_util.random_alphanum_string, argparse.ArgumentParser, argparse.RawDescriptionHelpFormatter, os, pathlib.Path, shutil, subprocess, sys. Classes: ClusterFileGenerator. Top-level functions: main, __init__, __enter__, __exit__, close. Methods: ClusterFileGenerator.__init__, ClusterFileGenerator.__enter__, ClusterFileGenerator.__exit__, ClusterFileGenerator.close. Constants: none. CLI flags/options observed: --output-dir, -o.
- **Control flow:** Executable module: parse command-line arguments, perform setup, run the requested child/test workflow, and convert internal success/failure to process exit status.
- **State and persistence:** launches or inspects child processes (1 subprocess call sites) creates, reads, renames, or removes filesystem artifacts (3 filesystem call sites)
- **Dependencies:** Python imports: .test_util.random_alphanum_string, argparse.ArgumentParser, argparse.RawDescriptionHelpFormatter, os, pathlib.Path, shutil, subprocess, sys; external FoundationDB binaries and shell tools are invoked through subprocess.
- **Integration points:** Integrated as wrapper scripts around test commands that need FDB_CLUSTER_FILE or FDB_CLUSTERS without making each test reimplement cluster setup.
- **Risks:** Failures depend on external FoundationDB binaries, return codes, and trace contents; missing binaries or platform-specific behavior can fail before workload assertions run. The file uses assertions for contract checks, so optimized Python execution would weaken some validation. Randomized names, ports, or workflow choices make collision avoidance and reproducibility dependent on surrounding seed/control logic.
- **Test signals:** Observable signals include returncode, assert; failures normally surface as non-zero process exits, failed assertions, missing expected output, or trace severity events.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/fake_cluster.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/fdb_version.py -->
# Research: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/fdb_version.py

- **Purpose:** Generated/static version constants consumed by upgrade and binary-download tests.
- **Source facts:** 4 lines, 115 bytes, executable=False.
- **Important APIs/types/functions:** Imports: none. Classes: none. Top-level functions: none. Methods: none. Constants: CURRENT_VERSION, FUTURE_VERSION, PREV2_RELEASE_VERSION, PREV_RELEASE_VERSION. CLI flags/options observed: none.
- **Control flow:** Library-style helpers are called by neighboring test-runner modules; control flow is direct function or context-manager execution.
- **State and persistence:** keeps no durable state beyond function-local values
- **Dependencies:** Python imports: none.
- **Integration points:** Used by neighboring FoundationDB test harness modules through package-relative imports or direct script execution.
- **Risks:** Risk is mainly integration drift with the surrounding test harness.
- **Test signals:** Observable signals include none; failures normally surface as non-zero process exits, failed assertions, missing expected output, or trace severity events.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/fdb_version.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/local_cluster.py -->
# Research: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/local_cluster.py

- **Purpose:** Local FoundationDB process-cluster harness. It allocates ports, writes cluster/config files, starts/stops fdbmonitor, runs fdbcli, provisions TLS/auth material, performs wiggling, and checks traces.
- **Source facts:** 729 lines, 27723 bytes, executable=False.
- **Important APIs/types/functions:** Imports: .authz_util.private_key_gen, .authz_util.public_keyset_from_keys, .test_util.random_alphanum_string, fcntl, glob, json, os, pathlib.Path, random, socket, string, subprocess; plus 4 more. Classes: PortProvider, TLSConfig, LocalCluster. Top-level functions: __init__, get_free_port, is_port_in_use, _get_free_port_internal, release_locks, __init__, __init__, __next_port, save_config, create_cluster_file, get_connection_string, start_cluster; plus 33 more. Methods: PortProvider.__init__, PortProvider.get_free_port, PortProvider.is_port_in_use, PortProvider._get_free_port_internal, PortProvider.release_locks, TLSConfig.__init__, LocalCluster.__init__, LocalCluster.__next_port, LocalCluster.save_config, LocalCluster.create_cluster_file, LocalCluster.get_connection_string, LocalCluster.start_cluster; plus 32 more. Constants: CLUSTER_UPDATE_TIMEOUT_SEC, EXCLUDE_SERVERS_TIMEOUT_SEC, MAX_PORT_ACQUIRE_ATTEMPTS, PORT_LOCK_DIR, RETRY_INTERVAL_SEC. CLI flags/options observed: none.
- **Control flow:** Constructors allocate ports and write initial config; context entry starts fdbmonitor; helper methods run fdbcli for configure/status/exclude/coordinator operations; cluster_wiggle adds servers, moves coordinators, excludes old servers, and rewrites config; context exit stops processes, releases locks, and runs trace callbacks.
- **State and persistence:** launches or inspects child processes (4 subprocess call sites) creates, reads, renames, or removes filesystem artifacts (10 filesystem call sites)
- **Dependencies:** Python imports: .authz_util.private_key_gen, .authz_util.public_keyset_from_keys, .test_util.random_alphanum_string, fcntl, glob, json, os, pathlib.Path, random, socket, string, subprocess; plus 4 more; external FoundationDB binaries and shell tools are invoked through subprocess.
- **Integration points:** Used by upgrade and temporary-cluster tests to bridge Python orchestration with built FoundationDB binaries, local config files, and simulation/tester workloads.
- **Risks:** Failures depend on external FoundationDB binaries, return codes, and trace contents; missing binaries or platform-specific behavior can fail before workload assertions run. The file uses assertions for contract checks, so optimized Python execution would weaken some validation. Randomized names, ports, or workflow choices make collision avoidance and reproducibility dependent on surrounding seed/control logic.
- **Test signals:** Observable signals include returncode, assert, status json; failures normally surface as non-zero process exits, failed assertions, missing expected output, or trace severity events.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/local_cluster.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/test_util.py -->
# Research: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/test_util.py

- **Purpose:** Small shared utilities for random names and scoped trace-check registration against LocalCluster instances.
- **Source facts:** 27 lines, 833 bytes, executable=False.
- **Important APIs/types/functions:** Imports: random, string, time. Classes: ScopedTraceChecker. Top-level functions: random_alphanum_string, __init__, __enter__, __exit__. Methods: ScopedTraceChecker.__init__, ScopedTraceChecker.__enter__, ScopedTraceChecker.__exit__. Constants: none. CLI flags/options observed: none.
- **Control flow:** Library-style helpers are called by neighboring test-runner modules; control flow is direct function or context-manager execution.
- **State and persistence:** keeps no durable state beyond function-local values
- **Dependencies:** Python imports: random, string, time.
- **Integration points:** Used by neighboring FoundationDB test harness modules through package-relative imports or direct script execution.
- **Risks:** Randomized names, ports, or workflow choices make collision avoidance and reproducibility dependent on surrounding seed/control logic.
- **Test signals:** Observable signals include none; failures normally surface as non-zero process exits, failed assertions, missing expected output, or trace severity events.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/test_util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/tmp_cluster.py -->
# Research: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/tmp_cluster.py

- **Purpose:** CLI/context-manager wrapper that creates a fresh temporary LocalCluster, substitutes cluster/data/log/cert placeholders into a child command, and tears the cluster down afterward.
- **Source facts:** 178 lines, 6747 bytes, executable=True.
- **Important APIs/types/functions:** Imports: .cluster_args.CreateTmpFdbClusterArgParser, .local_cluster.LocalCluster, .local_cluster.TLSConfig, .test_util.random_alphanum_string, glob, os, pathlib.Path, shutil, subprocess, sys. Classes: TempCluster. Top-level functions: main, __init__, __enter__, __exit__, close. Methods: TempCluster.__init__, TempCluster.__enter__, TempCluster.__exit__, TempCluster.close. Constants: none. CLI flags/options observed: --disable-log-dump.
- **Control flow:** Argument parsing builds TLS/auth options, creates a TempCluster context, prints generated paths, substitutes placeholders in the child command, runs it with FDB_CLUSTER_FILE, scans logs for severity 40, optionally dumps diagnostics, and exits with the child or trace-check status.
- **State and persistence:** launches or inspects child processes (2 subprocess call sites) creates, reads, renames, or removes filesystem artifacts (6 filesystem call sites)
- **Dependencies:** Python imports: .cluster_args.CreateTmpFdbClusterArgParser, .local_cluster.LocalCluster, .local_cluster.TLSConfig, .test_util.random_alphanum_string, glob, os, pathlib.Path, shutil, subprocess, sys; external FoundationDB binaries and shell tools are invoked through subprocess.
- **Integration points:** Integrated as wrapper scripts around test commands that need FDB_CLUSTER_FILE or FDB_CLUSTERS without making each test reimplement cluster setup.
- **Risks:** Failures depend on external FoundationDB binaries, return codes, and trace contents; missing binaries or platform-specific behavior can fail before workload assertions run. The file uses assertions for contract checks, so optimized Python execution would weaken some validation. Randomized names, ports, or workflow choices make collision avoidance and reproducibility dependent on surrounding seed/control logic.
- **Test signals:** Observable signals include returncode, assert; failures normally surface as non-zero process exits, failed assertions, missing expected output, or trace severity events.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/tmp_cluster.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/tmp_multi_cluster.py -->
# Research: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/tmp_multi_cluster.py

- **Purpose:** CLI wrapper that starts multiple temporary clusters, exposes their cluster files through FDB_CLUSTERS, runs a child command, and then closes all clusters.
- **Source facts:** 92 lines, 2843 bytes, executable=True.
- **Important APIs/types/functions:** Imports: .cluster_args.CreateTmpFdbClusterArgParser, .tmp_cluster.TempCluster, os, subprocess, sys. Classes: none. Top-level functions: main. Methods: none. Constants: none. CLI flags/options observed: --clusters, -c.
- **Control flow:** Executable module: parse command-line arguments, perform setup, run the requested child/test workflow, and convert internal success/failure to process exit status.
- **State and persistence:** launches or inspects child processes (1 subprocess call sites)
- **Dependencies:** Python imports: .cluster_args.CreateTmpFdbClusterArgParser, .tmp_cluster.TempCluster, os, subprocess, sys; external FoundationDB binaries and shell tools are invoked through subprocess.
- **Integration points:** Integrated as wrapper scripts around test commands that need FDB_CLUSTER_FILE or FDB_CLUSTERS without making each test reimplement cluster setup.
- **Risks:** Failures depend on external FoundationDB binaries, return codes, and trace contents; missing binaries or platform-specific behavior can fail before workload assertions run.
- **Test signals:** Observable signals include returncode; failures normally surface as non-zero process exits, failed assertions, missing expected output, or trace severity events.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/tmp_multi_cluster.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/upgrade_test.py -->
# Research: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/upgrade_test.py

- **Purpose:** Cross-version upgrade test harness. It downloads/resolves client/server binaries, starts a LocalCluster, runs fdb_c_api_tester through named pipes, performs upgrade/wiggle steps, and verifies progress after each transition.
- **Source facts:** 492 lines, 18686 bytes, executable=True.
- **Important APIs/types/functions:** Imports: .binary_download.FdbBinaryDownloader, .fdb_version.CURRENT_VERSION, .fdb_version.FUTURE_VERSION, .local_cluster.LocalCluster, .test_util.random_alphanum_string, argparse.ArgumentParser, argparse.RawDescriptionHelpFormatter, glob, os, pathlib.Path, random, shutil; plus 6 more. Classes: UpgradeTest. Top-level functions: version_from_str, api_version_from_str, version_before, random_sleep, main, __init__, download_old_binaries, create_external_lib_dir, health_check, configure_version, upgrade_to, __enter__; plus 11 more. Methods: UpgradeTest.__init__, UpgradeTest.download_old_binaries, UpgradeTest.create_external_lib_dir, UpgradeTest.health_check, UpgradeTest.configure_version, UpgradeTest.upgrade_to, UpgradeTest.__enter__, UpgradeTest.__exit__, UpgradeTest.determine_api_version, UpgradeTest.exec_workload, UpgradeTest.progress_check, UpgradeTest.output_pipe_reader; plus 6 more. Constants: CLEANUP_ON_EXIT, CLUSTER_ACTIONS, HEALTH_CHECK_TIMEOUT_SEC, PROGRESS_CHECK_TIMEOUT_SEC, RUN_WITH_GDB, TESTER_STATS_INTERVAL_SEC, TRANSACTION_RETRY_LIMIT. CLI flags/options observed: --build-dir, --disable-log-dump, --no-cleanup-on-error, --process-number, --redundancy, --run-with-gdb, --test-file, --upgrade-path, -b, -p.
- **Control flow:** The test object resolves binaries, creates an initial cluster, launches fdb_c_api_tester in one thread, reads named-pipe progress events in another, then the main thread performs version transitions or cluster wiggles with health/progress checks after each step.
- **State and persistence:** launches or inspects child processes (3 subprocess call sites) creates, reads, renames, or removes filesystem artifacts (6 filesystem call sites)
- **Dependencies:** Python imports: .binary_download.FdbBinaryDownloader, .fdb_version.CURRENT_VERSION, .fdb_version.FUTURE_VERSION, .local_cluster.LocalCluster, .test_util.random_alphanum_string, argparse.ArgumentParser, argparse.RawDescriptionHelpFormatter, glob, os, pathlib.Path, random, shutil; plus 6 more.
- **Integration points:** Used by upgrade and temporary-cluster tests to bridge Python orchestration with built FoundationDB binaries, local config files, and simulation/tester workloads.
- **Risks:** Failures depend on external FoundationDB binaries, return codes, and trace contents; missing binaries or platform-specific behavior can fail before workload assertions run. The file uses assertions for contract checks, so optimized Python execution would weaken some validation. Randomized names, ports, or workflow choices make collision avoidance and reproducibility dependent on surrounding seed/control logic.
- **Test signals:** Observable signals include assert, CHECK_OK; failures normally surface as non-zero process exits, failed assertions, missing expected output, or trace severity events.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_test_runner/upgrade_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_version.py.cmake -->
# Research: sources/storage-engines/foundationdb/tests/TestRunner/fdb_version.py.cmake

- **Purpose:** CMake template for producing fdb_version.py from configured current/future/previous release version variables.
- **Source facts:** 4 lines, 192 bytes, executable=False.
- **Important APIs/types/functions:** CMake substitution variables: none.
- **Control flow:** No runtime control flow; CMake configures this template into a Python constants module before tests run.
- **State and persistence:** Persists configured version strings into the generated fdb_version.py module.
- **Dependencies:** Depends on CMake configure_file-style substitution and release-version variables from the FoundationDB build.
- **Integration points:** The generated Python file is imported by binary_download.py and upgrade_test.py to choose current, future, and previous release binaries.
- **Risks:** Incorrect configured versions can make upgrade tests download or select the wrong binaries.
- **Test signals:** Importability of the generated module and successful upgrade/binary-download tests are the relevant signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/fdb_version.py.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/pyproject.toml -->
# Research: sources/storage-engines/foundationdb/tests/TestRunner/pyproject.toml

- **Purpose:** Packaging metadata for the local fdb_test_runner Python package and its console-script entry points.
- **Source facts:** 12 lines, 280 bytes, executable=False.
- **Important APIs/types/functions:** Poetry package metadata with scripts {} and dependencies {}.
- **Control flow:** No runtime control flow; packaging tools read this metadata to expose console entry points.
- **State and persistence:** Persists package configuration only; it does not create runtime state.
- **Dependencies:** Declared dependencies include {}; Python version constraints and package name are controlled here.
- **Integration points:** Connects installed commands such as temporary-cluster, fake-cluster, multi-cluster, upgrade-test, and run-test-runner to Python module main functions.
- **Risks:** Script entry-point drift would break CI/test invocations even if module code still imports directly.
- **Test signals:** Package installation and console-script invocation are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/pyproject.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/run_test_runner.py -->
# Research: sources/storage-engines/foundationdb/tests/TestRunner/run_test_runner.py

- **Purpose:** Thin executable entry point that imports fdb_test_runner.TestRunner.main so TestRunner can be run as a direct script without relative import failures.
- **Source facts:** 8 lines, 232 bytes, executable=False.
- **Important APIs/types/functions:** Imports: fdb_test_runner.TestRunner.main. Classes: none. Top-level functions: none. Methods: none. Constants: none. CLI flags/options observed: none.
- **Control flow:** Library-style helpers are called by neighboring test-runner modules; control flow is direct function or context-manager execution.
- **State and persistence:** keeps no durable state beyond function-local values
- **Dependencies:** Python imports: fdb_test_runner.TestRunner.main.
- **Integration points:** Integrated as the simulation-test command entry point from CMake/ctest and as the `run-test-runner` console script.
- **Risks:** Risk is mainly integration drift with the surrounding test harness.
- **Test signals:** Observable signals include none; failures normally surface as non-zero process exits, failed assertions, missing expected output, or trace severity events.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/TestRunner/run_test_runner.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/argument_parsing/test_argument_parsing.py -->
# Research: sources/storage-engines/foundationdb/tests/argument_parsing/test_argument_parsing.py

- **Purpose:** Executable regression test for FoundationDB command-line option parsing across fdbserver, fdbcli, and fdbbackup.
- **Source facts:** 119 lines, 4310 bytes, executable=True.
- **Important APIs/types/functions:** Imports: argparse, subprocess. Classes: none. Top-level functions: check, run_command, is_unknown_option, is_unknown_knob, is_cli_usage, test_fdbserver, test_fdbcli, test_fdbbackup. Methods: none. Constants: none. CLI flags/options observed: none.
- **Control flow:** Executable module: parse command-line arguments, perform setup, run the requested child/test workflow, and convert internal success/failure to process exit status.
- **State and persistence:** launches or inspects child processes (1 subprocess call sites)
- **Dependencies:** Python imports: argparse, subprocess; external FoundationDB binaries and shell tools are invoked through subprocess.
- **Integration points:** Used by neighboring FoundationDB test harness modules through package-relative imports or direct script execution.
- **Risks:** Failures depend on external FoundationDB binaries, return codes, and trace contents; missing binaries or platform-specific behavior can fail before workload assertions run. The file uses assertions for contract checks, so optimized Python execution would weaken some validation.
- **Test signals:** Observable signals include assert, unknown option, Invalid knob option; failures normally surface as non-zero process exits, failed assertions, missing expected output, or trace severity events.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/argument_parsing/test_argument_parsing.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/AtomicBackupCorrectness.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/AtomicBackupCorrectness.toml

- **Purpose:** Fast simulation test specification for the `AtomicBackupCorrectness` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 39 lines, 822 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles BackupAndRestore, workloads Attrition(2), AtomicOps, BackupAndRestoreCorrectness, RandomClogging, Rollback, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (BackupAndRestore) and schedules each block's workload list (BackupAndRestore:6). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Backup-oriented workloads add simulated backup agent and restore state that must survive fault injection long enough for correctness validation.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Attrition(2), AtomicOps, BackupAndRestoreCorrectness, RandomClogging, Rollback. Top-level keys: none. Configuration/test knobs: BackupAndRestore.simBackupAgents='BackupToFile', BackupAndRestore/AtomicOps.testDuration=30.0, BackupAndRestore/AtomicOps.transactionsPerSecond=2500.0, BackupAndRestore/AtomicOps.nodeCount=30000, BackupAndRestore/BackupAndRestoreCorrectness.backupAfter=10.0, BackupAndRestore/BackupAndRestoreCorrectness.restoreAfter=60.0, BackupAndRestore/RandomClogging.testDuration=90.0, BackupAndRestore/Rollback.testDuration=90.0, BackupAndRestore/Rollback.meanDelay=90.0, BackupAndRestore/Attrition.testDuration=90.0, BackupAndRestore/Attrition.machinesToKill=10, BackupAndRestore/Attrition.machinesToLeave=3, BackupAndRestore/Attrition.testDuration=90.0, BackupAndRestore/Attrition.machinesToKill=10, BackupAndRestore/Attrition.machinesToLeave=3.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/AtomicBackupCorrectness.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Backup/restore specs depend on simulated backup-agent mode, timing, and range selection; timing drift can mask restore validation failures.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Attrition(2), AtomicOps, BackupAndRestoreCorrectness, RandomClogging, Rollback. Clear-after-test modes: BackupAndRestore:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/AtomicBackupCorrectness.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/AtomicBackupToDBCorrectness.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/AtomicBackupToDBCorrectness.toml

- **Purpose:** Fast simulation test specification for the `AtomicBackupToDBCorrectness` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 42 lines, 866 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles BackupAndRestore, workloads Attrition(2), AtomicOps, BackupToDBCorrectness, RandomClogging, Rollback, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (BackupAndRestore) and schedules each block's workload list (BackupAndRestore:6). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Backup-oriented workloads add simulated backup agent and restore state that must survive fault injection long enough for correctness validation.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Attrition(2), AtomicOps, BackupToDBCorrectness, RandomClogging, Rollback. Top-level keys: configuration. Configuration/test knobs: extraDatabaseMode='LocalOrSingle', BackupAndRestore.simBackupAgents='BackupToDB', BackupAndRestore/AtomicOps.testDuration=30.0, BackupAndRestore/AtomicOps.transactionsPerSecond=750.0, BackupAndRestore/AtomicOps.nodeCount=10000, BackupAndRestore/BackupToDBCorrectness.backupAfter=10.0, BackupAndRestore/BackupToDBCorrectness.restoreAfter=60.0, BackupAndRestore/RandomClogging.testDuration=90.0, BackupAndRestore/Rollback.testDuration=90.0, BackupAndRestore/Rollback.meanDelay=90.0, BackupAndRestore/Attrition.testDuration=90.0, BackupAndRestore/Attrition.machinesToKill=10, BackupAndRestore/Attrition.machinesToLeave=3, BackupAndRestore/Attrition.testDuration=90.0, BackupAndRestore/Attrition.machinesToKill=10, BackupAndRestore/Attrition.machinesToLeave=3.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/AtomicBackupToDBCorrectness.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Backup/restore specs depend on simulated backup-agent mode, timing, and range selection; timing drift can mask restore validation failures.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Attrition(2), AtomicOps, BackupToDBCorrectness, RandomClogging, Rollback. Clear-after-test modes: BackupAndRestore:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/AtomicBackupToDBCorrectness.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/AtomicOps.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/AtomicOps.toml

- **Purpose:** Fast simulation test specification for the `AtomicOps` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 38 lines, 735 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 2 test block(s), titles Clogged, Unclogged, workloads AtomicOps(2), Attrition(2), RandomClogging, Rollback, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 2 `[[test]]` block(s) (Clogged, Unclogged) and schedules each block's workload list (Clogged:5, Unclogged:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: AtomicOps(2), Attrition(2), RandomClogging, Rollback. Top-level keys: none. Configuration/test knobs: Clogged/AtomicOps.testDuration=10.0, Clogged/AtomicOps.transactionsPerSecond=2500.0, Clogged/RandomClogging.testDuration=10.0, Clogged/Rollback.testDuration=10.0, Clogged/Rollback.meanDelay=10.0, Clogged/Attrition.testDuration=10.0, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3, Clogged/Attrition.testDuration=10.0, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3, Unclogged/AtomicOps.testDuration=10.0, Unclogged/AtomicOps.transactionsPerSecond=250.0.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/AtomicOps.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for AtomicOps(2), Attrition(2), RandomClogging, Rollback. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/AtomicOps.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/AtomicOpsApiCorrectness.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/AtomicOpsApiCorrectness.toml

- **Purpose:** Fast simulation test specification for the `AtomicOpsApiCorrectness` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 5 lines, 112 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles AtomicOpsCorrectnessTest, workloads AtomicOpsApiCorrectness, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (AtomicOpsCorrectnessTest) and schedules each block's workload list (AtomicOpsCorrectnessTest:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: AtomicOpsApiCorrectness. Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/AtomicOpsApiCorrectness.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for AtomicOpsApiCorrectness. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/AtomicOpsApiCorrectness.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/AutomaticIdempotency.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/AutomaticIdempotency.toml

- **Purpose:** Fast simulation test specification for the `AutomaticIdempotency` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 11 lines, 238 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles AutomaticIdempotency, workloads AutomaticIdempotencyCorrectness, Attrition, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (AutomaticIdempotency) and schedules each block's workload list (AutomaticIdempotency:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: AutomaticIdempotencyCorrectness, Attrition. Top-level keys: none. Configuration/test knobs: AutomaticIdempotency/Attrition.testDuration=10.0.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/AutomaticIdempotency.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for AutomaticIdempotencyCorrectness, Attrition. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/AutomaticIdempotency.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/BackupCorrectness.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/BackupCorrectness.toml

- **Purpose:** Fast simulation test specification for the `BackupCorrectness` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 41 lines, 839 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles BackupAndRestore, workloads Attrition(2), Cycle, BackupAndRestoreCorrectness, RandomClogging, Rollback, top-level keys testClass.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (BackupAndRestore) and schedules each block's workload list (BackupAndRestore:6). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Backup-oriented workloads add simulated backup agent and restore state that must survive fault injection long enough for correctness validation.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Attrition(2), Cycle, BackupAndRestoreCorrectness, RandomClogging, Rollback. Top-level keys: testClass. Configuration/test knobs: BackupAndRestore.simBackupAgents='BackupToFile', BackupAndRestore/Cycle.testDuration=30.0, BackupAndRestore/Cycle.transactionsPerSecond=2500.0, BackupAndRestore/Cycle.nodeCount=30000, BackupAndRestore/BackupAndRestoreCorrectness.backupAfter=10.0, BackupAndRestore/BackupAndRestoreCorrectness.restoreAfter=60.0, BackupAndRestore/RandomClogging.testDuration=90.0, BackupAndRestore/Rollback.testDuration=90.0, BackupAndRestore/Rollback.meanDelay=90.0, BackupAndRestore/Attrition.testDuration=90.0, BackupAndRestore/Attrition.machinesToKill=10, BackupAndRestore/Attrition.machinesToLeave=3, BackupAndRestore/Attrition.testDuration=90.0, BackupAndRestore/Attrition.machinesToKill=10, BackupAndRestore/Attrition.machinesToLeave=3.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/BackupCorrectness.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Backup/restore specs depend on simulated backup-agent mode, timing, and range selection; timing drift can mask restore validation failures.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Attrition(2), Cycle, BackupAndRestoreCorrectness, RandomClogging, Rollback. Clear-after-test modes: BackupAndRestore:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/BackupCorrectness.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/BackupCorrectnessClean.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/BackupCorrectnessClean.toml

- **Purpose:** Fast simulation test specification for the `BackupCorrectnessClean` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 61 lines, 1364 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles BackupAndRestore, workloads Cycle(3), BackupAndRestoreCorrectness(3), ReadWrite, top-level keys testClass.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (BackupAndRestore) and schedules each block's workload list (BackupAndRestore:7). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Backup-oriented workloads add simulated backup agent and restore state that must survive fault injection long enough for correctness validation.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle(3), BackupAndRestoreCorrectness(3), ReadWrite. Top-level keys: testClass. Configuration/test knobs: BackupAndRestore.simBackupAgents='BackupToFile', BackupAndRestore/Cycle.testDuration=20.0, BackupAndRestore/Cycle.transactionsPerSecond=250.0, BackupAndRestore/Cycle.keyPrefix='a', BackupAndRestore/Cycle.testDuration=30.0, BackupAndRestore/Cycle.transactionsPerSecond=250.0, BackupAndRestore/Cycle.keyPrefix='A', BackupAndRestore/Cycle.testDuration=40.0, BackupAndRestore/Cycle.transactionsPerSecond=250.0, BackupAndRestore/Cycle.keyPrefix='m', BackupAndRestore/ReadWrite.testDuration=30.0, BackupAndRestore/ReadWrite.transactionsPerSecond=10, BackupAndRestore/BackupAndRestoreCorrectness.backupAfter=10.0, BackupAndRestore/BackupAndRestoreCorrectness.restoreAfter=60.0, BackupAndRestore/BackupAndRestoreCorrectness.backupAfter=15.0, BackupAndRestore/BackupAndRestoreCorrectness.restoreAfter=60.0, BackupAndRestore/BackupAndRestoreCorrectness.backupAfter=20.0, BackupAndRestore/BackupAndRestoreCorrectness.restoreAfter=60.0.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/BackupCorrectnessClean.toml` through the Python TestRunner/CTest path.
- **Risks:** Backup/restore specs depend on simulated backup-agent mode, timing, and range selection; timing drift can mask restore validation failures.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle(3), BackupAndRestoreCorrectness(3), ReadWrite. Clear-after-test modes: BackupAndRestore:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/BackupCorrectnessClean.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/BackupS3BlobCorrectness.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/BackupS3BlobCorrectness.toml

- **Purpose:** Fast simulation test specification for the `BackupS3BlobCorrectness` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 63 lines, 2081 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles BackupS3BlobCorrectness, workloads Cycle, BackupS3BlobCorrectness, top-level keys configuration, testClass.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (BackupS3BlobCorrectness) and schedules each block's workload list (BackupS3BlobCorrectness:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Backup-oriented workloads add simulated backup agent and restore state that must survive fault injection long enough for correctness validation.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle, BackupS3BlobCorrectness. Top-level keys: configuration, testClass. Configuration/test knobs: buggify=False, faultInjection=False, BackupS3BlobCorrectness.simBackupAgents='BackupToFile', BackupS3BlobCorrectness.runConsistencyCheck=False, BackupS3BlobCorrectness/Cycle.testDuration=30.0, BackupS3BlobCorrectness/Cycle.transactionsPerSecond=1000.0, BackupS3BlobCorrectness/Cycle.nodeCount=10000, BackupS3BlobCorrectness/BackupS3BlobCorrectness.backupAfter=10.0, BackupS3BlobCorrectness/BackupS3BlobCorrectness.restoreAfter=80.0.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/BackupS3BlobCorrectness.toml` through the Python TestRunner/CTest path.
- **Risks:** Backup/restore specs depend on simulated backup-agent mode, timing, and range selection; timing drift can mask restore validation failures.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle, BackupS3BlobCorrectness. Clear-after-test modes: BackupS3BlobCorrectness:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/BackupS3BlobCorrectness.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/BackupToDBCorrectness.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/BackupToDBCorrectness.toml

- **Purpose:** Fast simulation test specification for the `BackupToDBCorrectness` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 44 lines, 885 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles BackupAndRestore, workloads Attrition(2), Cycle, BackupToDBCorrectness, RandomClogging, Rollback, top-level keys configuration, testClass.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (BackupAndRestore) and schedules each block's workload list (BackupAndRestore:6). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Backup-oriented workloads add simulated backup agent and restore state that must survive fault injection long enough for correctness validation.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Attrition(2), Cycle, BackupToDBCorrectness, RandomClogging, Rollback. Top-level keys: configuration, testClass. Configuration/test knobs: extraDatabaseMode='LocalOrSingle', BackupAndRestore.simBackupAgents='BackupToDB', BackupAndRestore/Cycle.testDuration=30.0, BackupAndRestore/Cycle.transactionsPerSecond=2500.0, BackupAndRestore/Cycle.nodeCount=30000, BackupAndRestore/BackupToDBCorrectness.backupAfter=10.0, BackupAndRestore/BackupToDBCorrectness.restoreAfter=60.0, BackupAndRestore/RandomClogging.testDuration=90.0, BackupAndRestore/Rollback.testDuration=90.0, BackupAndRestore/Rollback.meanDelay=90.0, BackupAndRestore/Attrition.testDuration=90.0, BackupAndRestore/Attrition.machinesToKill=10, BackupAndRestore/Attrition.machinesToLeave=3, BackupAndRestore/Attrition.testDuration=90.0, BackupAndRestore/Attrition.machinesToKill=10, BackupAndRestore/Attrition.machinesToLeave=3.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/BackupToDBCorrectness.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Backup/restore specs depend on simulated backup-agent mode, timing, and range selection; timing drift can mask restore validation failures.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Attrition(2), Cycle, BackupToDBCorrectness, RandomClogging, Rollback. Clear-after-test modes: BackupAndRestore:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/BackupToDBCorrectness.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/BackupToDBCorrectnessClean.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/BackupToDBCorrectnessClean.toml

- **Purpose:** Fast simulation test specification for the `BackupToDBCorrectnessClean` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 51 lines, 1098 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles BackupAndRestore, workloads Cycle(3), BackupToDBCorrectness(3), top-level keys configuration, testClass.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (BackupAndRestore) and schedules each block's workload list (BackupAndRestore:6). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Backup-oriented workloads add simulated backup agent and restore state that must survive fault injection long enough for correctness validation.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle(3), BackupToDBCorrectness(3). Top-level keys: configuration, testClass. Configuration/test knobs: extraDatabaseMode='LocalOrSingle', BackupAndRestore.simBackupAgents='BackupToDB', BackupAndRestore/Cycle.testDuration=20.0, BackupAndRestore/Cycle.transactionsPerSecond=500.0, BackupAndRestore/Cycle.keyPrefix='a', BackupAndRestore/Cycle.testDuration=30.0, BackupAndRestore/Cycle.transactionsPerSecond=500.0, BackupAndRestore/Cycle.keyPrefix='A', BackupAndRestore/Cycle.testDuration=40.0, BackupAndRestore/Cycle.transactionsPerSecond=500.0, BackupAndRestore/Cycle.keyPrefix='m', BackupAndRestore/BackupToDBCorrectness.backupAfter=10.0, BackupAndRestore/BackupToDBCorrectness.restoreAfter=60.0, BackupAndRestore/BackupToDBCorrectness.backupAfter=15.0, BackupAndRestore/BackupToDBCorrectness.restoreAfter=60.0, BackupAndRestore/BackupToDBCorrectness.backupAfter=20.0, BackupAndRestore/BackupToDBCorrectness.restoreAfter=60.0.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/BackupToDBCorrectnessClean.toml` through the Python TestRunner/CTest path.
- **Risks:** Backup/restore specs depend on simulated backup-agent mode, timing, and range selection; timing drift can mask restore validation failures.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle(3), BackupToDBCorrectness(3). Clear-after-test modes: BackupAndRestore:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/BackupToDBCorrectnessClean.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/BulkDumping.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/BulkDumping.toml

- **Purpose:** Fast simulation test specification for the `BulkDumping` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 42 lines, 1641 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles BulkDumpingWorkload, workloads BulkDumpingWorkload, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (BulkDumpingWorkload) and schedules each block's workload list (BulkDumpingWorkload:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: BulkDumpingWorkload. Top-level keys: configuration, knobs. Configuration/test knobs: storageEngineExcludeTypes=['ssd-sharded-rocksdb'], disableTss=True.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/BulkDumping.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for BulkDumpingWorkload. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/BulkDumping.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/BulkLoading.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/BulkLoading.toml

- **Purpose:** Fast simulation test specification for the `BulkLoading` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 40 lines, 1570 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles BulkLoadingWorkload, workloads BulkLoadingWorkload, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (BulkLoadingWorkload) and schedules each block's workload list (BulkLoadingWorkload:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: BulkLoadingWorkload. Top-level keys: configuration, knobs. Configuration/test knobs: storageEngineExcludeTypes=['ssd-sharded-rocksdb'], disableTss=True.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/BulkLoading.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for BulkLoadingWorkload. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/BulkLoading.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/CheckMetadataEncodingForward.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/CheckMetadataEncodingForward.toml

- **Purpose:** Fast simulation test specification for the `CheckMetadataEncodingForward` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 17 lines, 347 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles CheckMetadataEncodingForward, workloads Cycle, RandomMoveKeys, CheckMetadataEncoding, top-level keys knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (CheckMetadataEncodingForward) and schedules each block's workload list (CheckMetadataEncodingForward:3). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle, RandomMoveKeys, CheckMetadataEncoding. Top-level keys: knobs. Configuration/test knobs: CheckMetadataEncodingForward/Cycle.testDuration=10.0, CheckMetadataEncodingForward/Cycle.transactionsPerSecond=2500.0, CheckMetadataEncodingForward/RandomMoveKeys.testDuration=10.0.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/CheckMetadataEncodingForward.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle, RandomMoveKeys, CheckMetadataEncoding. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/CheckMetadataEncodingForward.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/CheckMetadataEncodingOldPath.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/CheckMetadataEncodingOldPath.toml

- **Purpose:** Fast simulation test specification for the `CheckMetadataEncodingOldPath` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 21 lines, 457 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles CheckMetadataEncodingOldPath, workloads Cycle, RandomMoveKeys, CheckMetadataEncoding, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (CheckMetadataEncodingOldPath) and schedules each block's workload list (CheckMetadataEncodingOldPath:3). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle, RandomMoveKeys, CheckMetadataEncoding. Top-level keys: configuration, knobs. Configuration/test knobs: storageEngineExcludeTypes=[3, 4, 5], CheckMetadataEncodingOldPath/Cycle.testDuration=10.0, CheckMetadataEncodingOldPath/Cycle.transactionsPerSecond=2500.0, CheckMetadataEncodingOldPath/RandomMoveKeys.testDuration=10.0.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/CheckMetadataEncodingOldPath.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle, RandomMoveKeys, CheckMetadataEncoding. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/CheckMetadataEncodingOldPath.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/CloggedSideband.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/CloggedSideband.toml

- **Purpose:** Fast simulation test specification for the `CloggedSideband` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 31 lines, 630 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles CloggedCausalConsistencyTest, workloads RandomClogging(2), Attrition(2), Sideband, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (CloggedCausalConsistencyTest) and schedules each block's workload list (CloggedCausalConsistencyTest:5). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: RandomClogging(2), Attrition(2), Sideband. Top-level keys: none. Configuration/test knobs: CloggedCausalConsistencyTest/Sideband.testDuration=30.0, CloggedCausalConsistencyTest/RandomClogging.testDuration=30.0, CloggedCausalConsistencyTest/RandomClogging.testDuration=30.0, CloggedCausalConsistencyTest/Attrition.testDuration=30.0, CloggedCausalConsistencyTest/Attrition.machinesToKill=10, CloggedCausalConsistencyTest/Attrition.machinesToLeave=3, CloggedCausalConsistencyTest/Attrition.testDuration=30.0, CloggedCausalConsistencyTest/Attrition.machinesToKill=10, CloggedCausalConsistencyTest/Attrition.machinesToLeave=3.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/CloggedSideband.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for RandomClogging(2), Attrition(2), Sideband. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/CloggedSideband.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/CompressionUtilsUnit.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/CompressionUtilsUnit.toml

- **Purpose:** Fast simulation test specification for the `CompressionUtilsUnit` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 8 lines, 162 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles CompressionUtilsTest, workloads UnitTests, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (CompressionUtilsTest) and schedules each block's workload list (CompressionUtilsTest:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: UnitTests. Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/CompressionUtilsUnit.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for UnitTests. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/CompressionUtilsUnit.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/ConfigureLocked.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/ConfigureLocked.toml

- **Purpose:** Fast simulation test specification for the `ConfigureLocked` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 11 lines, 210 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles ConfigureLocked, workloads LockDatabase, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (ConfigureLocked) and schedules each block's workload list (ConfigureLocked:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: LockDatabase. Top-level keys: configuration. Configuration/test knobs: configureLocked=True, ConfigureLocked.runConsistencyCheck=False.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/ConfigureLocked.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for LockDatabase. Clear-after-test modes: ConfigureLocked:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/ConfigureLocked.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/ConstrainedRandomSelector.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/ConstrainedRandomSelector.toml

- **Purpose:** Fast simulation test specification for the `ConstrainedRandomSelector` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 6 lines, 108 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles RYOW_Test, workloads RandomSelector, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (RYOW_Test) and schedules each block's workload list (RYOW_Test:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: RandomSelector. Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/ConstrainedRandomSelector.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for RandomSelector. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/ConstrainedRandomSelector.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/CycleAndLock.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/CycleAndLock.toml

- **Purpose:** Fast simulation test specification for the `CycleAndLock` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 35 lines, 686 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles Clogged, workloads Attrition(2), Cycle, LockDatabase, RandomClogging, Rollback, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (Clogged) and schedules each block's workload list (Clogged:6). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Attrition(2), Cycle, LockDatabase, RandomClogging, Rollback. Top-level keys: none. Configuration/test knobs: Clogged/Cycle.testDuration=60.0, Clogged/Cycle.transactionsPerSecond=2500.0, Clogged/RandomClogging.testDuration=30.0, Clogged/Rollback.testDuration=30.0, Clogged/Rollback.meanDelay=30.0, Clogged/Attrition.testDuration=30.0, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3, Clogged/Attrition.testDuration=30.0, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/CycleAndLock.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Attrition(2), Cycle, LockDatabase, RandomClogging, Rollback. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/CycleAndLock.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/CycleTest.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/CycleTest.toml

- **Purpose:** Fast simulation test specification for the `CycleTest` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 38 lines, 727 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 2 test block(s), titles Clogged, Unclogged, workloads Cycle(2), Attrition(2), RandomClogging, Rollback, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 2 `[[test]]` block(s) (Clogged, Unclogged) and schedules each block's workload list (Clogged:5, Unclogged:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle(2), Attrition(2), RandomClogging, Rollback. Top-level keys: none. Configuration/test knobs: Clogged/Cycle.testDuration=10.0, Clogged/Cycle.transactionsPerSecond=2500.0, Clogged/RandomClogging.testDuration=10.0, Clogged/Rollback.testDuration=10.0, Clogged/Rollback.meanDelay=10.0, Clogged/Attrition.testDuration=10.0, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3, Clogged/Attrition.testDuration=10.0, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3, Unclogged/Cycle.testDuration=10.0, Unclogged/Cycle.transactionsPerSecond=250.0.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/CycleTest.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle(2), Attrition(2), RandomClogging, Rollback. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/CycleTest.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/DataLossRecovery.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/DataLossRecovery.toml

- **Purpose:** Fast simulation test specification for the `DataLossRecovery` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 21 lines, 726 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles DataLossRecovery, workloads DataLossRecovery, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (DataLossRecovery) and schedules each block's workload list (DataLossRecovery:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: DataLossRecovery. Top-level keys: configuration. Configuration/test knobs: buggify=False, generateFearless=False, config='triple', processesPerMachine=2, coordinators=3, machineCount=45, asanMachineCount=20.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/DataLossRecovery.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for DataLossRecovery. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/DataLossRecovery.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/FuzzApiCorrectness.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/FuzzApiCorrectness.toml

- **Purpose:** Fast simulation test specification for the `FuzzApiCorrectness` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 32 lines, 615 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles FuzzApiCorrectness, workloads Attrition(2), FuzzApiCorrectness, RandomClogging, Rollback, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (FuzzApiCorrectness) and schedules each block's workload list (FuzzApiCorrectness:5). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Attrition(2), FuzzApiCorrectness, RandomClogging, Rollback. Top-level keys: configuration. Configuration/test knobs: StderrSeverity=30, FuzzApiCorrectness/FuzzApiCorrectness.testDuration=30.0, FuzzApiCorrectness/RandomClogging.testDuration=30.0, FuzzApiCorrectness/Rollback.testDuration=30.0, FuzzApiCorrectness/Rollback.meanDelay=30.0, FuzzApiCorrectness/Attrition.testDuration=30.0, FuzzApiCorrectness/Attrition.machinesToKill=10, FuzzApiCorrectness/Attrition.machinesToLeave=3, FuzzApiCorrectness/Attrition.testDuration=30.0, FuzzApiCorrectness/Attrition.machinesToKill=10, FuzzApiCorrectness/Attrition.machinesToLeave=3.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/FuzzApiCorrectness.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Attrition(2), FuzzApiCorrectness, RandomClogging, Rollback. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/FuzzApiCorrectness.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/FuzzApiCorrectnessClean.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/FuzzApiCorrectnessClean.toml

- **Purpose:** Fast simulation test specification for the `FuzzApiCorrectnessClean` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 9 lines, 162 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles FuzzApiCorrectness, workloads FuzzApiCorrectness, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (FuzzApiCorrectness) and schedules each block's workload list (FuzzApiCorrectness:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: FuzzApiCorrectness. Top-level keys: configuration. Configuration/test knobs: StderrSeverity=30, FuzzApiCorrectness/FuzzApiCorrectness.testDuration=30.0.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/FuzzApiCorrectnessClean.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for FuzzApiCorrectness. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/FuzzApiCorrectnessClean.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/GetEstimatedRangeSize.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/GetEstimatedRangeSize.toml

- **Purpose:** Fast simulation test specification for the `GetEstimatedRangeSize` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 13 lines, 276 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles GetEstimatedRangeSizeTest, workloads GetEstimatedRangeSize(2), top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (GetEstimatedRangeSizeTest) and schedules each block's workload list (GetEstimatedRangeSizeTest:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: GetEstimatedRangeSize(2). Top-level keys: configuration. Configuration/test knobs: GetEstimatedRangeSizeTest/GetEstimatedRangeSize.nodeCount=250000, GetEstimatedRangeSizeTest/GetEstimatedRangeSize.nodeCount=250000.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/GetEstimatedRangeSize.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for GetEstimatedRangeSize(2). Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/GetEstimatedRangeSize.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/GetMappedRange.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/GetMappedRange.toml

- **Purpose:** Fast simulation test specification for the `GetMappedRange` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 8 lines, 162 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles GetMappedRange, workloads GetMappedRange, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (GetMappedRange) and schedules each block's workload list (GetMappedRange:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: GetMappedRange. Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/GetMappedRange.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for GetMappedRange. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/GetMappedRange.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/HTTPKeyValueStore.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/HTTPKeyValueStore.toml

- **Purpose:** Fast simulation test specification for the `HTTPKeyValueStore` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 30 lines, 609 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles HTTPKeyValueStoreTest, workloads Attrition(2), HTTPKeyValueStore, RandomClogging, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (HTTPKeyValueStoreTest) and schedules each block's workload list (HTTPKeyValueStoreTest:4). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Attrition(2), HTTPKeyValueStore, RandomClogging. Top-level keys: none. Configuration/test knobs: HTTPKeyValueStoreTest/HTTPKeyValueStore.testDuration=30.0, HTTPKeyValueStoreTest/RandomClogging.testDuration=30.0, HTTPKeyValueStoreTest/Attrition.testDuration=30.0, HTTPKeyValueStoreTest/Attrition.machinesToKill=10, HTTPKeyValueStoreTest/Attrition.machinesToLeave=3, HTTPKeyValueStoreTest/Attrition.testDuration=30.0, HTTPKeyValueStoreTest/Attrition.machinesToKill=10, HTTPKeyValueStoreTest/Attrition.machinesToLeave=3.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/HTTPKeyValueStore.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Attrition(2), HTTPKeyValueStore, RandomClogging. Clear-after-test modes: none. Timeouts: HTTPKeyValueStoreTest:1000.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/HTTPKeyValueStore.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/IDDTxnProcessorMoveKeys.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/IDDTxnProcessorMoveKeys.toml

- **Purpose:** Fast simulation test specification for the `IDDTxnProcessorMoveKeys` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 22 lines, 706 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 2 test block(s), titles IDDTxnProcessorRawStartMovement, IDDTxnProcessorMoveKeys, workloads IDDTxnProcessorApiCorrectness(2), top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 2 `[[test]]` block(s) (IDDTxnProcessorRawStartMovement, IDDTxnProcessorMoveKeys) and schedules each block's workload list (IDDTxnProcessorRawStartMovement:1, IDDTxnProcessorMoveKeys:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: IDDTxnProcessorApiCorrectness(2). Top-level keys: configuration, knobs. Configuration/test knobs: generateFearless=False, disableTss=True, IDDTxnProcessorRawStartMovement/IDDTxnProcessorApiCorrectness.testDuration=50.0, IDDTxnProcessorMoveKeys/IDDTxnProcessorApiCorrectness.testDuration=50.0.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/IDDTxnProcessorMoveKeys.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for IDDTxnProcessorApiCorrectness(2). Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/IDDTxnProcessorMoveKeys.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/IncrementTest.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/IncrementTest.toml

- **Purpose:** Fast simulation test specification for the `IncrementTest` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 53 lines, 1019 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 3 test block(s), titles Clogged, Unclogged, Moving, workloads Increment(3), Attrition(2), RandomClogging, Rollback, RandomMoveKeys, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 3 `[[test]]` block(s) (Clogged, Unclogged, Moving) and schedules each block's workload list (Clogged:5, Unclogged:1, Moving:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Increment(3), Attrition(2), RandomClogging, Rollback, RandomMoveKeys. Top-level keys: none. Configuration/test knobs: Clogged/Increment.testDuration=10.0, Clogged/Increment.transactionsPerSecond=500.0, Clogged/RandomClogging.testDuration=10.0, Clogged/Rollback.testDuration=10.0, Clogged/Rollback.meanDelay=10.0, Clogged/Attrition.testDuration=10.0, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3, Clogged/Attrition.testDuration=10.0, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3, Unclogged/Increment.testDuration=10.0, Unclogged/Increment.transactionsPerSecond=50.0, Moving/Increment.testDuration=10.0, Moving/Increment.transactionsPerSecond=50.0, Moving/RandomMoveKeys.testDuration=10.0.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/IncrementTest.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Increment(3), Attrition(2), RandomClogging, Rollback, RandomMoveKeys. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/IncrementTest.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/IncrementalBackup.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/IncrementalBackup.toml

- **Purpose:** Fast simulation test specification for the `IncrementalBackup` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 48 lines, 938 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 4 test block(s), titles SubmitBackup, CycleTest, SubmitRestore, VerifyCycle, workloads IncrementalBackup(3), Cycle(2), top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 4 `[[test]]` block(s) (SubmitBackup, CycleTest, SubmitRestore, VerifyCycle) and schedules each block's workload list (SubmitBackup:1, CycleTest:2, SubmitRestore:1, VerifyCycle:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Backup-oriented workloads add simulated backup agent and restore state that must survive fault injection long enough for correctness validation.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: IncrementalBackup(3), Cycle(2). Top-level keys: none. Configuration/test knobs: SubmitBackup.simBackupAgents='BackupToFile', SubmitBackup.runConsistencyCheck=False, CycleTest.simBackupAgents='BackupToFile', CycleTest/Cycle.testDuration=10.0, CycleTest/Cycle.transactionsPerSecond=3000.0, CycleTest/Cycle.nodeCount=3000, SubmitRestore.simBackupAgents='BackupToFile', VerifyCycle/Cycle.testDuration=10.0, VerifyCycle/Cycle.transactionsPerSecond=3000.0, VerifyCycle/Cycle.nodeCount=3000.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/IncrementalBackup.toml` through the Python TestRunner/CTest path.
- **Risks:** Backup/restore specs depend on simulated backup-agent mode, timing, and range selection; timing drift can mask restore validation failures.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for IncrementalBackup(3), Cycle(2). Clear-after-test modes: CycleTest:True, SubmitRestore:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/IncrementalBackup.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/InventoryTestAlmostReadOnly.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/InventoryTestAlmostReadOnly.toml

- **Purpose:** Fast simulation test specification for the `InventoryTestAlmostReadOnly` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 23 lines, 503 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles InventoryTestAlmostReadOnly, workloads Attrition(2), InventoryTest, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (InventoryTestAlmostReadOnly) and schedules each block's workload list (InventoryTestAlmostReadOnly:3). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Attrition(2), InventoryTest. Top-level keys: none. Configuration/test knobs: InventoryTestAlmostReadOnly/InventoryTest.testDuration=10.0, InventoryTestAlmostReadOnly/InventoryTest.transactionsPerSecond=5000.0, InventoryTestAlmostReadOnly/Attrition.testDuration=10.0, InventoryTestAlmostReadOnly/Attrition.machinesToKill=10, InventoryTestAlmostReadOnly/Attrition.machinesToLeave=3, InventoryTestAlmostReadOnly/Attrition.testDuration=10.0, InventoryTestAlmostReadOnly/Attrition.machinesToKill=10, InventoryTestAlmostReadOnly/Attrition.machinesToLeave=3.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/InventoryTestAlmostReadOnly.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Attrition(2), InventoryTest. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/InventoryTestAlmostReadOnly.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/InventoryTestSomeWrites.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/InventoryTestSomeWrites.toml

- **Purpose:** Fast simulation test specification for the `InventoryTestSomeWrites` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 22 lines, 477 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles InventoryTestSomeWrites, workloads Attrition(2), InventoryTest, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (InventoryTestSomeWrites) and schedules each block's workload list (InventoryTestSomeWrites:3). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Attrition(2), InventoryTest. Top-level keys: none. Configuration/test knobs: InventoryTestSomeWrites/InventoryTest.testDuration=10.0, InventoryTestSomeWrites/InventoryTest.transactionsPerSecond=10000.0, InventoryTestSomeWrites/Attrition.testDuration=10.0, InventoryTestSomeWrites/Attrition.machinesToKill=10, InventoryTestSomeWrites/Attrition.machinesToLeave=3, InventoryTestSomeWrites/Attrition.testDuration=10.0, InventoryTestSomeWrites/Attrition.machinesToKill=10, InventoryTestSomeWrites/Attrition.machinesToLeave=3.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/InventoryTestSomeWrites.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Attrition(2), InventoryTest. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/InventoryTestSomeWrites.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/KRMCoalescingFragmentation.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/KRMCoalescingFragmentation.toml

- **Purpose:** Fast simulation test specification for the `KRMCoalescingFragmentation` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 5 lines, 117 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles KRMCoalescingFragmentation, workloads KRMCoalescingFragmentation, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (KRMCoalescingFragmentation) and schedules each block's workload list (KRMCoalescingFragmentation:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: KRMCoalescingFragmentation. Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/KRMCoalescingFragmentation.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for KRMCoalescingFragmentation. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/KRMCoalescingFragmentation.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/KillRegionCycle.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/KillRegionCycle.toml

- **Purpose:** Fast simulation test specification for the `KillRegionCycle` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 19 lines, 356 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles KillRegionCycle, workloads Cycle, KillRegion, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (KillRegionCycle) and schedules each block's workload list (KillRegionCycle:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle, KillRegion. Top-level keys: configuration, knobs. Configuration/test knobs: minimumRegions=2, KillRegionCycle/Cycle.testDuration=30.0, KillRegionCycle/Cycle.transactionsPerSecond=2500.0, KillRegionCycle/Cycle.nodeCount=30000, KillRegionCycle/KillRegion.testDuration=30.0.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/KillRegionCycle.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle, KillRegion. Clear-after-test modes: KillRegionCycle:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/KillRegionCycle.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/LocalRatekeeper.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/LocalRatekeeper.toml

- **Purpose:** Fast simulation test specification for the `LocalRatekeeper` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 12 lines, 243 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles LocalRateKeeper, workloads LocalRatekeeper, Cycle, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (LocalRateKeeper) and schedules each block's workload list (LocalRateKeeper:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: LocalRatekeeper, Cycle. Top-level keys: none. Configuration/test knobs: LocalRateKeeper/Cycle.testDuration=200, LocalRateKeeper/Cycle.transactionsPerSecond=25.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/LocalRatekeeper.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for LocalRatekeeper, Cycle. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/LocalRatekeeper.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/LongStackWriteDuringRead.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/LongStackWriteDuringRead.toml

- **Purpose:** Fast simulation test specification for the `LongStackWriteDuringRead` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 11 lines, 201 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles WriteDuringReadTest, workloads WriteDuringRead, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (WriteDuringReadTest) and schedules each block's workload list (WriteDuringReadTest:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: WriteDuringRead. Top-level keys: configuration. Configuration/test knobs: StderrSeverity=30, WriteDuringReadTest/WriteDuringRead.testDuration=30.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/LongStackWriteDuringRead.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for WriteDuringRead. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/LongStackWriteDuringRead.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/LowLatency.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/LowLatency.toml

- **Purpose:** Fast simulation test specification for the `LowLatency` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 35 lines, 1067 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles Clogged, workloads Cycle, LowLatency, Attrition, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (Clogged) and schedules each block's workload list (Clogged:3). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle, LowLatency, Attrition. Top-level keys: configuration, knobs. Configuration/test knobs: buggify=False, minimumReplication=2, Clogged/Cycle.testDuration=30.0, Clogged/Cycle.transactionsPerSecond=1000.0, Clogged/LowLatency.testDuration=30.0, Clogged/Attrition.testDuration=30.0, Clogged/Attrition.machinesToKill=1, Clogged/Attrition.machinesToLeave=3.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/LowLatency.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle, LowLatency, Attrition. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/LowLatency.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/LowLatencySingleClog.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/LowLatencySingleClog.toml

- **Purpose:** Fast simulation test specification for the `LowLatencySingleClog` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 30 lines, 965 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles Clogged, workloads Cycle, LowLatency, ClogSingleConnection, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (Clogged) and schedules each block's workload list (Clogged:3). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle, LowLatency, ClogSingleConnection. Top-level keys: configuration, knobs. Configuration/test knobs: buggify=False, minimumReplication=2, Clogged/Cycle.testDuration=60.0, Clogged/Cycle.transactionsPerSecond=1000.0, Clogged/LowLatency.testDuration=60.0.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/LowLatencySingleClog.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle, LowLatency, ClogSingleConnection. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/LowLatencySingleClog.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/MaxGrvQueueDelay.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/MaxGrvQueueDelay.toml

- **Purpose:** Fast simulation test specification for the `MaxGrvQueueDelay` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 19 lines, 484 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles MaxGrvQueueDelay, workloads MaxGrvQueueDelay, top-level keys knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (MaxGrvQueueDelay) and schedules each block's workload list (MaxGrvQueueDelay:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: MaxGrvQueueDelay. Top-level keys: knobs. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/MaxGrvQueueDelay.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for MaxGrvQueueDelay. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/MaxGrvQueueDelay.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/MemoryLifetime.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/MemoryLifetime.toml

- **Purpose:** Fast simulation test specification for the `MemoryLifetime` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 5 lines, 97 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles MemoryLifetimeTest, workloads MemoryLifetime, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (MemoryLifetimeTest) and schedules each block's workload list (MemoryLifetimeTest:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: MemoryLifetime. Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/MemoryLifetime.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for MemoryLifetime. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/MemoryLifetime.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/MinimumThroughput.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/MinimumThroughput.toml

- **Purpose:** Fast simulation test specification for the `MinimumThroughput` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 14 lines, 302 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles MinimumThroughput, workloads MinimumThroughput, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (MinimumThroughput) and schedules each block's workload list (MinimumThroughput:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: MinimumThroughput. Top-level keys: configuration. Configuration/test knobs: buggify=False, MinimumThroughput/MinimumThroughput.testDuration=30.0, MinimumThroughput/MinimumThroughput.transactionsPerSecond=200.0, MinimumThroughput/MinimumThroughput.nodeCount=100000.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/MinimumThroughput.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for MinimumThroughput. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/MinimumThroughput.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/MockDDReadWrite.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/MockDDReadWrite.toml

- **Purpose:** Fast simulation test specification for the `MockDDReadWrite` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 27 lines, 495 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 2 test block(s), titles MockDDTracker, MockDDReadWriteTest, workloads MockDDTrackerShardEvaluator, MockDDReadWrite, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 2 `[[test]]` block(s) (MockDDTracker, MockDDReadWriteTest) and schedules each block's workload list (MockDDTracker:1, MockDDReadWriteTest:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: MockDDTrackerShardEvaluator, MockDDReadWrite. Top-level keys: configuration, knobs. Configuration/test knobs: testClass='MockDD', MockDDTracker/MockDDTrackerShardEvaluator.testDuration=50.0, MockDDReadWriteTest/MockDDReadWrite.testDuration=500.0.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/MockDDReadWrite.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for MockDDTrackerShardEvaluator, MockDDReadWrite. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/MockDDReadWrite.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/MoveKeysCycle.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/MoveKeysCycle.toml

- **Purpose:** Fast simulation test specification for the `MoveKeysCycle` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 25 lines, 499 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles MoveKeysCycle, workloads Attrition(2), Cycle, RandomMoveKeys, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (MoveKeysCycle) and schedules each block's workload list (MoveKeysCycle:4). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Attrition(2), Cycle, RandomMoveKeys. Top-level keys: none. Configuration/test knobs: MoveKeysCycle/Cycle.testDuration=10.0, MoveKeysCycle/Cycle.transactionsPerSecond=2500.0, MoveKeysCycle/RandomMoveKeys.testDuration=10.0, MoveKeysCycle/Attrition.testDuration=10.0, MoveKeysCycle/Attrition.machinesToKill=1, MoveKeysCycle/Attrition.machinesToLeave=3, MoveKeysCycle/Attrition.testDuration=10.0, MoveKeysCycle/Attrition.machinesToKill=1, MoveKeysCycle/Attrition.machinesToLeave=3.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/MoveKeysCycle.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Attrition(2), Cycle, RandomMoveKeys. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/MoveKeysCycle.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/MutationLogReaderCorrectness.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/MutationLogReaderCorrectness.toml

- **Purpose:** Fast simulation test specification for the `MutationLogReaderCorrectness` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 6 lines, 134 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles MutationLogReaderCorrectness, workloads MutationLogReaderCorrectness, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (MutationLogReaderCorrectness) and schedules each block's workload list (MutationLogReaderCorrectness:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: MutationLogReaderCorrectness. Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/MutationLogReaderCorrectness.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for MutationLogReaderCorrectness. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/MutationLogReaderCorrectness.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/PerpetualWiggleStats.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/PerpetualWiggleStats.toml

- **Purpose:** Fast simulation test specification for the `PerpetualWiggleStats` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 6 lines, 117 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles PerpetualWiggleStats, workloads PerpetualWiggleStatsWorkload, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (PerpetualWiggleStats) and schedules each block's workload list (PerpetualWiggleStats:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: PerpetualWiggleStatsWorkload. Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/PerpetualWiggleStats.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for PerpetualWiggleStatsWorkload. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/PerpetualWiggleStats.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/PhysicalShardMove.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/PhysicalShardMove.toml

- **Purpose:** Fast simulation test specification for the `PhysicalShardMove` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 29 lines, 1022 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles PhysicalShardMove, workloads PhysicalShardMove, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (PhysicalShardMove) and schedules each block's workload list (PhysicalShardMove:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: PhysicalShardMove. Top-level keys: configuration, knobs. Configuration/test knobs: config='triple', storageEngineType=5, processesPerMachine=1, coordinators=3, machineCount=15, disableTss=True.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/PhysicalShardMove.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for PhysicalShardMove. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/PhysicalShardMove.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/PrivateEndpoints.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/PrivateEndpoints.toml

- **Purpose:** Fast simulation test specification for the `PrivateEndpoints` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 5 lines, 89 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles PrivateEndpoints, workloads PrivateEndpoints, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (PrivateEndpoints) and schedules each block's workload list (PrivateEndpoints:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: PrivateEndpoints. Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/PrivateEndpoints.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for PrivateEndpoints. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/PrivateEndpoints.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/ProtocolVersion.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/ProtocolVersion.toml

- **Purpose:** Fast simulation test specification for the `ProtocolVersion` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 8 lines, 148 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles ProtocolVersionTest, workloads ProtocolVersion, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (ProtocolVersionTest) and schedules each block's workload list (ProtocolVersionTest:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: ProtocolVersion. Top-level keys: configuration. Configuration/test knobs: startIncompatibleProcess=True.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/ProtocolVersion.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for ProtocolVersion. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/ProtocolVersion.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/RESTUnit.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/RESTUnit.toml

- **Purpose:** Fast simulation test specification for the `RESTUnit` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 8 lines, 149 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles RESTUtilsTest, workloads UnitTests, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (RESTUtilsTest) and schedules each block's workload list (RESTUtilsTest:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: UnitTests. Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/RESTUnit.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for UnitTests. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/RESTUnit.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/RandomSelector.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/RandomSelector.toml

- **Purpose:** Fast simulation test specification for the `RandomSelector` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 5 lines, 88 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles RYOW_Test, workloads RandomSelector, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (RYOW_Test) and schedules each block's workload list (RYOW_Test:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: RandomSelector. Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/RandomSelector.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for RandomSelector. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/RandomSelector.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/RandomUnitTests.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/RandomUnitTests.toml

- **Purpose:** Fast simulation test specification for the `RandomUnitTests` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 13 lines, 248 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles UnitTests, workloads UnitTests, top-level keys knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (UnitTests) and schedules each block's workload list (UnitTests:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: UnitTests. Top-level keys: knobs. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/RandomUnitTests.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for UnitTests. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/RandomUnitTests.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/RangeLockCycle.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/RangeLockCycle.toml

- **Purpose:** Fast simulation test specification for the `RangeLockCycle` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 21 lines, 451 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles RangeLockCycle, workloads Cycle, RandomRangeLock, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (RangeLockCycle) and schedules each block's workload list (RangeLockCycle:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle, RandomRangeLock. Top-level keys: configuration, knobs. Configuration/test knobs: RangeLockCycle/Cycle.testDuration=30.0, RangeLockCycle/Cycle.transactionsPerSecond=1000.0, RangeLockCycle/Cycle.nodeCount=30000.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/RangeLockCycle.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle, RandomRangeLock. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/RangeLockCycle.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/RangeLocking.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/RangeLocking.toml

- **Purpose:** Fast simulation test specification for the `RangeLocking` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 15 lines, 326 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles RangeLocking, workloads RangeLocking, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (RangeLocking) and schedules each block's workload list (RangeLocking:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: RangeLocking. Top-level keys: configuration, knobs. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/RangeLocking.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for RangeLocking. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/RangeLocking.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/ReadHotDetectionCorrectness.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/ReadHotDetectionCorrectness.toml

- **Purpose:** Fast simulation test specification for the `ReadHotDetectionCorrectness` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 6 lines, 130 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles ReadHotDetection, workloads ReadHotDetection, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (ReadHotDetection) and schedules each block's workload list (ReadHotDetection:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: ReadHotDetection. Top-level keys: none. Configuration/test knobs: ReadHotDetection/ReadHotDetection.transactionsPerSecond=1000.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/ReadHotDetectionCorrectness.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for ReadHotDetection. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/ReadHotDetectionCorrectness.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/ReportConflictingKeys.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/ReportConflictingKeys.toml

- **Purpose:** Fast simulation test specification for the `ReportConflictingKeys` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 15 lines, 348 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles ReportConflictingKeysTest, workloads ReportConflictingKeys, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (ReportConflictingKeysTest) and schedules each block's workload list (ReportConflictingKeysTest:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: ReportConflictingKeys. Top-level keys: configuration. Configuration/test knobs: buggify=False, ReportConflictingKeysTest/ReportConflictingKeys.testDuration=20.0, ReportConflictingKeysTest/ReportConflictingKeys.nodeCount=10000, ReportConflictingKeysTest/ReportConflictingKeys.keyPrefix='RCK'.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/ReportConflictingKeys.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for ReportConflictingKeys. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/ReportConflictingKeys.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/RestoreValidation.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/RestoreValidation.toml

- **Purpose:** Fast simulation test specification for the `RestoreValidation` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 41 lines, 960 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles RestoreValidationSimple, workloads Cycle, BackupAndRestoreValidation, RestoreValidation, top-level keys configuration, testClass.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (RestoreValidationSimple) and schedules each block's workload list (RestoreValidationSimple:3). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Backup-oriented workloads add simulated backup agent and restore state that must survive fault injection long enough for correctness validation.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle, BackupAndRestoreValidation, RestoreValidation. Top-level keys: configuration, testClass. Configuration/test knobs: buggify=False, faultInjection=False, generateFearless=False, minimumRegions=1, config='single usable_regions=1 storage_engine=ssd-2 tenant_mode=disabled', RestoreValidationSimple.simBackupAgents='BackupToFile', RestoreValidationSimple/Cycle.testDuration=10.0, RestoreValidationSimple/Cycle.transactionsPerSecond=10.0, RestoreValidationSimple/Cycle.nodeCount=100, RestoreValidationSimple/BackupAndRestoreValidation.backupAfter=60.0, RestoreValidationSimple/BackupAndRestoreValidation.restoreAfter=110.0.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/RestoreValidation.toml` through the Python TestRunner/CTest path.
- **Risks:** Backup/restore specs depend on simulated backup-agent mode, timing, and range selection; timing drift can mask restore validation failures.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle, BackupAndRestoreValidation, RestoreValidation. Clear-after-test modes: RestoreValidationSimple:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/RestoreValidation.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/RocksdbNondeterministicTest.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/RocksdbNondeterministicTest.toml

- **Purpose:** Fast simulation test specification for the `RocksdbNondeterministicTest` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 46 lines, 845 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 2 test block(s), titles Clogged, Unclogged, workloads Cycle(2), Attrition(2), RandomClogging, Rollback, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 2 `[[test]]` block(s) (Clogged, Unclogged) and schedules each block's workload list (Clogged:5, Unclogged:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Storage-engine-focused workloads stress on-disk or checkpoint representations in the simulated/noSim environment.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle(2), Attrition(2), RandomClogging, Rollback. Top-level keys: configuration, knobs. Configuration/test knobs: storageEngineType=4, Clogged/Cycle.testDuration=10.0, Clogged/Cycle.transactionsPerSecond=2500.0, Clogged/RandomClogging.testDuration=10.0, Clogged/Rollback.testDuration=10.0, Clogged/Rollback.meanDelay=10.0, Clogged/Attrition.testDuration=10.0, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3, Clogged/Attrition.testDuration=10.0, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3, Unclogged/Cycle.testDuration=10.0, Unclogged/Cycle.transactionsPerSecond=250.0.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/RocksdbNondeterministicTest.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Storage-engine tests are sensitive to engine selection/exclusion knobs and checkpoint determinism.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle(2), Attrition(2), RandomClogging, Rollback. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/RocksdbNondeterministicTest.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/SelectorCorrectness.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/SelectorCorrectness.toml

- **Purpose:** Fast simulation test specification for the `SelectorCorrectness` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 5 lines, 93 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles RYOW_Test, workloads SelectorCorrectness, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (RYOW_Test) and schedules each block's workload list (RYOW_Test:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: SelectorCorrectness. Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/SelectorCorrectness.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for SelectorCorrectness. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/SelectorCorrectness.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/ShardEncodeRollback.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/ShardEncodeRollback.toml

- **Purpose:** Fast simulation test specification for the `ShardEncodeRollback` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 60 lines, 1526 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 2 test block(s), titles ShardEncodeRollbackSetup, ShardEncodeRollbackVerify, workloads Cycle(2), RandomMoveKeys(2), Attrition, Rollback, CheckMetadataEncoding, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 2 `[[test]]` block(s) (ShardEncodeRollbackSetup, ShardEncodeRollbackVerify) and schedules each block's workload list (ShardEncodeRollbackSetup:2, ShardEncodeRollbackVerify:5). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle(2), RandomMoveKeys(2), Attrition, Rollback, CheckMetadataEncoding. Top-level keys: configuration, knobs. Configuration/test knobs: storageEngineExcludeTypes=[3, 4, 5], ShardEncodeRollbackSetup/Cycle.testDuration=10.0, ShardEncodeRollbackSetup/Cycle.transactionsPerSecond=2500.0, ShardEncodeRollbackSetup/Cycle.nodeCount=2500, ShardEncodeRollbackSetup/RandomMoveKeys.testDuration=10.0, ShardEncodeRollbackVerify/Cycle.testDuration=30.0, ShardEncodeRollbackVerify/Cycle.transactionsPerSecond=2500.0, ShardEncodeRollbackVerify/Cycle.nodeCount=2500, ShardEncodeRollbackVerify/RandomMoveKeys.testDuration=30.0, ShardEncodeRollbackVerify/Attrition.testDuration=30.0, ShardEncodeRollbackVerify/Attrition.machinesToKill=1, ShardEncodeRollbackVerify/Attrition.machinesToLeave=3, ShardEncodeRollbackVerify/Rollback.testDuration=30.0, ShardEncodeRollbackVerify/Rollback.meanDelay=15.0.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/ShardEncodeRollback.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle(2), RandomMoveKeys(2), Attrition, Rollback, CheckMetadataEncoding. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/ShardEncodeRollback.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/ShardedRocksNondeterministicTest.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/ShardedRocksNondeterministicTest.toml

- **Purpose:** Fast simulation test specification for the `ShardedRocksNondeterministicTest` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 48 lines, 889 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 2 test block(s), titles Clogged, Unclogged, workloads Cycle(2), Attrition(2), RandomClogging, Rollback, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 2 `[[test]]` block(s) (Clogged, Unclogged) and schedules each block's workload list (Clogged:5, Unclogged:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Storage-engine-focused workloads stress on-disk or checkpoint representations in the simulated/noSim environment.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle(2), Attrition(2), RandomClogging, Rollback. Top-level keys: configuration, knobs. Configuration/test knobs: storageEngineType=5, Clogged/Cycle.testDuration=10.0, Clogged/Cycle.transactionsPerSecond=2500.0, Clogged/RandomClogging.testDuration=10.0, Clogged/Rollback.testDuration=10.0, Clogged/Rollback.meanDelay=10.0, Clogged/Attrition.testDuration=10.0, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3, Clogged/Attrition.testDuration=10.0, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3, Unclogged/Cycle.testDuration=10.0, Unclogged/Cycle.transactionsPerSecond=250.0.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/ShardedRocksNondeterministicTest.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Storage-engine tests are sensitive to engine selection/exclusion knobs and checkpoint determinism.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle(2), Attrition(2), RandomClogging, Rollback. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/ShardedRocksNondeterministicTest.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/Sideband.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/Sideband.toml

- **Purpose:** Fast simulation test specification for the `Sideband` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 30 lines, 601 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles CausalConsistencyTest, workloads Attrition(2), Sideband, RandomClogging, Rollback, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (CausalConsistencyTest) and schedules each block's workload list (CausalConsistencyTest:5). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Attrition(2), Sideband, RandomClogging, Rollback. Top-level keys: none. Configuration/test knobs: CausalConsistencyTest/Sideband.testDuration=30.0, CausalConsistencyTest/RandomClogging.testDuration=30.0, CausalConsistencyTest/Rollback.testDuration=30.0, CausalConsistencyTest/Rollback.meanDelay=10.0, CausalConsistencyTest/Attrition.testDuration=30.0, CausalConsistencyTest/Attrition.machinesToKill=10, CausalConsistencyTest/Attrition.machinesToLeave=3, CausalConsistencyTest/Attrition.testDuration=30.0, CausalConsistencyTest/Attrition.machinesToKill=10, CausalConsistencyTest/Attrition.machinesToLeave=3.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/Sideband.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Attrition(2), Sideband, RandomClogging, Rollback. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/Sideband.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/SidebandSingle.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/SidebandSingle.toml

- **Purpose:** Fast simulation test specification for the `SidebandSingle` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 30 lines, 619 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles SingleClientCausalConsistencyTest, workloads Attrition(2), SidebandSingle, RandomClogging, Rollback, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (SingleClientCausalConsistencyTest) and schedules each block's workload list (SingleClientCausalConsistencyTest:5). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Attrition(2), SidebandSingle, RandomClogging, Rollback. Top-level keys: none. Configuration/test knobs: SingleClientCausalConsistencyTest/SidebandSingle.testDuration=30.0, SingleClientCausalConsistencyTest/RandomClogging.testDuration=30.0, SingleClientCausalConsistencyTest/Rollback.testDuration=30.0, SingleClientCausalConsistencyTest/Rollback.meanDelay=10.0, SingleClientCausalConsistencyTest/Attrition.testDuration=30.0, SingleClientCausalConsistencyTest/Attrition.machinesToKill=10, SingleClientCausalConsistencyTest/Attrition.machinesToLeave=3, SingleClientCausalConsistencyTest/Attrition.testDuration=30.0, SingleClientCausalConsistencyTest/Attrition.machinesToKill=10, SingleClientCausalConsistencyTest/Attrition.machinesToLeave=3.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/SidebandSingle.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Attrition(2), SidebandSingle, RandomClogging, Rollback. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/SidebandSingle.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/SidebandWithStatus.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/SidebandWithStatus.toml

- **Purpose:** Fast simulation test specification for the `SidebandWithStatus` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 35 lines, 701 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles CloggedCausalConsistencyTest, workloads RandomClogging(2), Attrition(2), Sideband, Status, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (CloggedCausalConsistencyTest) and schedules each block's workload list (CloggedCausalConsistencyTest:6). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: RandomClogging(2), Attrition(2), Sideband, Status. Top-level keys: none. Configuration/test knobs: CloggedCausalConsistencyTest/Sideband.testDuration=30.0, CloggedCausalConsistencyTest/Status.testDuration=30.0, CloggedCausalConsistencyTest/RandomClogging.testDuration=30.0, CloggedCausalConsistencyTest/RandomClogging.testDuration=30.0, CloggedCausalConsistencyTest/Attrition.testDuration=30.0, CloggedCausalConsistencyTest/Attrition.machinesToKill=10, CloggedCausalConsistencyTest/Attrition.machinesToLeave=3, CloggedCausalConsistencyTest/Attrition.testDuration=30.0, CloggedCausalConsistencyTest/Attrition.machinesToKill=10, CloggedCausalConsistencyTest/Attrition.machinesToLeave=3.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/SidebandWithStatus.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for RandomClogging(2), Attrition(2), Sideband, Status. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/SidebandWithStatus.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/SimpleAtomicAdd.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/SimpleAtomicAdd.toml

- **Purpose:** Fast simulation test specification for the `SimpleAtomicAdd` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 9 lines, 178 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles SimpleAtomicAdd, workloads SimpleAtomicAdd, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (SimpleAtomicAdd) and schedules each block's workload list (SimpleAtomicAdd:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: SimpleAtomicAdd. Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/SimpleAtomicAdd.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for SimpleAtomicAdd. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/SimpleAtomicAdd.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/SpecialKeySpaceCorrectness.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/SpecialKeySpaceCorrectness.toml

- **Purpose:** Fast simulation test specification for the `SpecialKeySpaceCorrectness` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 10 lines, 200 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles SpecialKeySpaceCorrectnessTest, workloads SpecialKeySpaceCorrectness, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (SpecialKeySpaceCorrectnessTest) and schedules each block's workload list (SpecialKeySpaceCorrectnessTest:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: SpecialKeySpaceCorrectness. Top-level keys: configuration. Configuration/test knobs: SpecialKeySpaceCorrectnessTest/SpecialKeySpaceCorrectness.testDuration=30.0.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/SpecialKeySpaceCorrectness.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for SpecialKeySpaceCorrectness. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/SpecialKeySpaceCorrectness.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/SpecialKeySpaceRobustness.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/SpecialKeySpaceRobustness.toml

- **Purpose:** Fast simulation test specification for the `SpecialKeySpaceRobustness` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 7 lines, 136 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles SpecialKeySpaceRobustnessTest, workloads SpecialKeySpaceRobustness, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (SpecialKeySpaceRobustnessTest) and schedules each block's workload list (SpecialKeySpaceRobustnessTest:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: SpecialKeySpaceRobustness. Top-level keys: configuration. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/SpecialKeySpaceRobustness.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for SpecialKeySpaceRobustness. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/SpecialKeySpaceRobustness.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/StatusDuringOutage.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/StatusDuringOutage.toml

- **Purpose:** Fast simulation test specification for the `StatusDuringOutage` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 26 lines, 662 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles StatusDuringOutage, workloads Status, Attrition, RandomClogging, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (StatusDuringOutage) and schedules each block's workload list (StatusDuringOutage:3). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Status, Attrition, RandomClogging. Top-level keys: none. Configuration/test knobs: StatusDuringOutage/Status.testDuration=60.0, StatusDuringOutage/Attrition.testDuration=60.0, StatusDuringOutage/Attrition.machinesToKill=10, StatusDuringOutage/Attrition.machinesToLeave=1, StatusDuringOutage/RandomClogging.testDuration=60.0.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/StatusDuringOutage.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Status, Attrition, RandomClogging. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/StatusDuringOutage.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/StorageServerCheckpointRestore.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/StorageServerCheckpointRestore.toml

- **Purpose:** Fast simulation test specification for the `StorageServerCheckpointRestore` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 13 lines, 248 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles SSCheckpointRestoreWorkload, workloads SSCheckpointRestoreWorkload, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (SSCheckpointRestoreWorkload) and schedules each block's workload list (SSCheckpointRestoreWorkload:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Backup-oriented workloads add simulated backup agent and restore state that must survive fault injection long enough for correctness validation. Storage-engine-focused workloads stress on-disk or checkpoint representations in the simulated/noSim environment.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: SSCheckpointRestoreWorkload. Top-level keys: configuration. Configuration/test knobs: config='triple', storageEngineType=4, processesPerMachine=1, coordinators=3, machineCount=15.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/StorageServerCheckpointRestore.toml` through the Python TestRunner/CTest path.
- **Risks:** Backup/restore specs depend on simulated backup-agent mode, timing, and range selection; timing drift can mask restore validation failures. Storage-engine tests are sensitive to engine selection/exclusion knobs and checkpoint determinism.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for SSCheckpointRestoreWorkload. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/StorageServerCheckpointRestore.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/StreamingRangeRead.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/StreamingRangeRead.toml

- **Purpose:** Fast simulation test specification for the `StreamingRangeRead` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 29 lines, 582 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles StreamingRangeReadTest, workloads Attrition(2), StreamingRangeRead, RandomClogging, Rollback, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (StreamingRangeReadTest) and schedules each block's workload list (StreamingRangeReadTest:5). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Attrition(2), StreamingRangeRead, RandomClogging, Rollback. Top-level keys: none. Configuration/test knobs: StreamingRangeReadTest/StreamingRangeRead.testDuration=60.0, StreamingRangeReadTest/RandomClogging.testDuration=60.0, StreamingRangeReadTest/Rollback.testDuration=60.0, StreamingRangeReadTest/Rollback.meanDelay=60.0, StreamingRangeReadTest/Attrition.testDuration=60.0, StreamingRangeReadTest/Attrition.machinesToKill=10, StreamingRangeReadTest/Attrition.machinesToLeave=3, StreamingRangeReadTest/Attrition.testDuration=60.0, StreamingRangeReadTest/Attrition.machinesToKill=10, StreamingRangeReadTest/Attrition.machinesToLeave=3.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/StreamingRangeRead.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Attrition(2), StreamingRangeRead, RandomClogging, Rollback. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/StreamingRangeRead.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/SwizzledRollbackSideband.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/SwizzledRollbackSideband.toml

- **Purpose:** Fast simulation test specification for the `SwizzledRollbackSideband` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 41 lines, 817 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles SwizzledCausalConsistencyTest, workloads Attrition(3), Sideband, RandomClogging, Rollback, RemoveServersSafely, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (SwizzledCausalConsistencyTest) and schedules each block's workload list (SwizzledCausalConsistencyTest:7). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Attrition(3), Sideband, RandomClogging, Rollback, RemoveServersSafely. Top-level keys: none. Configuration/test knobs: SwizzledCausalConsistencyTest/Sideband.testDuration=300.0, SwizzledCausalConsistencyTest/RandomClogging.testDuration=300.0, SwizzledCausalConsistencyTest/Rollback.testDuration=300.0, SwizzledCausalConsistencyTest/Rollback.meanDelay=10.0, SwizzledCausalConsistencyTest/Attrition.testDuration=300.0, SwizzledCausalConsistencyTest/Attrition.testDuration=300.0, SwizzledCausalConsistencyTest/Attrition.machinesToKill=10, SwizzledCausalConsistencyTest/Attrition.machinesToLeave=3, SwizzledCausalConsistencyTest/Attrition.testDuration=300.0, SwizzledCausalConsistencyTest/Attrition.machinesToKill=10, SwizzledCausalConsistencyTest/Attrition.machinesToLeave=3.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/SwizzledRollbackSideband.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Attrition(3), Sideband, RandomClogging, Rollback, RemoveServersSafely. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/SwizzledRollbackSideband.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/SystemRebootTestCycle.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/SystemRebootTestCycle.toml

- **Purpose:** Fast simulation test specification for the `SystemRebootTestCycle` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 39 lines, 731 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 3 test block(s), titles Clogged, KillAllButOne, Unclogged, workloads Cycle(2), RandomClogging, Rollback, Attrition, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 3 `[[test]]` block(s) (Clogged, KillAllButOne, Unclogged) and schedules each block's workload list (Clogged:3, KillAllButOne:1, Unclogged:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle(2), RandomClogging, Rollback, Attrition. Top-level keys: none. Configuration/test knobs: Clogged/Cycle.testDuration=20.0, Clogged/Cycle.transactionsPerSecond=250.0, Clogged/Cycle.nodeCount=50000, Clogged/RandomClogging.testDuration=10.0, Clogged/Rollback.testDuration=10.0, Clogged/Rollback.meanDelay=10.0, KillAllButOne/Attrition.testDuration=1.0, KillAllButOne/Attrition.machinesToKill=100, KillAllButOne/Attrition.machinesToLeave=1, Unclogged.runSetup=False, Unclogged/Cycle.testDuration=10.0, Unclogged/Cycle.transactionsPerSecond=250.0, Unclogged/Cycle.nodeCount=50000.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/SystemRebootTestCycle.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle(2), RandomClogging, Rollback, Attrition. Clear-after-test modes: Clogged:False, KillAllButOne:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/SystemRebootTestCycle.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/TaskBucketCorrectness.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/TaskBucketCorrectness.toml

- **Purpose:** Fast simulation test specification for the `TaskBucketCorrectness` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 7 lines, 149 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles TaskBucketCorrectness, workloads TaskBucketCorrectness, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (TaskBucketCorrectness) and schedules each block's workload list (TaskBucketCorrectness:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: TaskBucketCorrectness. Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/TaskBucketCorrectness.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for TaskBucketCorrectness. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/TaskBucketCorrectness.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/TimeKeeperCorrectness.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/TimeKeeperCorrectness.toml

- **Purpose:** Fast simulation test specification for the `TimeKeeperCorrectness` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 6 lines, 131 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles TimeKeeperCorrectness, workloads TimeKeeperCorrectness, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (TimeKeeperCorrectness) and schedules each block's workload list (TimeKeeperCorrectness:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: TimeKeeperCorrectness. Top-level keys: none. Configuration/test knobs: TimeKeeperCorrectness/TimeKeeperCorrectness.testDuration=40.0.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/TimeKeeperCorrectness.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for TimeKeeperCorrectness. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/TimeKeeperCorrectness.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/TxnStateStoreCycleTest.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/TxnStateStoreCycleTest.toml

- **Purpose:** Fast simulation test specification for the `TxnStateStoreCycleTest` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 48 lines, 1028 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 2 test block(s), titles PreLoad, Clogged, workloads Attrition(2), BulkLoad, Cycle, RandomClogging, Rollback, LockDatabaseFrequently, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 2 `[[test]]` block(s) (PreLoad, Clogged) and schedules each block's workload list (PreLoad:1, Clogged:6). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Attrition(2), BulkLoad, Cycle, RandomClogging, Rollback, LockDatabaseFrequently. Top-level keys: configuration. Configuration/test knobs: storageEngineExcludeTypes=[5], PreLoad/BulkLoad.testDuration=3000.0, PreLoad/BulkLoad.keyPrefix='\\xff/TESTONLYtxnStateStore/notcycle/', Clogged/Cycle.testDuration=10.0, Clogged/Cycle.transactionsPerSecond=2500.0, Clogged/Cycle.keyPrefix='\\xff/TESTONLYtxnStateStore/', Clogged/RandomClogging.testDuration=10.0, Clogged/Rollback.testDuration=10.0, Clogged/Rollback.meanDelay=10.0, Clogged/Attrition.testDuration=10.0, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3, Clogged/Attrition.testDuration=10.0, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/TxnStateStoreCycleTest.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Attrition(2), BulkLoad, Cycle, RandomClogging, Rollback, LockDatabaseFrequently. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/TxnStateStoreCycleTest.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/TxnTimeout.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/TxnTimeout.toml

- **Purpose:** Fast simulation test specification for the `TxnTimeout` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 56 lines, 2229 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles TxnTimeout, workloads TxnTimeout, Cycle, top-level keys knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (TxnTimeout) and schedules each block's workload list (TxnTimeout:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: TxnTimeout, Cycle. Top-level keys: knobs. Configuration/test knobs: TxnTimeout/TxnTimeout.testDuration=360.0, TxnTimeout/Cycle.testDuration=360.0, TxnTimeout/Cycle.transactionsPerSecond=250.0, TxnTimeout/Cycle.nodeCount=30.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/TxnTimeout.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for TxnTimeout, Cycle. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/TxnTimeout.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/UDP.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/UDP.toml

- **Purpose:** Fast simulation test specification for the `UDP` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 5 lines, 79 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles UDP, workloads UDPWorkload, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (UDP) and schedules each block's workload list (UDP:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: UDPWorkload. Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/UDP.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for UDPWorkload. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/UDP.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/Unreadable.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/Unreadable.toml

- **Purpose:** Fast simulation test specification for the `Unreadable` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 5 lines, 85 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles Unreadable, workloads Unreadable, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (Unreadable) and schedules each block's workload list (Unreadable:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Unreadable. Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/Unreadable.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Unreadable. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/Unreadable.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/ValidateStorage.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/ValidateStorage.toml

- **Purpose:** Fast simulation test specification for the `ValidateStorage` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 14 lines, 250 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles ValidateStorageWorkload, workloads ValidateStorageWorkload, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (ValidateStorageWorkload) and schedules each block's workload list (ValidateStorageWorkload:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Storage-engine-focused workloads stress on-disk or checkpoint representations in the simulated/noSim environment.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: ValidateStorageWorkload. Top-level keys: configuration, knobs. Configuration/test knobs: config='triple', generateFearless=True, machineCount=18.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/ValidateStorage.toml` through the Python TestRunner/CTest path.
- **Risks:** Storage-engine tests are sensitive to engine selection/exclusion knobs and checkpoint determinism.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for ValidateStorageWorkload. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/ValidateStorage.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/VersionStamp.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/VersionStamp.toml

- **Purpose:** Fast simulation test specification for the `VersionStamp` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 9 lines, 193 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles VersionStamp, workloads VersionStamp, LockDatabaseFrequently, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (VersionStamp) and schedules each block's workload list (VersionStamp:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: VersionStamp, LockDatabaseFrequently. Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/VersionStamp.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for VersionStamp, LockDatabaseFrequently. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/VersionStamp.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/Watches.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/Watches.toml

- **Purpose:** Fast simulation test specification for the `Watches` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 9 lines, 168 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles WatchesTest, workloads Watches, WatchesSameKeyCorrectness, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (WatchesTest) and schedules each block's workload list (WatchesTest:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Watches, WatchesSameKeyCorrectness. Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/Watches.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Watches, WatchesSameKeyCorrectness. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/Watches.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/WriteDuringRead.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/WriteDuringRead.toml

- **Purpose:** Fast simulation test specification for the `WriteDuringRead` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 32 lines, 613 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles WriteDuringReadTest, workloads Attrition(2), WriteDuringRead, RandomClogging, Rollback, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (WriteDuringReadTest) and schedules each block's workload list (WriteDuringReadTest:5). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Attrition(2), WriteDuringRead, RandomClogging, Rollback. Top-level keys: configuration. Configuration/test knobs: StderrSeverity=30, WriteDuringReadTest/WriteDuringRead.testDuration=30.0, WriteDuringReadTest/RandomClogging.testDuration=30.0, WriteDuringReadTest/Rollback.testDuration=30.0, WriteDuringReadTest/Rollback.meanDelay=30.0, WriteDuringReadTest/Attrition.testDuration=30.0, WriteDuringReadTest/Attrition.machinesToKill=10, WriteDuringReadTest/Attrition.machinesToLeave=3, WriteDuringReadTest/Attrition.testDuration=30.0, WriteDuringReadTest/Attrition.machinesToKill=10, WriteDuringReadTest/Attrition.machinesToLeave=3.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/WriteDuringRead.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Attrition(2), WriteDuringRead, RandomClogging, Rollback. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/WriteDuringRead.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/WriteDuringReadClean.toml -->
# Research: sources/storage-engines/foundationdb/tests/fast/WriteDuringReadClean.toml

- **Purpose:** Fast simulation test specification for the `WriteDuringReadClean` scenario. It defines a short-running FoundationDB workload mix used by the simulation runner for high-frequency correctness and fault-injection coverage.
- **Source facts:** 8 lines, 136 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles WriteDuringReadTest, workloads WriteDuringRead, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (WriteDuringReadTest) and schedules each block's workload list (WriteDuringReadTest:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: WriteDuringRead. Top-level keys: configuration. Configuration/test knobs: StderrSeverity=30.
- **Integration points:** Integrated by suite location `fast` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/fast/WriteDuringReadClean.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for WriteDuringRead. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/fast/WriteDuringReadClean.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/loopback_cluster/run_cluster.sh -->
# Research: sources/storage-engines/foundationdb/tests/loopback_cluster/run_cluster.sh

- **Purpose:** Loopback-cluster launcher that prepares a build-directory run area and starts a local cluster using built binaries.
- **Source facts:** 48 lines, 911 bytes, executable=True.
- **Important APIs/types/functions:** Shell commands observed: set, trap, ROOT=`pwd`, function, echo, exit, }, if, usage, fi, BUILD=$1, FDB=${BUILD}/bin/fdbserver, rm, for, DIR=./loopback-cluster-$i, mkdir, PORT_PREFIX=${i}50, CLUSTER_FILE=test$i:testdb$i@127.0.0.1:${PORT_PREFIX}1; plus 10 more. Variable assignments: ROOT, BUILD, FDB, DIR, PORT_PREFIX, CLUSTER_FILE, CLUSTER, LOG, DATA, CLI.
- **Control flow:** Script control constructs: none. It executes sequential shell setup and command-launch steps.
- **State and persistence:** Creates or reuses local cluster runtime directories, configuration files, data/log directories, and process state for a loopback FoundationDB cluster.
- **Dependencies:** Depends on bash, built FoundationDB binaries/config paths, and local filesystem permissions for cluster runtime directories.
- **Integration points:** Used manually or by tests that need a loopback cluster outside deterministic simulation.
- **Risks:** Shell path assumptions and long-running processes can leave stale cluster state if interrupted; environment-specific binary paths must match the build tree.
- **Test signals:** Successful cluster startup and child process exit are the key signals; failures usually appear as shell non-zero exits or cluster logs.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/loopback_cluster/run_cluster.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/loopback_cluster/run_custom_cluster.sh -->
# Research: sources/storage-engines/foundationdb/tests/loopback_cluster/run_custom_cluster.sh

- **Purpose:** Customizable loopback cluster launcher for running fdbmonitor/fdbserver from explicit or build-derived paths.
- **Source facts:** 236 lines, 6880 bytes, executable=True.
- **Important APIs/types/functions:** Shell commands observed: set, SERVER_COUNT=1, readonly, STATELESS_COUNT=4, REPLICATION_COUNT=1, LOGS_COUNT=8, STORAGE_COUNT=16, KNOBS=, LOGS_TASKSET=, STATELESS_TASKSET=, STORAGE_TASKSET=, STORAGE_TYPE=ssd, LOGROUTER_COUNT=0, DUMP_PIDS=, PIDS=(), function, echo, printf; plus 79 more. Variable assignments: SERVER_COUNT, STATELESS_COUNT, REPLICATION_COUNT, LOGS_COUNT, STORAGE_COUNT, KNOBS, LOGS_TASKSET, STATELESS_TASKSET, STORAGE_TASKSET, STORAGE_TYPE, LOGROUTER_COUNT, DUMP_PIDS, PIDS, status, BUILD, FDB, replication, LOOPBACK_DIR; plus 3 more.
- **Control flow:** Script control constructs: none. It executes sequential shell setup and command-launch steps.
- **State and persistence:** Creates or reuses local cluster runtime directories, configuration files, data/log directories, and process state for a loopback FoundationDB cluster.
- **Dependencies:** Depends on bash, built FoundationDB binaries/config paths, and local filesystem permissions for cluster runtime directories.
- **Integration points:** Used manually or by tests that need a loopback cluster outside deterministic simulation.
- **Risks:** Shell path assumptions and long-running processes can leave stale cluster state if interrupted; environment-specific binary paths must match the build tree.
- **Test signals:** Successful cluster startup and child process exit are the key signals; failures usually appear as shell non-zero exits or cluster logs.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/loopback_cluster/run_custom_cluster.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/negative/ResolverIgnoreReads.toml -->
# Research: sources/storage-engines/foundationdb/tests/negative/ResolverIgnoreReads.toml

- **Purpose:** Negative simulation test specification for `ResolverIgnoreReads`. It intentionally exercises error or fault behavior where the expected signal is not normal success-path workload completion.
- **Source facts:** 6 lines, 119 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles ResolverIgnoreReads, workloads ResolverBug, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (ResolverIgnoreReads) and schedules each block's workload list (ResolverIgnoreReads:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: ResolverBug. Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `negative` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/negative/ResolverIgnoreReads.toml` through the Python TestRunner/CTest path.
- **Risks:** Negative tests rely on expected failure/ignore behavior, so a plain non-zero exit is not always enough context without matching trace assertions.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for ResolverBug. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/negative/ResolverIgnoreReads.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/negative/ResolverIgnoreTooOld.toml -->
# Research: sources/storage-engines/foundationdb/tests/negative/ResolverIgnoreTooOld.toml

- **Purpose:** Negative simulation test specification for `ResolverIgnoreTooOld`. It intentionally exercises error or fault behavior where the expected signal is not normal success-path workload completion.
- **Source facts:** 14 lines, 339 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles ResolverIgnoreTooOld, workloads ResolverBug, top-level keys knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (ResolverIgnoreTooOld) and schedules each block's workload list (ResolverIgnoreTooOld:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: ResolverBug. Top-level keys: knobs. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `negative` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/negative/ResolverIgnoreTooOld.toml` through the Python TestRunner/CTest path.
- **Risks:** Negative tests rely on expected failure/ignore behavior, so a plain non-zero exit is not always enough context without matching trace assertions.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for ResolverBug. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/negative/ResolverIgnoreTooOld.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/negative/ResolverIgnoreWrites.toml -->
# Research: sources/storage-engines/foundationdb/tests/negative/ResolverIgnoreWrites.toml

- **Purpose:** Negative simulation test specification for `ResolverIgnoreWrites`. It intentionally exercises error or fault behavior where the expected signal is not normal success-path workload completion.
- **Source facts:** 6 lines, 120 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles ResolverIgnoreReads, workloads ResolverBug, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (ResolverIgnoreReads) and schedules each block's workload list (ResolverIgnoreReads:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: ResolverBug. Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `negative` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/negative/ResolverIgnoreWrites.toml` through the Python TestRunner/CTest path.
- **Risks:** Negative tests rely on expected failure/ignore behavior, so a plain non-zero exit is not always enough context without matching trace assertions.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for ResolverBug. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/negative/ResolverIgnoreWrites.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/negative/StorageCorruption.toml -->
# Research: sources/storage-engines/foundationdb/tests/negative/StorageCorruption.toml

- **Purpose:** Negative simulation test specification for `StorageCorruption`. It intentionally exercises error or fault behavior where the expected signal is not normal success-path workload completion.
- **Source facts:** 21 lines, 432 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles StorageCorruption, workloads StorageCorruption, ReadWrite, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (StorageCorruption) and schedules each block's workload list (StorageCorruption:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Storage-engine-focused workloads stress on-disk or checkpoint representations in the simulated/noSim environment.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: StorageCorruption, ReadWrite. Top-level keys: none. Configuration/test knobs: StorageCorruption/StorageCorruption.testDuration=60.0, StorageCorruption/ReadWrite.testDuration=60.0, StorageCorruption/ReadWrite.transactionsPerSecond=200, StorageCorruption/ReadWrite.nodeCount=10000.
- **Integration points:** Integrated by suite location `negative` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/negative/StorageCorruption.toml` through the Python TestRunner/CTest path.
- **Risks:** Negative tests rely on expected failure/ignore behavior, so a plain non-zero exit is not always enough context without matching trace assertions. Storage-engine tests are sensitive to engine selection/exclusion knobs and checkpoint determinism.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for StorageCorruption, ReadWrite. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/negative/StorageCorruption.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/noSim/KeyValueStoreRocksDBTest.toml -->
# Research: sources/storage-engines/foundationdb/tests/noSim/KeyValueStoreRocksDBTest.toml

- **Purpose:** Non-simulation test specification for `KeyValueStoreRocksDBTest`. It targets storage-engine or unit-test behavior that runs outside the normal deterministic simulation harness.
- **Source facts:** 9 lines, 201 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles UnitTests, workloads UnitTests, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (UnitTests) and schedules each block's workload list (UnitTests:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Storage-engine-focused workloads stress on-disk or checkpoint representations in the simulated/noSim environment.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: UnitTests. Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `noSim` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/noSim/KeyValueStoreRocksDBTest.toml` through the Python TestRunner/CTest path.
- **Risks:** Storage-engine tests are sensitive to engine selection/exclusion knobs and checkpoint determinism.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for UnitTests. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/noSim/KeyValueStoreRocksDBTest.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/noSim/PerfShardedRocksDBTest.toml -->
# Research: sources/storage-engines/foundationdb/tests/noSim/PerfShardedRocksDBTest.toml

- **Purpose:** Non-simulation test specification for `PerfShardedRocksDBTest`. It targets storage-engine or unit-test behavior that runs outside the normal deterministic simulation harness.
- **Source facts:** 17 lines, 381 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles UnitTests, workloads UnitTests, top-level keys knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (UnitTests) and schedules each block's workload list (UnitTests:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Storage-engine-focused workloads stress on-disk or checkpoint representations in the simulated/noSim environment.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: UnitTests. Top-level keys: knobs. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `noSim` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/noSim/PerfShardedRocksDBTest.toml` through the Python TestRunner/CTest path.
- **Risks:** Storage-engine tests are sensitive to engine selection/exclusion knobs and checkpoint determinism.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for UnitTests. Clear-after-test modes: none. Timeouts: UnitTests:3600.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/noSim/PerfShardedRocksDBTest.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/noSim/RandomUnitTests.toml -->
# Research: sources/storage-engines/foundationdb/tests/noSim/RandomUnitTests.toml

- **Purpose:** Non-simulation test specification for `RandomUnitTests`. It targets storage-engine or unit-test behavior that runs outside the normal deterministic simulation harness.
- **Source facts:** 12 lines, 205 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles UnitTests, workloads UnitTests, top-level keys knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (UnitTests) and schedules each block's workload list (UnitTests:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: UnitTests. Top-level keys: knobs. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `noSim` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/noSim/RandomUnitTests.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for UnitTests. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/noSim/RandomUnitTests.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/noSim/ShardedRocksDBCheckpointDeterminism.toml -->
# Research: sources/storage-engines/foundationdb/tests/noSim/ShardedRocksDBCheckpointDeterminism.toml

- **Purpose:** Non-simulation test specification for `ShardedRocksDBCheckpointDeterminism`. It targets storage-engine or unit-test behavior that runs outside the normal deterministic simulation harness.
- **Source facts:** 9 lines, 201 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles UnitTests, workloads UnitTests, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (UnitTests) and schedules each block's workload list (UnitTests:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Storage-engine-focused workloads stress on-disk or checkpoint representations in the simulated/noSim environment.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: UnitTests. Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `noSim` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/noSim/ShardedRocksDBCheckpointDeterminism.toml` through the Python TestRunner/CTest path.
- **Risks:** Storage-engine tests are sensitive to engine selection/exclusion knobs and checkpoint determinism.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for UnitTests. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/noSim/ShardedRocksDBCheckpointDeterminism.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/noSim/ShardedRocksDBCheckpointTest.toml -->
# Research: sources/storage-engines/foundationdb/tests/noSim/ShardedRocksDBCheckpointTest.toml

- **Purpose:** Non-simulation test specification for `ShardedRocksDBCheckpointTest`. It targets storage-engine or unit-test behavior that runs outside the normal deterministic simulation harness.
- **Source facts:** 14 lines, 324 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles UnitTests, workloads UnitTests, top-level keys knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (UnitTests) and schedules each block's workload list (UnitTests:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Storage-engine-focused workloads stress on-disk or checkpoint representations in the simulated/noSim environment.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: UnitTests. Top-level keys: knobs. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `noSim` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/noSim/ShardedRocksDBCheckpointTest.toml` through the Python TestRunner/CTest path.
- **Risks:** Storage-engine tests are sensitive to engine selection/exclusion knobs and checkpoint determinism.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for UnitTests. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/noSim/ShardedRocksDBCheckpointTest.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/noSim/ShardedRocksDBTest.toml -->
# Research: sources/storage-engines/foundationdb/tests/noSim/ShardedRocksDBTest.toml

- **Purpose:** Non-simulation test specification for `ShardedRocksDBTest`. It targets storage-engine or unit-test behavior that runs outside the normal deterministic simulation harness.
- **Source facts:** 16 lines, 399 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles UnitTests, workloads UnitTests, top-level keys knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (UnitTests) and schedules each block's workload list (UnitTests:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Storage-engine-focused workloads stress on-disk or checkpoint representations in the simulated/noSim environment.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: UnitTests. Top-level keys: knobs. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `noSim` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/noSim/ShardedRocksDBTest.toml` through the Python TestRunner/CTest path.
- **Risks:** Storage-engine tests are sensitive to engine selection/exclusion knobs and checkpoint determinism.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for UnitTests. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/noSim/ShardedRocksDBTest.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/python_tests/__init__.py -->
# Research: sources/storage-engines/foundationdb/tests/python_tests/__init__.py

- **Purpose:** Package marker for the fdb_test_runner module namespace. It has no runtime exports, but makes relative imports from the TestRunner helper scripts work under module execution.
- **Source facts:** 126 lines, 4031 bytes, executable=False.
- **Important APIs/types/functions:** Imports: argparse, fdb, json, os, random, traceback. Classes: Result, PythonTest. Top-level functions: __init__, add_kpi, add_error, save, __init__, run_test, multi_version_description, run. Methods: Result.__init__, Result.add_kpi, Result.add_error, Result.save, PythonTest.__init__, PythonTest.run_test, PythonTest.multi_version_description, PythonTest.run. Constants: none. CLI flags/options observed: --disable-multiversion-api, --enable-callbacks-on-external-threads, --output-directory, --use-external-client.
- **Control flow:** Library-style helpers are called by neighboring test-runner modules; control flow is direct function or context-manager execution.
- **State and persistence:** keeps no durable state beyond function-local values
- **Dependencies:** Python imports: argparse, fdb, json, os, random, traceback.
- **Integration points:** Part of the Python API correctness/performance test area; it integrates with the FoundationDB Python binding and local test clusters.
- **Risks:** Randomized names, ports, or workflow choices make collision avoidance and reproducibility dependent on surrounding seed/control logic.
- **Test signals:** Observable signals include none; failures normally surface as non-zero process exits, failed assertions, missing expected output, or trace severity events.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/python_tests/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/python_tests/multithreaded_client.py -->
# Research: sources/storage-engines/foundationdb/tests/python_tests/multithreaded_client.py

- **Purpose:** Python support or test module `multithreaded_client.py` in the FoundationDB test tree.
- **Source facts:** 79 lines, 2652 bytes, executable=True.
- **Important APIs/types/functions:** Imports: argparse, fdb, os, random, sys. Classes: none. Top-level functions: none. Methods: none. Constants: none. CLI flags/options observed: --build-dir, --client-log-dir, --skip-so-files, --threads.
- **Control flow:** Library-style helpers are called by neighboring test-runner modules; control flow is direct function or context-manager execution.
- **State and persistence:** creates, reads, renames, or removes filesystem artifacts (2 filesystem call sites)
- **Dependencies:** Python imports: argparse, fdb, os, random, sys.
- **Integration points:** Part of the Python API correctness/performance test area; it integrates with the FoundationDB Python binding and local test clusters.
- **Risks:** The file uses assertions for contract checks, so optimized Python execution would weaken some validation. Randomized names, ports, or workflow choices make collision avoidance and reproducibility dependent on surrounding seed/control logic.
- **Test signals:** Observable signals include assert; failures normally surface as non-zero process exits, failed assertions, missing expected output, or trace severity events.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/python_tests/multithreaded_client.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/python_tests/python_correctness.py -->
# Research: sources/storage-engines/foundationdb/tests/python_tests/python_correctness.py

- **Purpose:** Python support or test module `python_correctness.py` in the FoundationDB test tree.
- **Source facts:** 864 lines, 28967 bytes, executable=True.
- **Important APIs/types/functions:** Imports: fdb, fdb.tuple, os, python_tests.PythonTest, random, sys, time, traceback. Classes: KeyValueStore, PythonCorrectness. Top-level functions: get, get_key, get_range, get_range_startswith, set, clear, clear_range, clear_range_startswith, run_test, generate_data, test_callback, test_functions; plus 20 more. Methods: KeyValueStore.get, KeyValueStore.get_key, KeyValueStore.get_range, KeyValueStore.get_range_startswith, KeyValueStore.set, KeyValueStore.clear, KeyValueStore.clear_range, KeyValueStore.clear_range_startswith, PythonCorrectness.run_test, PythonCorrectness.generate_data, PythonCorrectness.test_callback, PythonCorrectness.test_functions; plus 20 more. Constants: none. CLI flags/options observed: none.
- **Control flow:** Executable module: parse command-line arguments, perform setup, run the requested child/test workflow, and convert internal success/failure to process exit status.
- **State and persistence:** creates, reads, renames, or removes filesystem artifacts (1 filesystem call sites)
- **Dependencies:** Python imports: fdb, fdb.tuple, os, python_tests.PythonTest, random, sys, time, traceback.
- **Integration points:** Part of the Python API correctness/performance test area; it integrates with the FoundationDB Python binding and local test clusters.
- **Risks:** Randomized names, ports, or workflow choices make collision avoidance and reproducibility dependent on surrounding seed/control logic.
- **Test signals:** Observable signals include none; failures normally surface as non-zero process exits, failed assertions, missing expected output, or trace severity events.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/python_tests/python_correctness.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/python_tests/python_performance.py -->
# Research: sources/storage-engines/foundationdb/tests/python_tests/python_performance.py

- **Purpose:** Python support or test module `python_performance.py` in the FoundationDB test tree.
- **Source facts:** 348 lines, 10398 bytes, executable=True.
- **Important APIs/types/functions:** Imports: argparse, collections.OrderedDict, fdb, fdb.tuple, math, os, python_tests.PythonTest, random, sys, time, traceback. Classes: PythonPerformance. Top-level functions: __init__, run_test, random_key, key, value, insert_data, test_performance, run_future_latency, run_clear, run_clear_range, run_set, run_parallel_get; plus 8 more. Methods: PythonPerformance.__init__, PythonPerformance.run_test, PythonPerformance.random_key, PythonPerformance.key, PythonPerformance.value, PythonPerformance.insert_data, PythonPerformance.test_performance, PythonPerformance.run_future_latency, PythonPerformance.run_clear, PythonPerformance.run_clear_range, PythonPerformance.run_set, PythonPerformance.run_parallel_get; plus 8 more. Constants: none. CLI flags/options observed: --tests-to-run.
- **Control flow:** Executable module: parse command-line arguments, perform setup, run the requested child/test workflow, and convert internal success/failure to process exit status.
- **State and persistence:** creates, reads, renames, or removes filesystem artifacts (1 filesystem call sites)
- **Dependencies:** Python imports: argparse, collections.OrderedDict, fdb, fdb.tuple, math, os, python_tests.PythonTest, random, sys, time, traceback.
- **Integration points:** Part of the Python API correctness/performance test area; it integrates with the FoundationDB Python binding and local test clusters.
- **Risks:** The file uses assertions for contract checks, so optimized Python execution would weaken some validation. Randomized names, ports, or workflow choices make collision avoidance and reproducibility dependent on surrounding seed/control logic.
- **Test signals:** Observable signals include assert; failures normally surface as non-zero process exits, failed assertions, missing expected output, or trace severity events.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/python_tests/python_performance.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/python_tests/ryw_benchmark.py -->
# Research: sources/storage-engines/foundationdb/tests/python_tests/ryw_benchmark.py

- **Purpose:** Python support or test module `ryw_benchmark.py` in the FoundationDB test tree.
- **Source facts:** 197 lines, 6375 bytes, executable=True.
- **Important APIs/types/functions:** Imports: argparse, fdb, os, python_tests.PythonTest, sys, time, traceback. Classes: RYWBenchmark. Top-level functions: __init__, run_test, key, get_error, test_performance, insert_data, run_get_single, run_get_many_sequential, run_get_range_basic, run_single_clear_get_range, run_clear_range_get_range, run_interleaved_sets_gets. Methods: RYWBenchmark.__init__, RYWBenchmark.run_test, RYWBenchmark.key, RYWBenchmark.get_error, RYWBenchmark.test_performance, RYWBenchmark.insert_data, RYWBenchmark.run_get_single, RYWBenchmark.run_get_many_sequential, RYWBenchmark.run_get_range_basic, RYWBenchmark.run_single_clear_get_range, RYWBenchmark.run_clear_range_get_range, RYWBenchmark.run_interleaved_sets_gets. Constants: none. CLI flags/options observed: --tests-to-run.
- **Control flow:** Executable module: parse command-line arguments, perform setup, run the requested child/test workflow, and convert internal success/failure to process exit status.
- **State and persistence:** creates, reads, renames, or removes filesystem artifacts (1 filesystem call sites)
- **Dependencies:** Python imports: argparse, fdb, os, python_tests.PythonTest, sys, time, traceback.
- **Integration points:** Part of the Python API correctness/performance test area; it integrates with the FoundationDB Python binding and local test clusters.
- **Risks:** The file uses assertions for contract checks, so optimized Python execution would weaken some validation.
- **Test signals:** Observable signals include assert; failures normally surface as non-zero process exits, failed assertions, missing expected output, or trace severity events.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/python_tests/ryw_benchmark.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/AllSimUnitTests.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/AllSimUnitTests.toml

- **Purpose:** Rare simulation test specification for the `AllSimUnitTests` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 10 lines, 191 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles UnitTests, workloads UnitTests, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (UnitTests) and schedules each block's workload list (UnitTests:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: UnitTests. Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/AllSimUnitTests.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for UnitTests. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/AllSimUnitTests.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/CheckRelocation.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/CheckRelocation.toml

- **Purpose:** Rare simulation test specification for the `CheckRelocation` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 18 lines, 466 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles RandomReadWriteTest, workloads ReadWrite, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (RandomReadWriteTest) and schedules each block's workload list (RandomReadWriteTest:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: ReadWrite. Top-level keys: none. Configuration/test knobs: RandomReadWriteTest/ReadWrite.testDuration=30.0, RandomReadWriteTest/ReadWrite.transactionsPerSecond=750, RandomReadWriteTest/ReadWrite.nodeCount=150000.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/CheckRelocation.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for ReadWrite. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/CheckRelocation.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/ClogRemoteTLog.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/ClogRemoteTLog.toml

- **Purpose:** Rare simulation test specification for the `ClogRemoteTLog` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 42 lines, 1126 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles ClogRemoteTLog, workloads Cycle, ClogRemoteTLog, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (ClogRemoteTLog) and schedules each block's workload list (ClogRemoteTLog:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle, ClogRemoteTLog. Top-level keys: configuration, knobs. Configuration/test knobs: processesPerMachine=1, machineCount=30, generateFearless=True, minimumRegions=2, remoteDesiredTLogCount=4, statelessProcessClassesPerDC=2, ClogRemoteTLog/Cycle.testDuration=360.0, ClogRemoteTLog/Cycle.transactionsPerSecond=250.0, ClogRemoteTLog/Cycle.nodeCount=30, ClogRemoteTLog/ClogRemoteTLog.testDuration=360.0.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/ClogRemoteTLog.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle, ClogRemoteTLog. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/ClogRemoteTLog.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/ClogTlog.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/ClogTlog.toml

- **Purpose:** Rare simulation test specification for the `ClogTlog` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 29 lines, 644 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles ClogTlog, workloads Cycle, ClogTlog, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (ClogTlog) and schedules each block's workload list (ClogTlog:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle, ClogTlog. Top-level keys: configuration, knobs. Configuration/test knobs: generateFearless=False, processesPerMachine=1, machineCount=20, commitProxyCount=4, config='triple', desiredTLogCount=6, ClogTlog/Cycle.testDuration=60.0, ClogTlog/Cycle.transactionsPerSecond=2500.0, ClogTlog/Cycle.nodeCount=30000, ClogTlog/ClogTlog.testDuration=250.0.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/ClogTlog.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle, ClogTlog. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/ClogTlog.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/ClogUnclog.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/ClogUnclog.toml

- **Purpose:** Rare simulation test specification for the `ClogUnclog` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 51 lines, 969 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 4 test block(s), titles CloggedCycleTest, UncloggedCycleTest, CloggedCycleTest, UncloggedCycleTest, workloads Cycle(4), RandomClogging(4), top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 4 `[[test]]` block(s) (CloggedCycleTest, UncloggedCycleTest, CloggedCycleTest, UncloggedCycleTest) and schedules each block's workload list (CloggedCycleTest:3, UncloggedCycleTest:1, CloggedCycleTest:3, UncloggedCycleTest:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle(4), RandomClogging(4). Top-level keys: none. Configuration/test knobs: CloggedCycleTest/Cycle.testDuration=5.0, CloggedCycleTest/Cycle.transactionsPerSecond=5000.0, CloggedCycleTest/RandomClogging.testDuration=5.0, CloggedCycleTest/RandomClogging.testDuration=5.0, UncloggedCycleTest/Cycle.testDuration=5.0, UncloggedCycleTest/Cycle.transactionsPerSecond=5000.0, CloggedCycleTest/Cycle.testDuration=5.0, CloggedCycleTest/Cycle.transactionsPerSecond=5000.0, CloggedCycleTest/RandomClogging.testDuration=5.0, CloggedCycleTest/RandomClogging.testDuration=5.0, UncloggedCycleTest/Cycle.testDuration=5.0, UncloggedCycleTest/Cycle.transactionsPerSecond=5000.0.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/ClogUnclog.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle(4), RandomClogging(4). Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/ClogUnclog.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/CloggedCycleWithKills.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/CloggedCycleWithKills.toml

- **Purpose:** Rare simulation test specification for the `CloggedCycleWithKills` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 25 lines, 552 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles CloggedCycleTestWithKills, workloads RandomClogging(2), Cycle, Attrition, top-level keys testPriority.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (CloggedCycleTestWithKills) and schedules each block's workload list (CloggedCycleTestWithKills:4). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: RandomClogging(2), Cycle, Attrition. Top-level keys: testPriority. Configuration/test knobs: CloggedCycleTestWithKills/Cycle.testDuration=30.0, CloggedCycleTestWithKills/Cycle.transactionsPerSecond=5000.0, CloggedCycleTestWithKills/RandomClogging.testDuration=30.0, CloggedCycleTestWithKills/RandomClogging.testDuration=30.0, CloggedCycleTestWithKills/Attrition.testDuration=30.0.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/CloggedCycleWithKills.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for RandomClogging(2), Cycle, Attrition. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/CloggedCycleWithKills.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/ConflictRangeCheck.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/ConflictRangeCheck.toml

- **Purpose:** Rare simulation test specification for the `ConflictRangeCheck` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 9 lines, 173 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles RandomReadWriteTest, workloads ConflictRange, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (RandomReadWriteTest) and schedules each block's workload list (RandomReadWriteTest:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: ConflictRange. Top-level keys: configuration. Configuration/test knobs: buggify=False.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/ConflictRangeCheck.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for ConflictRange. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/ConflictRangeCheck.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/ConflictRangeRYOWCheck.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/ConflictRangeRYOWCheck.toml

- **Purpose:** Rare simulation test specification for the `ConflictRangeRYOWCheck` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 10 lines, 203 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles RandomReadWriteTest, workloads ConflictRange, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (RandomReadWriteTest) and schedules each block's workload list (RandomReadWriteTest:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: ConflictRange. Top-level keys: configuration. Configuration/test knobs: buggify=False.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/ConflictRangeRYOWCheck.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for ConflictRange. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/ConflictRangeRYOWCheck.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/CycleRollbackClogged.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/CycleRollbackClogged.toml

- **Purpose:** Rare simulation test specification for the `CycleRollbackClogged` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 30 lines, 636 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles RollbackCycleTest, workloads RandomClogging(2), Cycle, Rollback, Attrition, top-level keys testPriority.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (RollbackCycleTest) and schedules each block's workload list (RollbackCycleTest:5). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: RandomClogging(2), Cycle, Rollback, Attrition. Top-level keys: testPriority. Configuration/test knobs: RollbackCycleTest/Cycle.testDuration=30.0, RollbackCycleTest/Cycle.transactionsPerSecond=2500.0, RollbackCycleTest/Rollback.testDuration=30.0, RollbackCycleTest/Rollback.meanDelay=10, RollbackCycleTest/RandomClogging.testDuration=30.0, RollbackCycleTest/RandomClogging.testDuration=30.0, RollbackCycleTest/Attrition.testDuration=30.0.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/CycleRollbackClogged.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for RandomClogging(2), Cycle, Rollback, Attrition. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/CycleRollbackClogged.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/CycleWithDeadHall.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/CycleWithDeadHall.toml

- **Purpose:** Rare simulation test specification for the `CycleWithDeadHall` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 57 lines, 1982 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles Two out of Three Data Halls, workloads Attrition(2), Cycle, ChangeConfig, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (Two out of Three Data Halls) and schedules each block's workload list (Two out of Three Data Halls:4). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Attrition(2), Cycle, ChangeConfig. Top-level keys: configuration. Configuration/test knobs: config='three_data_hall', datacenters=3, generateFearless=False, Two out of Three Data Halls/Cycle.testDuration=30.0, Two out of Three Data Halls/Cycle.transactionsPerSecond=2500.0, Two out of Three Data Halls/Attrition.testDuration=0, Two out of Three Data Halls/Attrition.machinesToKill=1, Two out of Three Data Halls/Attrition.testDuration=30.0, Two out of Three Data Halls/Attrition.machinesToKill=300.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/CycleWithDeadHall.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Attrition(2), Cycle, ChangeConfig. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/CycleWithDeadHall.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/CycleWithKills.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/CycleWithKills.toml

- **Purpose:** Rare simulation test specification for the `CycleWithKills` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 15 lines, 350 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles CycleTestWithKills, workloads Cycle, Attrition, top-level keys testPriority.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (CycleTestWithKills) and schedules each block's workload list (CycleTestWithKills:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle, Attrition. Top-level keys: testPriority. Configuration/test knobs: CycleTestWithKills/Cycle.testDuration=30.0, CycleTestWithKills/Cycle.transactionsPerSecond=2500.0, CycleTestWithKills/Attrition.testDuration=30.0.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/CycleWithKills.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle, Attrition. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/CycleWithKills.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/DataDistributionMetrics.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/DataDistributionMetrics.toml

- **Purpose:** Rare simulation test specification for the `DataDistributionMetrics` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 8 lines, 148 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles DataDistributionMetricsTest, workloads DataDistributionMetrics, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (DataDistributionMetricsTest) and schedules each block's workload list (DataDistributionMetricsTest:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: DataDistributionMetrics. Top-level keys: configuration. Configuration/test knobs: buggify=False.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/DataDistributionMetrics.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for DataDistributionMetrics. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/DataDistributionMetrics.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/DcLag.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/DcLag.toml

- **Purpose:** Rare simulation test specification for the `DcLag` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 18 lines, 329 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles DcLag, workloads Cycle, DcLag, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (DcLag) and schedules each block's workload list (DcLag:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle, DcLag. Top-level keys: configuration. Configuration/test knobs: generateFearless=True, processesPerMachine=1, machineCount=20, minimumRegions=2, DcLag/Cycle.testDuration=200.0, DcLag/Cycle.transactionsPerSecond=250.0, DcLag/Cycle.nodeCount=3000, DcLag/DcLag.testDuration=1000.0.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/DcLag.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle, DcLag. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/DcLag.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/FailoverWithSSLag.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/FailoverWithSSLag.toml

- **Purpose:** Rare simulation test specification for the `FailoverWithSSLag` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 18 lines, 361 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles FailoverWithSSLag, workloads Cycle, FailoverWithSSLagWorkload, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (FailoverWithSSLag) and schedules each block's workload list (FailoverWithSSLag:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle, FailoverWithSSLagWorkload. Top-level keys: configuration. Configuration/test knobs: generateFearless=True, processesPerMachine=1, machineCount=20, minimumRegions=2, FailoverWithSSLag/Cycle.testDuration=200.0, FailoverWithSSLag/Cycle.transactionsPerSecond=250.0, FailoverWithSSLag/Cycle.nodeCount=3000, FailoverWithSSLag/FailoverWithSSLagWorkload.testDuration=1000.0.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/FailoverWithSSLag.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle, FailoverWithSSLagWorkload. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/FailoverWithSSLag.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/HighContentionPrefixAllocator.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/HighContentionPrefixAllocator.toml

- **Purpose:** Rare simulation test specification for the `HighContentionPrefixAllocator` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 5 lines, 123 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles HighContentionPrefixAllocator, workloads HighContentionPrefixAllocator, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (HighContentionPrefixAllocator) and schedules each block's workload list (HighContentionPrefixAllocator:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: HighContentionPrefixAllocator. Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/HighContentionPrefixAllocator.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for HighContentionPrefixAllocator. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/HighContentionPrefixAllocator.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/InventoryTestHeavyWrites.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/InventoryTestHeavyWrites.toml

- **Purpose:** Rare simulation test specification for the `InventoryTestHeavyWrites` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 12 lines, 327 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles InventoryTestHeavyWrites, workloads InventoryTest, top-level keys testPriority.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (InventoryTestHeavyWrites) and schedules each block's workload list (InventoryTestHeavyWrites:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: InventoryTest. Top-level keys: testPriority. Configuration/test knobs: InventoryTestHeavyWrites/InventoryTest.testDuration=10.0, InventoryTestHeavyWrites/InventoryTest.transactionsPerSecond=10000.0.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/InventoryTestHeavyWrites.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for InventoryTest. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/InventoryTestHeavyWrites.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/LargeApiCorrectness.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/LargeApiCorrectness.toml

- **Purpose:** Rare simulation test specification for the `LargeApiCorrectness` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 26 lines, 610 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles ApiCorrectnessTest, workloads ApiCorrectness, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (ApiCorrectnessTest) and schedules each block's workload list (ApiCorrectnessTest:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: ApiCorrectness. Top-level keys: none. Configuration/test knobs: ApiCorrectnessTest.runSetup=True.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/LargeApiCorrectness.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for ApiCorrectness. Clear-after-test modes: ApiCorrectnessTest:True. Timeouts: ApiCorrectnessTest:2100.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/LargeApiCorrectness.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/LargeApiCorrectnessStatus.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/LargeApiCorrectnessStatus.toml

- **Purpose:** Rare simulation test specification for the `LargeApiCorrectnessStatus` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 30 lines, 681 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles ApiCorrectnessTest, workloads ApiCorrectness, Status, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (ApiCorrectnessTest) and schedules each block's workload list (ApiCorrectnessTest:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: ApiCorrectness, Status. Top-level keys: none. Configuration/test knobs: ApiCorrectnessTest.runSetup=True, ApiCorrectnessTest/Status.testDuration=30.0.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/LargeApiCorrectnessStatus.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for ApiCorrectness, Status. Clear-after-test modes: ApiCorrectnessTest:True. Timeouts: ApiCorrectnessTest:2100.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/LargeApiCorrectnessStatus.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/PerpetualWiggleStorageMigration.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/PerpetualWiggleStorageMigration.toml

- **Purpose:** Rare simulation test specification for the `PerpetualWiggleStorageMigration` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 18 lines, 414 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles PerpetualWiggleStorageMigration, workloads PerpetualWiggleStorageMigrationWorkload, top-level keys configuration, testPriority.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (PerpetualWiggleStorageMigration) and schedules each block's workload list (PerpetualWiggleStorageMigration:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Storage-engine-focused workloads stress on-disk or checkpoint representations in the simulated/noSim environment.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: PerpetualWiggleStorageMigrationWorkload. Top-level keys: configuration, testPriority. Configuration/test knobs: config='triple', storageEngineType=0, processesPerMachine=2, coordinators=3, machineCount=45, asanMachineCount=20.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/PerpetualWiggleStorageMigration.toml` through the Python TestRunner/CTest path.
- **Risks:** Storage-engine tests are sensitive to engine selection/exclusion knobs and checkpoint determinism.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for PerpetualWiggleStorageMigrationWorkload. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/PerpetualWiggleStorageMigration.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/RYWDisable.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/RYWDisable.toml

- **Purpose:** Rare simulation test specification for the `RYWDisable` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 9 lines, 218 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles RYWDisableTest, workloads RYWDisable, top-level keys testPriority.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (RYWDisableTest) and schedules each block's workload list (RYWDisableTest:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: RYWDisable. Top-level keys: testPriority. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/RYWDisable.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for RYWDisable. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/RYWDisable.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/RandomReadWriteTest.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/RandomReadWriteTest.toml

- **Purpose:** Rare simulation test specification for the `RandomReadWriteTest` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 7 lines, 152 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles RandomReadWriteTest, workloads ReadWrite, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (RandomReadWriteTest) and schedules each block's workload list (RandomReadWriteTest:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: ReadWrite. Top-level keys: none. Configuration/test knobs: RandomReadWriteTest/ReadWrite.testDuration=30.0, RandomReadWriteTest/ReadWrite.transactionsPerSecond=1000.0.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/RandomReadWriteTest.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for ReadWrite. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/RandomReadWriteTest.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/ReadSkewReadWrite.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/ReadSkewReadWrite.toml

- **Purpose:** Rare simulation test specification for the `ReadSkewReadWrite` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 24 lines, 558 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles SkewedReadWriteTest, workloads SkewedReadWrite, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (SkewedReadWriteTest) and schedules each block's workload list (SkewedReadWriteTest:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: SkewedReadWrite. Top-level keys: none. Configuration/test knobs: SkewedReadWriteTest.runSetup=True, SkewedReadWriteTest/SkewedReadWrite.testDuration=40.0, SkewedReadWriteTest/SkewedReadWrite.transactionsPerSecond=100, SkewedReadWriteTest/SkewedReadWrite.nodeCount=3000.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/ReadSkewReadWrite.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for SkewedReadWrite. Clear-after-test modes: SkewedReadWriteTest:True. Timeouts: SkewedReadWriteTest:3600.0.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/ReadSkewReadWrite.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/RedwoodCorrectnessBTree.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/RedwoodCorrectnessBTree.toml

- **Purpose:** Rare simulation test specification for the `RedwoodCorrectnessBTree` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 11 lines, 257 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles UnitTests, workloads UnitTests, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (UnitTests) and schedules each block's workload list (UnitTests:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Storage-engine-focused workloads stress on-disk or checkpoint representations in the simulated/noSim environment.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: UnitTests. Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/RedwoodCorrectnessBTree.toml` through the Python TestRunner/CTest path.
- **Risks:** Storage-engine tests are sensitive to engine selection/exclusion knobs and checkpoint determinism.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for UnitTests. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/RedwoodCorrectnessBTree.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/RedwoodDeltaTree.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/RedwoodDeltaTree.toml

- **Purpose:** Rare simulation test specification for the `RedwoodDeltaTree` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 21 lines, 549 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 2 test block(s), titles RedwoodDeltaTree, RedwoodRecordRef, workloads UnitTests(2), top-level keys testPriority.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 2 `[[test]]` block(s) (RedwoodDeltaTree, RedwoodRecordRef) and schedules each block's workload list (RedwoodDeltaTree:1, RedwoodRecordRef:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Storage-engine-focused workloads stress on-disk or checkpoint representations in the simulated/noSim environment.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: UnitTests(2). Top-level keys: testPriority. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/RedwoodDeltaTree.toml` through the Python TestRunner/CTest path.
- **Risks:** Storage-engine tests are sensitive to engine selection/exclusion knobs and checkpoint determinism.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for UnitTests(2). Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/RedwoodDeltaTree.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/RestoreMultiRanges.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/RestoreMultiRanges.toml

- **Purpose:** Rare simulation test specification for the `RestoreMultiRanges` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 14 lines, 303 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles RestoreMultiRanges, workloads RestoreMultiRanges, top-level keys configuration, testPriority.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (RestoreMultiRanges) and schedules each block's workload list (RestoreMultiRanges:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Backup-oriented workloads add simulated backup agent and restore state that must survive fault injection long enough for correctness validation.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: RestoreMultiRanges. Top-level keys: configuration, testPriority. Configuration/test knobs: RestoreMultiRanges.simBackupAgents='BackupToFile'.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/RestoreMultiRanges.toml` through the Python TestRunner/CTest path.
- **Risks:** Backup/restore specs depend on simulated backup-agent mode, timing, and range selection; timing drift can mask restore validation failures.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for RestoreMultiRanges. Clear-after-test modes: RestoreMultiRanges:True. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/RestoreMultiRanges.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/SpecificUnitTests.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/SpecificUnitTests.toml

- **Purpose:** Rare simulation test specification for the `SpecificUnitTests` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 15 lines, 323 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles UnitTests, workloads UnitTests, top-level keys knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (UnitTests) and schedules each block's workload list (UnitTests:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: UnitTests. Top-level keys: knobs. Configuration/test knobs: UnitTests.runSetup=False.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/SpecificUnitTests.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for UnitTests. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/SpecificUnitTests.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/StatusBuilderPerf.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/StatusBuilderPerf.toml

- **Purpose:** Rare simulation test specification for the `StatusBuilderPerf` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 13 lines, 316 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles StatusBuilderPerf, workloads UnitTests, top-level keys testPriority.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (StatusBuilderPerf) and schedules each block's workload list (StatusBuilderPerf:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: UnitTests. Top-level keys: testPriority. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/StatusBuilderPerf.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for UnitTests. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/StatusBuilderPerf.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/SwizzledLargeApiCorrectness.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/SwizzledLargeApiCorrectness.toml

- **Purpose:** Rare simulation test specification for the `SwizzledLargeApiCorrectness` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 53 lines, 1115 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles ApiCorrectnessTest, workloads Attrition(3), ApiCorrectness, RandomClogging, Rollback, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (ApiCorrectnessTest) and schedules each block's workload list (ApiCorrectnessTest:6). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Attrition(3), ApiCorrectness, RandomClogging, Rollback. Top-level keys: none. Configuration/test knobs: ApiCorrectnessTest.runSetup=True, ApiCorrectnessTest/RandomClogging.testDuration=120.0, ApiCorrectnessTest/Rollback.testDuration=120.0, ApiCorrectnessTest/Rollback.meanDelay=10.0, ApiCorrectnessTest/Attrition.testDuration=120.0, ApiCorrectnessTest/Attrition.testDuration=120.0, ApiCorrectnessTest/Attrition.machinesToKill=10, ApiCorrectnessTest/Attrition.machinesToLeave=3, ApiCorrectnessTest/Attrition.testDuration=120.0, ApiCorrectnessTest/Attrition.machinesToKill=10, ApiCorrectnessTest/Attrition.machinesToLeave=3.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/SwizzledLargeApiCorrectness.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Attrition(3), ApiCorrectness, RandomClogging, Rollback. Clear-after-test modes: ApiCorrectnessTest:True. Timeouts: ApiCorrectnessTest:2100.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/SwizzledLargeApiCorrectness.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/TLogVersionMessagesOverheadFactor.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/TLogVersionMessagesOverheadFactor.toml

- **Purpose:** Rare simulation test specification for the `TLogVersionMessagesOverheadFactor` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 12 lines, 338 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles TLogVersionMessagesOverheadFactor, workloads UnitTests, top-level keys testPriority.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (TLogVersionMessagesOverheadFactor) and schedules each block's workload list (TLogVersionMessagesOverheadFactor:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: UnitTests. Top-level keys: testPriority. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/TLogVersionMessagesOverheadFactor.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for UnitTests. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/TLogVersionMessagesOverheadFactor.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/Throttling.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/Throttling.toml

- **Purpose:** Rare simulation test specification for the `Throttling` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 17 lines, 418 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles ThrottlingTest, workloads Throttling, HealthMetricsApi, top-level keys testPriority.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (ThrottlingTest) and schedules each block's workload list (ThrottlingTest:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Throttling, HealthMetricsApi. Top-level keys: testPriority. Configuration/test knobs: ThrottlingTest/Throttling.testDuration=60.0.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/Throttling.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Throttling, HealthMetricsApi. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/Throttling.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/TransactionCost.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/TransactionCost.toml

- **Purpose:** Rare simulation test specification for the `TransactionCost` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 10 lines, 250 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles TransactionCostTest, workloads TransactionCost, top-level keys testPriority.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (TransactionCostTest) and schedules each block's workload list (TransactionCostTest:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: TransactionCost. Top-level keys: testPriority. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/TransactionCost.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for TransactionCost. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/TransactionCost.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/TransactionTagApiCorrectness.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/TransactionTagApiCorrectness.toml

- **Purpose:** Rare simulation test specification for the `TransactionTagApiCorrectness` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 29 lines, 664 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles TransactionTagWithApiCorrectness, workloads ApiCorrectness, TagThrottleApi, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (TransactionTagWithApiCorrectness) and schedules each block's workload list (TransactionTagWithApiCorrectness:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: ApiCorrectness, TagThrottleApi. Top-level keys: none. Configuration/test knobs: TransactionTagWithApiCorrectness.runSetup=True, TransactionTagWithApiCorrectness/TagThrottleApi.testDuration=120.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/TransactionTagApiCorrectness.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for ApiCorrectness, TagThrottleApi. Clear-after-test modes: TransactionTagWithApiCorrectness:True. Timeouts: TransactionTagWithApiCorrectness:2100.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/TransactionTagApiCorrectness.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/TransactionTagSwizzledApiCorrectness.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/TransactionTagSwizzledApiCorrectness.toml

- **Purpose:** Rare simulation test specification for the `TransactionTagSwizzledApiCorrectness` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 57 lines, 1224 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles TransactionTagWithSwizzledApiCorrectnessTest, workloads Attrition(3), ApiCorrectness, TagThrottleApi, RandomClogging, Rollback, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (TransactionTagWithSwizzledApiCorrectnessTest) and schedules each block's workload list (TransactionTagWithSwizzledApiCorrectnessTest:7). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Attrition(3), ApiCorrectness, TagThrottleApi, RandomClogging, Rollback. Top-level keys: none. Configuration/test knobs: TransactionTagWithSwizzledApiCorrectnessTest.runSetup=True, TransactionTagWithSwizzledApiCorrectnessTest/TagThrottleApi.testDuration=120, TransactionTagWithSwizzledApiCorrectnessTest/RandomClogging.testDuration=120.0, TransactionTagWithSwizzledApiCorrectnessTest/Rollback.testDuration=120.0, TransactionTagWithSwizzledApiCorrectnessTest/Rollback.meanDelay=10.0, TransactionTagWithSwizzledApiCorrectnessTest/Attrition.testDuration=120.0, TransactionTagWithSwizzledApiCorrectnessTest/Attrition.testDuration=120.0, TransactionTagWithSwizzledApiCorrectnessTest/Attrition.machinesToKill=10, TransactionTagWithSwizzledApiCorrectnessTest/Attrition.machinesToLeave=3, TransactionTagWithSwizzledApiCorrectnessTest/Attrition.testDuration=120.0, TransactionTagWithSwizzledApiCorrectnessTest/Attrition.machinesToKill=10, TransactionTagWithSwizzledApiCorrectnessTest/Attrition.machinesToLeave=3.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/TransactionTagSwizzledApiCorrectness.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Attrition(3), ApiCorrectness, TagThrottleApi, RandomClogging, Rollback. Clear-after-test modes: TransactionTagWithSwizzledApiCorrectnessTest:True. Timeouts: TransactionTagWithSwizzledApiCorrectnessTest:2100.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/TransactionTagSwizzledApiCorrectness.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/WriteTagThrottling.toml -->
# Research: sources/storage-engines/foundationdb/tests/rare/WriteTagThrottling.toml

- **Purpose:** Rare simulation test specification for the `WriteTagThrottling` scenario. It keeps broader, heavier, or less frequently scheduled workloads in the simulation suite.
- **Source facts:** 39 lines, 815 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 2 test block(s), titles withoutWriteThrottling, withWriteThrottling, workloads WriteTagThrottling(2), HealthMetricsApi(2), top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 2 `[[test]]` block(s) (withoutWriteThrottling, withWriteThrottling) and schedules each block's workload list (withoutWriteThrottling:2, withWriteThrottling:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: WriteTagThrottling(2), HealthMetricsApi(2). Top-level keys: none. Configuration/test knobs: none.
- **Integration points:** Integrated by suite location `rare` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/rare/WriteTagThrottling.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for WriteTagThrottling(2), HealthMetricsApi(2). Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/rare/WriteTagThrottling.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.2.0_until_7.3.0/ConfigureStorageMigrationTestRestart-1.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.2.0_until_7.3.0/ConfigureStorageMigrationTestRestart-1.toml

- **Purpose:** Restarting simulation stage for `ConfigureStorageMigrationTestRestart-1`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 29 lines, 639 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles CloggedConfigureDatabaseTest, workloads RandomClogging(2), ConfigureDatabase, SaveAndKill, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (CloggedConfigureDatabaseTest) and schedules each block's workload list (CloggedConfigureDatabaseTest:4). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts. Storage-engine-focused workloads stress on-disk or checkpoint representations in the simulated/noSim environment.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: RandomClogging(2), ConfigureDatabase, SaveAndKill. Top-level keys: configuration. Configuration/test knobs: extraMachineCountDC=2, encryptModes=['disabled'], tenantModes=['disabled'], CloggedConfigureDatabaseTest/ConfigureDatabase.testDuration=30.0, CloggedConfigureDatabaseTest/RandomClogging.testDuration=30.0, CloggedConfigureDatabaseTest/RandomClogging.testDuration=30.0, CloggedConfigureDatabaseTest/SaveAndKill.testDuration=30.0, CloggedConfigureDatabaseTest/SaveAndKill.restartInfoLocation='simfdb/restartInfo.ini'.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.2.0_until_7.3.0/ConfigureStorageMigrationTestRestart-1.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection. Storage-engine tests are sensitive to engine selection/exclusion knobs and checkpoint determinism.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for RandomClogging(2), ConfigureDatabase, SaveAndKill. Clear-after-test modes: CloggedConfigureDatabaseTest:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.2.0_until_7.3.0/ConfigureStorageMigrationTestRestart-1.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.2.0_until_7.3.0/ConfigureStorageMigrationTestRestart-2.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.2.0_until_7.3.0/ConfigureStorageMigrationTestRestart-2.toml

- **Purpose:** Restarting simulation stage for `ConfigureStorageMigrationTestRestart-2`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 23 lines, 488 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles CloggedConfigureDatabaseTest, workloads RandomClogging(2), ConfigureDatabase, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (CloggedConfigureDatabaseTest) and schedules each block's workload list (CloggedConfigureDatabaseTest:3). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts. Storage-engine-focused workloads stress on-disk or checkpoint representations in the simulated/noSim environment.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: RandomClogging(2), ConfigureDatabase. Top-level keys: configuration. Configuration/test knobs: extraMachineCountDC=2, CloggedConfigureDatabaseTest.runSetup=False, CloggedConfigureDatabaseTest/ConfigureDatabase.testDuration=300.0, CloggedConfigureDatabaseTest/RandomClogging.testDuration=300.0, CloggedConfigureDatabaseTest/RandomClogging.testDuration=300.0.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.2.0_until_7.3.0/ConfigureStorageMigrationTestRestart-2.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection. Storage-engine tests are sensitive to engine selection/exclusion knobs and checkpoint determinism.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for RandomClogging(2), ConfigureDatabase. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.2.0_until_7.3.0/ConfigureStorageMigrationTestRestart-2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.2.0_until_7.3.0/ConfigureTestRestart-1.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.2.0_until_7.3.0/ConfigureTestRestart-1.toml

- **Purpose:** Restarting simulation stage for `ConfigureTestRestart-1`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 27 lines, 557 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles CloggedConfigureDatabaseTest, workloads RandomClogging(2), ConfigureDatabase, SaveAndKill, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (CloggedConfigureDatabaseTest) and schedules each block's workload list (CloggedConfigureDatabaseTest:4). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: RandomClogging(2), ConfigureDatabase, SaveAndKill. Top-level keys: configuration. Configuration/test knobs: encryptModes=['disabled'], tenantModes=['disabled'], CloggedConfigureDatabaseTest/ConfigureDatabase.testDuration=30.0, CloggedConfigureDatabaseTest/RandomClogging.testDuration=30.0, CloggedConfigureDatabaseTest/RandomClogging.testDuration=30.0, CloggedConfigureDatabaseTest/SaveAndKill.testDuration=30.0, CloggedConfigureDatabaseTest/SaveAndKill.restartInfoLocation='simfdb/restartInfo.ini'.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.2.0_until_7.3.0/ConfigureTestRestart-1.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for RandomClogging(2), ConfigureDatabase, SaveAndKill. Clear-after-test modes: CloggedConfigureDatabaseTest:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.2.0_until_7.3.0/ConfigureTestRestart-1.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.2.0_until_7.3.0/ConfigureTestRestart-2.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.2.0_until_7.3.0/ConfigureTestRestart-2.toml

- **Purpose:** Restarting simulation stage for `ConfigureTestRestart-2`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 21 lines, 404 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles CloggedConfigureDatabaseTest, workloads RandomClogging(2), ConfigureDatabase, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (CloggedConfigureDatabaseTest) and schedules each block's workload list (CloggedConfigureDatabaseTest:3). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: RandomClogging(2), ConfigureDatabase. Top-level keys: configuration. Configuration/test knobs: randomlyRenameZoneId=True, CloggedConfigureDatabaseTest.runSetup=False, CloggedConfigureDatabaseTest/ConfigureDatabase.testDuration=300.0, CloggedConfigureDatabaseTest/RandomClogging.testDuration=300.0, CloggedConfigureDatabaseTest/RandomClogging.testDuration=300.0.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.2.0_until_7.3.0/ConfigureTestRestart-2.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for RandomClogging(2), ConfigureDatabase. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.2.0_until_7.3.0/ConfigureTestRestart-2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.2.0_until_7.3.0/DrUpgradeRestart-1.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.2.0_until_7.3.0/DrUpgradeRestart-1.toml

- **Purpose:** Restarting simulation stage for `DrUpgradeRestart-1`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 26 lines, 582 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles DrUpgrade, workloads Cycle, BackupToDBUpgrade, SaveAndKill, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (DrUpgrade) and schedules each block's workload list (DrUpgrade:3). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle, BackupToDBUpgrade, SaveAndKill. Top-level keys: configuration. Configuration/test knobs: extraDatabaseMode='Local', encryptModes=['disabled'], tenantModes=['disabled'], DrUpgrade.simBackupAgents='BackupToDB', DrUpgrade/Cycle.testDuration=30.0, DrUpgrade/Cycle.transactionsPerSecond=1000.0, DrUpgrade/Cycle.nodeCount=30000, DrUpgrade/BackupToDBUpgrade.backupAfter=10.0, DrUpgrade/SaveAndKill.testDuration=40.0, DrUpgrade/SaveAndKill.restartInfoLocation='simfdb/restartInfo.ini'.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.2.0_until_7.3.0/DrUpgradeRestart-1.toml` through the Python TestRunner/CTest path.
- **Risks:** Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle, BackupToDBUpgrade, SaveAndKill. Clear-after-test modes: DrUpgrade:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.2.0_until_7.3.0/DrUpgradeRestart-1.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.2.0_until_7.3.0/DrUpgradeRestart-2.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.2.0_until_7.3.0/DrUpgradeRestart-2.toml

- **Purpose:** Restarting simulation stage for `DrUpgradeRestart-2`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 21 lines, 448 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles DrUpgrade, workloads Cycle, BackupToDBUpgrade, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (DrUpgrade) and schedules each block's workload list (DrUpgrade:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle, BackupToDBUpgrade. Top-level keys: configuration. Configuration/test knobs: extraDatabaseMode='Local', DrUpgrade.simBackupAgents='BackupToDB', DrUpgrade.runSetup=False, DrUpgrade/Cycle.testDuration=30.0, DrUpgrade/Cycle.transactionsPerSecond=1000.0, DrUpgrade/Cycle.nodeCount=30000, DrUpgrade/BackupToDBUpgrade.backupAfter=10.0.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.2.0_until_7.3.0/DrUpgradeRestart-2.toml` through the Python TestRunner/CTest path.
- **Risks:** Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle, BackupToDBUpgrade. Clear-after-test modes: DrUpgrade:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.2.0_until_7.3.0/DrUpgradeRestart-2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.2.4_until_7.3.0/UpgradeAndBackupRestore-1.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.2.4_until_7.3.0/UpgradeAndBackupRestore-1.toml

- **Purpose:** Restarting simulation stage for `UpgradeAndBackupRestore-1`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 68 lines, 1435 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 3 test block(s), titles SubmitBackup, FirstCycleTest, SaveDatabase, workloads Attrition(3), SubmitBackup, Cycle, RandomClogging, Rollback, SaveAndKill, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 3 `[[test]]` block(s) (SubmitBackup, FirstCycleTest, SaveDatabase) and schedules each block's workload list (SubmitBackup:2, FirstCycleTest:5, SaveDatabase:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts. Backup-oriented workloads add simulated backup agent and restore state that must survive fault injection long enough for correctness validation.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Attrition(3), SubmitBackup, Cycle, RandomClogging, Rollback, SaveAndKill. Top-level keys: configuration. Configuration/test knobs: storageEngineExcludeTypes=[3], encryptModes=['disabled'], tenantModes=['disabled'], SubmitBackup.simBackupAgents='BackupToFile', SubmitBackup.disabledFailureInjectionWorkloads='Attrition', SubmitBackup.runConsistencyCheck=False, SubmitBackup/Attrition.testDuration=30.0, SubmitBackup/Attrition.machinesToKill=10, SubmitBackup/Attrition.machinesToLeave=3, FirstCycleTest.disabledFailureInjectionWorkloads='Attrition', FirstCycleTest.runConsistencyCheck=False, FirstCycleTest/Cycle.testDuration=30.0, FirstCycleTest/Cycle.transactionsPerSecond=2500.0, FirstCycleTest/Cycle.nodeCount=30000, FirstCycleTest/Cycle.keyPrefix='BeforeRestart', FirstCycleTest/RandomClogging.testDuration=90.0, FirstCycleTest/Rollback.testDuration=90.0, FirstCycleTest/Rollback.meanDelay=90.0, FirstCycleTest/Attrition.testDuration=90.0, FirstCycleTest/Attrition.machinesToKill=10, FirstCycleTest/Attrition.machinesToLeave=3, FirstCycleTest/Attrition.testDuration=90.0; plus 4 more.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.2.4_until_7.3.0/UpgradeAndBackupRestore-1.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection. Backup/restore specs depend on simulated backup-agent mode, timing, and range selection; timing drift can mask restore validation failures.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Attrition(3), SubmitBackup, Cycle, RandomClogging, Rollback, SaveAndKill. Clear-after-test modes: SubmitBackup:False, FirstCycleTest:False, SaveDatabase:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.2.4_until_7.3.0/UpgradeAndBackupRestore-1.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.2.4_until_7.3.0/UpgradeAndBackupRestore-2.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.2.4_until_7.3.0/UpgradeAndBackupRestore-2.toml

- **Purpose:** Restarting simulation stage for `UpgradeAndBackupRestore-2`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 58 lines, 1155 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 3 test block(s), titles SecondCycleTest, RestoreBackup, CheckCycles, workloads Cycle(3), Attrition(2), RandomClogging, Rollback, RestoreBackup, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 3 `[[test]]` block(s) (SecondCycleTest, RestoreBackup, CheckCycles) and schedules each block's workload list (SecondCycleTest:5, RestoreBackup:1, CheckCycles:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts. Backup-oriented workloads add simulated backup agent and restore state that must survive fault injection long enough for correctness validation.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle(3), Attrition(2), RandomClogging, Rollback, RestoreBackup. Top-level keys: none. Configuration/test knobs: SecondCycleTest.simBackupAgents='BackupToFile', SecondCycleTest.runConsistencyCheck=False, SecondCycleTest/Cycle.testDuration=30.0, SecondCycleTest/Cycle.transactionsPerSecond=2500.0, SecondCycleTest/Cycle.nodeCount=30000, SecondCycleTest/Cycle.keyPrefix='AfterRestart', SecondCycleTest/RandomClogging.testDuration=90.0, SecondCycleTest/Rollback.testDuration=90.0, SecondCycleTest/Rollback.meanDelay=90.0, SecondCycleTest/Attrition.testDuration=90.0, SecondCycleTest/Attrition.machinesToKill=10, SecondCycleTest/Attrition.machinesToLeave=3, SecondCycleTest/Attrition.testDuration=90.0, SecondCycleTest/Attrition.machinesToKill=10, SecondCycleTest/Attrition.machinesToLeave=3, RestoreBackup.simBackupAgents='BackupToFile', CheckCycles/Cycle.nodeCount=30000, CheckCycles/Cycle.keyPrefix='AfterRestart', CheckCycles/Cycle.nodeCount=30000, CheckCycles/Cycle.keyPrefix='BeforeRestart'.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.2.4_until_7.3.0/UpgradeAndBackupRestore-2.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection. Backup/restore specs depend on simulated backup-agent mode, timing, and range selection; timing drift can mask restore validation failures.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle(3), Attrition(2), RandomClogging, Rollback, RestoreBackup. Clear-after-test modes: SecondCycleTest:False, RestoreBackup:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.2.4_until_7.3.0/UpgradeAndBackupRestore-2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/ConfigureStorageMigrationTestRestart-1.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/ConfigureStorageMigrationTestRestart-1.toml

- **Purpose:** Restarting simulation stage for `ConfigureStorageMigrationTestRestart-1`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 30 lines, 667 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles CloggedConfigureDatabaseTest, workloads RandomClogging(2), ConfigureDatabase, SaveAndKill, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (CloggedConfigureDatabaseTest) and schedules each block's workload list (CloggedConfigureDatabaseTest:4). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts. Storage-engine-focused workloads stress on-disk or checkpoint representations in the simulated/noSim environment.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: RandomClogging(2), ConfigureDatabase, SaveAndKill. Top-level keys: configuration. Configuration/test knobs: storageEngineExcludeTypes=[3, 5], extraMachineCountDC=2, encryptModes=['disabled'], tenantModes=['disabled'], CloggedConfigureDatabaseTest/ConfigureDatabase.testDuration=30.0, CloggedConfigureDatabaseTest/RandomClogging.testDuration=30.0, CloggedConfigureDatabaseTest/RandomClogging.testDuration=30.0, CloggedConfigureDatabaseTest/SaveAndKill.testDuration=30.0, CloggedConfigureDatabaseTest/SaveAndKill.restartInfoLocation='simfdb/restartInfo.ini'.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/ConfigureStorageMigrationTestRestart-1.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection. Storage-engine tests are sensitive to engine selection/exclusion knobs and checkpoint determinism.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for RandomClogging(2), ConfigureDatabase, SaveAndKill. Clear-after-test modes: CloggedConfigureDatabaseTest:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/ConfigureStorageMigrationTestRestart-1.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/ConfigureStorageMigrationTestRestart-2.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/ConfigureStorageMigrationTestRestart-2.toml

- **Purpose:** Restarting simulation stage for `ConfigureStorageMigrationTestRestart-2`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 24 lines, 518 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles CloggedConfigureDatabaseTest, workloads RandomClogging(2), ConfigureDatabase, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (CloggedConfigureDatabaseTest) and schedules each block's workload list (CloggedConfigureDatabaseTest:3). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts. Storage-engine-focused workloads stress on-disk or checkpoint representations in the simulated/noSim environment.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: RandomClogging(2), ConfigureDatabase. Top-level keys: configuration. Configuration/test knobs: storageEngineExcludeTypes=[5], extraMachineCountDC=2, CloggedConfigureDatabaseTest.runSetup=False, CloggedConfigureDatabaseTest/ConfigureDatabase.testDuration=300.0, CloggedConfigureDatabaseTest/RandomClogging.testDuration=300.0, CloggedConfigureDatabaseTest/RandomClogging.testDuration=300.0.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/ConfigureStorageMigrationTestRestart-2.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection. Storage-engine tests are sensitive to engine selection/exclusion knobs and checkpoint determinism.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for RandomClogging(2), ConfigureDatabase. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/ConfigureStorageMigrationTestRestart-2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/ConfigureTestRestart-1.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/ConfigureTestRestart-1.toml

- **Purpose:** Restarting simulation stage for `ConfigureTestRestart-1`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 28 lines, 587 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles CloggedConfigureDatabaseTest, workloads RandomClogging(2), ConfigureDatabase, SaveAndKill, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (CloggedConfigureDatabaseTest) and schedules each block's workload list (CloggedConfigureDatabaseTest:4). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: RandomClogging(2), ConfigureDatabase, SaveAndKill. Top-level keys: configuration. Configuration/test knobs: storageEngineExcludeTypes=[3, 5], tenantModes=['disabled'], encryptModes=['disabled'], CloggedConfigureDatabaseTest/ConfigureDatabase.testDuration=30.0, CloggedConfigureDatabaseTest/RandomClogging.testDuration=30.0, CloggedConfigureDatabaseTest/RandomClogging.testDuration=30.0, CloggedConfigureDatabaseTest/SaveAndKill.testDuration=30.0, CloggedConfigureDatabaseTest/SaveAndKill.restartInfoLocation='simfdb/restartInfo.ini'.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/ConfigureTestRestart-1.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for RandomClogging(2), ConfigureDatabase, SaveAndKill. Clear-after-test modes: CloggedConfigureDatabaseTest:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/ConfigureTestRestart-1.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/ConfigureTestRestart-2.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/ConfigureTestRestart-2.toml

- **Purpose:** Restarting simulation stage for `ConfigureTestRestart-2`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 22 lines, 434 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles CloggedConfigureDatabaseTest, workloads RandomClogging(2), ConfigureDatabase, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (CloggedConfigureDatabaseTest) and schedules each block's workload list (CloggedConfigureDatabaseTest:3). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: RandomClogging(2), ConfigureDatabase. Top-level keys: configuration. Configuration/test knobs: storageEngineExcludeTypes=[5], randomlyRenameZoneId=True, CloggedConfigureDatabaseTest.runSetup=False, CloggedConfigureDatabaseTest/ConfigureDatabase.testDuration=300.0, CloggedConfigureDatabaseTest/RandomClogging.testDuration=300.0, CloggedConfigureDatabaseTest/RandomClogging.testDuration=300.0.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/ConfigureTestRestart-2.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for RandomClogging(2), ConfigureDatabase. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/ConfigureTestRestart-2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/DrUpgradeRestart-1.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/DrUpgradeRestart-1.toml

- **Purpose:** Restarting simulation stage for `DrUpgradeRestart-1`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 28 lines, 617 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles DrUpgrade, workloads Cycle, BackupToDBUpgrade, SaveAndKill, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (DrUpgrade) and schedules each block's workload list (DrUpgrade:3). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle, BackupToDBUpgrade, SaveAndKill. Top-level keys: configuration. Configuration/test knobs: extraDatabaseMode='Local', storageEngineExcludeTypes=[3, 4, 5], encryptModes=['disabled'], tenantModes=['disabled'], DrUpgrade.simBackupAgents='BackupToDB', DrUpgrade/Cycle.testDuration=30.0, DrUpgrade/Cycle.transactionsPerSecond=1000.0, DrUpgrade/Cycle.nodeCount=30000, DrUpgrade/BackupToDBUpgrade.backupAfter=10.0, DrUpgrade/SaveAndKill.testDuration=40.0, DrUpgrade/SaveAndKill.restartInfoLocation='simfdb/restartInfo.ini'.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/DrUpgradeRestart-1.toml` through the Python TestRunner/CTest path.
- **Risks:** Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle, BackupToDBUpgrade, SaveAndKill. Clear-after-test modes: DrUpgrade:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/DrUpgradeRestart-1.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/DrUpgradeRestart-2.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/DrUpgradeRestart-2.toml

- **Purpose:** Restarting simulation stage for `DrUpgradeRestart-2`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 22 lines, 480 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles DrUpgrade, workloads Cycle, BackupToDBUpgrade, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (DrUpgrade) and schedules each block's workload list (DrUpgrade:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle, BackupToDBUpgrade. Top-level keys: configuration. Configuration/test knobs: extraDatabaseMode='Local', storageEngineExcludeTypes=[4, 5], DrUpgrade.simBackupAgents='BackupToDB', DrUpgrade.runSetup=False, DrUpgrade/Cycle.testDuration=30.0, DrUpgrade/Cycle.transactionsPerSecond=1000.0, DrUpgrade/Cycle.nodeCount=30000, DrUpgrade/BackupToDBUpgrade.backupAfter=10.0.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/DrUpgradeRestart-2.toml` through the Python TestRunner/CTest path.
- **Risks:** Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle, BackupToDBUpgrade. Clear-after-test modes: DrUpgrade:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/DrUpgradeRestart-2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/StorefrontTestRestart-1.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/StorefrontTestRestart-1.toml

- **Purpose:** Restarting simulation stage for `StorefrontTestRestart-1`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 20 lines, 422 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles StorefrontTest, workloads Storefront, SaveAndKill, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (StorefrontTest) and schedules each block's workload list (StorefrontTest:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Storefront, SaveAndKill. Top-level keys: configuration. Configuration/test knobs: storageEngineExcludeTypes=[3, 5], tenantModes=['disabled'], encryptModes=['disabled'], StorefrontTest/Storefront.transactionsPerSecond=200, StorefrontTest/SaveAndKill.testDuration=10.0, StorefrontTest/SaveAndKill.restartInfoLocation='simfdb/restartInfo.ini'.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/StorefrontTestRestart-1.toml` through the Python TestRunner/CTest path.
- **Risks:** Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Storefront, SaveAndKill. Clear-after-test modes: StorefrontTest:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/StorefrontTestRestart-1.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/StorefrontTestRestart-2.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/StorefrontTestRestart-2.toml

- **Purpose:** Restarting simulation stage for `StorefrontTestRestart-2`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 13 lines, 241 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles StorefrontTest, workloads Storefront, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (StorefrontTest) and schedules each block's workload list (StorefrontTest:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Storefront. Top-level keys: configuration. Configuration/test knobs: storageEngineExcludeTypes=[3, 5], StorefrontTest.runSetup=False, StorefrontTest/Storefront.transactionsPerSecond=200.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/StorefrontTestRestart-2.toml` through the Python TestRunner/CTest path.
- **Risks:** Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Storefront. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/StorefrontTestRestart-2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/UpgradeAndBackupRestore-1.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/UpgradeAndBackupRestore-1.toml

- **Purpose:** Restarting simulation stage for `UpgradeAndBackupRestore-1`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 68 lines, 1431 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 3 test block(s), titles SubmitBackup, FirstCycleTest, SaveDatabase, workloads Attrition(3), SubmitBackup, Cycle, RandomClogging, Rollback, SaveAndKill, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 3 `[[test]]` block(s) (SubmitBackup, FirstCycleTest, SaveDatabase) and schedules each block's workload list (SubmitBackup:2, FirstCycleTest:5, SaveDatabase:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts. Backup-oriented workloads add simulated backup agent and restore state that must survive fault injection long enough for correctness validation.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Attrition(3), SubmitBackup, Cycle, RandomClogging, Rollback, SaveAndKill. Top-level keys: configuration. Configuration/test knobs: storageEngineExcludeTypes=[3, 5], tenantModes=['disabled'], encryptModes=['disabled'], SubmitBackup.simBackupAgents='BackupToFile', SubmitBackup.disabledFailureInjectionWorkloads='Attrition', SubmitBackup.runConsistencyCheck=False, SubmitBackup/Attrition.testDuration=30.0, SubmitBackup/Attrition.machinesToKill=10, SubmitBackup/Attrition.machinesToLeave=3, FirstCycleTest.disabledFailureInjectionWorkloads='Attrition', FirstCycleTest.runConsistencyCheck=False, FirstCycleTest/Cycle.testDuration=30.0, FirstCycleTest/Cycle.transactionsPerSecond=2500.0, FirstCycleTest/Cycle.nodeCount=30000, FirstCycleTest/Cycle.keyPrefix='BeforeRestart', FirstCycleTest/RandomClogging.testDuration=90.0, FirstCycleTest/Rollback.testDuration=90.0, FirstCycleTest/Rollback.meanDelay=90.0, FirstCycleTest/Attrition.testDuration=90.0, FirstCycleTest/Attrition.machinesToKill=10, FirstCycleTest/Attrition.machinesToLeave=3, FirstCycleTest/Attrition.testDuration=90.0; plus 4 more.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/UpgradeAndBackupRestore-1.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection. Backup/restore specs depend on simulated backup-agent mode, timing, and range selection; timing drift can mask restore validation failures.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Attrition(3), SubmitBackup, Cycle, RandomClogging, Rollback, SaveAndKill. Clear-after-test modes: SubmitBackup:False, FirstCycleTest:False, SaveDatabase:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/UpgradeAndBackupRestore-1.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/UpgradeAndBackupRestore-2.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/UpgradeAndBackupRestore-2.toml

- **Purpose:** Restarting simulation stage for `UpgradeAndBackupRestore-2`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 61 lines, 1204 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 3 test block(s), titles SecondCycleTest, RestoreBackup, CheckCycles, workloads Cycle(3), Attrition(2), RandomClogging, Rollback, RestoreBackup, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 3 `[[test]]` block(s) (SecondCycleTest, RestoreBackup, CheckCycles) and schedules each block's workload list (SecondCycleTest:5, RestoreBackup:1, CheckCycles:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts. Backup-oriented workloads add simulated backup agent and restore state that must survive fault injection long enough for correctness validation.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle(3), Attrition(2), RandomClogging, Rollback, RestoreBackup. Top-level keys: configuration. Configuration/test knobs: storageEngineExcludeTypes=[3, 5], SecondCycleTest.simBackupAgents='BackupToFile', SecondCycleTest.runConsistencyCheck=False, SecondCycleTest/Cycle.testDuration=30.0, SecondCycleTest/Cycle.transactionsPerSecond=2500.0, SecondCycleTest/Cycle.nodeCount=30000, SecondCycleTest/Cycle.keyPrefix='AfterRestart', SecondCycleTest/RandomClogging.testDuration=90.0, SecondCycleTest/Rollback.testDuration=90.0, SecondCycleTest/Rollback.meanDelay=90.0, SecondCycleTest/Attrition.testDuration=90.0, SecondCycleTest/Attrition.machinesToKill=10, SecondCycleTest/Attrition.machinesToLeave=3, SecondCycleTest/Attrition.testDuration=90.0, SecondCycleTest/Attrition.machinesToKill=10, SecondCycleTest/Attrition.machinesToLeave=3, RestoreBackup.simBackupAgents='BackupToFile', CheckCycles/Cycle.nodeCount=30000, CheckCycles/Cycle.keyPrefix='AfterRestart', CheckCycles/Cycle.nodeCount=30000, CheckCycles/Cycle.keyPrefix='BeforeRestart'.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/UpgradeAndBackupRestore-2.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection. Backup/restore specs depend on simulated backup-agent mode, timing, and range selection; timing drift can mask restore validation failures.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle(3), Attrition(2), RandomClogging, Rollback, RestoreBackup. Clear-after-test modes: SecondCycleTest:False, RestoreBackup:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/UpgradeAndBackupRestore-2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/VersionVectorDisableRestart-1.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/VersionVectorDisableRestart-1.toml

- **Purpose:** Restarting simulation stage for `VersionVectorDisableRestart-1`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 62 lines, 1271 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles VersionVectorDowngrade, workloads Cycle(3), Attrition(2), RandomClogging, Rollback, SaveAndKill, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (VersionVectorDowngrade) and schedules each block's workload list (VersionVectorDowngrade:8). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle(3), Attrition(2), RandomClogging, Rollback, SaveAndKill. Top-level keys: configuration, knobs. Configuration/test knobs: storageEngineExcludeTypes=[5], tenantModes=['disabled'], encryptModes=['disabled'], VersionVectorDowngrade/Cycle.testDuration=30.0, VersionVectorDowngrade/Cycle.transactionsPerSecond=2500.0, VersionVectorDowngrade/Cycle.nodeCount=1000, VersionVectorDowngrade/Cycle.keyPrefix='cycle', VersionVectorDowngrade/Cycle.testDuration=30.0, VersionVectorDowngrade/Cycle.transactionsPerSecond=2500.0, VersionVectorDowngrade/Cycle.nodeCount=1000, VersionVectorDowngrade/Cycle.keyPrefix='!', VersionVectorDowngrade/Cycle.testDuration=30.0, VersionVectorDowngrade/Cycle.transactionsPerSecond=2500.0, VersionVectorDowngrade/Cycle.nodeCount=1000, VersionVectorDowngrade/Cycle.keyPrefix='ZZZ', VersionVectorDowngrade/RandomClogging.testDuration=10.0, VersionVectorDowngrade/Rollback.testDuration=10.0, VersionVectorDowngrade/Rollback.meanDelay=10.0, VersionVectorDowngrade/Attrition.testDuration=10.0, VersionVectorDowngrade/Attrition.machinesToKill=10, VersionVectorDowngrade/Attrition.machinesToLeave=3, VersionVectorDowngrade/Attrition.testDuration=10.0; plus 4 more.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/VersionVectorDisableRestart-1.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle(3), Attrition(2), RandomClogging, Rollback, SaveAndKill. Clear-after-test modes: VersionVectorDowngrade:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/VersionVectorDisableRestart-1.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/VersionVectorDisableRestart-2.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/VersionVectorDisableRestart-2.toml

- **Purpose:** Restarting simulation stage for `VersionVectorDisableRestart-2`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 54 lines, 1049 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles VersionVectorDowngrade, workloads Cycle(3), Attrition(2), RandomClogging, Rollback, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (VersionVectorDowngrade) and schedules each block's workload list (VersionVectorDowngrade:7). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle(3), Attrition(2), RandomClogging, Rollback. Top-level keys: configuration, knobs. Configuration/test knobs: storageEngineExcludeTypes=[5], VersionVectorDowngrade.runSetup=False, VersionVectorDowngrade/Cycle.testDuration=30.0, VersionVectorDowngrade/Cycle.transactionsPerSecond=2500.0, VersionVectorDowngrade/Cycle.nodeCount=1000, VersionVectorDowngrade/Cycle.keyPrefix='cycle', VersionVectorDowngrade/Cycle.testDuration=30.0, VersionVectorDowngrade/Cycle.transactionsPerSecond=2500.0, VersionVectorDowngrade/Cycle.nodeCount=1000, VersionVectorDowngrade/Cycle.keyPrefix='!', VersionVectorDowngrade/Cycle.testDuration=30.0, VersionVectorDowngrade/Cycle.transactionsPerSecond=2500.0, VersionVectorDowngrade/Cycle.nodeCount=1000, VersionVectorDowngrade/Cycle.keyPrefix='ZZZ', VersionVectorDowngrade/RandomClogging.testDuration=10.0, VersionVectorDowngrade/Rollback.testDuration=10.0, VersionVectorDowngrade/Rollback.meanDelay=10.0, VersionVectorDowngrade/Attrition.testDuration=10.0, VersionVectorDowngrade/Attrition.machinesToKill=10, VersionVectorDowngrade/Attrition.machinesToLeave=3, VersionVectorDowngrade/Attrition.testDuration=60.0, VersionVectorDowngrade/Attrition.machinesToKill=10; plus 1 more.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/VersionVectorDisableRestart-2.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle(3), Attrition(2), RandomClogging, Rollback. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/VersionVectorDisableRestart-2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/VersionVectorEnableRestart-1.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/VersionVectorEnableRestart-1.toml

- **Purpose:** Restarting simulation stage for `VersionVectorEnableRestart-1`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 61 lines, 1227 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles VersionVectorUpgrade, workloads Cycle(3), Attrition(2), RandomClogging, Rollback, SaveAndKill, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (VersionVectorUpgrade) and schedules each block's workload list (VersionVectorUpgrade:8). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle(3), Attrition(2), RandomClogging, Rollback, SaveAndKill. Top-level keys: configuration, knobs. Configuration/test knobs: storageEngineExcludeTypes=[5], tenantModes=['disabled'], encryptModes=['disabled'], VersionVectorUpgrade/Cycle.testDuration=30.0, VersionVectorUpgrade/Cycle.transactionsPerSecond=2500.0, VersionVectorUpgrade/Cycle.nodeCount=1000, VersionVectorUpgrade/Cycle.keyPrefix='cycle', VersionVectorUpgrade/Cycle.testDuration=30.0, VersionVectorUpgrade/Cycle.transactionsPerSecond=2500.0, VersionVectorUpgrade/Cycle.nodeCount=1000, VersionVectorUpgrade/Cycle.keyPrefix='!', VersionVectorUpgrade/Cycle.testDuration=30.0, VersionVectorUpgrade/Cycle.transactionsPerSecond=2500.0, VersionVectorUpgrade/Cycle.nodeCount=1000, VersionVectorUpgrade/Cycle.keyPrefix='ZZZ', VersionVectorUpgrade/RandomClogging.testDuration=10.0, VersionVectorUpgrade/Rollback.testDuration=10.0, VersionVectorUpgrade/Rollback.meanDelay=10.0, VersionVectorUpgrade/Attrition.testDuration=10.0, VersionVectorUpgrade/Attrition.machinesToKill=10, VersionVectorUpgrade/Attrition.machinesToLeave=3, VersionVectorUpgrade/Attrition.testDuration=10.0; plus 4 more.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/VersionVectorEnableRestart-1.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle(3), Attrition(2), RandomClogging, Rollback, SaveAndKill. Clear-after-test modes: VersionVectorUpgrade:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/VersionVectorEnableRestart-1.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/VersionVectorEnableRestart-2.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/VersionVectorEnableRestart-2.toml

- **Purpose:** Restarting simulation stage for `VersionVectorEnableRestart-2`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 55 lines, 1089 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles VersionVectorUpgrade, workloads Cycle(3), Attrition(2), RandomClogging, Rollback, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (VersionVectorUpgrade) and schedules each block's workload list (VersionVectorUpgrade:7). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle(3), Attrition(2), RandomClogging, Rollback. Top-level keys: configuration, knobs. Configuration/test knobs: storageEngineExcludeTypes=[5], VersionVectorUpgrade.runSetup=False, VersionVectorUpgrade/Cycle.testDuration=30.0, VersionVectorUpgrade/Cycle.transactionsPerSecond=2500.0, VersionVectorUpgrade/Cycle.nodeCount=1000, VersionVectorUpgrade/Cycle.keyPrefix='cycle', VersionVectorUpgrade/Cycle.testDuration=30.0, VersionVectorUpgrade/Cycle.transactionsPerSecond=2500.0, VersionVectorUpgrade/Cycle.nodeCount=1000, VersionVectorUpgrade/Cycle.keyPrefix='!', VersionVectorUpgrade/Cycle.testDuration=30.0, VersionVectorUpgrade/Cycle.transactionsPerSecond=2500.0, VersionVectorUpgrade/Cycle.nodeCount=1000, VersionVectorUpgrade/Cycle.keyPrefix='ZZZ', VersionVectorUpgrade/RandomClogging.testDuration=10.0, VersionVectorUpgrade/Rollback.testDuration=10.0, VersionVectorUpgrade/Rollback.meanDelay=10.0, VersionVectorUpgrade/Attrition.testDuration=10.0, VersionVectorUpgrade/Attrition.machinesToKill=10, VersionVectorUpgrade/Attrition.machinesToLeave=3, VersionVectorUpgrade/Attrition.testDuration=60.0, VersionVectorUpgrade/Attrition.machinesToKill=10; plus 1 more.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/VersionVectorEnableRestart-2.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle(3), Attrition(2), RandomClogging, Rollback. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0/VersionVectorEnableRestart-2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapCycleRestart-1.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapCycleRestart-1.toml

- **Purpose:** Restarting simulation stage for `SnapCycleRestart-1`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 30 lines, 567 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 2 test block(s), titles SnapCyclePre, SnapCycleShutdown, workloads Cycle, SnapTest, SaveAndKill, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 2 `[[test]]` block(s) (SnapCyclePre, SnapCycleShutdown) and schedules each block's workload list (SnapCyclePre:2, SnapCycleShutdown:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle, SnapTest, SaveAndKill. Top-level keys: configuration. Configuration/test knobs: storageEngineExcludeTypes=[3, 4, 5], logAntiQuorum=0, encryptModes=['disabled'], tenantModes=['disabled'], SnapCyclePre/Cycle.testDuration=10.0, SnapCyclePre/Cycle.transactionsPerSecond=2500.0, SnapCyclePre/Cycle.nodeCount=2500, SnapCycleShutdown/SaveAndKill.testDuration=10.0, SnapCycleShutdown/SaveAndKill.restartInfoLocation='simfdb/restartInfo.ini'.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapCycleRestart-1.toml` through the Python TestRunner/CTest path.
- **Risks:** Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle, SnapTest, SaveAndKill. Clear-after-test modes: SnapCyclePre:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapCycleRestart-1.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapCycleRestart-2.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapCycleRestart-2.toml

- **Purpose:** Restarting simulation stage for `SnapCycleRestart-2`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 14 lines, 252 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles SnapCycleRestore, workloads Cycle, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (SnapCycleRestore) and schedules each block's workload list (SnapCycleRestore:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle. Top-level keys: configuration. Configuration/test knobs: storageEngineExcludeTypes=[4, 5], buggify=False, SnapCycleRestore.runSetup=False, SnapCycleRestore/Cycle.testDuration=10.0, SnapCycleRestore/Cycle.transactionsPerSecond=2500.0, SnapCycleRestore/Cycle.nodeCount=2500.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapCycleRestart-2.toml` through the Python TestRunner/CTest path.
- **Risks:** Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapCycleRestart-2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapTestAttrition-1.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapTestAttrition-1.toml

- **Purpose:** Restarting simulation stage for `SnapTestAttrition-1`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 61 lines, 1269 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 4 test block(s), titles SnapTestPre, SnapTestTakeSnap, SnapTestPost, SnapSimpleShutdown, workloads SnapTest(3), ReadWrite, Attrition, SaveAndKill, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 4 `[[test]]` block(s) (SnapTestPre, SnapTestTakeSnap, SnapTestPost, SnapSimpleShutdown) and schedules each block's workload list (SnapTestPre:1, SnapTestTakeSnap:3, SnapTestPost:1, SnapSimpleShutdown:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: SnapTest(3), ReadWrite, Attrition, SaveAndKill. Top-level keys: configuration. Configuration/test knobs: storageEngineExcludeTypes=[3, 4, 5], logAntiQuorum=0, encryptModes=['disabled'], tenantModes=['disabled'], SnapTestTakeSnap/ReadWrite.testDuration=10.0, SnapTestTakeSnap/ReadWrite.transactionsPerSecond=10000, SnapTestTakeSnap/ReadWrite.nodeCount=100000, SnapTestTakeSnap/Attrition.testDuration=10.0, SnapSimpleShutdown/SaveAndKill.testDuration=10.0, SnapSimpleShutdown/SaveAndKill.restartInfoLocation='simfdb/restartInfo.ini'.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapTestAttrition-1.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for SnapTest(3), ReadWrite, Attrition, SaveAndKill. Clear-after-test modes: SnapTestPre:False, SnapTestTakeSnap:False, SnapTestPost:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapTestAttrition-1.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapTestAttrition-2.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapTestAttrition-2.toml

- **Purpose:** Restarting simulation stage for `SnapTestAttrition-2`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 14 lines, 262 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles SnapTestVerify, workloads SnapTest, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (SnapTestVerify) and schedules each block's workload list (SnapTestVerify:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: SnapTest. Top-level keys: configuration. Configuration/test knobs: storageEngineExcludeTypes=[4, 5], buggify=False, SnapTestVerify/SnapTest.restartInfoLocation='simfdb/restartInfo.ini'.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapTestAttrition-2.toml` through the Python TestRunner/CTest path.
- **Risks:** Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for SnapTest. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapTestAttrition-2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapTestRestart-1.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapTestRestart-1.toml

- **Purpose:** Restarting simulation stage for `SnapTestRestart-1`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 57 lines, 1185 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 4 test block(s), titles SnapTestPre, SnapTestTakeSnap, SnapTestPost, SnapTestShutdown, workloads SnapTest(3), ReadWrite, SaveAndKill, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 4 `[[test]]` block(s) (SnapTestPre, SnapTestTakeSnap, SnapTestPost, SnapTestShutdown) and schedules each block's workload list (SnapTestPre:1, SnapTestTakeSnap:2, SnapTestPost:1, SnapTestShutdown:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: SnapTest(3), ReadWrite, SaveAndKill. Top-level keys: configuration. Configuration/test knobs: storageEngineExcludeTypes=[3, 4, 5], logAntiQuorum=0, encryptModes=['disabled'], tenantModes=['disabled'], SnapTestTakeSnap/ReadWrite.testDuration=10.0, SnapTestTakeSnap/ReadWrite.transactionsPerSecond=10000, SnapTestTakeSnap/ReadWrite.nodeCount=100000, SnapTestShutdown/SaveAndKill.testDuration=10.0, SnapTestShutdown/SaveAndKill.restartInfoLocation='simfdb/restartInfo.ini'.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapTestRestart-1.toml` through the Python TestRunner/CTest path.
- **Risks:** Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for SnapTest(3), ReadWrite, SaveAndKill. Clear-after-test modes: SnapTestPre:False, SnapTestTakeSnap:False, SnapTestPost:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapTestRestart-1.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapTestRestart-2.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapTestRestart-2.toml

- **Purpose:** Restarting simulation stage for `SnapTestRestart-2`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 13 lines, 213 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles SnapTestVerify, workloads SnapTest, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (SnapTestVerify) and schedules each block's workload list (SnapTestVerify:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: SnapTest. Top-level keys: configuration. Configuration/test knobs: storageEngineExcludeTypes=[4, 5], buggify=False.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapTestRestart-2.toml` through the Python TestRunner/CTest path.
- **Risks:** Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for SnapTest. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapTestRestart-2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapTestSimpleRestart-1.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapTestSimpleRestart-1.toml

- **Purpose:** Restarting simulation stage for `SnapTestSimpleRestart-1`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 53 lines, 1016 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 5 test block(s), titles SnapSimplePre, SnapSimpleTakeSnap, SnapSimplePost, SnapCreateNotWhitelistedBinaryPath, SnapSimpleShutdown, workloads SnapTest(4), SaveAndKill, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 5 `[[test]]` block(s) (SnapSimplePre, SnapSimpleTakeSnap, SnapSimplePost, SnapCreateNotWhitelistedBinaryPath, SnapSimpleShutdown) and schedules each block's workload list (SnapSimplePre:1, SnapSimpleTakeSnap:1, SnapSimplePost:1, SnapCreateNotWhitelistedBinaryPath:1, SnapSimpleShutdown:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: SnapTest(4), SaveAndKill. Top-level keys: configuration. Configuration/test knobs: storageEngineExcludeTypes=[3, 4, 5], logAntiQuorum=0, encryptModes=['disabled'], tenantModes=['disabled'], SnapSimpleShutdown/SaveAndKill.testDuration=10.0, SnapSimpleShutdown/SaveAndKill.restartInfoLocation='simfdb/restartInfo.ini'.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapTestSimpleRestart-1.toml` through the Python TestRunner/CTest path.
- **Risks:** Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for SnapTest(4), SaveAndKill. Clear-after-test modes: SnapSimplePre:False, SnapSimpleTakeSnap:False, SnapSimplePost:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapTestSimpleRestart-1.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapTestSimpleRestart-2.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapTestSimpleRestart-2.toml

- **Purpose:** Restarting simulation stage for `SnapTestSimpleRestart-2`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 13 lines, 215 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles SnapSimpleVerify, workloads SnapTest, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (SnapSimpleVerify) and schedules each block's workload list (SnapSimpleVerify:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: SnapTest. Top-level keys: configuration. Configuration/test knobs: storageEngineExcludeTypes=[4, 5], buggify=False.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapTestSimpleRestart-2.toml` through the Python TestRunner/CTest path.
- **Risks:** Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for SnapTest. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.0_until_7.4.0/SnapTestSimpleRestart-2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.29/ClientTransactionProfilingCorrectness-1.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.29/ClientTransactionProfilingCorrectness-1.toml

- **Purpose:** Restarting simulation stage for `ClientTransactionProfilingCorrectness-1`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 38 lines, 842 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles ClientTransactionProfilingCorrectness, workloads ApiCorrectness, ClientTransactionProfileCorrectness, SaveAndKill, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (ClientTransactionProfilingCorrectness) and schedules each block's workload list (ClientTransactionProfilingCorrectness:3). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: ApiCorrectness, ClientTransactionProfileCorrectness, SaveAndKill. Top-level keys: configuration. Configuration/test knobs: storageEngineExcludeTypes=[3, 5], tenantModes=['disabled'], encryptModes=['disabled'], ClientTransactionProfilingCorrectness.runSetup=True, ClientTransactionProfilingCorrectness/SaveAndKill.testDuration=60, ClientTransactionProfilingCorrectness/SaveAndKill.restartInfoLocation='simfdb/restartInfo.ini'.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.29/ClientTransactionProfilingCorrectness-1.toml` through the Python TestRunner/CTest path.
- **Risks:** Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for ApiCorrectness, ClientTransactionProfileCorrectness, SaveAndKill. Clear-after-test modes: ClientTransactionProfilingCorrectness:False. Timeouts: ClientTransactionProfilingCorrectness:2100.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.29/ClientTransactionProfilingCorrectness-1.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.29/ClientTransactionProfilingCorrectness-2.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.29/ClientTransactionProfilingCorrectness-2.toml

- **Purpose:** Restarting simulation stage for `ClientTransactionProfilingCorrectness-2`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 32 lines, 670 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles ClientTransactionProfilingCorrectness, workloads ApiCorrectness, ClientTransactionProfileCorrectness, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (ClientTransactionProfilingCorrectness) and schedules each block's workload list (ClientTransactionProfilingCorrectness:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: ApiCorrectness, ClientTransactionProfileCorrectness. Top-level keys: configuration. Configuration/test knobs: storageEngineExcludeTypes=[3, 5], ClientTransactionProfilingCorrectness.runSetup=True.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.29/ClientTransactionProfilingCorrectness-2.toml` through the Python TestRunner/CTest path.
- **Risks:** Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for ApiCorrectness, ClientTransactionProfileCorrectness. Clear-after-test modes: ClientTransactionProfilingCorrectness:True. Timeouts: ClientTransactionProfilingCorrectness:2100.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.29/ClientTransactionProfilingCorrectness-2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.29/CycleTestRestart-1.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.29/CycleTestRestart-1.toml

- **Purpose:** Restarting simulation stage for `CycleTestRestart-1`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 42 lines, 820 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles Clogged, workloads Attrition(2), Cycle, RandomClogging, Rollback, SaveAndKill, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (Clogged) and schedules each block's workload list (Clogged:6). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Attrition(2), Cycle, RandomClogging, Rollback, SaveAndKill. Top-level keys: configuration. Configuration/test knobs: storageEngineExcludeTypes=[3, 5], encryptModes=['disabled'], tenantModes=['disabled'], Clogged/Cycle.testDuration=10.0, Clogged/Cycle.transactionsPerSecond=500.0, Clogged/Cycle.nodeCount=2500, Clogged/RandomClogging.testDuration=10.0, Clogged/Rollback.testDuration=10.0, Clogged/Rollback.meanDelay=10.0, Clogged/Attrition.testDuration=10.0, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3, Clogged/Attrition.testDuration=10.0, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3, Clogged/SaveAndKill.testDuration=10.0, Clogged/SaveAndKill.restartInfoLocation='simfdb/restartInfo.ini'.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.29/CycleTestRestart-1.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Attrition(2), Cycle, RandomClogging, Rollback, SaveAndKill. Clear-after-test modes: Clogged:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.29/CycleTestRestart-1.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.29/CycleTestRestart-2.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.29/CycleTestRestart-2.toml

- **Purpose:** Restarting simulation stage for `CycleTestRestart-2`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 36 lines, 653 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles Clogged, workloads Attrition(2), Cycle, RandomClogging, Rollback, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (Clogged) and schedules each block's workload list (Clogged:5). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Attrition(2), Cycle, RandomClogging, Rollback. Top-level keys: configuration. Configuration/test knobs: storageEngineExcludeTypes=[3, 5], Clogged.runSetup=False, Clogged/Cycle.testDuration=10.0, Clogged/Cycle.transactionsPerSecond=2500.0, Clogged/Cycle.nodeCount=2500, Clogged/RandomClogging.testDuration=10.0, Clogged/Rollback.testDuration=10.0, Clogged/Rollback.meanDelay=10.0, Clogged/Attrition.testDuration=10.0, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3, Clogged/Attrition.testDuration=10.0, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.29/CycleTestRestart-2.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Attrition(2), Cycle, RandomClogging, Rollback. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.29/CycleTestRestart-2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.49/ClientMetricRestart-1.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.49/ClientMetricRestart-1.toml

- **Purpose:** Restarting simulation stage for `ClientMetricRestart-1`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 20 lines, 434 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles ClientMetricRestartTest, workloads ClientMetric, SaveAndKill, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (ClientMetricRestartTest) and schedules each block's workload list (ClientMetricRestartTest:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: ClientMetric, SaveAndKill. Top-level keys: configuration. Configuration/test knobs: storageEngineExcludeTypes=[3, 5], tenantModes=['disabled'], encryptModes=['disabled'], ClientMetricRestartTest/ClientMetric.testDuration=500.0, ClientMetricRestartTest/SaveAndKill.testDuration=500.0, ClientMetricRestartTest/SaveAndKill.restartInfoLocation='simfdb/restartInfo.ini'.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.49/ClientMetricRestart-1.toml` through the Python TestRunner/CTest path.
- **Risks:** Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for ClientMetric, SaveAndKill. Clear-after-test modes: ClientMetricRestartTest:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.49/ClientMetricRestart-1.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.49/ClientMetricRestart-2.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.49/ClientMetricRestart-2.toml

- **Purpose:** Restarting simulation stage for `ClientMetricRestart-2`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 13 lines, 255 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles ClientMetricRestartTest, workloads ClientMetric, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (ClientMetricRestartTest) and schedules each block's workload list (ClientMetricRestartTest:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: ClientMetric. Top-level keys: configuration. Configuration/test knobs: storageEngineExcludeTypes=[5], ClientMetricRestartTest.runConsistencyCheck=False, ClientMetricRestartTest/ClientMetric.testDuration=500.0.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.49/ClientMetricRestart-2.toml` through the Python TestRunner/CTest path.
- **Risks:** Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for ClientMetric. Clear-after-test modes: ClientMetricRestartTest:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.49/ClientMetricRestart-2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.5_until_7.3.29/ClientTransactionProfilingCorrectness-1.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.5_until_7.3.29/ClientTransactionProfilingCorrectness-1.toml

- **Purpose:** Restarting simulation stage for `ClientTransactionProfilingCorrectness-1`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 40 lines, 864 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles ClientTransactionProfilingCorrectness, workloads ApiCorrectness, ClientTransactionProfileCorrectness, SaveAndKill, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (ClientTransactionProfilingCorrectness) and schedules each block's workload list (ClientTransactionProfilingCorrectness:3). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: ApiCorrectness, ClientTransactionProfileCorrectness, SaveAndKill. Top-level keys: configuration, knobs. Configuration/test knobs: storageEngineExcludeTypes=[3], tenantModes=['disabled'], ClientTransactionProfilingCorrectness.runSetup=True, ClientTransactionProfilingCorrectness/SaveAndKill.testDuration=60, ClientTransactionProfilingCorrectness/SaveAndKill.restartInfoLocation='simfdb/restartInfo.ini'.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.5_until_7.3.29/ClientTransactionProfilingCorrectness-1.toml` through the Python TestRunner/CTest path.
- **Risks:** Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for ApiCorrectness, ClientTransactionProfileCorrectness, SaveAndKill. Clear-after-test modes: ClientTransactionProfilingCorrectness:False. Timeouts: ClientTransactionProfilingCorrectness:2100.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.5_until_7.3.29/ClientTransactionProfilingCorrectness-1.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.5_until_7.3.29/ClientTransactionProfilingCorrectness-2.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.5_until_7.3.29/ClientTransactionProfilingCorrectness-2.toml

- **Purpose:** Restarting simulation stage for `ClientTransactionProfilingCorrectness-2`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 29 lines, 621 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles ClientTransactionProfilingCorrectness, workloads ApiCorrectness, ClientTransactionProfileCorrectness, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (ClientTransactionProfilingCorrectness) and schedules each block's workload list (ClientTransactionProfilingCorrectness:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: ApiCorrectness, ClientTransactionProfileCorrectness. Top-level keys: none. Configuration/test knobs: ClientTransactionProfilingCorrectness.runSetup=True.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.5_until_7.3.29/ClientTransactionProfilingCorrectness-2.toml` through the Python TestRunner/CTest path.
- **Risks:** Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for ApiCorrectness, ClientTransactionProfileCorrectness. Clear-after-test modes: ClientTransactionProfilingCorrectness:True. Timeouts: ClientTransactionProfilingCorrectness:2100.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.5_until_7.3.29/ClientTransactionProfilingCorrectness-2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.5_until_7.3.29/CycleTestRestart-1.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.5_until_7.3.29/CycleTestRestart-1.toml

- **Purpose:** Restarting simulation stage for `CycleTestRestart-1`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 45 lines, 868 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles Clogged, workloads Attrition(2), Cycle, RandomClogging, Rollback, SaveAndKill, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (Clogged) and schedules each block's workload list (Clogged:6). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Attrition(2), Cycle, RandomClogging, Rollback, SaveAndKill. Top-level keys: configuration, knobs. Configuration/test knobs: storageEngineExcludeTypes=[3], encryptModes=['disabled'], tenantModes=['disabled'], Clogged/Cycle.testDuration=10.0, Clogged/Cycle.transactionsPerSecond=500.0, Clogged/Cycle.nodeCount=2500, Clogged/RandomClogging.testDuration=10.0, Clogged/Rollback.testDuration=10.0, Clogged/Rollback.meanDelay=10.0, Clogged/Attrition.testDuration=10.0, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3, Clogged/Attrition.testDuration=10.0, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3, Clogged/SaveAndKill.testDuration=10.0, Clogged/SaveAndKill.restartInfoLocation='simfdb/restartInfo.ini'.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.5_until_7.3.29/CycleTestRestart-1.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Attrition(2), Cycle, RandomClogging, Rollback, SaveAndKill. Clear-after-test modes: Clogged:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.5_until_7.3.29/CycleTestRestart-1.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.5_until_7.3.29/CycleTestRestart-2.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.3.5_until_7.3.29/CycleTestRestart-2.toml

- **Purpose:** Restarting simulation stage for `CycleTestRestart-2`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 32 lines, 585 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles Clogged, workloads Attrition(2), Cycle, RandomClogging, Rollback, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (Clogged) and schedules each block's workload list (Clogged:5). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Attrition(2), Cycle, RandomClogging, Rollback. Top-level keys: none. Configuration/test knobs: Clogged.runSetup=False, Clogged/Cycle.testDuration=10.0, Clogged/Cycle.transactionsPerSecond=2500.0, Clogged/Cycle.nodeCount=2500, Clogged/RandomClogging.testDuration=10.0, Clogged/Rollback.testDuration=10.0, Clogged/Rollback.meanDelay=10.0, Clogged/Attrition.testDuration=10.0, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3, Clogged/Attrition.testDuration=10.0, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.3.5_until_7.3.29/CycleTestRestart-2.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Attrition(2), Cycle, RandomClogging, Rollback. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.3.5_until_7.3.29/CycleTestRestart-2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapCycleRestart-1.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapCycleRestart-1.toml

- **Purpose:** Restarting simulation stage for `SnapCycleRestart-1`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 33 lines, 617 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 2 test block(s), titles SnapCyclePre, SnapCycleShutdown, workloads Cycle, SnapTest, SaveAndKill, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 2 `[[test]]` block(s) (SnapCyclePre, SnapCycleShutdown) and schedules each block's workload list (SnapCyclePre:2, SnapCycleShutdown:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle, SnapTest, SaveAndKill. Top-level keys: configuration, knobs. Configuration/test knobs: storageEngineExcludeTypes=[3, 4, 5], logAntiQuorum=0, tenantModes=['disabled'], encryptModes=['disabled'], SnapCyclePre/Cycle.testDuration=10.0, SnapCyclePre/Cycle.transactionsPerSecond=2500.0, SnapCyclePre/Cycle.nodeCount=2500, SnapCycleShutdown/SaveAndKill.testDuration=10.0, SnapCycleShutdown/SaveAndKill.restartInfoLocation='simfdb/restartInfo.ini'.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapCycleRestart-1.toml` through the Python TestRunner/CTest path.
- **Risks:** Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle, SnapTest, SaveAndKill. Clear-after-test modes: SnapCyclePre:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapCycleRestart-1.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapCycleRestart-2.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapCycleRestart-2.toml

- **Purpose:** Restarting simulation stage for `SnapCycleRestart-2`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 14 lines, 252 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles SnapCycleRestore, workloads Cycle, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (SnapCycleRestore) and schedules each block's workload list (SnapCycleRestore:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Cycle. Top-level keys: configuration. Configuration/test knobs: storageEngineExcludeTypes=[4, 5], buggify=False, SnapCycleRestore.runSetup=False, SnapCycleRestore/Cycle.testDuration=10.0, SnapCycleRestore/Cycle.transactionsPerSecond=2500.0, SnapCycleRestore/Cycle.nodeCount=2500.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapCycleRestart-2.toml` through the Python TestRunner/CTest path.
- **Risks:** Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Cycle. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapCycleRestart-2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapTestAttrition-1.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapTestAttrition-1.toml

- **Purpose:** Restarting simulation stage for `SnapTestAttrition-1`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 64 lines, 1319 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 4 test block(s), titles SnapTestPre, SnapTestTakeSnap, SnapTestPost, SnapSimpleShutdown, workloads SnapTest(3), ReadWrite, Attrition, SaveAndKill, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 4 `[[test]]` block(s) (SnapTestPre, SnapTestTakeSnap, SnapTestPost, SnapSimpleShutdown) and schedules each block's workload list (SnapTestPre:1, SnapTestTakeSnap:3, SnapTestPost:1, SnapSimpleShutdown:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: SnapTest(3), ReadWrite, Attrition, SaveAndKill. Top-level keys: configuration, knobs. Configuration/test knobs: storageEngineExcludeTypes=[3, 4, 5], logAntiQuorum=0, tenantModes=['disabled'], encryptModes=['disabled'], SnapTestTakeSnap/ReadWrite.testDuration=10.0, SnapTestTakeSnap/ReadWrite.transactionsPerSecond=10000, SnapTestTakeSnap/ReadWrite.nodeCount=100000, SnapTestTakeSnap/Attrition.testDuration=10.0, SnapSimpleShutdown/SaveAndKill.testDuration=10.0, SnapSimpleShutdown/SaveAndKill.restartInfoLocation='simfdb/restartInfo.ini'.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapTestAttrition-1.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for SnapTest(3), ReadWrite, Attrition, SaveAndKill. Clear-after-test modes: SnapTestPre:False, SnapTestTakeSnap:False, SnapTestPost:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapTestAttrition-1.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapTestAttrition-2.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapTestAttrition-2.toml

- **Purpose:** Restarting simulation stage for `SnapTestAttrition-2`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 14 lines, 262 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles SnapTestVerify, workloads SnapTest, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (SnapTestVerify) and schedules each block's workload list (SnapTestVerify:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: SnapTest. Top-level keys: configuration. Configuration/test knobs: storageEngineExcludeTypes=[4, 5], buggify=False, SnapTestVerify/SnapTest.restartInfoLocation='simfdb/restartInfo.ini'.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapTestAttrition-2.toml` through the Python TestRunner/CTest path.
- **Risks:** Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for SnapTest. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapTestAttrition-2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapTestRestart-1.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapTestRestart-1.toml

- **Purpose:** Restarting simulation stage for `SnapTestRestart-1`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 60 lines, 1235 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 4 test block(s), titles SnapTestPre, SnapTestTakeSnap, SnapTestPost, SnapTestShutdown, workloads SnapTest(3), ReadWrite, SaveAndKill, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 4 `[[test]]` block(s) (SnapTestPre, SnapTestTakeSnap, SnapTestPost, SnapTestShutdown) and schedules each block's workload list (SnapTestPre:1, SnapTestTakeSnap:2, SnapTestPost:1, SnapTestShutdown:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: SnapTest(3), ReadWrite, SaveAndKill. Top-level keys: configuration, knobs. Configuration/test knobs: storageEngineExcludeTypes=[3, 4, 5], logAntiQuorum=0, tenantModes=['disabled'], encryptModes=['disabled'], SnapTestTakeSnap/ReadWrite.testDuration=10.0, SnapTestTakeSnap/ReadWrite.transactionsPerSecond=10000, SnapTestTakeSnap/ReadWrite.nodeCount=100000, SnapTestShutdown/SaveAndKill.testDuration=10.0, SnapTestShutdown/SaveAndKill.restartInfoLocation='simfdb/restartInfo.ini'.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapTestRestart-1.toml` through the Python TestRunner/CTest path.
- **Risks:** Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for SnapTest(3), ReadWrite, SaveAndKill. Clear-after-test modes: SnapTestPre:False, SnapTestTakeSnap:False, SnapTestPost:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapTestRestart-1.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapTestRestart-2.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapTestRestart-2.toml

- **Purpose:** Restarting simulation stage for `SnapTestRestart-2`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 13 lines, 213 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles SnapTestVerify, workloads SnapTest, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (SnapTestVerify) and schedules each block's workload list (SnapTestVerify:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: SnapTest. Top-level keys: configuration. Configuration/test knobs: storageEngineExcludeTypes=[4, 5], buggify=False.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapTestRestart-2.toml` through the Python TestRunner/CTest path.
- **Risks:** Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for SnapTest. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapTestRestart-2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapTestSimpleRestart-1.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapTestSimpleRestart-1.toml

- **Purpose:** Restarting simulation stage for `SnapTestSimpleRestart-1`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 56 lines, 1066 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 5 test block(s), titles SnapSimplePre, SnapSimpleTakeSnap, SnapSimplePost, SnapCreateNotWhitelistedBinaryPath, SnapSimpleShutdown, workloads SnapTest(4), SaveAndKill, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 5 `[[test]]` block(s) (SnapSimplePre, SnapSimpleTakeSnap, SnapSimplePost, SnapCreateNotWhitelistedBinaryPath, SnapSimpleShutdown) and schedules each block's workload list (SnapSimplePre:1, SnapSimpleTakeSnap:1, SnapSimplePost:1, SnapCreateNotWhitelistedBinaryPath:1, SnapSimpleShutdown:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: SnapTest(4), SaveAndKill. Top-level keys: configuration, knobs. Configuration/test knobs: storageEngineExcludeTypes=[3, 4, 5], logAntiQuorum=0, tenantModes=['disabled'], encryptModes=['disabled'], SnapSimpleShutdown/SaveAndKill.testDuration=10.0, SnapSimpleShutdown/SaveAndKill.restartInfoLocation='simfdb/restartInfo.ini'.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapTestSimpleRestart-1.toml` through the Python TestRunner/CTest path.
- **Risks:** Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for SnapTest(4), SaveAndKill. Clear-after-test modes: SnapSimplePre:False, SnapSimpleTakeSnap:False, SnapSimplePost:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapTestSimpleRestart-1.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapTestSimpleRestart-2.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapTestSimpleRestart-2.toml

- **Purpose:** Restarting simulation stage for `SnapTestSimpleRestart-2`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 13 lines, 215 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles SnapSimpleVerify, workloads SnapTest, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (SnapSimpleVerify) and schedules each block's workload list (SnapSimpleVerify:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: SnapTest. Top-level keys: configuration. Configuration/test knobs: storageEngineExcludeTypes=[4, 5], buggify=False.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapTestSimpleRestart-2.toml` through the Python TestRunner/CTest path.
- **Risks:** Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for SnapTest. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/from_7.4.0/SnapTestSimpleRestart-2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/to_7.4.5/ConfigureStorageMigrationTestRestart-1.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/to_7.4.5/ConfigureStorageMigrationTestRestart-1.toml

- **Purpose:** Restarting simulation stage for `ConfigureStorageMigrationTestRestart-1`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 30 lines, 648 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles CloggedConfigureDatabaseTest, workloads RandomClogging(2), ConfigureDatabase, SaveAndKill, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (CloggedConfigureDatabaseTest) and schedules each block's workload list (CloggedConfigureDatabaseTest:4). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts. Storage-engine-focused workloads stress on-disk or checkpoint representations in the simulated/noSim environment.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: RandomClogging(2), ConfigureDatabase, SaveAndKill. Top-level keys: configuration. Configuration/test knobs: extraMachineCountDC=2, maxTLogVersion=7, disableHostname=True, CloggedConfigureDatabaseTest/ConfigureDatabase.testDuration=30.0, CloggedConfigureDatabaseTest/RandomClogging.testDuration=30.0, CloggedConfigureDatabaseTest/RandomClogging.testDuration=30.0, CloggedConfigureDatabaseTest/SaveAndKill.testDuration=30.0, CloggedConfigureDatabaseTest/SaveAndKill.restartInfoLocation='simfdb/restartInfo.ini'.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/to_7.4.5/ConfigureStorageMigrationTestRestart-1.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection. Storage-engine tests are sensitive to engine selection/exclusion knobs and checkpoint determinism.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for RandomClogging(2), ConfigureDatabase, SaveAndKill. Clear-after-test modes: CloggedConfigureDatabaseTest:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/to_7.4.5/ConfigureStorageMigrationTestRestart-1.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/to_7.4.5/ConfigureStorageMigrationTestRestart-2.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/to_7.4.5/ConfigureStorageMigrationTestRestart-2.toml

- **Purpose:** Restarting simulation stage for `ConfigureStorageMigrationTestRestart-2`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 23 lines, 488 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles CloggedConfigureDatabaseTest, workloads RandomClogging(2), ConfigureDatabase, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (CloggedConfigureDatabaseTest) and schedules each block's workload list (CloggedConfigureDatabaseTest:3). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts. Storage-engine-focused workloads stress on-disk or checkpoint representations in the simulated/noSim environment.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: RandomClogging(2), ConfigureDatabase. Top-level keys: configuration. Configuration/test knobs: extraMachineCountDC=2, CloggedConfigureDatabaseTest.runSetup=False, CloggedConfigureDatabaseTest/ConfigureDatabase.testDuration=300.0, CloggedConfigureDatabaseTest/RandomClogging.testDuration=300.0, CloggedConfigureDatabaseTest/RandomClogging.testDuration=300.0.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/to_7.4.5/ConfigureStorageMigrationTestRestart-2.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection. Storage-engine tests are sensitive to engine selection/exclusion knobs and checkpoint determinism.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for RandomClogging(2), ConfigureDatabase. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/to_7.4.5/ConfigureStorageMigrationTestRestart-2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/to_7.4.5/CycleTestRestart-1.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/to_7.4.5/CycleTestRestart-1.toml

- **Purpose:** Restarting simulation stage for `CycleTestRestart-1`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 42 lines, 836 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles Clogged, workloads Attrition(2), Cycle, RandomClogging, Rollback, SaveAndKill, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (Clogged) and schedules each block's workload list (Clogged:6). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Attrition(2), Cycle, RandomClogging, Rollback, SaveAndKill. Top-level keys: configuration. Configuration/test knobs: maxTLogVersion=7, disableTss=True, disableHostname=True, Clogged/Cycle.testDuration=10.0, Clogged/Cycle.transactionsPerSecond=500.0, Clogged/Cycle.nodeCount=2500, Clogged/RandomClogging.testDuration=10.0, Clogged/Rollback.testDuration=10.0, Clogged/Rollback.meanDelay=10.0, Clogged/Attrition.testDuration=10.0, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3, Clogged/Attrition.testDuration=10.0, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3, Clogged/SaveAndKill.testDuration=10.0, Clogged/SaveAndKill.restartInfoLocation='simfdb/restartInfo.ini'.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/to_7.4.5/CycleTestRestart-1.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Attrition(2), Cycle, RandomClogging, Rollback, SaveAndKill. Clear-after-test modes: Clogged:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/to_7.4.5/CycleTestRestart-1.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/to_7.4.5/CycleTestRestart-2.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/to_7.4.5/CycleTestRestart-2.toml

- **Purpose:** Restarting simulation stage for `CycleTestRestart-2`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 41 lines, 817 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles Clogged, workloads Attrition(2), Cycle, RandomClogging, Rollback, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (Clogged) and schedules each block's workload list (Clogged:5). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Attrition(2), Cycle, RandomClogging, Rollback. Top-level keys: configuration, knobs. Configuration/test knobs: maxTLogVersion=7, disableTss=True, Clogged.runSetup=False, Clogged/Cycle.testDuration=10.0, Clogged/Cycle.transactionsPerSecond=2500.0, Clogged/Cycle.nodeCount=2500, Clogged/RandomClogging.testDuration=10.0, Clogged/Rollback.testDuration=10.0, Clogged/Rollback.meanDelay=10.0, Clogged/Attrition.testDuration=10.0, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/to_7.4.5/CycleTestRestart-2.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Attrition(2), Cycle, RandomClogging, Rollback. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/to_7.4.5/CycleTestRestart-2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/to_8.0.0/ConfigureStorageMigrationTestRestart-1.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/to_8.0.0/ConfigureStorageMigrationTestRestart-1.toml

- **Purpose:** Restarting simulation stage for `ConfigureStorageMigrationTestRestart-1`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 30 lines, 648 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles CloggedConfigureDatabaseTest, workloads RandomClogging(2), ConfigureDatabase, SaveAndKill, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (CloggedConfigureDatabaseTest) and schedules each block's workload list (CloggedConfigureDatabaseTest:4). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts. Storage-engine-focused workloads stress on-disk or checkpoint representations in the simulated/noSim environment.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: RandomClogging(2), ConfigureDatabase, SaveAndKill. Top-level keys: configuration. Configuration/test knobs: extraMachineCountDC=2, maxTLogVersion=7, disableHostname=True, CloggedConfigureDatabaseTest/ConfigureDatabase.testDuration=30.0, CloggedConfigureDatabaseTest/RandomClogging.testDuration=30.0, CloggedConfigureDatabaseTest/RandomClogging.testDuration=30.0, CloggedConfigureDatabaseTest/SaveAndKill.testDuration=30.0, CloggedConfigureDatabaseTest/SaveAndKill.restartInfoLocation='simfdb/restartInfo.ini'.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/to_8.0.0/ConfigureStorageMigrationTestRestart-1.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection. Storage-engine tests are sensitive to engine selection/exclusion knobs and checkpoint determinism.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for RandomClogging(2), ConfigureDatabase, SaveAndKill. Clear-after-test modes: CloggedConfigureDatabaseTest:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/to_8.0.0/ConfigureStorageMigrationTestRestart-1.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/to_8.0.0/ConfigureStorageMigrationTestRestart-2.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/to_8.0.0/ConfigureStorageMigrationTestRestart-2.toml

- **Purpose:** Restarting simulation stage for `ConfigureStorageMigrationTestRestart-2`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 23 lines, 489 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles CloggedConfigureDatabaseTest, workloads RandomClogging(2), ConfigureDatabase, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (CloggedConfigureDatabaseTest) and schedules each block's workload list (CloggedConfigureDatabaseTest:3). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts. Storage-engine-focused workloads stress on-disk or checkpoint representations in the simulated/noSim environment.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: RandomClogging(2), ConfigureDatabase. Top-level keys: configuration. Configuration/test knobs: extraMachineCountDC=2, CloggedConfigureDatabaseTest.runSetup=False, CloggedConfigureDatabaseTest/ConfigureDatabase.testDuration=300.0, CloggedConfigureDatabaseTest/RandomClogging.testDuration=300.0, CloggedConfigureDatabaseTest/RandomClogging.testDuration=300.0.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/to_8.0.0/ConfigureStorageMigrationTestRestart-2.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection. Storage-engine tests are sensitive to engine selection/exclusion knobs and checkpoint determinism.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for RandomClogging(2), ConfigureDatabase. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/to_8.0.0/ConfigureStorageMigrationTestRestart-2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/to_8.0.0/CycleTestRestart-1.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/to_8.0.0/CycleTestRestart-1.toml

- **Purpose:** Restarting simulation stage for `CycleTestRestart-1`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 42 lines, 836 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles Clogged, workloads Attrition(2), Cycle, RandomClogging, Rollback, SaveAndKill, top-level keys configuration.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (Clogged) and schedules each block's workload list (Clogged:6). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Attrition(2), Cycle, RandomClogging, Rollback, SaveAndKill. Top-level keys: configuration. Configuration/test knobs: maxTLogVersion=7, disableTss=True, disableHostname=True, Clogged/Cycle.testDuration=10.0, Clogged/Cycle.transactionsPerSecond=500.0, Clogged/Cycle.nodeCount=2500, Clogged/RandomClogging.testDuration=10.0, Clogged/Rollback.testDuration=10.0, Clogged/Rollback.meanDelay=10.0, Clogged/Attrition.testDuration=10.0, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3, Clogged/Attrition.testDuration=10.0, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3, Clogged/SaveAndKill.testDuration=10.0, Clogged/SaveAndKill.restartInfoLocation='simfdb/restartInfo.ini'.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/to_8.0.0/CycleTestRestart-1.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Attrition(2), Cycle, RandomClogging, Rollback, SaveAndKill. Clear-after-test modes: Clogged:False. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/to_8.0.0/CycleTestRestart-1.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/to_8.0.0/CycleTestRestart-2.toml -->
# Research: sources/storage-engines/foundationdb/tests/restarting/to_8.0.0/CycleTestRestart-2.toml

- **Purpose:** Restarting simulation stage for `CycleTestRestart-2`. It participates in a two-file restart workflow that saves state, restarts under version constraints, and validates upgrade/downgrade behavior.
- **Source facts:** 41 lines, 817 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles Clogged, workloads Attrition(2), Cycle, RandomClogging, Rollback, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (Clogged) and schedules each block's workload list (Clogged:5). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Because it is under `restarting/`, it may intentionally save or consume simulated state across paired `-1`/`-2` files via restart-info artifacts.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: Attrition(2), Cycle, RandomClogging, Rollback. Top-level keys: configuration, knobs. Configuration/test knobs: maxTLogVersion=7, disableTss=True, Clogged.runSetup=False, Clogged/Cycle.testDuration=10.0, Clogged/Cycle.transactionsPerSecond=2500.0, Clogged/Cycle.nodeCount=2500, Clogged/RandomClogging.testDuration=10.0, Clogged/Rollback.testDuration=10.0, Clogged/Rollback.meanDelay=10.0, Clogged/Attrition.testDuration=10.0, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3, Clogged/Attrition.machinesToKill=10, Clogged/Attrition.machinesToLeave=3.
- **Integration points:** Integrated by suite location `restarting` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/restarting/to_8.0.0/CycleTestRestart-2.toml` through the Python TestRunner/CTest path.
- **Risks:** Fault-injection workloads can make failures seed-sensitive; regressions may require preserving the CMake seed and trace output. Restarting tests depend on exact version-directory semantics and paired stage ordering; moving files can change RestartTestPolicy binary selection.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for Attrition(2), Cycle, RandomClogging, Rollback. Clear-after-test modes: none. Timeouts: none.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/restarting/to_8.0.0/CycleTestRestart-2.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ApiCorrectness.toml -->
# Research: sources/storage-engines/foundationdb/tests/slow/ApiCorrectness.toml

- **Purpose:** Slow simulation test specification for `ApiCorrectness`. It runs a longer or more exhaustive workload than the fast/rare variants.
- **Source facts:** 25 lines, 571 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles ApiCorrectnessTest, workloads ApiCorrectness, top-level keys none.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (ApiCorrectnessTest) and schedules each block's workload list (ApiCorrectnessTest:1). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: ApiCorrectness. Top-level keys: none. Configuration/test knobs: ApiCorrectnessTest.runSetup=True.
- **Integration points:** Integrated by suite location `slow` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/slow/ApiCorrectness.toml` through the Python TestRunner/CTest path.
- **Risks:** Main risk is workload-name or knob drift against the simulator's accepted TOML schema.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for ApiCorrectness. Clear-after-test modes: ApiCorrectnessTest:True. Timeouts: ApiCorrectnessTest:2100.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ApiCorrectness.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ApiCorrectnessAtomicRestore.toml -->
# Research: sources/storage-engines/foundationdb/tests/slow/ApiCorrectnessAtomicRestore.toml

- **Purpose:** Slow simulation test specification for `ApiCorrectnessAtomicRestore`. It runs a longer or more exhaustive workload than the fast/rare variants.
- **Source facts:** 40 lines, 958 bytes, executable=False.
- **Important APIs/types/functions:** Declarative TOML contract: 1 test block(s), titles ApiCorrectnessTest, workloads ApiCorrectness, AtomicRestore, top-level keys configuration, knobs.
- **Control flow:** The TestRunner passes this TOML to fdbserver simulation with `-f`. The simulator iterates 1 `[[test]]` block(s) (ApiCorrectnessTest) and schedules each block's workload list (ApiCorrectnessTest:2). Workload ordering, durations, clear-after-test settings, and failure-injection workloads determine the control flow inside simulation.
- **State and persistence:** The file is declarative and persists no state by itself. Runtime state is created by the simulation engine, including simulated database contents, backup/restore artifacts, restart information, logs, or workload-specific key ranges named by the workloads. Backup-oriented workloads add simulated backup agent and restore state that must survive fault injection long enough for correctness validation.
- **Dependencies:** Depends on the FoundationDB simulator workload registry for: ApiCorrectness, AtomicRestore. Top-level keys: configuration, knobs. Configuration/test knobs: ApiCorrectnessTest.simBackupAgents='BackupToFile', ApiCorrectnessTest.runSetup=True, ApiCorrectnessTest/AtomicRestore.restoreAfter=50.0.
- **Integration points:** Integrated by suite location `slow` and consumed by `fdbserver -r simulation -f sources/storage-engines/foundationdb/tests/slow/ApiCorrectnessAtomicRestore.toml` through the Python TestRunner/CTest path.
- **Risks:** Backup/restore specs depend on simulated backup-agent mode, timing, and range selection; timing drift can mask restore validation failures.
- **Test signals:** Signals are simulator parse success, workload completion, trace absence/presence of severity 40, and any workload-specific invariants for ApiCorrectness, AtomicRestore. Clear-after-test modes: ApiCorrectnessTest:False. Timeouts: ApiCorrectnessTest:2100.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/slow/ApiCorrectnessAtomicRestore.toml -->
