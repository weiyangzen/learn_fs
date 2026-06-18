# sources/cloud-native/soci-snapshotter/benchmark/comparisonTest/main.go

Purpose: executable benchmark runner that compares OverlayFS full runs and SOCI full runs across configured image workloads.

Important APIs/types/functions: flags `-show-commit`, `-count`, and `-f`; uses `benchmark.GetCommitHash`, `GetDefaultWorkloads`, `GetImageList`, `framework.GetTestContext`, `BenchmarkTestDriver`, and `BenchmarkFramework.Run`.

Control flow: parses flags, chooses commit tag, loads default or JSON image descriptors, creates output directory/log file, builds a context with JSON logging, appends two benchmark drivers per image, and runs the framework to produce JSON results.

State and persistence: writes `../comparisonTest/output/benchmark_log` and `results.json`.

Dependencies/integration: built/run by Makefile `benchmarks-comparison-test` and CI comparison workflow.

Risks: loop variables `shortName` and `image` are captured by closures; with Go versions before per-iteration loop variable semantics this would make all drivers use the last image. Output dir creation does not clean existing files except log truncation.

Test signals: benchmark output JSON and log file; CI cat of results.
