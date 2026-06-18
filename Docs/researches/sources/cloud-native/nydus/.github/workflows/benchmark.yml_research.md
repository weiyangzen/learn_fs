# sources/cloud-native/nydus/.github/workflows/benchmark.yml

## Purpose
This GitHub Actions workflow benchmarks OCI and Nydus image modes on a scheduled Monday/Wednesday cadence, on manual dispatch, and when the workflow file itself changes in PRs.

## Important APIs, Types, and Functions
Jobs include `contrib-build`, `nydus-build`, `benchmark-description`, four benchmark matrices (`benchmark-oci`, `benchmark-fsversion-v5`, `benchmark-fsversion-v6`, `benchmark-zran`), and `benchmark-result`. The image matrix covers wordpress, node, python, golang, ruby, and amazoncorretto. The workflow uses `actions/checkout`, `actions/setup-go`, `Swatinem/rust-cache`, `dsherret/rust-toolchain-file`, artifact upload/download actions, `misc/prepare.sh`, and `make smoke-benchmark`.

## Control Flow
The workflow builds `nydusify` and Nydus binaries, uploads them as artifacts, then each benchmark job downloads them and runs `sudo -E make smoke-benchmark` with `BENCHMARK_TEST_IMAGE`, `BENCHMARK_MODE`, and `BENCHMARK_METRIC_FILE`. The result job downloads JSON artifacts for each image and appends a markdown table to `GITHUB_STEP_SUMMARY` using `jq` and `awk`.

## State and Persistence
Artifacts carry built binaries and per-image benchmark JSON between jobs. Step summaries persist benchmark tables in the Actions UI. No repository files are changed.

## Dependencies and Integration Points
The workflow depends on Makefile `nydusify-release`, `release`, and `smoke-benchmark`, the smoke benchmark harness, Docker/container runtime setup from `misc/prepare.sh`, and `jq` for summary generation.

## Risks and Edge Cases
Benchmarks are sensitive to runner CPU, memory, network, registry availability, and Docker state. The summary shell has nested quoting for python/ruby workload descriptions that is fragile. It uploads separate artifacts per image and mode, so artifact naming consistency is critical for the final result job.

## Test Signals
Benchmark job success, uploaded metric JSON files, and rendered `GITHUB_STEP_SUMMARY` tables are the main signals. Comparing OCI, RAFS v5, RAFS v6, and zran rows exposes performance regressions.
