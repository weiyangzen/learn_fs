# Research Group: subset-b-009593

This grouped report covers the requested gcsfuse perfmetrics continuous-test, GKE benchmark, FIO, Google Sheets, and HNS data-generation files. Each source file has its own marker-delimited section for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/e2e-tests-tpc.cfg -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/e2e-tests-tpc.cfg

Purpose: Kokoro job configuration for TPC-universe end-to-end tests. It declares artifacts for failed integration logs and Sponge logs, strips them relative to `github/gcsfuse/perfmetrics/scripts`, and dispatches to `gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/tpc_build.sh`.

APIs and integration: This is a Kokoro config, not executable code. The main contract is the `build_file` path plus artifact regexes consumed by Kokoro.

Control flow and state: Kokoro runs the referenced shell script; this file persists no local state. Artifact matching is the only output behavior.

Dependencies and risks: It depends on Kokoro path conventions and the build script staying at the configured path. Risk is low but artifact regex drift can hide failure evidence.

Test signals: Validation is operational: a Kokoro run should invoke `tpc_build.sh` and collect matching logs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/e2e-tests-tpc.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/tpc_build.sh -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/tpc_build.sh

Purpose: Runs installed-package gcsfuse integration tests against the TPC endpoint. It builds gcsfuse at a selected commit, configures a TPC gcloud universe, authenticates with a service account key copied from GCS, and runs `improved_run_e2e_tests.sh`.

APIs and control flow: The script takes no arguments and enforces `set -euo pipefail`. It installs latest gcloud, determines branch and commit, builds via `build_and_install_gcsfuse.sh`, checks out the tested commit, creates and activates a `prptst` gcloud configuration, sets TPC API endpoint overrides, runs tests with `--test-on-tpc-endpoint`, then restores default gcloud config and exits with the captured test status.

State and persistence: It mutates the local git checkout, gcloud configurations, `/tmp/sa.key.json`, and installed gcsfuse package. Daily Kokoro scheduler runs use yesterday's final master commit; manual runs use HEAD.

Dependencies and risks: Depends on Kokoro env vars, GCS credential bucket access, gcloud storage, Git, and TPC endpoint availability. Cleanup is best-effort after tests; failures before the final restore can leave gcloud config altered.

Test signals: Exit code reflects integration-test result. Logs from build failure are printed from a temp file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/e2e_tests/tpc_build.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/local_tests.cfg -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/local_tests.cfg

Purpose: Kokoro config for local Ubuntu performance tests, including HNS and flat logs plus FIO output.

APIs and integration: Dispatches to `gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/build.sh` with `BENCHMARK_TYPE=local_tests`; Kokoro collects four gcsfuse log files, `fio-output.json`, and Sponge logs.

Control flow and state: No runtime logic here. The config defines a 300-minute timeout and delegates behavior to the shared Ubuntu build script.

Dependencies and risks: Relies on `BENCHMARK_TYPE` being understood by the build script and artifact names matching produced logs. If filenames change, benchmark results may run but not be archived.

Test signals: Successful Kokoro execution should upload the configured artifacts and complete within the timeout.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/local_tests.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/micro_benchmarks/build.sh -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/micro_benchmarks/build.sh

Purpose: Remotely runs micro-benchmark tests on a persistent GCE VM named `periodic-micro-benchmark-tests`.

APIs and control flow: Defines `log()` and `run_script_on_vm()`. The main path calls `sudo gcloud compute ssh` with `--internal-ip`, updates apt, installs git, unmounts an existing gcsfuse mount if present, deletes `~/github`, clones `GoogleCloudPlatform/gcsfuse`, checks out yesterday's last commit, and runs `perfmetrics/scripts/micro_benchmarks/run_microbenchmark.sh`.

State and persistence: Mutates the remote VM heavily: package cache, repository checkout, mount state, and benchmark outputs. Local script state is limited to stdout logs.

Dependencies and risks: Requires gcloud auth, SSH permission, VM availability, sudo, network access, and correct hard-coded zone/path values. It deletes `~/github` on the VM, so the VM must be dedicated.

Test signals: Exit status from remote command controls the build. Timestamped logs show progress.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/micro_benchmarks/build.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/micro_benchmarks/continuous.cfg -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/micro_benchmarks/continuous.cfg

Purpose: Minimal Kokoro continuous config for micro-benchmarks.

APIs and integration: The sole behavior is `build_file: "gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/micro_benchmarks/build.sh"`, binding the Kokoro job to the remote VM runner.

Control flow and state: No env vars, artifacts, or timeout are declared in this file; defaults come from Kokoro/job configuration and the shell script.

Dependencies and risks: Any output collection must be provided elsewhere. Risk is mostly hidden failure evidence if the build script logs are not configured as artifacts by the job wrapper.

Test signals: A job should invoke `build.sh` successfully.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/micro_benchmarks/continuous.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/periodic_experiments/build.sh -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/periodic_experiments/build.sh

Purpose: Kokoro build script for parameterized periodic gcsfuse performance experiments.

APIs and control flow: Installs `git` and `jq`, loads `experiments_configuration.json`, filters configurations with `end_date >= current_date`, selects by one-based `EXPERIMENT_NUMBER`, optionally writes `config_flags.yml` from `config_file_flags_as_json`, builds gcsfuse for the configured branch, installs BigQuery requirements, registers/fetches a `CONFIG_ID`, conditionally enables BigQuery upload flags for Kokoro job types, runs FIO load tests through `run_load_test_and_fetch_metrics.sh`, then runs list benchmarks via `ls_metrics/run_ls_benchmark.sh`.

State and persistence: Writes transient config files under `KOKORO_ARTIFACTS_DIR`, installs packages and Python user packages, builds/install gcsfuse, writes log files and metrics, and uploads to BigQuery when enabled.

Dependencies and risks: Depends on `EXPERIMENT_NUMBER`, Kokoro env vars, jq, pip requirements, BigQuery modules, bucket names, and shell quoting. Use of `eval` around the Python config command and unquoted JSON variables increases quoting risk.

Test signals: Logs, FIO output JSON, list logs, and BigQuery rows indicate successful execution.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/periodic_experiments/build.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/periodic_experiments/continuous.cfg -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/periodic_experiments/continuous.cfg

Purpose: Kokoro config for the unnumbered periodic experiment job.

APIs and integration: Collects `gcsfuse-logs.txt`, `gcsfuse-list-logs.txt`, and `fio-output.json`; invokes `periodic_experiments/build.sh`.

Control flow and state: This file provides artifact collection only and does not set `EXPERIMENT_NUMBER`. The build script therefore requires the environment to provide it or may fail under `set -e`.

Dependencies and risks: Artifact names differ from the numbered experiment configs. Risk is an unset `EXPERIMENT_NUMBER` if Kokoro does not inject it separately.

Test signals: Kokoro should archive the configured logs and FIO JSON.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/periodic_experiments/continuous.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/periodic_experiments/experiment1.cfg -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/periodic_experiments/experiment1.cfg

Purpose: Kokoro config for periodic experiment slot 1.

APIs and integration: Sets `EXPERIMENT_NUMBER=1`, collects numbered FIO and list logs, and invokes `periodic_experiments/build.sh`.

Control flow and state: The build script uses the environment value to select the first currently enabled item from `experiments_configuration.json`.

Dependencies and risks: The one-based slot is order-dependent after filtering expired configurations. Reordering active configs changes what experiment this Kokoro job runs.

Test signals: Numbered artifacts `gcsfuse-logs1.txt`, `gcsfuse-list-logs1.txt`, and `fio-output1.json` should be produced.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/periodic_experiments/experiment1.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/periodic_experiments/experiment2.cfg -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/periodic_experiments/experiment2.cfg

Purpose: Kokoro config for periodic experiment slot 2.

APIs and integration: Sets `EXPERIMENT_NUMBER=2`, archives slot-specific gcsfuse and FIO artifacts, and dispatches to the shared periodic build script.

Control flow and state: Slot selection is performed by `jq -s ".[$EXPERIMENT_NUMBER-1]"` after date filtering.

Dependencies and risks: The job is coupled to active configuration order rather than a stable config name. Artifact regexes must match the build script's numbered log naming.

Test signals: Presence of slot-2 logs and FIO JSON is the main signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/periodic_experiments/experiment2.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/periodic_experiments/experiment3.cfg -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/periodic_experiments/experiment3.cfg

Purpose: Kokoro config for periodic experiment slot 3.

APIs and integration: Sets `EXPERIMENT_NUMBER=3`, defines artifact regexes for `gcsfuse-logs3.txt`, `gcsfuse-list-logs3.txt`, and `fio-output3.json`, and invokes the shared build script.

Control flow and state: It delegates experiment choice and all benchmark execution to `build.sh`.

Dependencies and risks: Same order-coupling risk as other numbered slots. Missing or expired third configuration causes the build script to print no enabled config and exit successfully without running benchmarks.

Test signals: Slot-3 artifact collection and BigQuery upload, when enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/periodic_experiments/experiment3.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/periodic_experiments/experiment4.cfg -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/periodic_experiments/experiment4.cfg

Purpose: Kokoro config for periodic experiment slot 4.

APIs and integration: Sets `EXPERIMENT_NUMBER=4`, archives the fourth numbered logs/FIO output, and runs `periodic_experiments/build.sh`.

Control flow and state: This config has no logic beyond env var and artifact definitions.

Dependencies and risks: Requires at least four active configs in `experiments_configuration.json`. The current config set has exactly four entries, so adding expiry or reordering affects the job.

Test signals: Slot-4 gcsfuse log, list log, and FIO JSON are expected outputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/periodic_experiments/experiment4.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/periodic_experiments/experiments_configuration.json -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/periodic_experiments/experiments_configuration.json

Purpose: Data contract for periodic experiment variants consumed by `build.sh`.

APIs and structure: Contains `experiment_configuration`, an ordered array of config objects with `config_name`, `gcsfuse_flags`, `branch`, `end_date`, and optional `config_file_flags_as_json`. The current entries compare master defaults, range-read cache enabled, range-read cache disabled, and gRPC client protocol.

Control flow and state: The shell script filters entries by `end_date`, then selects by `EXPERIMENT_NUMBER` index. Optional config-file flags are serialized into a temporary config file and passed via `--config-file`.

Dependencies and risks: Date strings are compared by jq as strings, so format consistency matters. The file's array order is an external scheduling API for numbered Kokoro jobs.

Test signals: A valid config should produce a BigQuery config id through `bigquery.get_experiments_config`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/periodic_experiments/experiments_configuration.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/read_distributed.cfg -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/read_distributed.cfg

Purpose: Kokoro config for distributed read benchmark on Ubuntu.

APIs and integration: Sets a 300-minute timeout, calls `continuous_test/gcp_ubuntu/build.sh`, and passes `BENCHMARK_TYPE=distributed_benchmark_read`.

Control flow and state: All benchmark behavior is delegated to the shared build script.

Dependencies and risks: Relies on the build script's dispatch table recognizing the exact benchmark type string. No artifacts are declared here, so output retention depends on shared or external Kokoro config.

Test signals: Successful run should complete within 300 minutes and execute the read workload path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/read_distributed.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/write_distributed.cfg -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/write_distributed.cfg

Purpose: Kokoro config for distributed write benchmark on Ubuntu.

APIs and integration: Delegates to the shared Ubuntu build script with `BENCHMARK_TYPE=distributed_benchmark_write` and a 300-minute timeout.

Control flow and state: No local logic; state and artifacts are controlled by the build script.

Dependencies and risks: Exact env var value is the integration contract. Missing artifact definitions can make performance-debug evidence unavailable unless inherited elsewhere.

Test signals: Expected signal is successful execution of the write benchmark branch.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/write_distributed.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/zonal_distributed.cfg -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/zonal_distributed.cfg

Purpose: Kokoro config for zonal distributed benchmark on Ubuntu.

APIs and integration: Invokes `continuous_test/gcp_ubuntu/build.sh` with `BENCHMARK_TYPE=distributed_benchmark_zonal` and a 300-minute timeout.

Control flow and state: The file only configures job dispatch.

Dependencies and risks: It depends on the shared build script mapping the benchmark type to the correct zonal workload. Output capture is not declared locally.

Test signals: Successful Kokoro job execution is the primary validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gcp_ubuntu/zonal_distributed.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/common/__init__.py -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/common/__init__.py

Purpose: Marks `common` as a Python package for GKE continuous-test helpers.

APIs and integration: It exports no symbols and has no import side effects. Consumers import `from common import utils` after adding the GKE parent directory to `sys.path`.

Control flow and state: None beyond package discovery.

Dependencies and risks: Low risk. The package remains importable as long as callers set `sys.path` correctly.

Test signals: Import success from neighboring benchmark scripts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/common/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/common/utils.py -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/common/utils.py

Purpose: Shared async command, prerequisite, GKE cluster, node-pool, network, cleanup, and gcsfuse CSI image build utilities for GKE benchmark scripts.

APIs and control flow: Key APIs are `run_command_async`, `check_prerequisites`, `setup_gke_cluster`, existence/health helpers for clusters and node pools, `create_node_pool_async`, `delete_node_pool_async`, `create_network`, `cleanup`, and `build_gcsfuse_image`. Commands are passed as argument lists to avoid shell injection in most helpers. `setup_gke_cluster` creates missing network/subnet/cluster/node pool, recreates unhealthy node pools, then fetches credentials.

State and persistence: Mutates the host by installing apt packages, adding Google Cloud apt sources, installing gcloud/kubectl/auth plugin/make, and mutates Google Cloud by creating/deleting clusters, node pools, VPCs, subnets, firewall rules, and container images.

Dependencies and risks: Requires sudo, apt, curl, gpg, gcloud, kubectl, make, git, Google Cloud auth, and quota/reservations. Cleanup deletes firewall rules by network filter and deletes the network/subnet, so name isolation is critical.

Test signals: No local unit tests in this subset. Consumers rely on command return codes and printed stdout/stderr.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/common/utils.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/machine_type_test/continuous.cfg -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/machine_type_test/continuous.cfg

Purpose: Kokoro config for the GKE machine-type optimization test.

APIs and integration: Sets `BUCKET_NAME=gcsfuse_gke_machine_type_test_flat_euw4` and runs `gke/machine_type_test/run.py` as the build file.

Control flow and state: The Python script creates cloud resources, deploys a pod, and runs integration tests. This config only supplies the bucket default.

Dependencies and risks: Bucket IAM and Workload Identity setup must match the runner. No timeout or artifacts are declared locally.

Test signals: The runner's exit code and pod logs are the main validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/machine_type_test/continuous.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/machine_type_test/run.py -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/machine_type_test/run.py

Purpose: Orchestrates a GKE TPU machine-type integration test verifying that CSI driver passes machine type to gcsfuse and gcsfuse enables expected optimization flags.

APIs and control flow: Functions include `set_up_bucket_permissions`, `is_tpu_machine_type`, `execute_test_workload`, and async `main`. `main` parses CLI/env defaults, appends zone to default network/subnet names, checks prerequisites, optionally builds the CSI image in parallel with cluster setup, grants bucket IAM to the default KSA principal, creates a timestamped pod manifest from `pod_tpu.yaml.template`, streams pod logs, checks final pod phase, cleans configmap/manifest/pod resources, and optionally deletes cloud infrastructure.

State and persistence: Creates GKE clusters, node pools, networks, IAM bucket bindings, Kubernetes configmaps/pods, temp manifests, and possibly a CSI image. `--no_cleanup` preserves cloud resources.

Dependencies and risks: Requires TPU-compatible machine types; non-TPU types raise `ValueError`. Pod status parsing strips quotes from kubectl JSONPath output. Cleanup references `manifest_filename` in `finally` after manifest creation; failures before assignment could be fragile.

Test signals: Success requires pod phase `Succeeded`; `run_test.sh` performs the in-pod Go integration tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/machine_type_test/run.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/machine_type_test/run_test.sh -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/machine_type_test/run_test.sh

Purpose: In-pod workload script for the GKE machine-type test.

APIs and control flow: Installs OS dependencies, clones gcsfuse at `$GCSFUSE_BRANCH`, validates `.go-version` with a semantic-version regex, installs Go through `perfmetrics/scripts/install_go.sh`, and runs integration tests under `tools/integration_tests/flag_optimizations` with `--mountedDirectory=/data_mnt`, `--testbucket=$BUCKET_NAME`, and a regex selecting implicit-dirs and rename-dir-limit tests.

State and persistence: Mutates the container filesystem, installs Go, and writes test output to pod logs. GCS bucket contents may be touched by integration tests.

Dependencies and risks: Depends on apt, git, build tools, Go version format, GCS bucket access through Workload Identity, and mounted CSI volume at `/data_mnt`.

Test signals: `set -e` makes any install, clone, Go install, or `go test` failure fail the pod.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/machine_type_test/run_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/orbax_benchmark/continuous.cfg -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/orbax_benchmark/continuous.cfg

Purpose: Kokoro config for the default HTTP GKE Orbax benchmark.

APIs and integration: Sets `BUCKET_NAME=llama_europe_west4` and dispatches to `gke/orbax_benchmark/run_benchmark.py`.

Control flow and state: The Python runner handles GKE setup, image build, pod execution, throughput parsing, and cleanup.

Dependencies and risks: Bucket must contain or expose the checkpoint path expected by the pod template/test script. No client protocol override means the runner default `http1` is used.

Test signals: Runner success depends on parsed throughput threshold.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/orbax_benchmark/continuous.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/orbax_benchmark/run_benchmark.py -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/orbax_benchmark/run_benchmark.py

Purpose: Runs the Orbax checkpoint load benchmark in a GKE pod and gates success on throughput.

APIs and control flow: `parse_all_gbytes_per_sec` extracts floats from log lines matching `gbytes_per_sec: <num> Bytes/s`. `execute_workload_and_gather_results` creates a ConfigMap from `test_load.py`, renders `pod.yaml.template`, applies it, polls pod phase until completion or timeout, reads logs, parses throughput, then deletes configmap/manifest. `main` parses env/CLI, sets up GKE and optionally builds CSI in parallel, executes the workload, and requires at least 5/8 of parsed iterations to meet `performance_threshold_gbps`.

State and persistence: Creates cluster resources via `common.utils`, Kubernetes ConfigMap/pod/manifest files, and optionally a CSI image. Cleanup may run both in error branches and `finally`.

Dependencies and risks: Regex unit label says `Bytes/s` while variables say GB/s. The fixed pod name `gcsfuse-test` can collide if parallel runs share a namespace. Cleanup deletes configmap without `check=False`, so missing configmap can mask earlier errors.

Test signals: Throughput count, threshold pass/fail message, and process exit status.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/orbax_benchmark/run_benchmark.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/orbax_benchmark/test_load.py -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/orbax_benchmark/test_load.py

Purpose: In-pod CLI for loading and resaving Orbax checkpoints while measuring restore time.

APIs and control flow: Provides `set_no_of_jax_cpu`, `load_ckpt`, `save_ckpt`, Click group `cli`, and commands `load_test` and `resave`. `load_ckpt` reads Orbax metadata, rewrites array sharding metadata for CPU/TPU backends when needed, converts metadata to shape/dtype structs, restores with `StandardCheckpointer`, logs restored types, and returns elapsed time plus restored data. `load_test` repeats restore and prints per-loop and average timings.

State and persistence: Mutates `XLA_FLAGS` and JAX config, may clear JAX caches, loads checkpoint data into memory, and `resave` writes a checkpoint to the output path.

Dependencies and risks: Requires absl, click, etils, jax, numpy, and orbax. Sharding rewrite assumes leading dimension divisibility for some arrays. `RESTORE_CONCURRENT_GB` can drive high resource use.

Test signals: Printed loop timings and average elapsed time are consumed indirectly by pod logs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/orbax_benchmark/test_load.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/orbax_benchmark_grpc/continuous.cfg -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/orbax_benchmark_grpc/continuous.cfg

Purpose: Kokoro config for the gRPC variant of the GKE Orbax benchmark.

APIs and integration: Sets the same `BUCKET_NAME` as the default job, overrides `CLIENT_PROTOCOL=grpc`, and uses separate cluster/network/subnet names to isolate resources from the HTTP job. Runs `orbax_benchmark/run_benchmark.py`.

Control flow and state: The protocol value is passed into the pod template by the Python runner.

Dependencies and risks: Resource names must remain unique if jobs run concurrently. Benchmark comparison relies on all other defaults matching the HTTP config.

Test signals: Same as the Orbax runner, but with gRPC protocol in pod manifest.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/continuous_test/gke/orbax_benchmark_grpc/continuous.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/custom_vm_perf_test/custom_vm_perf_script.py -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/custom_vm_perf_test/custom_vm_perf_script.py

Purpose: Creates a configurable GCE VM for custom performance tests with a startup script.

APIs and control flow: `_parse_arguments(argv)` defines defaults for VM name, machine type, image family/project, zone, and startup script. In `__main__`, it builds a `gcloud compute instances create` command with a 100GiB boot disk and metadata startup script, then invokes it via `subprocess.check_output(..., shell=True)`.

State and persistence: Creates a real VM and attaches startup-script metadata. No cleanup is implemented.

Dependencies and risks: Requires gcloud auth/quota. `_parse_arguments` ignores its argument parameter except for `argv[1:]` after replacing `argv = sys.argv` in the caller context; tests call it directly with a script-name-prefixed list. Shell string construction exposes command-injection risk if untrusted args are passed.

Test signals: Unit tests cover explicit and default argument parsing, not VM creation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/custom_vm_perf_test/custom_vm_perf_script.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/custom_vm_perf_test/custom_vm_perf_script_test.py -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/custom_vm_perf_test/custom_vm_perf_script_test.py

Purpose: Unit tests for `custom_vm_perf_script._parse_arguments`.

APIs and control flow: `TestParseArguments` has `test_explicit_values` to assert CLI flags override all defaults and `test_default_values` to assert module constants populate omitted values.

State and persistence: No external state; tests do not mock or execute gcloud VM creation.

Dependencies and risks: Uses Python `unittest`. Coverage is narrow: parsing only, no validation of shell command construction, boot disk size, startup metadata, or error handling.

Test signals: Passing tests prove default and explicit argument mapping only.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/custom_vm_perf_test/custom_vm_perf_script_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fetch_and_upload_metrics.py -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fetch_and_upload_metrics.py

Purpose: Coordinates parsing FIO JSON, optional upload to Google Sheets/BigQuery, waits for VM metrics availability, then fetches VM metrics for each FIO job and optionally uploads them.

APIs and control flow: `_parse_arguments` accepts FIO output path, `--upload_gs`, `--upload_bq`, `--config_id`, `--start_time_build`, and `--spreadsheet_id`. Main creates `FioMetrics`, parses jobs, formats upload rows, optionally writes FIO metrics, validates BigQuery args, sleeps 360 seconds, prints per-job time windows, fetches VM metrics with `VmMetrics.fetch_metrics(INSTANCE, PERIOD_SEC, rw)`, and uploads VM rows.

State and persistence: Reads FIO JSON, sleeps, writes to Sheets/BigQuery if flags are set. Uses host name as VM instance identity.

Dependencies and risks: Imports `fio`, `vm_metrics`, `gsheet`, and BigQuery modules. `_parse_arguments(argv)` ignores its parameter and always uses `sys.argv`. BigQuery validation is duplicated. Long fixed sleep slows tests and operations.

Test signals: No test file in this subset; integration signal is successful uploads or printed metrics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fetch_and_upload_metrics.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/constants.py -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/constants.py

Purpose: Central constants for FIO JSON parsing and unit conversion.

APIs and data: Defines JSON key names for global/job options, params, read/write metrics, latency percentile keys, and conversion tables `FILESIZE_TO_KB_CONVERSION` and `TIME_TO_MS_CONVERSION`. `NS_TO_S` converts nanoseconds to seconds.

Control flow and state: No functions or mutable runtime state. Constants are imported by `fio_metrics.py` and tests.

Dependencies and risks: File-size conversion uses decimal KB multiples for M/G/T/P rather than binary. `_convert_value` lowercases units before lookup, so table keys are lower-case.

Test signals: Indirectly covered by `fio_metrics_test` conversion, parameter, and metric extraction tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/constants.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/fio_metrics.py -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/fio_metrics.py

Purpose: Parses FIO JSON output into rows suitable for Google Sheets and BigQuery.

APIs and control flow: Dataclasses `JobParam` and `JobMetric` describe required parameter and metric extraction. Helpers `_convert_value` and `_get_rw` normalize units and read/write modes. `FioMetrics` loads JSON, reads global/job ramp times, derives start/end windows, merges global job params with job overrides, extracts required metrics from read/write sections, skips jobs with invalid time windows or all-zero metrics, formats upload rows, and exposes `get_metrics(filepath)`.

State and persistence: Reads only the input JSON file. Upload imports are present but this module's main path prints parsed metrics rather than uploading.

Dependencies and risks: Assumes every job has `job options` when iterating params and that global params exist if job options omit a required param. Missing nested metrics raise `NoValuesError`. `_convert_value` handles integers only and can fail on decimal sizes/times. Dict insertion order controls upload column order.

Test signals: Extensive unit tests cover load failures, conversion failures, rw normalization, ramp time, good/partial/missing/no-data, and multiple-job global/job-option cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/fio_metrics.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/fio_metrics_test.py -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/fio_metrics_test.py

Purpose: Unit test suite for FIO metrics parsing.

APIs and control flow: Uses `unittest` with fixture filenames in `./fio/testdata/`. Tests cover `_load_file_dict` success and error modes, `_convert_value`, `_get_rw`, job parameter extraction, start/end time error behavior, global and job ramp time handling, `_extract_metrics`, skipped zero-metric jobs, `NoValuesError` paths, `get_metrics`, and multiple job scenarios with global or job-level options.

State and persistence: Reads JSON fixtures from the testdata folder. Does not touch Google Sheets or BigQuery.

Dependencies and risks: Tests assume they are run from `perfmetrics/scripts` because `TEST_PATH` is relative. Expected dict order mirrors the parser's insertion order.

Test signals: Strong parser coverage, but no CLI-main or upload integration coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/fio_metrics_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/install_fio.sh -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/install_fio.sh

Purpose: Installs a patched source build of fio for performance tests.

APIs and control flow: Requires one argument, the directory under which to clone fio. Installs `libaio-dev`, removes an existing `$SRC_DIR/fio`, clones `https://github.com/axboe/fio.git`, checks out `fio-3.36`, patches `FIO_IO_U_PLAT_GROUP_NR` in `stat.h` to `32`, configures, builds, installs, prints `fio -version`, and returns to the original directory.

State and persistence: Mutates the source directory, installs system packages, and installs fio globally via `sudo make install`.

Dependencies and risks: Requires sudo, apt, git, build tooling, network access, and an unchanged `stat.h` pattern. `cd -` prints the previous directory and can fail if shell state is unusual.

Test signals: Printed `fio version=` is the verification point; no unit tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/install_fio.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/bad_format.json -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/bad_format.json

Purpose: Negative parser fixture for malformed FIO JSON.

APIs and structure: Starts with non-JSON text before an otherwise FIO-like object. It is consumed by `fio_metrics_test.test_load_file_dict_bad_format_file_raises_value_error`.

Control flow and state: No executable behavior. It exercises `json.load` failure in `_load_file_dict`.

Dependencies and risks: If the fixture is accidentally corrected into valid JSON, the malformed-file test stops proving parser rejection.

Test signals: Expected exception is `ValueError`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/bad_format.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/empty_file.json -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/empty_file.json

Purpose: Negative parser fixture for a zero-byte FIO output file.

APIs and structure: Contains no JSON content. It is used to verify `_load_file_dict` surfaces `json.load` `ValueError` for empty files.

Control flow and state: No runtime behavior.

Dependencies and risks: The file intentionally must remain empty. Adding whitespace or `{}` would test a different error path.

Test signals: `fio_metrics_test` expects `ValueError` when loading this fixture.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/empty_file.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/empty_json.json -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/empty_json.json

Purpose: Negative parser fixture for syntactically valid but semantically empty JSON.

APIs and structure: Contains `{}`. It exercises the `_load_file_dict` check that rejects empty objects after successful JSON parsing.

Control flow and state: No executable behavior.

Dependencies and risks: The parser raises custom `NoValuesError`; tests depend on the exact empty-object path rather than invalid JSON.

Test signals: Expected message includes `returned empty object`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/empty_json.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/good_out_job.json -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/good_out_job.json

Purpose: Canonical successful FIO fixture with one read job.

APIs and structure: Includes global options such as `rw=read`, `ramp_time=10s`, `runtime=60s`, `filesize=50M`, one job with `numjobs=40`, `job_start`, populated `read` metrics, zeroed `write`/`trim`, and latency percentiles required by the parser.

Control flow and state: No code; the parser uses it to verify params, start/end time calculation, required metrics, and upload-row ordering.

Dependencies and risks: Fixture values are duplicated in expected dicts in `fio_metrics_test`, so changes require test updates.

Test signals: Should produce one metrics record with start `1653027084`, end `1653027155`, filesize 50000 KB, and read metrics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/good_out_job.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/missing_metric_key.json -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/missing_metric_key.json

Purpose: Negative FIO fixture for missing required metric keys.

APIs and structure: FIO-like JSON with a job whose metric tree lacks at least one nested key required by `REQ_JOB_METRICS`. It is loaded successfully but fails during `_extract_metrics`.

Control flow and state: No executable behavior.

Dependencies and risks: The fixture must remain valid JSON while omitting the target metric; otherwise it would exercise the wrong parser failure.

Test signals: `fio_metrics_test` expects `NoValuesError` matching `Required metric .* not present in json output`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/missing_metric_key.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/multiple_jobs_global_options.json -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/multiple_jobs_global_options.json

Purpose: Successful multi-job fixture where required parameters come from global options.

APIs and structure: Contains global `rw`, `numjobs`, `filesize`, `ramp_time`, and `startdelay`, with two read jobs whose job options are empty. Populated read metrics validate parser handling of repeated jobs sharing global params.

Control flow and state: No code. `_get_job_params` should use global defaults for both jobs, and `_get_start_end_times` should compute separate windows from each `job_start`.

Dependencies and risks: Requires `job options` keys even when empty because the parser only appends params inside that branch.

Test signals: Expected output is two read metric records with shared filesize/thread params.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/multiple_jobs_global_options.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/multiple_jobs_job_options.json -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/multiple_jobs_job_options.json

Purpose: Successful multi-job fixture where job-level options override or provide required params.

APIs and structure: Global options omit some required params while each job supplies `filesize`, `numjobs`, and read/write mode as needed. The expected parser output includes a read job and a write job with distinct sizes and thread counts.

Control flow and state: No executable behavior; exercises `_get_job_params` override logic and `_get_rw` dispatch to the correct `read` or `write` metrics section.

Dependencies and risks: Job options are required for parser completeness. Fixture values are tightly coupled to expected outputs in tests.

Test signals: Two metrics records, one read and one write, with job-specific params.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/multiple_jobs_job_options.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/no_global_ramp_time.json -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/no_global_ramp_time.json

Purpose: FIO fixture for ramp-time fallback behavior.

APIs and structure: Global options omit `ramp_time`; at least one job supplies a job-level `ramp_time` such as `20s` and may override rw/filesize/thread params.

Control flow and state: No code. It lets tests assert `_get_global_ramp_time` returns 0 and `_get_job_ramp_time` reads the job value.

Dependencies and risks: Parser start/end calculations depend on this distinction. Changing ramp times requires expected test updates.

Test signals: Unit tests expect global ramp time 0 and job ramp time 20000 ms.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/no_global_ramp_time.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/no_metrics.json -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/no_metrics.json

Purpose: Negative FIO fixture for valid JSON with no usable nonzero metrics.

APIs and structure: Contains FIO-like global and job sections, but the selected read metrics are zeroed such that the parser skips the job and ends with no extracted jobs.

Control flow and state: No executable behavior.

Dependencies and risks: It must keep required keys present, otherwise it would trigger missing-key errors instead of the no-data path.

Test signals: `_extract_metrics` should raise `NoValuesError('No data could be extracted from file')`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/no_metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/partial_metrics.json -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/partial_metrics.json

Purpose: Fixture for mixed valid and invalid/zero jobs.

APIs and structure: Contains multiple jobs where the first selected job has zero metrics and a later job has populated read metrics. This validates skip-and-continue behavior.

Control flow and state: No code; parser should skip all-zero job metrics but still return later valid records.

Dependencies and risks: Required metric keys must remain present in zeroed jobs to test skip behavior rather than missing-key failure.

Test signals: Expected output is one valid metrics record from the nonzero job.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/partial_metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/generate_files.py -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/generate_files.py

Purpose: Generates batches of sparse local files and uploads them to a GCS bucket according to an INI config.

APIs and control flow: `logmessage` appends to a timestamped output file and logs to stdout. `generate_files_and_upload_to_gcs_bucket` batches by `BATCH_SIZE=100`, creates sparse files using `truncate` based on b/KB/MB/GB units, optionally uploads with `gcloud storage cp --recursive`, copies files to a local bucket-shaped folder, deletes temp batch files, and logs progress. Main parses `config_file` and `--keep_files`, checks gcloud, reads config sections, creates local directories, uploads each section, and deletes local/temp folders unless kept.

State and persistence: Writes sparse files under `./tmp/data_gen`, local bucket directories, timestamped `.out` log, and GCS objects.

Dependencies and risks: Uses shell commands for gcloud/cp/rm and drops into an interactive shell on errors. File-size parsing assumes two-character units, so `1b` is problematic.

Test signals: No tests in this subset; operational progress appears in the output log.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/generate_files.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/gsheet/gsheet.py -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/gsheet/gsheet.py

Purpose: Minimal Google Sheets writer for perf metrics.

APIs and control flow: `_get_sheets_service_client` loads service-account credentials from `./gsheet/creds.json` with spreadsheets scope and builds a Sheets v4 client. `write_to_google_sheet(worksheet, data, spreadsheet_id)` reads column A to determine occupied rows, clears `A2:<last>`, and writes provided rows starting at `A2` with `USER_ENTERED` input.

State and persistence: Mutates the target spreadsheet by clearing old rows and replacing data. Reads local credentials.

Dependencies and risks: Assumes the worksheet exists and the get response contains `values`; empty sheets without `values` can raise `KeyError`. Clearing range format uses `A2:<row>` without a column on the end, which relies on API interpretation.

Test signals: `gsheet_test` mocks service calls and verifies get/clear/update plus HttpError propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/gsheet/gsheet.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/gsheet/gsheet_test.py -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/gsheet/gsheet_test.py

Purpose: Unit tests for the Google Sheets helper.

APIs and control flow: Tests `_get_sheets_service_client` by replacing credential loading and asserting a discovery `Resource`, tests `write_to_google_sheet` by mocking chained Sheets API calls and expected get/clear/update arguments, and tests permission failure by injecting an `HttpError`.

State and persistence: No real Sheets access because service calls are mocked. The credential test still builds a discovery resource.

Dependencies and risks: Monkeypatches `service_account.Credentials.from_service_account_file` directly rather than using a context manager. The mocked fluent API uses broad `MagicMock`, so it checks call shape but not actual API request validity.

Test signals: Verifies write path call sequence and error propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/gsheet/gsheet_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/config-flat.json -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/config-flat.json

Purpose: Input configuration for flat-bucket HNS rename-folder benchmark data generation.

APIs and structure: Defines bucket/name `hns-rename-benchmark-flat`, three top-level folders containing 1k, 5k, and 10k one-kilobyte files, and a nested folder group with ten second-level folders of 1k files each.

Control flow and state: Consumed by `generate_folders_and_files.py`, which verifies or creates the described GCS object structure.

Dependencies and risks: `num_folders` must match `folder_structure` lengths or validation fails. File sizes use the two-character `1kb` format expected by the generator.

Test signals: The generator's structure comparison should find exactly the configured folder and file counts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/config-flat.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/config-hns.json -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/config-hns.json

Purpose: Input configuration for HNS-bucket rename-folder benchmark data generation.

APIs and structure: Mirrors `config-flat.json` but targets bucket/name `hns-rename-benchmark-hns`. It defines identical top-level and nested folder/file counts for comparing flat versus hierarchical namespace behavior.

Control flow and state: The data generator uses it to validate existing GCS structure or recreate bucket contents.

Dependencies and risks: Because it is intentionally parallel to the flat config, drift between the two files would weaken benchmark comparability.

Test signals: Successful validation requires all configured folders and file counts to match in the HNS bucket.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/config-hns.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/generate_folders_and_files.py -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/generate_folders_and_files.py

Purpose: Creates and validates GCS folder/file structures for HNS rename benchmarks.

APIs and control flow: Key helpers validate config consistency, list GCS directories via `gcloud alpha storage ls`, compare folder/file counts, delete existing bucket data, generate sparse files in batches, upload with `gcloud storage cp`, create top-level and nested folder structures, and delete the temp directory. Main checks gcloud, loads JSON, validates, compares existing bucket structure, deletes mismatched content, and regenerates data.

State and persistence: Writes temp files under `./tmp/data_gen`, timestamped `.out` logs, and GCS objects. It may delete all existing objects under the configured bucket.

Dependencies and risks: Heavy shell use with `shell=True`; upload uses `Popen(...).communicate()` but does not inspect return code, so some upload failures may be missed. Broad `except` blocks hide specific listing errors. `--keep_files` is parsed but not used.

Test signals: Unit tests cover config validation, listing, structure comparison, deletion, generation/upload happy and failure paths, and directory parsing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/generate_folders_and_files.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/generate_folders_and_files_test.py -->
## sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/generate_folders_and_files_test.py

Purpose: Unit tests for HNS rename benchmark data generation helpers.

APIs and control flow: Uses `unittest`, `mock`, and `patch` to test missing and valid config cases, directory listing success/failure, folder-structure comparison, whole directory existence matching, deletion success/failure, file generation/upload success, local file creation failure, upload failure, and parse/generate behavior for valid and failing directory structures.

State and persistence: External subprocesses, filesystem writes, and logs are mocked in most tests. No real GCS operations are intended.

Dependencies and risks: Imports third-party `mock` rather than only `unittest.mock`. Some assertions expect truthy `1` instead of `True`, matching Python bool/int behavior. Failure simulation around `Popen` does not cover nonzero process return codes because production code does not check them.

Test signals: Good coverage of helper-level behavior, less coverage of main script control flow.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/perfmetrics/scripts/hns_rename_folders_metrics/generate_folders_and_files_test.py -->
