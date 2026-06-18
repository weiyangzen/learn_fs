# Research Group subset-b-009592

Grouped research for gcsfuse OpenTelemetry metric tests and perfmetrics BigQuery, fio, package-build, and Kokoro continuous-test scripts. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/metrics/otel_metrics_test.go -->
# sources/user-network-fs/gcsfuse/metrics/otel_metrics_test.go

## Purpose

`otel_metrics_test.go` is an auto-generated Go test suite for the `metrics` package's OpenTelemetry-backed implementation. It verifies that `NewOTelMetrics` creates usable instruments and that every generated metric method emits the expected OpenTelemetry metric name, attribute set, value aggregation, and histogram unit conversion.

## Important APIs, Types, and Functions

The file defines two local map aliases, `metricValueMap` for attribute-encoded integer sums and `metricHistogramMap` for attribute-encoded `metricdata.HistogramDataPoint[int64]` values. `setupOTel` installs a `metric.ManualReader`-backed meter provider with `otel.SetMeterProvider`, calls `NewOTelMetrics(ctx, 10, 100)`, and returns the concrete `*otelMetrics` plus reader for assertions.

`gatherNonZeroCounterMetrics` collects `metricdata.Sum[int64]` data points and skips zero-valued points. `gatherHistogramMetrics` collects `metricdata.Histogram[int64]` data points and skips zero-count buckets. Both encode attributes with `attribute.DefaultEncoder`, which makes assertions stable across OpenTelemetry's attribute set ordering.

The test coverage is organized around generated methods on `otelMetrics`: buffered read fallback and read latency; file cache read bytes/count/latency; filesystem operation count, error count, and latency; streaming write fallback count; GCS download/read/reader/request/retry metrics; metadata cache read count; read block size histograms; and test-only up/down counters. Large table-driven sections enumerate all known `FsOp`, `GcsMethod`, open mode, fallback reason, read type, cache hit, lookup detail, entry status, retry category, and filesystem error category combinations.

## Control Flow

Each test creates a fresh context, meter provider, manual reader, and `otelMetrics` instance. The test invokes one or more metric methods, sleeps briefly through `waitForMetricsProcessing`, manually collects the provider state, and compares the encoded attribute-value map or histogram data point against expected values. Counter tests include simple cases, multiple calls that should aggregate by identical attributes, and negative increment cases. Histogram tests add durations or sizes, then assert data point count and sum.

The filesystem error count test is intentionally expansive: it cross-products error categories such as `DEVICE_ERROR`, `DIR_NOT_EMPTY`, `FILE_EXISTS`, `IO_ERROR`, `NETWORK_ERROR`, `NO_FILE_OR_DIR`, `PERM_ERROR`, `PROCESS_RESOURCE_MGMT_ERROR`, and `TOO_MANY_OPEN_FILES` with filesystem operations such as `BatchForget`, `CreateFile`, `LookUpInode`, `ReadFile`, `Rename`, `Unlink`, and `WriteFile`.

## State and Persistence Behavior

The tests mutate only process-local OpenTelemetry global provider state and the in-memory metric accumulators behind the manual reader. They do not persist files or external telemetry. Because `setupOTel` calls `otel.SetMeterProvider`, tests rely on each subtest replacing the global provider cleanly and are best kept serial unless the package's global metric initialization is proven parallel-safe.

## Dependencies and Integration Points

The suite depends on `github.com/stretchr/testify` for assertions, `go.opentelemetry.io/otel` global meter provider APIs, and `go.opentelemetry.io/otel/sdk/metric` manual collection types. It is tightly coupled to the generated `otelMetrics` implementation, metric names such as `fs/ops_count` and `gcs/request_latencies`, attribute names such as `fs_op`, `gcs_method`, `cache_hit`, and `lookup_detail`, and duration unit choices in the implementation.

This file is marked auto-generated, so the real integration point is the metric definition/generation pipeline that emits both the implementation and tests. Manual edits risk being overwritten and can hide generator defects.

## Risks and Edge Cases

The `waitForMetricsProcessing` sleep is small and assumes synchronous or near-synchronous SDK processing; it may become flaky if the implementation changes to asynchronous export behavior. `gatherNonZeroCounterMetrics` filters zeros, so tests cannot distinguish "not emitted" from "emitted zero" for sum instruments. Negative increments are expected to be ignored for monotonic counters but accepted for up/down counters; any mismatch between instrument type and generated method semantics will surface in these cases.

Histogram assertions check count and sum but not bucket boundaries or min/max, so bucket configuration regressions may escape this suite. The global provider replacement is another risk for parallelization or interaction with other tests in the `metrics` package.

## Test Signals

Strong signals are package tests that include this file, especially failures naming missing metrics or mismatched encoded attribute maps. Useful focused signals are counter aggregation tests, negative increment tests for monotonic vs up/down behavior, histogram count/sum checks for microsecond and millisecond conversions, and full cross-product coverage for filesystem operation/error attributes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/metrics/otel_metrics_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/bigquery/constants.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/bigquery/constants.py

## Purpose

`constants.py` centralizes the GCP project, BigQuery dataset, and table identifiers used by the perfmetrics BigQuery scripts.

## Important APIs, Types, and Functions

The module exports simple string constants: `PROJECT_ID = 'gcs-fuse-test-ml'`, `DATASET_ID = 'performance_metrics'`, `CONFIGURATION_TABLE_ID = 'experiment_configuration'`, `FIO_TABLE_ID = 'read_write_fio_metrics'`, `VM_TABLE_ID = 'read_write_vm_metrics'`, and `LS_TABLE_ID = 'list_metrics'`.

## Control Flow

There is no runtime control flow beyond module import. Importers read these constants to build BigQuery clients, table references, SQL strings, and upload targets.

## State and Persistence Behavior

The file holds static configuration only. It does not read environment variables or persist data. The constants determine where other scripts create datasets/tables and upload performance results.

## Dependencies and Integration Points

Primary importers include `experiments_gcsfuse_bq.py`, `get_experiments_config.py`, `setup.py`, and `experiments_gcsfuse_bq_test.py`. The values must match the actual BigQuery resources and IAM permissions used by Kokoro or local perfmetric runs.

## Risks and Edge Cases

Hard-coded project and dataset values make the scripts environment-specific. Running the scripts with credentials for another project still targets `gcs-fuse-test-ml` unless the code is changed. Renaming a table here without migrating existing BigQuery schema or downstream dashboards will disconnect metric uploads from consumers.

## Test Signals

Tests can assert that callers reference these constants instead of duplicating table names. Operational signals are successful BigQuery setup and upload jobs against `performance_metrics` and absence of "not found" or permission errors for the configured tables.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/bigquery/constants.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/bigquery/experiments_gcsfuse_bq.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/bigquery/experiments_gcsfuse_bq.py

## Purpose

`experiments_gcsfuse_bq.py` provides the BigQuery persistence layer for gcsfuse performance experiments. It creates the dataset and tables used by perfmetrics, manages experiment configuration IDs, validates configurations, and uploads metric rows.

## Important APIs, Types, and Functions

The main API is `ExperimentsGCSFuseBQ(project_id, dataset_id, bq_client=None)`. If no client is injected, it creates `google.cloud.bigquery.Client(project=project_id)`, making the class usable in production and testable with mocks.

`dataset_ref` retrieves the dataset through `client.get_dataset(self.dataset_id)`. `_get_table_from_table_id` resolves a table through `dataset_ref.table(table_id)` and `client.get_table`. `_execute_query` submits raw SQL through `client.query` and raises an exception if the returned job has errors. `_check_if_config_valid` tests for a `configuration_id` row in `experiment_configuration`.

`setup_dataset_and_tables` creates the dataset and four tables: `experiment_configuration`, `read_write_fio_metrics`, `read_write_vm_metrics`, and `list_metrics`. `get_experiment_configuration_id` either inserts a new configuration UUID, returns an existing configuration, or updates an existing end date. `upload_metrics_to_table` validates a config ID, prepends `(configuration_id, start_time_build)` to each metric row, and inserts the rows.

## Control Flow

Dataset setup creates a `bigquery.Dataset`, calls `create_dataset(..., exists_ok=True)`, waits 120 seconds, then executes `CREATE TABLE IF NOT EXISTS` statements for the configuration, fio, VM, and list metric schemas. The metric tables declare unenforced foreign keys back to the configuration table.

Configuration lookup first selects rows by `configuration_name`. Zero rows cause UUID generation and insertion. More than one row raises a data-corruption exception. One row is checked for matching `gcsfuse_flags` and `branch`; mismatches raise. Matching rows return the existing ID, with an update query issued when the stored end date differs from the requested end date.

Metric upload checks the configuration exists, gets the target table, transforms each metric row into a tuple with config metadata, and calls `_insert_rows`. `_insert_rows` treats any non-empty `insert_rows` result or raised exception as failure, then calls `_delete_rows_incomplete_transaction` to delete rows for the same table/config/start time before re-raising.

## State and Persistence Behavior

This module persists BigQuery datasets, tables, experiment configuration rows, and performance metric rows. It uses best-effort cleanup for failed multi-row insertions by deleting rows matching `configuration_id` and `start_time_build`. It does not use BigQuery transactions, parameterized queries, or schema migration versioning.

## Dependencies and Integration Points

Dependencies are `google.cloud.bigquery`, `google.cloud.bigquery.job.QueryJob`, Python `uuid` and `time`, and local `bigquery.constants`. It is invoked by the CLI wrapper `get_experiments_config.py`, the setup wrapper `setup.py`, perfmetrics upload scripts elsewhere under `perfmetrics/scripts`, and unit tests that inject a mock BigQuery client.

## Risks and Edge Cases

SQL strings are formatted with direct string interpolation, so quotes in flags, configuration names, or JSON config text can break queries and create injection risk. `dataset_ref` passes only `dataset_id` to `get_dataset`, which depends on the BigQuery client default project. The fixed `time.sleep(120)` slows setup and may still not guarantee readiness under control-plane delay.

`get_experiment_configuration_id` compares `end_date` with `is not`, which checks object identity rather than equality; that can trigger unnecessary updates or miss intended semantics. It checks only `gcsfuse_flags` and `branch`, not `config_file_flags_as_json`, when an existing `configuration_name` is reused. Error cleanup deletes all rows for the same config/start time, which can remove rows from a previous successful attempt if `start_time_build` is reused.

## Test Signals

`experiments_gcsfuse_bq_test.py` covers query execution errors, configuration validation, row insertion success/failure cleanup, setup query counts, new/existing configuration flows, end-date update flow, and upload validation. Integration signals are successful dataset/table creation, stable UUID reuse for matching configurations, and BigQuery upload rows containing the expected config and build timestamp prefixes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/bigquery/experiments_gcsfuse_bq.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/bigquery/experiments_gcsfuse_bq_test.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/bigquery/experiments_gcsfuse_bq_test.py

## Purpose

`experiments_gcsfuse_bq_test.py` is the unit test suite for `ExperimentsGCSFuseBQ`. It verifies BigQuery query handling, configuration lookup/insert/update behavior, insert cleanup on failures, setup behavior, and metrics upload validation without requiring live BigQuery calls.

## Important APIs, Types, and Functions

The suite defines representative constants for gcsfuse flags, config-file JSON text, branch, end dates, configuration names, valid/invalid IDs, and table ID. `TestExperimentsGCSFuseBQ.setUp` patches `bigquery.experiments_gcsfuse_bq.bigquery`, creates a mock client, and injects it into `ExperimentsGCSFuseBQ`.

Test methods cover `_check_if_config_valid`, `_execute_query`, `_insert_rows`, `setup_dataset_and_tables`, `get_experiment_configuration_id`, and `upload_metrics_to_table`. Mocks use `MagicMock`, patched `uuid.uuid4`, and `google.cloud.bigquery.table.Table` as a spec for table objects.

## Control Flow

Each test configures the mock BigQuery client or replaces private helper methods, invokes the target method, and asserts returned values, raised exception messages, and client call counts. Insert failure tests expect a cleanup `DELETE` query. Configuration tests simulate zero rows, one row, and changed end-date scenarios through mock query jobs and iterable rows.

## State and Persistence Behavior

No real BigQuery state is modified. The suite asserts intended persistence behavior indirectly by checking calls to `client.create_dataset`, `client.query`, `client.get_table`, and `client.insert_rows`.

## Dependencies and Integration Points

Dependencies are Python `unittest`, `uuid`, `unittest.mock`, `google.cloud.bigquery.table.Table`, local `bigquery.constants`, and `bigquery.experiments_gcsfuse_bq`. It is designed to run from `perfmetrics/scripts` as `python3 -m bigquery.experiments_gcsfuse_bq_test`.

## Risks and Edge Cases

The tests mirror current implementation details and include some argument-order expectations that expose fragility around `get_experiment_configuration_id`; one insert-new test calls the method with `BRANCH` and `CONFIG_FILE_FLAGS_AS_JSON` swapped relative to the function signature and asserts the resulting row order. Mocked query jobs may not fully match BigQuery client behavior, especially around `QueryJob.errors` timing and iteration. The tests do not cover SQL escaping, parameterization, missing optional CLI args, live schema compatibility, or IAM failures.

## Test Signals

Passing tests signal that the class-level control flow and mock client calls remain stable. High-value failures are changed exception text for query/insert errors, unexpected cleanup query shape, changed setup query count, duplicate or mismatched configuration behavior, and upload attempts for invalid config IDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/bigquery/experiments_gcsfuse_bq_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/bigquery/get_experiments_config.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/bigquery/get_experiments_config.py

## Purpose

`get_experiments_config.py` is a command-line wrapper that returns the BigQuery experiment configuration ID for a given gcsfuse performance configuration, creating or updating the row if needed.

## Important APIs, Types, and Functions

`parse_arguments(argv)` builds an `argparse.ArgumentParser` with required `--gcsfuse_flags`, `--branch`, `--end_date`, and `--config_name` arguments plus an optional `--config_file_flags_as_json`. Each argument uses `nargs=1`, so callers receive one-element lists. The main block creates `ExperimentsGCSFuseBQ(constants.PROJECT_ID, constants.DATASET_ID)`, calls `get_experiment_configuration_id`, and prints the returned ID.

## Control Flow

At startup the script parses `sys.argv`, constructs the BigQuery helper, extracts the first element from each parsed list, and delegates all database logic to `ExperimentsGCSFuseBQ.get_experiment_configuration_id`. The printed configuration ID is intended for shell scripts that need a stable ID before uploading metrics.

## State and Persistence Behavior

This script can persist a new `experiment_configuration` row or update the `end_date` of an existing row through the helper class. It does not write local files.

## Dependencies and Integration Points

Dependencies are local `bigquery.experiments_gcsfuse_bq`, local `bigquery.constants`, Python `argparse`, and BigQuery credentials available to the underlying client. It is intended to be run from `perfmetrics/scripts` as part of performance metric setup/upload workflows.

## Risks and Edge Cases

`parse_arguments` ignores its `argv` parameter by assigning `argv = sys.argv`, which makes direct unit testing with an injected argument list ineffective. `--config_file_flags_as_json` is declared optional but the main block unconditionally indexes `args.config_file_flags_as_json[0]`; omitting it raises before BigQuery logic runs. `nargs=1` complicates callers and makes all values lists until manually unwrapped.

Values are passed to downstream SQL string formatting without escaping, so shell quoting and special characters in flags or config JSON are operationally important.

## Test Signals

Useful tests are CLI parsing with all arguments, omitted optional config-file flags, injected argv behavior, and a mocked `ExperimentsGCSFuseBQ` verifying the exact argument order. Integration signals are a printed UUID and a corresponding row in `experiment_configuration`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/bigquery/get_experiments_config.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/bigquery/requirements.in -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/bigquery/requirements.in

## Purpose

`requirements.in` is the human-edited dependency input for the BigQuery perfmetrics Python package.

## Important APIs, Types, and Functions

The file pins `google-cloud-bigquery==3.11.1`, includes `argparse`, and pins `urllib3==1.26.19`. It does not define code APIs.

## Control Flow

There is no runtime control flow. Dependency tooling can compile this input into a fully pinned and hashed `requirements.txt`, which CI scripts then install.

## State and Persistence Behavior

The file influences Python environment state when dependencies are installed. It does not itself persist data.

## Dependencies and Integration Points

`build.sh` installs `bigquery/requirements.txt` with `pip install --require-hashes`, so this input must stay consistent with the generated lock file. `google-cloud-bigquery` supports all live BigQuery operations in `experiments_gcsfuse_bq.py`; `urllib3` constrains transitive HTTP behavior/security updates.

## Risks and Edge Cases

Including `argparse` is unnecessary for modern Python because it is in the standard library, and external `argparse` packages can create compatibility surprises. Pinning `urllib3` may be needed for transitive compatibility, but stale pins can carry security or TLS behavior risk. Changes to this file without regenerating the hashed requirements file will not affect Kokoro installs.

## Test Signals

Signals are successful dependency compilation, successful `pip install --require-hashes -r bigquery/requirements.txt`, and passing BigQuery unit tests in a fresh environment.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/bigquery/requirements.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/bigquery/setup.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/bigquery/setup.py

## Purpose

`setup.py` is a small executable wrapper that initializes the BigQuery dataset and perfmetrics tables for gcsfuse experiments.

## Important APIs, Types, and Functions

The script imports `bigquery.experiments_gcsfuse_bq` and `bigquery.constants`. In its main block it instantiates `ExperimentsGCSFuseBQ(constants.PROJECT_ID, constants.DATASET_ID)` and calls `setup_dataset_and_tables()`.

## Control Flow

The control flow is linear: construct helper, run setup. All schema creation, sleeps, and BigQuery query execution occur in `experiments_gcsfuse_bq.py`.

## State and Persistence Behavior

Running this script can create the `performance_metrics` dataset and the `experiment_configuration`, `read_write_fio_metrics`, `read_write_vm_metrics`, and `list_metrics` BigQuery tables. It does not write local files.

## Dependencies and Integration Points

It depends on BigQuery credentials, enabled BigQuery API, the constants module's hard-coded project/dataset, and the schema SQL in `ExperimentsGCSFuseBQ.setup_dataset_and_tables`. It is intended to run from `perfmetrics/scripts` using `python3 -m bigquery.setup`.

## Risks and Edge Cases

Despite the filename, this is not a Python packaging `setuptools` setup script; invoking generic packaging commands against it would be misleading. It has no CLI options for project or dataset override, so local or staging setup requires editing constants or wrapping the module differently. Schema drift is delegated to `CREATE TABLE IF NOT EXISTS`; existing tables are not migrated.

## Test Signals

A useful smoke test is a mocked `ExperimentsGCSFuseBQ` receiving one `setup_dataset_and_tables` call. Live signals are successful BigQuery dataset/table creation and idempotent reruns with no schema errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/bigquery/setup.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/build_and_install_gcsfuse.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/build_and_install_gcsfuse.sh

## Purpose

`build_and_install_gcsfuse.sh` builds a gcsfuse Debian package for a supplied branch or commit and installs it on the current machine. It is used by Kokoro perfmetrics and e2e scripts to test an installed package rather than a local `go run`.

## Important APIs, Types, and Functions

The script accepts one positional argument, `<branch-or-commit-id>`. It uses `dpkg --print-architecture`, Docker apt repository setup, `docker buildx build`, `docker run`, and `dpkg -i`. Build arguments include `ARCHITECTURE`, `GCSFUSE_VERSION=0.0.0`, and `BRANCH_NAME`.

## Control Flow

With `set -e`, the script exits on the first failing command. It detects architecture, installs Docker if absent or if running inside Kokoro, validates the branch/commit argument, builds `./tools/package_gcsfuse_docker/` into a local image tagged `gcsfuse:$branch`, copies `/packages` from the container into `$HOME/release`, and installs `$HOME/release/packages/gcsfuse_0.0.0_${architecture}.deb`.

## State and Persistence Behavior

The script changes system package state by installing Docker components and installing the generated gcsfuse `.deb`. It writes package artifacts under `$HOME/release/packages`, creates or updates apt sources/keyrings for Docker, and may alter the installed `gcsfuse` binary used by subsequent tests.

## Dependencies and Integration Points

Dependencies include Ubuntu apt, sudo, curl, gpg, lsb-release, Docker buildx, the local `tools/package_gcsfuse_docker/` build context, and Debian package tooling. It is called by `continuous_test/gcp_ubuntu/build.sh` for local perf tests and by `continuous_test/gcp_ubuntu/e2e_tests/build.sh` before running integration tests.

## Risks and Edge Cases

The Docker image tag uses the raw branch or commit argument; branch names containing slashes or other invalid tag characters can break the build. The script assumes Ubuntu-style apt and Debian packages. It installs Docker in Kokoro even if a Docker command exists because Kokoro may have an old Docker version. The fixed package version `0.0.0` means repeated builds overwrite the same package path and do not encode commit identity in the installed package version.

## Test Signals

Signals are a successful Docker build, presence of `$HOME/release/packages/gcsfuse_0.0.0_${architecture}.deb`, successful `dpkg -i`, and a working `gcsfuse --version` or downstream perf/e2e run using the installed package.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/build_and_install_gcsfuse.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/compare_fuse_types_using_fio.py -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/compare_fuse_types_using_fio.py

## Purpose

`compare_fuse_types_using_fio.py` runs a fio workload against two FUSE-based filesystems mounted on the same GCS bucket and writes extracted fio metrics to `out/output.txt`. It supports released gcsfuse versions, gcsfuse built from `master`, and arbitrary Go-based FUSE filesystem repositories.

## Important APIs, Types, and Functions

Constants are `GCSFUSE_REPO` and a default `GCSFUSE_FLAGS`. `_install_gcsfuse` downloads and installs a release `.deb`, creates `gcs`, and mounts the bucket with `gcsfuse`. `_install_gcsfuse_source` clones the gcsfuse repo and runs it with `go run`. `_remove_gcsfuse` unmounts and removes package/source artifacts.

For non-gcsfuse filesystems, `_install_fuse` clones the provided repository URL, sets `GOPATH`, runs `go run .` with flags and `gs://bucket`, and `_remove_fuse` unmounts and removes the clone. `_run_fio_test` executes `fio` with JSON output, asks `fio.fio_metrics.FioMetrics.get_metrics('output.json', False)` to parse it, appends the result to `out/output.txt`, and removes `output.json`.

`_fuse_test` dispatches to the gcsfuse-specific or generic flow. `main(argv)` parses two filesystem names, versions/repo URLs, mount flags, a fio jobfile path, and a GCS bucket, creates `out`, writes labels for both runs, and executes them in sequence. The script is launched through `absl.app.run(main)`.

## Control Flow

The script performs filesystem 1 setup, fio execution, cleanup, then repeats for filesystem 2. It expects all shell commands launched by `os.system` to work in the ambient environment, but it does not inspect return codes before continuing. Metrics extraction is done in Python after fio writes `output.json`.

## State and Persistence Behavior

The script installs packages, clones repositories, creates and removes a local `gcs` mount directory, mounts and unmounts FUSE filesystems, writes `output.json` temporarily, and appends durable comparison output to `out/output.txt`. It can also modify system package state through `dpkg`, `apt-get remove`, and any commands run by cloned projects.

## Dependencies and Integration Points

Dependencies include fio, fusermount, sudo/dpkg/apt for released gcsfuse, git, Go, GCS credentials, the local `fio` Python package, and `absl`. It integrates with GCS buckets, gcsfuse releases on GitHub, the gcsfuse source repository, arbitrary FUSE repos, and fio jobfiles maintained elsewhere under perfmetrics.

## Risks and Edge Cases

The script builds shell commands with unquoted f-strings and uses `os.system`, so flags, bucket names, paths, or repo URLs with shell metacharacters can break execution or become injection vectors. It does not check `os.system` exit codes, so failed mounts, fio failures, or cleanup failures may still lead to misleading output. The generic FUSE flow assumes a Go project whose `go run .` accepts `flags gs://bucket mountpoint`. Cleanup always targets `gcs`, so concurrent runs in the same directory conflict.

## Test Signals

Useful unit tests would mock `os.system` and `FioMetrics.get_metrics` to verify command ordering and output appends for released gcsfuse, source gcsfuse, and generic FUSE paths. Operational signals are successful mount/unmount, fio JSON generation, parsed metrics in `out/output.txt`, and no stale `gcs`, `output.json`, package, or clone artifacts after completion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/compare_fuse_types_using_fio.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/build.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/build.sh

## Purpose

`continuous_test/gcp_ubuntu/build.sh` is the Kokoro entrypoint for gcsfuse performance jobs on GCP Ubuntu workers. It selects distributed read benchmarks, distributed write benchmarks, local perf tests, or zonal scaffolding based on `BENCHMARK_TYPE`.

## Important APIs, Types, and Functions

The script uses `KOKORO_ARTIFACTS_DIR`, `KOKORO_BUILD_INITIATOR`, `KOKORO_JOB_TYPE`, and `BENCHMARK_TYPE`. Helper functions include `print_duration`, `exit_handler`, `run_load_test_and_fetch_metrics`, and `run_ls_benchmark`. It calls `perfmetrics/scripts/build_and_install_gcsfuse.sh`, `run_load_test_and_fetch_metrics.sh`, `ls_metrics/run_ls_benchmark.sh`, `hns_rename_folders_metrics/run_rename_benchmark.sh`, and `gcsfuse-tools/distributed-micro-benchmark/kokoro_run.sh`.

## Control Flow

The script installs git, enters `${KOKORO_ARTIFACTS_DIR}/github/gcsfuse`, identifies the current branch and commit. Automated Kokoro scheduler runs use the last commit before "yesterday 23:59:59"; manual runs use the latest checked-out commit. An exit trap prints total duration.

For `distributed_benchmark_read` and `distributed_benchmark_write`, it locates `${KOKORO_ARTIFACTS_DIR}/github/gcsfuse-tools` and runs the distributed micro-benchmark with `--read` or `--write`. For `local_tests`, it builds/installs gcsfuse, installs hashed BigQuery requirements, sets upload flags for release/CI/presubmit/sub jobs, and runs flat bucket fio and ls tests, HNS bucket fio and ls tests, and an HNS rename benchmark. For `distributed_benchmark_zonal`, it currently prints scaffolding only. Unknown `BENCHMARK_TYPE` exits with failure.

## State and Persistence Behavior

The script installs packages on the worker, installs gcsfuse, writes logs under `KOKORO_ARTIFACTS_DIR`, uploads or prepares uploads depending on downstream scripts and `UPLOAD_FLAGS`, and creates benchmark artifacts such as fio output. It changes directories into perfmetrics subtrees and relies on returning to expected paths.

## Dependencies and Integration Points

Dependencies include Kokoro checkout layout, Ubuntu apt, git, Docker/package build tooling via `build_and_install_gcsfuse.sh`, Python/pip, BigQuery requirements, gcsfuse-tools for distributed benchmarks, and GCS buckets/spreadsheets for flat and HNS measurements. `continuous.cfg` points Kokoro at this script and collects the logs it produces.

## Risks and Edge Cases

The commit selection for scheduler jobs depends on local git history containing yesterday's commit. `pip install --require-hashes -r bigquery/requirements.txt --user` requires the generated lock file to match `requirements.in`. Bucket names, spreadsheet IDs, and log filenames are hard-coded. The function-local `cd` operations require careful path restoration; failures inside nested scripts can leave cleanup and duration reporting as the only diagnostics. Zonal benchmark type is accepted but not implemented beyond a placeholder.

## Test Signals

Operational signals include the printed branch/commit ID, duration blocks for each benchmark, successful build/install, presence of collected log artifacts, successful distributed benchmark exit codes, and successful local fio/ls/rename script completions. Dry-run shell linting can catch unset variable and path issues because the script uses `set -euo pipefail`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/build.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/continuous.cfg -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/continuous.cfg

## Purpose

`continuous.cfg` is the Kokoro job configuration for the gcsfuse Ubuntu continuous perfmetrics workflow.

## Important APIs, Types, and Functions

The config defines artifact collection regexes for flat and HNS fio/ls logs, `github/gcsfuse/perfmetrics/scripts/fio-output.json`, and Sponge logs. It sets `strip_prefix: "github/gcsfuse/perfmetrics/scripts"`, increases `timeout_mins` to 360, and points `build_file` to `gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/build.sh`.

## Control Flow

Kokoro reads this config, runs the declared build file, and collects matching artifacts after execution. Runtime benchmark branching is delegated to environment variables consumed by the build script.

## State and Persistence Behavior

The config itself is static. It controls which build outputs persist as Kokoro artifacts and how paths are stripped in uploaded artifact names.

## Dependencies and Integration Points

It integrates directly with Kokoro's `action.define_artifacts`, timeout handling, Sponge logging, and the `continuous_test/gcp_ubuntu/build.sh` script. Artifact regexes must match filenames produced by local perf tests.

## Risks and Edge Cases

If downstream scripts change log names or output paths, Kokoro may complete without collecting useful diagnostics. A six-hour timeout accommodates long benchmarks but can also delay feedback for hung jobs. The `strip_prefix` is narrower than some artifact regexes, so path presentation depends on Kokoro's matching behavior.

## Test Signals

Signals are Kokoro jobs invoking the expected build script, artifact tabs containing fio/ls logs and Sponge logs, and timeout behavior matching benchmark duration expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/continuous.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/build.sh -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/build.sh

## Purpose

`e2e_tests/build.sh` is the Kokoro entrypoint for building an installed gcsfuse package at the selected commit and running integration tests against regional buckets by default or zonal buckets when requested.

## Important APIs, Types, and Functions

The script consumes `KOKORO_ARTIFACTS_DIR`, `KOKORO_BUILD_INITIATOR`, and optional `RUN_TESTS_WITH_ZONAL_BUCKET`. It calls `perfmetrics/scripts/build_and_install_gcsfuse.sh` and `tools/integration_tests/improved_run_e2e_tests.sh` with `--test-installed-package` plus optional `--zonal`.

## Control Flow

With `set -euo pipefail`, the script rejects all command-line arguments and requires bucket mode selection through the environment. It enters the Kokoro gcsfuse checkout, determines branch and commit using the same scheduler/manual logic as the perf build, builds and installs gcsfuse while capturing logs to a temp file, checks out the selected commit, then runs zonal or regional e2e tests.

## State and Persistence Behavior

It installs the generated gcsfuse package on the worker and changes the repository worktree to the selected commit with `git checkout`. It writes a temporary build log only on failure output; failed integration logs are collected by the Kokoro configs.

## Dependencies and Integration Points

Dependencies include Kokoro checkout layout, git history, `build_and_install_gcsfuse.sh`, installed package behavior, and the integration test runner under `tools/integration_tests`. It is referenced by master, release, and zonal-bucket e2e Kokoro configs.

## Risks and Edge Cases

The script fails if any positional argument is supplied, which is intentional but can surprise manual invocations. It uses unquoted `$commitId` in the build and checkout commands; commit hashes are safe, but a future branch-name path would need quoting. Scheduler commit selection requires enough git history. If `RUN_TESTS_WITH_ZONAL_BUCKET` is set to a value other than `true`, the script warns and runs regional tests, so misconfigured environment values do not fail fast.

## Test Signals

Signals are successful package build/install, checkout to the intended commit, e2e runner completion with `--test-installed-package`, and presence of failed integration logs or proxy logs when tests fail.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/build.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/checkpoint-tests.cfg -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/checkpoint-tests.cfg

## Purpose

`checkpoint-tests.cfg` is a Kokoro configuration for gcsfuse ML checkpoint tests.

## Important APIs, Types, and Functions

The config collects artifacts matching `gcsfuse_logs/*` and Sponge logs, strips `github/gcsfuse/perfmetrics/scripts`, and sets `build_file` to `gcsfuse/perfmetrics/scripts/ml_tests/checkpoint/Jax/run_checkpoints.sh`.

## Control Flow

Kokoro runs the checkpoint build file and collects matching logs after the job. The actual checkpoint workload control flow is in `run_checkpoints.sh`, not this config.

## State and Persistence Behavior

The config controls artifact persistence for gcsfuse logs and Sponge logs. It does not manage runtime state directly.

## Dependencies and Integration Points

It depends on the ML checkpoint script path, Kokoro artifact handling, and log outputs under `gcsfuse_logs`. It is adjacent to e2e configs but targets the checkpoint-specific workload rather than `e2e_tests/build.sh`.

## Risks and Edge Cases

If checkpoint logs move or are renamed, diagnostics may not be collected. There is no explicit timeout override in this file, so the job relies on Kokoro defaults or enclosing configuration. The build file path must stay synchronized with the ML test directory.

## Test Signals

Signals are Kokoro invoking `run_checkpoints.sh`, uploaded `gcsfuse_logs/*` artifacts, and Sponge logs for failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/checkpoint-tests.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/e2e-tests-master-zb.cfg -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/e2e-tests-master-zb.cfg

## Purpose

`e2e-tests-master-zb.cfg` configures Kokoro to run master-branch e2e tests against zonal buckets.

## Important APIs, Types, and Functions

The config collects `gcsfuse-failed-integration-test-logs-*`, Sponge logs, and `proxy*` artifacts with the perfmetrics strip prefix. It sets environment variable `RUN_TESTS_WITH_ZONAL_BUCKET=true` and uses build file `gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/build.sh`.

## Control Flow

Kokoro injects the zonal-bucket environment variable before invoking the shared e2e build script. The build script detects the exact string `true` and passes `--zonal` to `improved_run_e2e_tests.sh`.

## State and Persistence Behavior

The config persists failed integration logs, proxy artifacts, and Sponge logs. Runtime package installation and repository checkout happen in the shared build script.

## Dependencies and Integration Points

It integrates with Kokoro env var injection, artifact collection, the shared e2e build script, and the integration runner's zonal mode.

## Risks and Edge Cases

Zonal execution depends on the environment variable spelling and exact value. Artifact regex `proxy*` is broad and may collect unexpected files, while missing `proxy-server-failed-integration-test-logs-*` compared with non-zonal configs may change diagnostics. If the build script changes its zonal flag name, this config must change with it.

## Test Signals

Signals are logs showing `Running zonal e2e tests on installed package`, invocation of the integration runner with `--zonal`, and collected zonal failure/proxy artifacts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/e2e-tests-master-zb.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/e2e-tests-master.cfg -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/e2e-tests-master.cfg

## Purpose

`e2e-tests-master.cfg` configures Kokoro to run the standard master-branch gcsfuse e2e test workflow.

## Important APIs, Types, and Functions

The config collects `gcsfuse-failed-integration-test-logs-*`, `proxy-server-failed-integration-test-logs-*`, and Sponge logs, strips `github/gcsfuse/perfmetrics/scripts`, and points `build_file` to the shared `e2e_tests/build.sh`.

## Control Flow

Kokoro invokes the shared build script without setting `RUN_TESTS_WITH_ZONAL_BUCKET`, so the script's default path runs regional e2e tests with `--test-installed-package`.

## State and Persistence Behavior

The config persists failed integration diagnostics and Sponge logs. Package installation, git checkout, and test execution state are managed by the build script.

## Dependencies and Integration Points

It depends on Kokoro artifact collection and on the shared build script's default regional behavior. The artifact regexes align with integration and proxy-server failure log naming.

## Risks and Edge Cases

If integration logs are renamed or emitted outside the strip prefix, failures will be harder to diagnose. Because no zonal env var is set, accidental regional/zonal behavior changes would come from the shared script, not this config.

## Test Signals

Signals are build logs stating regional tests are running by default, e2e runner success/failure, and uploaded gcsfuse/proxy failure logs when tests fail.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/e2e-tests-master.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/e2e-tests-release.cfg -->
# sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/e2e-tests-release.cfg

## Purpose

`e2e-tests-release.cfg` configures Kokoro to run the standard gcsfuse e2e workflow for release jobs.

## Important APIs, Types, and Functions

It defines artifact collection for `gcsfuse-failed-integration-test-logs-*`, `proxy-server-failed-integration-test-logs-*`, and Sponge logs with the same strip prefix as the master config. Its build file is `gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/build.sh`.

## Control Flow

Kokoro runs the shared build script. With no zonal environment variable in this config, the script builds and installs the selected release checkout and runs regional e2e tests against the installed package.

## State and Persistence Behavior

The config persists failure artifacts and Sponge logs. Runtime state changes are delegated to the build script, including package installation and checkout to the selected commit.

## Dependencies and Integration Points

It integrates with release Kokoro scheduling, the shared e2e build script, and the integration test runner. Artifact regexes must match release-job log names.

## Risks and Edge Cases

The master and release configs are currently structurally identical, so any release-specific behavior must come from Kokoro job context rather than this file. If release jobs require different environment variables or artifact retention, this config would need explicit additions.

## Test Signals

Signals are release Kokoro logs showing the selected branch/commit, installed-package e2e execution, and collected gcsfuse/proxy/Sponge logs on failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/e2e-tests-release.cfg -->
