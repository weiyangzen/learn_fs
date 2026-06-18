## sources/cloud-native/soci-snapshotter/benchmark/performanceTest/main.go

Purpose: benchmark driver that runs full SOCI benchmark workloads, optionally parsing file-access logs after each run.

Important APIs/types/functions: top-level flags configure test count, workload JSON, commit tagging, and file-access parsing. It constructs `framework.BenchmarkTestDriver` values whose `TestFunction` calls `benchmark.SociFullRun`.

Control flow: parse flags, choose commit hash, optionally recreate `output/file_access_logs`, load default or JSON image descriptors, create `output/benchmark_log`, create a framework context, build one driver per image, and invoke `BenchmarkFramework.Run`.

State and persistence: writes benchmark output under `../performanceTest/output`, truncates `benchmark_log`, and may delete/recreate file access logs.

Dependencies and integration: integrates with `benchmark` package workload descriptors, SOCI run helpers, `benchmark/framework`, Go `testing.B`, and `benchmark/framework/parser`.

Risks and test signals: closures capture `testName` and `image` from loop variables; with current Go semantics this is safe, but older compiler assumptions would be risky. It panics on most setup failures and has no direct tests here.
