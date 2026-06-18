## sources/cloud-native/soci-snapshotter/benchmark/stargzTest/main.go

Purpose: benchmark driver for full stargz snapshotter runs against image descriptors from JSON.

Important APIs/types/functions: positional arguments supply commit, workload JSON, count, and stargz binary. For each image, a `framework.BenchmarkTestDriver` calls `benchmark.StargzFullRun`.

Control flow: parse positional arguments, load image descriptors, create `./output/benchmark_log`, create framework context, build drivers, and run the benchmark framework.

State and persistence: writes under local `./output`, truncating `benchmark_log` on each run.

Dependencies and integration: depends on the shared benchmark package, benchmark framework, and `StargzFullRun` implementation outside this source set.

Risks and test signals: direct `os.Args` indexing can panic on missing arguments. Invalid count and workload failures panic. No direct tests in this subset.
