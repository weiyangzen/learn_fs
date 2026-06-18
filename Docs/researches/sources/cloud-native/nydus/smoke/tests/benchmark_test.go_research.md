# sources/cloud-native/nydus/smoke/tests/benchmark_test.go

Purpose: gated benchmark smoke test that converts or selects a container image, runs it through a snapshotter, captures startup/read metrics, and writes a JSON metric file.

Important APIs/types: `BenchmarkTestSuite`, `TestBenchmark`, `prepareImage`, `dumpMetric`, and top-level `TestBenchmark` gate on `BENCHMARK_TEST`.

Control flow: chooses snapshotter from `SNAPSHOTTER` defaulting to `nydus`, chooses mode from `BENCHMARK_MODE` (`oci`, `fs-version-5`, `fs-version-6`, `zran`), validates/selects image, converts via `nydusify convert` when needed, reads conversion JSON, runs a container with a UUID name, builds `tool.ContainerMetrics`, and writes metrics to `BENCHMARK_METRIC_FILE` or `benchmark.json`.

State and persistence: pulls/prepares source image, creates target nydus image tags, writes transient conversion metric JSON, runs a container, and persists benchmark metric JSON.

Dependencies and integration: requires containerd/nerdctl/nydus-snapshotter setup, nydusd/nydus-image/nydusify binaries, smoke `tool` helpers, and image support checks.

Risks: disabled unless `BENCHMARK_TEST` is set; external image/network/runtime dependencies can dominate failures; old nydusify support changes flags; metric map keys are assumed to exist; generated target images/containers require cleanup by helpers/environment.

Test signals: successful conversion, container run metrics (`E2ETime`, read count/amount), image size/conversion elapsed in output JSON, and final benchmark metric file.
