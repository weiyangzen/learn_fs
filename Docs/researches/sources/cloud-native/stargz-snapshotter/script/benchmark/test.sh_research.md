# sources/cloud-native/stargz-snapshotter/script/benchmark/test.sh

Purpose: Builds an isolated Docker Compose benchmark node, runs hello-bench, and formats result artifacts.
Important APIs/types/functions: uses env `BENCHMARK_TARGETS`, `BENCHMARK_RUNTIME_MODE`, `BENCHMARK_RESULT_DIR`, `BENCHMARK_LOG_DIR`; defines `cleanup`.
Control flow: builds the base and node images, copies runtime-specific configs, starts a privileged compose service, executes `hello-bench/run.sh` inside it, collects `/tmp/hello-bench-output`, archives logs, runs format/plot/percentile/table/csv tools, then tears down compose volumes.
State and persistence: creates temporary Dockerfile/context/compose file, Docker images, volumes, output directory, and archived log artifacts.
Dependencies and integration points: depends on Docker BuildKit, docker compose, benchmark configs, jq/wget/crane in the node image, and all benchmark tools.
Risks: requires privileged containers and host Docker access; formatting failures are separated from run failures but still mark failure; compose cleanup is destructive to benchmark volumes.
Test signals: primary benchmark entrypoint; success produces `result.json`, graphs, percentile data, markdown table, CSV, and logs.
