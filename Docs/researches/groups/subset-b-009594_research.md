# Research: subset-b-009594

Grouped source research for GCSFuse perfmetrics benchmark scripts, wrappers, configs, utilities, and VM metric fixtures. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/renaming_benchmark.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/renaming_benchmark.py

## Purpose
Runs the HNS-vs-flat folder rename benchmark. It validates a generated folder configuration, mounts the bucket with the correct GCSFuse HNS or flat flags, times alternating `mv` operations for simple and nested folders, computes latency statistics, waits for Cloud Monitoring lag, fetches VM metrics, and optionally uploads both result families to Google Sheets.

## Important APIs, Types, And Functions
`_run_rename_benchmark`, `_perform_testing`, `_record_time_of_operation`, `_record_time_for_folder_rename`, `_parse_results`, `_compute_metrics_from_time_of_operation`, `_get_values_to_export`, `_extract_vm_metrics`, `_upload_to_gsheet`, and CLI parsing. Constants select sheet tabs and the monitoring instance hostname.

## Control Flow
The CLI requires a config path and `hns` or `flat`. `_run_rename_benchmark` loads JSON, delegates schema/existence checks to `generate_folders_and_files`, mounts using `mount_gcs_bucket`, records rename timings per folder, summarizes latency rows, sleeps 360 seconds for monitoring data availability, fetches VM metric rows for the same time ranges, then either prints or uploads.

## State And Persistence Behavior
Creates `/tmp/config.yml`, creates and removes a local mount directory named after the bucket through the mount helper, mutates benchmark folders by renaming them back and forth, changes process CWD around Google Sheets credential lookup, and sleeps before reading Cloud Monitoring data.

## Dependencies
Uses `numpy`, `statistics`, `gcsfuse`, `gcloud`, Google Sheets helper, VM metrics helper, `generate_folders_and_files`, and the shared mount/dependency utilities.

## Integration Points
Called by `run_rename_benchmark.sh` in VM/Kokoro style jobs and depends on prior population of config-declared folders. Its output rows align with `rename_metrics_*` and `vm_metrics_*` worksheets.

## Risks And Edge Cases
Most shell calls interpolate folder names with `shell=True`; unusual names can break commands. `stat.stdev` fails for one sample, mount errors drop into an interactive shell rather than raising, and the fixed 360 second sleep dominates runtime. CWD changes make credential path assumptions fragile.

## Test Signals
Unit coverage exercises file counting, rename command sequencing, mount flag selection, metric computation/export row shape, upload error handling, and high-level `_run_rename_benchmark` branches with mocks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/renaming_benchmark.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/renaming_benchmark_test.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/renaming_benchmark_test.py

## Purpose
Unit tests for the rename benchmark helper functions and top-level orchestration branches.

## Important APIs, Types, And Functions
Uses `unittest`, `mock.patch`, `call`, and `mock_open` to isolate subprocess, time, mount, JSON, Google Sheets, and VM metric behavior.

## Control Flow
Tests construct small folder-config dictionaries, patch external effects, invoke private helpers directly, and assert timing lists, time intervals, subprocess calls, generated export rows, and upload calls.

## State And Persistence Behavior
No durable state is intended; all filesystem, sleep, subprocess, and network-facing work is mocked. One duplicate `test_get_upload_value_for_vm_metrics` method shadows the earlier identical definition.

## Dependencies
Depends on the local `renaming_benchmark` module and the legacy `mock` package as well as stdlib `unittest`.

## Integration Points
Documents the expected contract for `run_rename_benchmark.sh` and for worksheet upload rows consumed downstream.

## Risks And Edge Cases
The tests assert implementation details but do not run real GCSFuse, Cloud Monitoring, or credential flows. Some fixture shapes differ from production config shape, so mount-flag tests can miss nested-folder assumptions.

## Test Signals
This file is itself the signal; it covers most pure functions but leaves CLI parsing, dependency checks, and real subprocess failure behavior thin.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/renaming_benchmark_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/requirements.in -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/requirements.in

## Purpose
Rename benchmark Python dependency input.

## Important APIs, Types, And Functions
Dependency input file for pip-compile or equivalent lock generation; no executable API.

## Control Flow
Includes argparse/statistics plus numpy and Google API/auth/monitoring packages for statistics, Sheets upload, and VM metrics.

## State And Persistence Behavior
No runtime state; compiled `requirements.txt` is installed by sibling wrappers with `--require-hashes`.

## Dependencies
Includes argparse/statistics plus numpy and Google API/auth/monitoring packages for statistics, Sheets upload, and VM metrics.

## Integration Points
Compiled to hashed `requirements.txt` consumed by `run_rename_benchmark.sh`.

## Risks And Edge Cases
Mixes stdlib module names (`argparse`, `statistics`) with third-party packages; pinned transitive versions are only in compiled output.

## Test Signals
Validated indirectly when wrapper scripts install the compiled requirements and import dependent modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/requirements.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/run_rename_benchmark.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/run_rename_benchmark.sh

## Purpose
Installs FUSE/pip and Python requirements, installs Ops Agent, fetches Sheets credentials, installs latest gcloud, and runs the HNS rename benchmark with user-supplied upload flags.

## Important APIs, Types, And Functions
Shell entry point with positional arguments and local helper functions where defined.

## Control Flow
It is a VM/Kokoro wrapper around `renaming_benchmark.py`; flat-bucket execution is currently commented out.

## State And Persistence Behavior
System package installs, Ops Agent install, credential copy from `gs://periodic-perf-tests/creds.json`, and gcloud replacement are persistent host mutations.

## Dependencies
Requires sudo apt, curl, gcloud storage access, `requirements.txt` generated from the sibling `.in`, and a config-hns JSON file.

## Integration Points
Part of the GCSFuse perfmetrics automation under the same source tree.

## Risks And Edge Cases
Risks include broad host mutation, no argument validation, commented flat path reducing comparison coverage, and reliance on relative paths.

## Test Signals
No direct tests in this subset unless invoked by a higher-level Kokoro or wrapper job.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/run_rename_benchmark.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/install_bash.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/install_bash.sh

## Purpose
Builds and installs a requested GNU Bash version into `/usr/local/bin/bash`.

## Important APIs, Types, And Functions
Shell entry point with positional arguments and local helper functions where defined.

## Control Flow
It installs build tools if needed, downloads `bash-$version.tar.gz`, configures with readline, compiles with all cores, and installs with sudo.

## State And Persistence Behavior
Mutates `/usr/local`, uses temporary source and log directories, and can install build-essential/wget.

## Dependencies
Depends on apt/dnf/yum, gcc, make, wget, tar, sudo, and GNU build tooling.

## Integration Points
Part of the GCSFuse perfmetrics automation under the same source tree.

## Risks And Edge Cases
No checksum verification, version is interpolated into download URL, and host package mutation is broad.

## Test Signals
No direct tests in this subset unless invoked by a higher-level Kokoro or wrapper job.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/install_bash.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/install_go.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/install_go.sh

## Purpose
Installs a requested Go version under `/usr/local/go` with architecture detection from `os_utils.sh`.

## Important APIs, Types, And Functions
Shell entry point with positional arguments and local helper functions where defined.

## Control Flow
It maps host arch to Go arch, installs `wget`/`tar`, downloads the Linux tarball, removes any existing `/usr/local/go`, extracts the new version, and verifies `go version`.

## State And Persistence Behavior
Replaces system Go under `/usr/local/go` and exports PATH only for the current shell.

## Dependencies
Depends on `os_utils.sh`, sudo, distro package managers, wget, tar, and go.dev downloads.

## Integration Points
Part of the GCSFuse perfmetrics automation under the same source tree.

## Risks And Edge Cases
No checksum verification; unsupported arch returns failure; replacing Go can affect other jobs on the host.

## Test Signals
No direct tests in this subset unless invoked by a higher-level Kokoro or wrapper job.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/install_go.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/install_latest_gcloud.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/install_latest_gcloud.sh

## Purpose
Installs the latest Google Cloud SDK and alpha component into `/usr/local/google-cloud-sdk`.

## Important APIs, Types, And Functions
Shell entry point with positional arguments and local helper functions where defined.

## Control Flow
It first runs `upgrade_python3.sh`, sets `CLOUDSDK_PYTHON`, downloads the rapid Cloud SDK tarball, removes any existing SDK, runs install, updates components, installs alpha, and prints version.

## State And Persistence Behavior
Mutates `/usr/local`, installs a local Python 3.11.9 under `$HOME/.local`, and changes PATH for the current process.

## Dependencies
Depends on `upgrade_python3.sh`, wget, sudo, Cloud SDK install scripts, and network access.

## Integration Points
Part of the GCSFuse perfmetrics automation under the same source tree.

## Risks And Edge Cases
No checksum pinning; installing latest SDK makes runs less reproducible, but it is needed for HNS/zonal compatibility in this suite.

## Test Signals
No direct tests in this subset unless invoked by a higher-level Kokoro or wrapper job.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/install_latest_gcloud.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/config-hns.json -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/config-hns.json

## Purpose
HNS listing benchmark config for bucket `list-benchmark-tests-hns`.

## Important APIs, Types, And Functions
JSON/configuration document rather than executable code.

## Control Flow
Same twelve one-kilobyte file-count cases as the flat config, targeted at the HNS bucket.

## State And Persistence Behavior
No state by itself; the benchmark creates bucket/local structures described here.

## Dependencies
Depends on the listing benchmark `Directory` schema.

## Integration Points
Used to compare HNS listing behavior with the same workload shape.

## Risks And Edge Cases
The 1M folder can be very expensive and is name-skipped by default in benchmark code.

## Test Signals
Exercised indirectly by listing benchmark parsing and directory-creation tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/config-hns.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/config.json -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/config.json

## Purpose
Flat listing benchmark config for bucket `list-benchmark-tests`.

## Important APIs, Types, And Functions
JSON/configuration document rather than executable code.

## Control Flow
Declares twelve top-level test folders from 1,000 through 1,000,000 one-kilobyte files and no nested subdirectories.

## State And Persistence Behavior
No state by itself; the benchmark creates bucket/local structures described here.

## Dependencies
Depends on the listing benchmark `Directory` schema.

## Integration Points
Consumed by `listing_benchmark.py` through the `Directory` protobuf schema.

## Risks And Edge Cases
Large counts make setup expensive; 1M case is skipped unless `--run_1m_test` is set.

## Test Signals
Exercised indirectly by listing benchmark parsing and directory-creation tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/directory.proto -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/directory.proto

## Purpose
Defines the recursive directory schema used by listing benchmarks and config JSON parsing.

## Important APIs, Types, And Functions
Package `perfmetrics` with message `Directory`: `name`, `num_files`, `file_name_prefix`, `file_size`, `num_folders`, and repeated child `folders`.

## Control Flow
JSON configs are parsed into this type with `ParseDict`; recursive benchmark helpers traverse `folders`, use file fields to create workloads, and validate actual bucket listings against the declared counts.

## State And Persistence Behavior
No runtime state; this is the source schema for generated Python code.

## Dependencies
Requires proto3 tooling and generated `directory_pb2.py` for Python consumers.

## Integration Points
Used by `listing_benchmark.py`, its tests, and `config*.json` files.

## Risks And Edge Cases
No validation constraints encode file-size units or count consistency; callers must treat zero defaults carefully.

## Test Signals
Exercised indirectly by listing benchmark tests that parse fixture dictionaries into `Directory` messages.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/directory.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/directory_pb2.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/directory_pb2.py

## Purpose
Generated Python protobuf bindings for `directory.proto`.

## Important APIs, Types, And Functions
Exports `Directory` and `DESCRIPTOR`, with self-recursive `folders` field metadata.

## Control Flow
Imported by listing benchmark scripts and tests, then populated via `ParseDict` from JSON configs.

## State And Persistence Behavior
No durable state; module registration occurs with the protobuf symbol database at import time.

## Dependencies
Generated for the classic Python protobuf runtime APIs such as descriptors, reflection, and symbol database.

## Integration Points
Must stay in sync with `directory.proto` and with the protobuf runtime pinned by `ls_metrics/requirements.in` and wrapper environment.

## Risks And Edge Cases
Generated-code/runtime version mismatch can raise descriptor errors; the wrapper sets `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python` to reduce this risk.

## Test Signals
Indirectly covered by `listing_benchmark_test.py` fixture parsing and field traversal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/directory_pb2.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/listing_benchmark.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/listing_benchmark.py

## Purpose
Benchmarks recursive listing or another supplied command against a GCSFuse-mounted bucket and a local persistent-disk mirror, then exports comparable latency summaries to Google Sheets and optionally BigQuery.

## Important APIs, Types, And Functions
`_count_number_of_files_and_folders`, `_get_values_to_export`, `_parse_results`, `_record_time_of_operation`, `_perform_testing`, `_create_directory_structure`, `_list_directory`, `_compare_directory_structure`, `_export_to_gsheet`, `_export_to_bigquery`, and CLI parsing. Global `RUN_1M_TEST` controls whether the 1M-file case is skipped.

## Control Flow
Main parses JSON into `Directory` protobuf, checks whether GCS already has the requested tree, deletes/recreates persistent-disk and temporary generation directories, optionally clears the bucket, generates files locally and in GCS, mounts with supplied flags, times the command for each top-level test folder on both media, computes statistics, uploads selected outputs, cleans the local tree, and unmounts.

## State And Persistence Behavior
Creates/removes `persistent_disk`, `generate_files.TEMPORARY_DIRECTORY`, the mount directory, and bucket contents when the structure mismatches. It mutates global `RUN_1M_TEST` from CLI state and uses process CWD changes for Sheets credentials.

## Dependencies
Uses generated `directory_pb2`, `google.protobuf.json_format.ParseDict`, `generate_files`, `gcloud storage`, `gcsfuse`, `numpy`, Sheets helpers, BigQuery helpers, and shared mount/dependency utilities.

## Integration Points
Driven by `run_ls_benchmark.sh`, with configs `config.json` and `config-hns.json`. Its BigQuery upload targets the experiments table constants and prepends mount type to row payloads.

## Risks And Edge Cases
Heavy use of `shell=True`, recursive deletion of bucket and local paths, and unchecked command strings makes input trust important. The 1M-file skip is name-based. Statistics require enough samples for stdev, and generated protobuf version compatibility is handled externally by the wrapper.

## Test Signals
Companion tests cover recursive file/folder counting, metrics formatting, timing, tree creation, structure comparison, export calls, and 1M-file skip behavior with subprocesses mocked.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/listing_benchmark.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/listing_benchmark_test.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/listing_benchmark_test.py

## Purpose
Regression tests for listing benchmark pure logic and mocked subprocess interactions.

## Important APIs, Types, And Functions
Defines several `Directory` protobuf fixtures through `ParseDict`, expected metric rows, and `unittest` cases around listing benchmark helpers.

## Control Flow
The suite validates counting recursion, statistical parse output, worksheet export calls, timing calculations, recursive directory creation, GCS directory comparison, and the global `RUN_1M_TEST` filter.

## State And Persistence Behavior
It does not persist state; all GCS listing and file generation effects are mocked. Global patching of `RUN_1M_TEST` demonstrates expected inclusion/exclusion of the 1M-file test.

## Dependencies
Depends on `directory_pb2`, `google.protobuf`, `mock`, and the local `listing_benchmark` module.

## Integration Points
Serves as executable documentation for config and proto contracts consumed by the listing benchmark.

## Risks And Edge Cases
The suite does not execute the main CLI, real bucket deletion, real `gcsfuse`, BigQuery upload, or cleanup paths, so deployment failures remain possible.

## Test Signals
Coverage is broad for helper functions, especially tree comparison edge cases and recursive file generation call ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/listing_benchmark_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/requirements.in -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/requirements.in

## Purpose
Listing benchmark dependency input.

## Important APIs, Types, And Functions
Dependency input file for pip-compile or equivalent lock generation; no executable API.

## Control Flow
Includes argparse/configparser/statistics, numpy, mock, and protobuf 5.29.* for tests and generated `directory_pb2` use.

## State And Persistence Behavior
No runtime state; compiled `requirements.txt` is installed by sibling wrappers with `--require-hashes`.

## Dependencies
Includes argparse/configparser/statistics, numpy, mock, and protobuf 5.29.* for tests and generated `directory_pb2` use.

## Integration Points
Compiled requirements are installed by `run_ls_benchmark.sh`.

## Risks And Edge Cases
The wrapper must set protobuf Python implementation for generated-code compatibility.

## Test Signals
Validated indirectly when wrapper scripts install the compiled requirements and import dependent modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/requirements.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/run_ls_benchmark.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/run_ls_benchmark.sh

## Purpose
Sets protobuf runtime compatibility, installs FUSE/pip and hashed requirements, then runs `listing_benchmark.py` for a supplied config with `ls -R`, 30 samples, upload flags, and spreadsheet id.

## Important APIs, Types, And Functions
Shell entry point with positional arguments and local helper functions where defined.

## Control Flow
It bridges periodic jobs to listing benchmarks for flat or HNS configs depending on the passed config file and GCSFuse flags.

## State And Persistence Behavior
Installs packages in user environment and sets `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python` for the process.

## Dependencies
Requires sudo apt, pip hashes, `listing_benchmark.py`, and caller-provided `GCSFUSE_FLAGS`, upload flags, sheet id, and config file.

## Integration Points
Part of the GCSFuse perfmetrics automation under the same source tree.

## Risks And Edge Cases
Argument order is positional and unvalidated; wrapper assumes `requirements.txt` exists and that user-site packages are importable.

## Test Signals
No direct tests in this subset unless invoked by a higher-level Kokoro or wrapper job.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ls_metrics/run_ls_benchmark.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/helper.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/helper.py

## Purpose
Shared helper for single-thread microbenchmarks: mount/unmount a bucket with GCSFuse, log throughput to BigQuery, and compare recent BigQuery bandwidth history against thresholds.

## Important APIs, Types, And Functions
`mount_bucket`, `unmount_gcs_directory`, `log_to_bigquery`, `get_last_n_days_bandwidth_entries`, and `check_and_alert_bandwidth`. Constants define the BigQuery project, dataset, and table.

## Control Flow
Mount helpers shell out to `gcsfuse` and `fusermount`. Logging computes MB/s, builds a pandas DataFrame, and loads it into BigQuery. Validation queries the last N days for a workload type and exits with status 1 if the historical average is below threshold.

## State And Persistence Behavior
Creates mount directories, mounts FUSE filesystems, writes BigQuery rows, and can terminate the process on alert failure.

## Dependencies
Uses `google-cloud-bigquery`, `pandas`, `subprocess`, and local GCSFuse installation.

## Integration Points
Imported by `read_single_thread.py` and `write_single_thread.py`; orchestrated by `run_microbenchmark.sh`.

## Risks And Edge Cases
The BigQuery query interpolates `workload_type` into SQL, threshold logic compares historical average rather than current run, and mount flags are passed through a shell command string.

## Test Signals
Unit tests mock subprocess and BigQuery clients, covering success/failure branches for mounts, unmounts, and BigQuery load exceptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/helper.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/helper_test.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/helper_test.py

## Purpose
Unit tests for microbenchmark helper functions.

## Important APIs, Types, And Functions
Uses `unittest.mock.patch` and `MagicMock` to validate subprocess and BigQuery interactions.

## Control Flow
Tests call helper functions under mocked success and failure conditions, then assert boolean returns or propagated exceptions.

## State And Persistence Behavior
No persistent state; directory creation, subprocesses, and BigQuery load jobs are mocked.

## Dependencies
Depends on `helper`, `subprocess`, and stdlib unittest mocks.

## Integration Points
Confirms the helper contract consumed by read/write benchmark scripts.

## Risks And Edge Cases
Does not cover SQL query construction, alert exit behavior, or actual pandas-to-BigQuery schema compatibility.

## Test Signals
Covers mount/unmount success and failure plus BigQuery load success and failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/helper_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/read_single_thread.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/read_single_thread.py

## Purpose
Measures single-thread read bandwidth through a GCSFuse mount after ensuring fixed-size test objects exist in the target bucket.

## Important APIs, Types, And Functions
`check_and_create_files`, `read_all_files`, and CLI `main`. Constants define mount directory `gcs` and `testfile_read` prefix.

## Control Flow
Main mounts the bucket, uses the Cloud Storage client to create or repair missing test files with `fallocate` and upload, reads all expected files through the mount, unmounts, logs throughput to BigQuery, and checks a 160 MB/s threshold.

## State And Persistence Behavior
Creates temporary `/tmp` files, uploads GCS objects, reads from the FUSE mount, removes local temp files, writes BigQuery rows, and exits nonzero on read or threshold failures.

## Dependencies
Uses `google-cloud-storage`, local `helper`, `fallocate`, GCSFuse, and filesystem IO.

## Integration Points
Called by `run_microbenchmark.sh` with a production bucket, 10 files, and 15GB file size by default.

## Risks And Edge Cases
Reads entire files into memory with `f.read()`, so large defaults can stress RAM. Mount failure return is not checked before continuing. Object names are deterministic and shared across runs.

## Test Signals
Tests cover byte counting, read errors, missing/undersized/exact-size object handling, upload failure cleanup, and temp file removal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/read_single_thread.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/read_single_thread_test.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/read_single_thread_test.py

## Purpose
Unit tests for read microbenchmark file creation and read loops.

## Important APIs, Types, And Functions
Mocks builtins `open`, `os.path`, `subprocess.run`, `google.cloud.storage.Client`, and GCS blob methods.

## Control Flow
Tests validate expected path naming, successful byte totals, RuntimeError wrapping on IO failures, and object upload decisions for missing, small, and correctly sized blobs.

## State And Persistence Behavior
All filesystem and GCS effects are mocked, including cleanup through `os.remove`.

## Dependencies
Depends on local `read_single_thread` and stdlib unittest mocks.

## Integration Points
Captures the contract used by the periodic microbenchmark wrapper.

## Risks And Edge Cases
Does not exercise CLI `main`, mount failures, BigQuery logging, or memory use from real large reads.

## Test Signals
Good focused coverage for helper branches; integration behavior remains untested.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/read_single_thread_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/requirements.in -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/requirements.in

## Purpose
Single-thread microbenchmark dependency input.

## Important APIs, Types, And Functions
Dependency input file for pip-compile or equivalent lock generation; no executable API.

## Control Flow
Includes pandas, BigQuery and Storage clients, pyarrow, pandas_gbq, google-crc32c, psutil, and setuptools.

## State And Persistence Behavior
No runtime state; compiled `requirements.txt` is installed by sibling wrappers with `--require-hashes`.

## Dependencies
Includes pandas, BigQuery and Storage clients, pyarrow, pandas_gbq, google-crc32c, psutil, and setuptools.

## Integration Points
Installed in a venv by `run_microbenchmark.sh` before read/write benchmark scripts run.

## Risks And Edge Cases
Heavy analytics dependencies can make setup slow; helper.py also relies on BigQuery auth.

## Test Signals
Validated indirectly when wrapper scripts install the compiled requirements and import dependent modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/requirements.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/run_microbenchmark.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/run_microbenchmark.sh

## Purpose
Builds and installs the current GCSFuse checkout, prepares a Python venv, then runs the single-thread read and write microbenchmarks.

## Important APIs, Types, And Functions
Shell entry point with positional arguments and local helper functions where defined.

## Control Flow
Installs base packages, changes to `$HOME/github/gcsfuse`, builds gcsfuse with the current short commit id, cleans stale mounts, installs hashed Python requirements, runs read and write benchmark scripts with log-file flags, uploads failure logs to a GCS artifact bucket, and exits nonzero if either benchmark fails.

## State And Persistence Behavior
Creates `venv`, unmounts any existing gcsfuse mounts, writes temporary log files under `/tmp`, installs gcsfuse on the host, and can copy logs to `gs://gcsfuse-kokoro-logs/...`.

## Dependencies
Depends on apt, git, Python venv, gcloud storage, `build_and_install_gcsfuse.sh`, the microbenchmark Python scripts, and bucket `single-threaded-tests`.

## Integration Points
Part of the GCSFuse perfmetrics automation under the same source tree.

## Risks And Edge Cases
Assumes a fixed checkout path and bucket name; mount cleanup scans all gcsfuse mounts on the host; failure-log upload assumes gcloud auth and artifact bucket permissions.

## Test Signals
No direct tests in this subset unless invoked by a higher-level Kokoro or wrapper job.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/run_microbenchmark.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/write_single_thread.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/write_single_thread.py

## Purpose
Measures single-thread write bandwidth through a GCSFuse mount by writing deterministic numbers of random binary files.

## Important APIs, Types, And Functions
`delete_existing_file`, `write_random_file`, `create_files`, and CLI `main`. Constants define mount directory `gcs` and object prefix `testfile`.

## Control Flow
Main mounts the bucket, builds target paths, deletes existing objects through the mount, writes random bytes with `os.urandom`, unmounts, logs throughput to BigQuery, and checks an 80 MB/s historical threshold.

## State And Persistence Behavior
Creates/removes files on the mounted bucket, writes BigQuery rows, and may exit the process on delete/write/threshold failures.

## Dependencies
Uses local `helper`, GCSFuse, Python filesystem APIs, and BigQuery through helper.

## Integration Points
Called by `run_microbenchmark.sh` with one 15GB file by default.

## Risks And Edge Cases
`os.urandom(file_size)` materializes the entire file payload in memory, which is risky for 15GB writes. Mount failures are not checked before writes, and `create_files` can return `None` only for some exception paths.

## Test Signals
Tests cover delete behavior, random file writes, aggregate byte count, and failure exit when write fails.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/write_single_thread.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/write_single_thread_test.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/write_single_thread_test.py

## Purpose
Unit tests for write microbenchmark filesystem helpers.

## Important APIs, Types, And Functions
Imports `create_files`, `delete_existing_file`, and `write_random_file` directly and patches `os.path.exists`, `os.remove`, `open`, and `os.urandom`.

## Control Flow
Tests validate existing-file deletion, missing-file no-op, write success/failure, aggregate size calculation, and SystemExit on create failure.

## State And Persistence Behavior
No durable state because all local IO is mocked.

## Dependencies
Depends on local `write_single_thread` and stdlib unittest mocks.

## Integration Points
Protects the write helper contract used by the CLI and periodic wrapper.

## Risks And Edge Cases
Does not cover mount/unmount, BigQuery logging, threshold check, or the real memory behavior of large `os.urandom` calls.

## Test Signals
Focused helper coverage with mocked IO.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/micro_benchmarks/write_single_thread_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ml_tests/checkpoint/Jax/emulated_checkpoints.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/ml_tests/checkpoint/Jax/emulated_checkpoints.py

## Purpose
Creates a synthetic JAX/Flax training state and writes repeated checkpoints to a supplied directory, exercising GCSFuse checkpoint write behavior.

## Important APIs, Types, And Functions
`SimpleModel` Flax module, `train_step`, and CLI arguments `--checkpoint_dir` and `--num_train_steps`.

## Control Flow
Initializes random sample data and a deep dense model, builds an Adam train state, performs one gradient update, then loops over training steps and saves a checkpoint every 200 steps with prefix `checkpoint_` and `keep=100`.

## State And Persistence Behavior
Writes checkpoint files to the supplied directory, which the wrapper mounts on flat, HNS, and zonal buckets.

## Dependencies
Uses JAX, Flax, Optax, and `flax.training.checkpoints` with dependencies pinned in the sibling requirements file.

## Integration Points
Called by `run_checkpoints.sh` after mounting target buckets with streaming writes enabled.

## Risks And Edge Cases
The model is very large for a mock workload, checkpoint writes can be expensive, and only one real train step occurs before repeated saves. Failure handling is left to the wrapper process.

## Test Signals
No direct unit test in this subset; integration signal is the shell wrapper running it against multiple bucket types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ml_tests/checkpoint/Jax/emulated_checkpoints.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ml_tests/checkpoint/Jax/requirements.in -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/ml_tests/checkpoint/Jax/requirements.in

## Purpose
Pinned JAX/Flax checkpoint dependency set.

## Important APIs, Types, And Functions
Dependency input file for pip-compile or equivalent lock generation; no executable API.

## Control Flow
Pins JAX, jaxlib, flax, optax, orbax-checkpoint/tensorstore-related packages, numpy/scipy, protobuf, and rich UI dependencies.

## State And Persistence Behavior
No runtime state; compiled `requirements.txt` is installed by sibling wrappers with `--require-hashes`.

## Dependencies
Pins JAX, jaxlib, flax, optax, orbax-checkpoint/tensorstore-related packages, numpy/scipy, protobuf, and rich UI dependencies.

## Integration Points
Installed in the checkpoint wrapper venv with hashes before running `emulated_checkpoints.py`.

## Risks And Edge Cases
Tightly pinned versions improve reproducibility but require compatible Python and platform wheels.

## Test Signals
Validated indirectly when wrapper scripts install the compiled requirements and import dependent modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ml_tests/checkpoint/Jax/requirements.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ml_tests/checkpoint/Jax/run_checkpoints.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/ml_tests/checkpoint/Jax/run_checkpoints.sh

## Purpose
Kokoro-style driver for JAX checkpoint tests across flat, HNS, and zonal buckets.

## Important APIs, Types, And Functions
Defines `mount_gcsfuse_and_run_test`, installs Go/gcloud/Python dependencies, builds GCSFuse, creates a venv, and launches three background checkpoint workloads.

## Control Flow
Installs Go, upgrades gcloud/Python, builds `gcsfuse`, installs JAX requirements, determines zone and architecture, clears each target bucket, mounts with streaming writes and trace logs, runs `emulated_checkpoints.py`, waits for all three background jobs, and fails if any job fails.

## State And Persistence Behavior
Deletes objects from test buckets, writes logs under `KOKORO_ARTIFACTS_DIR/gcsfuse_logs`, creates mount points under `$HOME/gcs`, creates a venv, and runs background processes.

## Dependencies
Requires Kokoro env vars, Go, gcloud alpha storage, Python 3.11, JAX dependencies, and Google metadata server.

## Integration Points
Invoked from presubmit build logic when checkpoint label is present.

## Risks And Edge Cases
No explicit unmount in the function, bucket cleanup is broad, and parallel jobs share the same built source tree. Architecture is taken from `dpkg --print-architecture` for Go tarball naming.

## Test Signals
No local tests; success is process exit status from the three checkpoint workloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ml_tests/checkpoint/Jax/run_checkpoints.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ml_tests/setup_host.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/ml_tests/setup_host.sh

## Purpose
Prepares a VM host for ML container workloads by installing Ops Agent, Docker, NVIDIA drivers, and NVIDIA container tooling.

## Important APIs, Types, And Functions
Single shell entry point taking `DRIVER_VERSION` as `$1`.

## Control Flow
Adds Google Ops Agent repository, installs common apt packages, configures Docker apt repo and Docker Engine, downloads and runs the Tesla NVIDIA driver installer, adds NVIDIA container toolkit repository, installs toolkit, and restarts Docker.

## State And Persistence Behavior
Mutates apt sources/keyrings, installs system packages, downloads a driver `.run` file, installs kernel driver components, and restarts Docker.

## Dependencies
Ubuntu apt, curl, gpg, Docker upstream repo, NVIDIA driver and container toolkit repositories.

## Integration Points
Supports ML perf/checkpoint workloads that need containerized GPU runtime.

## Risks And Edge Cases
Assumes Ubuntu, x86_64 Tesla driver URL, sudo privileges, and compatible kernel headers. It uses deprecated `apt-key` for one key path.

## Test Signals
No tests in this subset; validation is implicit through successful host provisioning.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/ml_tests/setup_host.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/os_utils.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/os_utils.sh

## Purpose
Shared shell utilities for OS detection, Go architecture mapping, and distro-aware package installation.

## Important APIs, Types, And Functions
`get_os_id`, `get_go_arch`, and `install_packages_by_os`; guarded against multiple sourcing with `_OS_UTILS_SH_LOADED`.

## Control Flow
Reads `/etc/os-release`, maps `uname -m` to Go arch strings, and dispatches package installation across apt, yum-family, and pacman systems with name remapping for Python/fuse packages.

## State And Persistence Behavior
Runs package-manager commands and may install Python CRC dependencies via pip using a repo requirements file.

## Dependencies
Requires `readlink`, distro package managers, sudo, optional `fuser`, and `OS_UTILS_DIR` path relation to tools requirements.

## Integration Points
Sourced by `install_go.sh` and suitable for other perfmetric installers.

## Risks And Edge Cases
Apt lock retry only wraps `apt-get update`, not install. RHEL `python3-crcmod` install path depends on a relative requirements file outside this subset.

## Test Signals
No tests here; behavior is covered only by scripts that source it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/os_utils.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/populate_metrics.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/populate_metrics.sh

## Purpose
Installs top-level perfmetrics requirements, fetches Sheets credentials, and runs `populate_vm_metrics.py` for a start/end range.

## Important APIs, Types, And Functions
Shell entry point with positional arguments and local helper functions where defined.

## Control Flow
It is a small operational wrapper for manual or scheduled VM metric backfill.

## State And Persistence Behavior
Installs user Python dependencies and writes credentials under `./gsheet`.

## Dependencies
Depends on pip hash requirements, gcloud storage access, and valid CLI times.

## Integration Points
Part of the GCSFuse perfmetrics automation under the same source tree.

## Risks And Edge Cases
No argument validation beyond the Python script; credentials path is relative.

## Test Signals
No direct tests in this subset unless invoked by a higher-level Kokoro or wrapper job.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/populate_metrics.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/populate_vm_metrics.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/populate_vm_metrics.py

## Purpose
Fetches VM metric summaries for a supplied time range and writes them to the `ml_metrics` Google Sheet tab.

## Important APIs, Types, And Functions
CLI takes `<start_time> <end_time>`, computes period, and calls `VmMetrics.fetch_metrics_and_write_to_google_sheet` with operation `read`.

## Control Flow
Validates argument count, waits 250 seconds for Cloud Monitoring samples, constructs a `VmMetrics` client, parses epoch boundaries, derives period, and delegates fetch/upload.

## State And Persistence Behavior
Sleeps, performs Cloud Monitoring reads, and writes Google Sheet output through the VM metrics helper.

## Dependencies
Uses `socket.gethostname`, `time`, and `vm_metrics.vm_metrics`; `populate_metrics.sh` installs requirements and fetches credentials.

## Integration Points
Paired with `populate_metrics.sh` and used for ML model metric backfill.

## Risks And Edge Cases
Fixed wait time, no validation that end is after start, and unused `metric_data_name` constant suggests older output contracts.

## Test Signals
No direct tests in this subset; VM metrics JSON fixtures support the underlying helper tests elsewhere.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/populate_vm_metrics.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit/fetch_results.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit/fetch_results.py

## Purpose
Extracts selected fio metrics from a presubmit fio JSON output and appends compact values to `result.txt`.

## Important APIs, Types, And Functions
CLI expects one fio JSON path, imports `FioMetrics` from `perfmetrics/scripts/fio/fio_metrics.py`, and writes size/read-write bandwidth lines.

## Control Flow
Loads fio metrics, iterates returned workload records, writes file size once for read rows, then writes bandwidth in MiB/s for each operation.

## State And Persistence Behavior
Appends to `result.txt` in the current working directory.

## Dependencies
Depends on fio metrics parser and a specific current-directory layout where `./perfmetrics/scripts/` is importable.

## Integration Points
Called by `presubmit/run_load_test_on_presubmit.sh`; consumed by `print_results.py` after master and PR runs append their data.

## Risks And Edge Cases
Hard-coded append order and line counts; no context manager; assumes `rw == read` identifies the start of each file-size group.

## Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit/fetch_results.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit/print_results.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit/print_results.py

## Purpose
Formats presubmit benchmark comparison data from `result.txt` as a PrettyTable comparing master and PR branches.

## Important APIs, Types, And Functions
Reads all lines from `result.txt`; constants `DATA_DIMENSION=5` and `DATA_SET_SPLIT_INDEX=15` define expected layout.

## Control Flow
Builds a table with branch, file size, and four bandwidth columns, then loops over three file-size groups for master and PR data.

## State And Persistence Behavior
Reads `result.txt` and prints the table to stdout.

## Dependencies
Requires `prettytable` and the exact output order produced by two `fetch_results.py` runs.

## Integration Points
Called by the PR perf Kokoro build after master and PR fio runs.

## Risks And Edge Cases
No length checks; malformed or missing result data causes index errors or misleading rows.

## Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit/print_results.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit/run_load_test_on_presubmit.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit/run_load_test_on_presubmit.sh

## Purpose
Runs the presubmit fio workload and appends parsed results to `result.txt`.

## Important APIs, Types, And Functions
Shell entry point with positional arguments and local helper functions where defined.

## Control Flow
Calls fio with `presubmit_perf_test.fio`, JSON output, and latency percentiles, then invokes `presubmit/fetch_results.py`.

## State And Persistence Behavior
Creates `output.json` and appends `result.txt` through the Python parser.

## Dependencies
Depends on fio and the repo-relative presubmit scripts.

## Integration Points
Part of the GCSFuse perfmetrics automation under the same source tree.

## Risks And Edge Cases
No cleanup or mount handling; it assumes caller has mounted the correct `gcs` path.

## Test Signals
No direct tests in this subset unless invoked by a higher-level Kokoro or wrapper job.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit/run_load_test_on_presubmit.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit_test/pr_perf_test/build.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit_test/pr_perf_test/build.sh

## Purpose
Kokoro presubmit dispatcher that runs expensive performance, integration, package, checkpoint, Orbax, and machine-type tests only when the PR carries opt-in labels.

## Important APIs, Types, And Functions
Defines label constants, `execute_perf_test`, `install_requirements`, and `execute_gke_test`; uses Kokoro env vars and GitHub pull request metadata.

## Control Flow
Fetches PR JSON, checks labels, installs Go and Python dependencies, fetches PR refs, and conditionally runs master/PR fio comparison, integration tests on zonal or non-zonal buckets, package build tests, JAX checkpoints, Orbax GKE benchmark, or machine-type GKE test.

## State And Persistence Behavior
Modifies `.git/config`, checks out branches, mounts/unmounts buckets, writes `result.txt`, installs packages, and creates benchmark artifacts/logs.

## Dependencies
Requires Kokoro artifacts layout, GitHub API, Go, gcsfuse build, fio installer, BigQuery and presubmit requirements, and multiple repo scripts.

## Integration Points
Referenced by `presubmit.cfg`; ties this subset's presubmit scripts and checkpoint script into PR validation.

## Risks And Edge Cases
Label detection uses grep over raw JSON, no API error handling, broad environment assumptions, and branch checkouts happen in-place.

## Test Signals
No unit tests; Kokoro config and label-gated execution are the validation path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit_test/pr_perf_test/build.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit_test/pr_perf_test/presubmit.cfg -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit_test/pr_perf_test/presubmit.cfg

## Purpose
Kokoro presubmit configuration for PR performance tests.

## Important APIs, Types, And Functions
JSON/configuration document rather than executable code.

## Control Flow
Defines artifact collection regexes for failed integration logs, gcsfuse logs, and sponge logs, then points `build_file` at `pr_perf_test/build.sh`.

## State And Persistence Behavior
No state by itself; the benchmark creates bucket/local structures described here.

## Dependencies
Depends on the listing benchmark `Directory` schema.

## Integration Points
Integrates the label-gated build shell script into Kokoro.

## Risks And Edge Cases
Artifact strip prefix assumes Kokoro checkout layout.

## Test Signals
Exercised indirectly by listing benchmark parsing and directory-creation tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit_test/pr_perf_test/presubmit.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit_test/pr_perf_test/requirements.in -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit_test/pr_perf_test/requirements.in

## Purpose
Presubmit PR perf Python dependency input.

## Important APIs, Types, And Functions
Dependency input file for pip-compile or equivalent lock generation; no executable API.

## Control Flow
Lists google-cloud, Vision/API client, and prettytable for presubmit scripts and reporting.

## State And Persistence Behavior
No runtime state; compiled `requirements.txt` is installed by sibling wrappers with `--require-hashes`.

## Dependencies
Lists google-cloud, Vision/API client, and prettytable for presubmit scripts and reporting.

## Integration Points
Installed by `build.sh` along with BigQuery requirements before optional perf tests.

## Risks And Edge Cases
Broad unpinned Google packages can drift unless compiled hash output is used.

## Test Signals
Validated indirectly when wrapper scripts install the compiled requirements and import dependent modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/presubmit_test/pr_perf_test/requirements.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/read_cache/generate_yml_config.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/read_cache/generate_yml_config.sh

## Purpose
Generates a GCSFuse read-cache `config.yml` from environment variables.

## Important APIs, Types, And Functions
Shell entry point with positional arguments and local helper functions where defined.

## Control Flow
Writes write, logging, cache-dir, file-cache, and metadata-cache settings with defaults for cache directory, max size, and range-read caching.

## State And Persistence Behavior
Overwrites `config.yml` in the current directory.

## Dependencies
Depends on environment variables such as `TTL_SECS` and `STAT_CACHE_MAX_SIZE_MB` being present.

## Integration Points
Part of the GCSFuse perfmetrics automation under the same source tree.

## Risks And Edge Cases
Unset required env vars can produce invalid config because `set -e` does not guard here-doc expansion for missing values without `set -u`.

## Test Signals
No direct tests in this subset unless invoked by a higher-level Kokoro or wrapper job.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/read_cache/generate_yml_config.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/read_cache/mount_gcsfuse.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/read_cache/mount_gcsfuse.sh

## Purpose
Mounts the read-cache benchmark bucket with generated config and optional debug logging.

## Important APIs, Types, And Functions
Shell entry point with positional arguments and local helper functions where defined.

## Control Flow
Parses flags for cache size, bucket, cache dir, range-read caching, metadata cache size, and logging; unmounts a stale mount, sleeps, generates config, and runs gcsfuse with stackdriver export.

## State And Persistence Behavior
Uses `$WORKING_DIR`, creates `$WORKING_DIR/gcs`, writes config and log files, and may unmount existing FUSE mounts.

## Dependencies
Depends on gcsfuse, mountpoint, umount, ps/grep/awk, and `generate_yml_config.sh`.

## Integration Points
Part of the GCSFuse perfmetrics automation under the same source tree.

## Risks And Edge Cases
Uses unquoted variables in several places; process-id detection by grep is heuristic; the stale-unmount sleep documents a real cache-race mitigation.

## Test Signals
No direct tests in this subset unless invoked by a higher-level Kokoro or wrapper job.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/read_cache/mount_gcsfuse.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/read_cache/run_read_cache_fio_workload.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/read_cache/run_read_cache_fio_workload.sh

## Purpose
Runs epoch-based fio read or random-read workload against a prepared read-cache mount.

## Important APIs, Types, And Functions
Shell entry point with positional arguments and local helper functions where defined.

## Control Flow
Validates workload dir, `WORKING_DIR`, and read type; drops caches; primes metadata cache with `ls -R`; then loops epochs running fio with environment variables and drops page cache between epochs.

## State And Persistence Behavior
Mutates kernel caches via `/proc/sys/vm/drop_caches`, prints memory stats, and executes fio from the repo job file.

## Dependencies
Depends on sudo, fio, `free`, valid `WORKING_DIR`, and `job_files/read_cache_load_test.fio`.

## Integration Points
Part of the GCSFuse perfmetrics automation under the same source tree.

## Risks And Edge Cases
Requires root privileges for cache dropping; `workload_dir` can be unset if `-d` is omitted; typo in read-type error text is harmless.

## Test Signals
No direct tests in this subset unless invoked by a higher-level Kokoro or wrapper job.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/read_cache/run_read_cache_fio_workload.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/read_cache/setup.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/read_cache/setup.sh

## Purpose
Provisions a VM for read-cache fio experiments, including local SSD RAID, fio from source, Go, gcsfuse, and helper aliases.

## Important APIs, Types, And Functions
Shell entry point with positional arguments and local helper functions where defined.

## Control Flow
Creates RAID0 over four local NVMe SSDs if needed, installs fio 3.36 from source with a percentile-range patch, clones gcsfuse, installs Go from `.go-version`, installs gcsfuse from master, mounts the benchmark bucket, and appends env/aliases to bashrc.

## State And Persistence Behavior
Formats and mounts `/dev/md0`, writes `$HOME/working_dir`, mutates `~/.bashrc`, installs system packages, and installs Go/gcsfuse binaries.

## Dependencies
Depends on four Google local SSD devices, mdadm, apt, git, Go downloads, fio source, and GitHub access.

## Integration Points
Part of the GCSFuse perfmetrics automation under the same source tree.

## Risks And Edge Cases
Very destructive if local SSD assumptions are wrong; installs gcsfuse from `master` rather than the checked-out source under test.

## Test Signals
No direct tests in this subset unless invoked by a higher-level Kokoro or wrapper job.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/read_cache/setup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/requirements.in -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/requirements.in

## Purpose
Top-level perfmetrics script dependency input.

## Important APIs, Types, And Functions
Dependency input file for pip-compile or equivalent lock generation; no executable API.

## Control Flow
Pins Cloud Monitoring, grpc, protobuf, Google auth/API clients, requests, pytest, and test helper dependencies.

## State And Persistence Behavior
No runtime state; compiled `requirements.txt` is installed by sibling wrappers with `--require-hashes`.

## Dependencies
Pins Cloud Monitoring, grpc, protobuf, Google auth/API clients, requests, pytest, and test helper dependencies.

## Integration Points
Installed by generic load/VM metric wrappers before fetch/upload scripts run.

## Risks And Edge Cases
Version set is old in places and may conflict with subdirectory-specific protobuf pins if installed into the same user environment.

## Test Signals
Validated indirectly when wrapper scripts install the compiled requirements and import dependent modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/requirements.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/run_load_test_and_fetch_metrics.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/run_load_test_and_fetch_metrics.sh

## Purpose
Runs a fio load test against a mounted GCSFuse bucket, unmounts it, then fetches and uploads fio metrics.

## Important APIs, Types, And Functions
Shell entry point with positional arguments and local helper functions where defined.

## Control Flow
It installs pip/fio, mounts a passed bucket under `gcs`, records start/end epoch times, runs `seq_rand_read_write.fio` with JSON output, unmounts, installs Python requirements, fetches credentials, and invokes `fetch_and_upload_metrics.py`.

## State And Persistence Behavior
Creates `gcs`, produces `fio-output${EXPERIMENT_NUMBER}.json`, installs user packages, and writes credentials under `gsheet`.

## Dependencies
Depends on Kokoro artifact layout, fio installer, gcsfuse binary, job file, pip requirements, gcloud storage, and spreadsheet id.

## Integration Points
Part of the GCSFuse perfmetrics automation under the same source tree.

## Risks And Edge Cases
Mount flags and bucket are unquoted; if fio fails, set -e prevents unmount cleanup; environment variable `EXPERIMENT_NUMBER` is assumed.

## Test Signals
No direct tests in this subset unless invoked by a higher-level Kokoro or wrapper job.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/run_load_test_and_fetch_metrics.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/testing_on_gke/examples/requirements.in -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/testing_on_gke/examples/requirements.in

## Purpose
GKE example workload dependency input.

## Important APIs, Types, And Functions
Dependency input file for pip-compile or equivalent lock generation; no executable API.

## Control Flow
Contains absl, Google Cloud Storage/API, Monitoring, and BigQuery clients needed by fio/dlio Helm generators and parsers.

## State And Persistence Behavior
No runtime state; compiled `requirements.txt` is installed by sibling wrappers with `--require-hashes`.

## Dependencies
Contains absl, Google Cloud Storage/API, Monitoring, and BigQuery clients needed by fio/dlio Helm generators and parsers.

## Integration Points
Installed in a local venv by `run-gke-tests.sh`.

## Risks And Edge Cases
Unpinned input depends on compiled hash output for reproducibility.

## Test Signals
Validated indirectly when wrapper scripts install the compiled requirements and import dependent modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/testing_on_gke/examples/requirements.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/testing_on_gke/examples/run-gke-tests.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/testing_on_gke/examples/run-gke-tests.sh

## Purpose
Standalone end-to-end GKE performance test harness for deploying fio/dlio workloads with the GCSFuse CSI driver, optionally building a custom CSI driver from local gcsfuse code.

## Important APIs, Types, And Functions
Large shell entry point controlled by environment variables. Key functions include `create_unique_experiment_id`, `verify_csi_driver_image`, `installDependencies`, `ensureGkeCluster`, `createCustomCsiDriverIfNeeded`, `deployAllFioHelmCharts`, `deployAllDlioHelmCharts`, `waitTillAllPodsComplete`, `fetchAndParseFioOutputs`, and `fetchAndParseDlioOutputs`.

## Control Flow
Validates env config, installs local tooling, authenticates gcloud, creates or updates GKE resources, prepares namespace/KSA, ensures source repos, optionally builds and publishes gcsfuse plus CSI image, deploys Helm charts, monitors pods until completion or timeout, cleans pods, and parses outputs to CSV/BigQuery. In `only_parse` mode it skips creation/deployment and only monitors/parses an existing experiment.

## State And Persistence Behavior
Creates clusters/node pools/namespaces/service accounts, builds images, writes binaries to GCS, clones repos, creates venv/tool installs, deploys/uninstalls Helm charts, mounts zonal buckets for output download, writes `fio/output.csv` and `dlio/output.csv`, and uploads parsed metrics.

## Dependencies
Requires gcloud, kubectl, helm, Docker, Go, jq, Python requirements, GKE APIs, GCS buckets, CSI driver repo, gcsfuse repo, and workload config JSON.

## Integration Points
Lives under `testing_on_gke/examples` and calls the fio/dlio chart generators and parsers in sibling directories. It is also referenced from presubmit paths for GKE benchmarks.

## Risks And Edge Cases
Mutates cloud resources, can run for a week by default, uses many unquoted shell expansions, and contains force-update code that may reset local repos when requested. Zonal output download relies on temporary gcsfuse mounts.

## Test Signals
No shell tests in this subset; runtime validation is via successful pod completion and parser output generation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/testing_on_gke/examples/run-gke-tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/upgrade_python3.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/upgrade_python3.sh

## Purpose
Builds Python 3.11.9 from source under `$HOME/.local/python-3.11.9` for gcloud compatibility.

## Important APIs, Types, And Functions
Shell entry point with positional arguments and local helper functions where defined.

## Control Flow
Installs build dependencies using apt or yum, downloads Python source to `/tmp`, configures with optimizations, builds with `nproc`, and runs `make altinstall`.

## State And Persistence Behavior
Mutates system packages and local user prefix, leaves source under `/tmp/Python-3.11.9` unless overwritten by later runs.

## Dependencies
Depends on apt/yum, compiler toolchain, development libraries, wget, make, and network access.

## Integration Points
Part of the GCSFuse perfmetrics automation under the same source tree.

## Risks And Edge Cases
Build from source is slow, unpinned by checksum, and only handles apt/yum families.

## Test Signals
No direct tests in this subset unless invoked by a higher-level Kokoro or wrapper job.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/upgrade_python3.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/utils/checks_util.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/utils/checks_util.py

## Purpose
Checks required command-line dependencies before benchmark execution.

## Important APIs, Types, And Functions
`check_dependencies(packages, log)` loops over package names, logs the check, runs `<package> --version`, logs an error and opens `bash` on failure.

## Control Flow
`check_dependencies(packages, log)` loops over package names, logs the check, runs `<package> --version`, logs an error and opens `bash` on failure.

## State And Persistence Behavior
No persistent state, but failed checks can leave the process in an interactive shell.

## Dependencies
Uses Python stdlib and local benchmark conventions.

## Integration Points
Used by rename and listing benchmarks before invoking `gcloud`, `gsutil`, or `gcsfuse`.

## Risks And Edge Cases
Opening `bash` is unsuitable for noninteractive automation and does not raise a Python exception.

## Test Signals
Covered by the sibling test file when present.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/utils/checks_util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/utils/metrics_util.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/utils/metrics_util.py

## Purpose
Removes old log/output files from a directory while retaining the newest names by reverse lexical sort.

## Important APIs, Types, And Functions
`remove_old_files(logging_dir, num_files_retain)` lists files, sorts descending, and removes entries after the retain count; CLI passes directory and count from argv.

## Control Flow
`remove_old_files(logging_dir, num_files_retain)` lists files, sorts descending, and removes entries after the retain count; CLI passes directory and count from argv.

## State And Persistence Behavior
Deletes files from the target logging directory.

## Dependencies
Uses Python stdlib and local benchmark conventions.

## Integration Points
Used by perf scripts that cap retained fio output files.

## Risks And Edge Cases
Lexical sort is only correct if filenames encode time/order consistently; imported `typing` is unused.

## Test Signals
Covered by the sibling test file when present.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/utils/metrics_util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/utils/metrics_util_test.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/utils/metrics_util_test.py

## Purpose
Unit tests for log-retention deletion behavior.

## Important APIs, Types, And Functions
Creates temporary `fio_log_test/log_dir`, populates numbered files, calls `remove_old_files`, and asserts remaining names.

## Control Flow
Creates temporary `fio_log_test/log_dir`, populates numbered files, calls `remove_old_files`, and asserts remaining names.

## State And Persistence Behavior
Creates and removes a local test directory with `os.system`.

## Dependencies
Uses Python stdlib and local benchmark conventions.

## Integration Points
Covers fewer-than, zero, and more-than retention scenarios.

## Risks And Edge Cases
Uses shell `rm -r`/`touch`; tests rely on current working directory.

## Test Signals
Covered by the sibling test file when present.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/utils/metrics_util_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/utils/mount_unmount_util.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/utils/mount_unmount_util.py

## Purpose
Shared GCSFuse mount/unmount helpers for Python benchmarks.

## Important APIs, Types, And Functions
`mount_gcs_bucket(bucket_name, gcsfuse_flags, log)` creates a same-named directory and runs `gcsfuse`; `unmount_gcs_bucket(gcs_bucket, log)` runs lazy `umount -l` and removes the directory.

## Control Flow
`mount_gcs_bucket(bucket_name, gcsfuse_flags, log)` creates a same-named directory and runs `gcsfuse`; `unmount_gcs_bucket(gcs_bucket, log)` runs lazy `umount -l` and removes the directory.

## State And Persistence Behavior
Creates/removes local mount directories and mutates mounted filesystems.

## Dependencies
Uses Python stdlib and local benchmark conventions.

## Integration Points
Imported by rename and listing benchmarks.

## Risks And Edge Cases
Uses shell interpolation and drops into interactive `bash` on errors; return value is `None` on mount failure.

## Test Signals
Covered by the sibling test file when present.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/utils/mount_unmount_util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/utils/mount_unmount_util_test.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/utils/mount_unmount_util_test.py

## Purpose
Unit tests for shared mount/unmount helper command sequencing.

## Important APIs, Types, And Functions
Patches `subprocess.call`, invokes success and error branches, and asserts `mkdir`, `gcsfuse`, `umount -l`, `rm -rf`, and fallback `bash` calls.

## Control Flow
Patches `subprocess.call`, invokes success and error branches, and asserts `mkdir`, `gcsfuse`, `umount -l`, `rm -rf`, and fallback `bash` calls.

## State And Persistence Behavior
No real mounts; all subprocesses are mocked.

## Dependencies
Uses Python stdlib and local benchmark conventions.

## Integration Points
Protects command strings relied on by benchmark scripts.

## Risks And Edge Cases
Does not verify logging calls or real failure behavior.

## Test Signals
Covered by the sibling test file when present.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/utils/mount_unmount_util_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/load_avg_os_threads_mean_response.json -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/load_avg_os_threads_mean_response.json

## Purpose
Agent CPU 1-minute load metric fixture used by VM metrics parser tests.

## Important APIs, Types, And Functions
Static Cloud Monitoring time-series JSON containing metric type `agent.googleapis.com/cpu/load_1m`, metric kind `GAUGE`, and point values under `double_value`.

## Control Flow
The VM metrics helper loads this payload to exercise extraction of mean load/OS thread style values over 120-second intervals from `points`, `interval`, and `value` fields.

## State And Persistence Behavior
No state; immutable testdata fixture.

## Dependencies
Depends on Cloud Monitoring response shape and parser code in the `vm_metrics` package.

## Integration Points
Supports tests for `vm_metrics` aggregation used by rename/load/ML metric upload scripts.

## Risks And Edge Cases
Fixture values are synthetic/static and may not represent all API response variants such as empty point sets or alternate labels.

## Test Signals
The presence of mean/peak and int/double/distribution variants gives parser tests coverage over the major value types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/load_avg_os_threads_mean_response.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/mean_cpu_utilization_response.json -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/mean_cpu_utilization_response.json

## Purpose
Mean CPU utilization fixture used by VM metrics parser tests.

## Important APIs, Types, And Functions
Static Cloud Monitoring time-series JSON containing metric type `compute.googleapis.com/instance/cpu/utilization`, metric kind `GAUGE`, and point values under `double_value`.

## Control Flow
The VM metrics helper loads this payload to exercise extraction of mean CPU samples for a GCE instance from `points`, `interval`, and `value` fields.

## State And Persistence Behavior
No state; immutable testdata fixture.

## Dependencies
Depends on Cloud Monitoring response shape and parser code in the `vm_metrics` package.

## Integration Points
Supports tests for `vm_metrics` aggregation used by rename/load/ML metric upload scripts.

## Risks And Edge Cases
Fixture values are synthetic/static and may not represent all API response variants such as empty point sets or alternate labels.

## Test Signals
The presence of mean/peak and int/double/distribution variants gives parser tests coverage over the major value types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/mean_cpu_utilization_response.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/mean_memory_usage_response.json -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/mean_memory_usage_response.json

## Purpose
Mean memory percent-used fixture used by VM metrics parser tests.

## Important APIs, Types, And Functions
Static Cloud Monitoring time-series JSON containing metric type `agent.googleapis.com/memory/percent_used`, metric kind `GAUGE`, and point values under `double_value`.

## Control Flow
The VM metrics helper loads this payload to exercise extraction of mean memory usage samples from `points`, `interval`, and `value` fields.

## State And Persistence Behavior
No state; immutable testdata fixture.

## Dependencies
Depends on Cloud Monitoring response shape and parser code in the `vm_metrics` package.

## Integration Points
Supports tests for `vm_metrics` aggregation used by rename/load/ML metric upload scripts.

## Risks And Edge Cases
Fixture values are synthetic/static and may not represent all API response variants such as empty point sets or alternate labels.

## Test Signals
The presence of mean/peak and int/double/distribution variants gives parser tests coverage over the major value types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/mean_memory_usage_response.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/mean_received_bytes_count_response.json -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/mean_received_bytes_count_response.json

## Purpose
Mean received network bytes fixture used by VM metrics parser tests.

## Important APIs, Types, And Functions
Static Cloud Monitoring time-series JSON containing metric type `compute.googleapis.com/instance/network/received_bytes_count`, metric kind `GAUGE`, and point values under `double_value`.

## Control Flow
The VM metrics helper loads this payload to exercise extraction of mean received-byte counts from `points`, `interval`, and `value` fields.

## State And Persistence Behavior
No state; immutable testdata fixture.

## Dependencies
Depends on Cloud Monitoring response shape and parser code in the `vm_metrics` package.

## Integration Points
Supports tests for `vm_metrics` aggregation used by rename/load/ML metric upload scripts.

## Risks And Edge Cases
Fixture values are synthetic/static and may not represent all API response variants such as empty point sets or alternate labels.

## Test Signals
The presence of mean/peak and int/double/distribution variants gives parser tests coverage over the major value types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/mean_received_bytes_count_response.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/mean_sent_bytes_count_response.json -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/mean_sent_bytes_count_response.json

## Purpose
Mean sent network bytes fixture used by VM metrics parser tests.

## Important APIs, Types, And Functions
Static Cloud Monitoring time-series JSON containing metric type `compute.googleapis.com/instance/network/sent_bytes_count`, metric kind `GAUGE`, and point values under `double_value`.

## Control Flow
The VM metrics helper loads this payload to exercise extraction of mean sent-byte counts from `points`, `interval`, and `value` fields.

## State And Persistence Behavior
No state; immutable testdata fixture.

## Dependencies
Depends on Cloud Monitoring response shape and parser code in the `vm_metrics` package.

## Integration Points
Supports tests for `vm_metrics` aggregation used by rename/load/ML metric upload scripts.

## Risks And Edge Cases
Fixture values are synthetic/static and may not represent all API response variants such as empty point sets or alternate labels.

## Test Signals
The presence of mean/peak and int/double/distribution variants gives parser tests coverage over the major value types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/mean_sent_bytes_count_response.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/ops_error_count_response.json -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/ops_error_count_response.json

## Purpose
GCSFuse operation error count fixture used by VM metrics parser tests.

## Important APIs, Types, And Functions
Static Cloud Monitoring time-series JSON containing metric type `custom.googleapis.com/gcsfuse/fs/ops_error_count`, metric kind `DELTA`, and point values under `int64_value`.

## Control Flow
The VM metrics helper loads this payload to exercise extraction of delta error counts from `points`, `interval`, and `value` fields.

## State And Persistence Behavior
No state; immutable testdata fixture.

## Dependencies
Depends on Cloud Monitoring response shape and parser code in the `vm_metrics` package.

## Integration Points
Supports tests for `vm_metrics` aggregation used by rename/load/ML metric upload scripts.

## Risks And Edge Cases
Fixture values are synthetic/static and may not represent all API response variants such as empty point sets or alternate labels.

## Test Signals
The presence of mean/peak and int/double/distribution variants gives parser tests coverage over the major value types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/ops_error_count_response.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/ops_mean_latency_response.json -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/ops_mean_latency_response.json

## Purpose
GCSFuse operation latency distribution fixture used by VM metrics parser tests.

## Important APIs, Types, And Functions
Static Cloud Monitoring time-series JSON containing metric type `custom.googleapis.com/gcsfuse/fs/ops_latency`, metric kind `DELTA`, and point values under `distribution_value`.

## Control Flow
The VM metrics helper loads this payload to exercise extraction of distribution mean latency for ReadFile operations from `points`, `interval`, and `value` fields.

## State And Persistence Behavior
No state; immutable testdata fixture.

## Dependencies
Depends on Cloud Monitoring response shape and parser code in the `vm_metrics` package.

## Integration Points
Supports tests for `vm_metrics` aggregation used by rename/load/ML metric upload scripts.

## Risks And Edge Cases
Fixture values are synthetic/static and may not represent all API response variants such as empty point sets or alternate labels.

## Test Signals
The presence of mean/peak and int/double/distribution variants gives parser tests coverage over the major value types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/ops_mean_latency_response.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/peak_cpu_utilization_response.json -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/peak_cpu_utilization_response.json

## Purpose
Peak CPU utilization fixture used by VM metrics parser tests.

## Important APIs, Types, And Functions
Static Cloud Monitoring time-series JSON containing metric type `compute.googleapis.com/instance/cpu/utilization`, metric kind `GAUGE`, and point values under `double_value`.

## Control Flow
The VM metrics helper loads this payload to exercise extraction of peak CPU samples from `points`, `interval`, and `value` fields.

## State And Persistence Behavior
No state; immutable testdata fixture.

## Dependencies
Depends on Cloud Monitoring response shape and parser code in the `vm_metrics` package.

## Integration Points
Supports tests for `vm_metrics` aggregation used by rename/load/ML metric upload scripts.

## Risks And Edge Cases
Fixture values are synthetic/static and may not represent all API response variants such as empty point sets or alternate labels.

## Test Signals
The presence of mean/peak and int/double/distribution variants gives parser tests coverage over the major value types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/peak_cpu_utilization_response.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/peak_memory_usage_response.json -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/peak_memory_usage_response.json

## Purpose
Peak memory percent-used fixture used by VM metrics parser tests.

## Important APIs, Types, And Functions
Static Cloud Monitoring time-series JSON containing metric type `agent.googleapis.com/memory/percent_used`, metric kind `GAUGE`, and point values under `double_value`.

## Control Flow
The VM metrics helper loads this payload to exercise extraction of peak memory samples from `points`, `interval`, and `value` fields.

## State And Persistence Behavior
No state; immutable testdata fixture.

## Dependencies
Depends on Cloud Monitoring response shape and parser code in the `vm_metrics` package.

## Integration Points
Supports tests for `vm_metrics` aggregation used by rename/load/ML metric upload scripts.

## Risks And Edge Cases
Fixture values are synthetic/static and may not represent all API response variants such as empty point sets or alternate labels.

## Test Signals
The presence of mean/peak and int/double/distribution variants gives parser tests coverage over the major value types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/peak_memory_usage_response.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/peak_received_bytes_count_response.json -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/peak_received_bytes_count_response.json

## Purpose
Peak received network bytes fixture used by VM metrics parser tests.

## Important APIs, Types, And Functions
Static Cloud Monitoring time-series JSON containing metric type `compute.googleapis.com/instance/network/received_bytes_count`, metric kind `GAUGE`, and point values under `int64_value`.

## Control Flow
The VM metrics helper loads this payload to exercise extraction of peak received-byte counts from `points`, `interval`, and `value` fields.

## State And Persistence Behavior
No state; immutable testdata fixture.

## Dependencies
Depends on Cloud Monitoring response shape and parser code in the `vm_metrics` package.

## Integration Points
Supports tests for `vm_metrics` aggregation used by rename/load/ML metric upload scripts.

## Risks And Edge Cases
Fixture values are synthetic/static and may not represent all API response variants such as empty point sets or alternate labels.

## Test Signals
The presence of mean/peak and int/double/distribution variants gives parser tests coverage over the major value types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/peak_received_bytes_count_response.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/peak_sent_bytes_count_response.json -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/peak_sent_bytes_count_response.json

## Purpose
Peak sent network bytes fixture used by VM metrics parser tests.

## Important APIs, Types, And Functions
Static Cloud Monitoring time-series JSON containing metric type `compute.googleapis.com/instance/network/sent_bytes_count`, metric kind `GAUGE`, and point values under `int64_value`.

## Control Flow
The VM metrics helper loads this payload to exercise extraction of peak sent-byte counts from `points`, `interval`, and `value` fields.

## State And Persistence Behavior
No state; immutable testdata fixture.

## Dependencies
Depends on Cloud Monitoring response shape and parser code in the `vm_metrics` package.

## Integration Points
Supports tests for `vm_metrics` aggregation used by rename/load/ML metric upload scripts.

## Risks And Edge Cases
Fixture values are synthetic/static and may not represent all API response variants such as empty point sets or alternate labels.

## Test Signals
The presence of mean/peak and int/double/distribution variants gives parser tests coverage over the major value types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/peak_sent_bytes_count_response.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/read_bytes_count_response.json -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/read_bytes_count_response.json

## Purpose
GCSFuse read bytes fixture used by VM metrics parser tests.

## Important APIs, Types, And Functions
Static Cloud Monitoring time-series JSON containing metric type `custom.googleapis.com/gcsfuse/gcs/read_bytes_count`, metric kind `DELTA`, and point values under `int64_value`.

## Control Flow
The VM metrics helper loads this payload to exercise extraction of delta read-byte counts from `points`, `interval`, and `value` fields.

## State And Persistence Behavior
No state; immutable testdata fixture.

## Dependencies
Depends on Cloud Monitoring response shape and parser code in the `vm_metrics` package.

## Integration Points
Supports tests for `vm_metrics` aggregation used by rename/load/ML metric upload scripts.

## Risks And Edge Cases
Fixture values are synthetic/static and may not represent all API response variants such as empty point sets or alternate labels.

## Test Signals
The presence of mean/peak and int/double/distribution variants gives parser tests coverage over the major value types.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/vm_metrics/testdata/read_bytes_count_response.json -->
