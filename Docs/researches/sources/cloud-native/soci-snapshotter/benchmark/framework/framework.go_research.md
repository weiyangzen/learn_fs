# sources/cloud-native/soci-snapshotter/benchmark/framework/framework.go

Purpose: benchmark execution framework that repeatedly runs test drivers, gathers metrics, computes descriptive statistics, and writes JSON results.

Important APIs/types/functions: `BenchmarkFramework`, `BenchmarkTestStats`, `BenchmarkTestDriver`, `Run`, `calculateStats`, and `calculateTestStat`.

Control flow: initializes Go testing flags with one iteration per benchmark, loops through drivers, runs optional before hooks, calls `testing.Benchmark` the requested number of times, records total duration and custom extra metrics converted from milliseconds to seconds, computes standard deviation/mean/min/percentiles/max using `montanaflynn/stats`, runs optional after hook, marshals the framework to `results.json`.

State and persistence: accumulates metrics in memory and writes JSON under `OutputDir`.

Dependencies/integration: used by comparison/performance benchmark executables and visualization workflows.

Risks: missing custom metrics default to zero in `res.Extra`, which can hide benchmark functions that forgot to report metrics. `os.MkdirAll` uses file permission `0644`, which lacks execute bits for directories and may fail or create unusable dirs on some systems.

Test signals: benchmark result JSON schema consumed by visualization tooling; unit tests should cover stats with empty/one-item samples.
