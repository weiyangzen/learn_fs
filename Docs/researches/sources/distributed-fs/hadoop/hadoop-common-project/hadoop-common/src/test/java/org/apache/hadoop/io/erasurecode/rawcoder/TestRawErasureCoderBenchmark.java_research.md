
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestRawErasureCoderBenchmark.java

Purpose: JUnit smoke tests for the raw erasure coder benchmark driver across dummy, legacy RS, Java RS, and native ISA-L coders.

Important APIs and types: Calls `RawErasureCoderBenchmark.performBench()` with `CODER.DUMMY_CODER`, `LEGACY_RS_CODER`, `RS_CODER`, and `ISAL_CODER`. Native benchmark is gated by `ErasureCodeNative.isNativeCodeLoaded()`.

Control flow: Each test invokes encode and decode benchmark runs with different thread counts, total data sizes, and chunk sizes. The driver handles warmup, worker execution, timing, and release.

State and persistence: Benchmark static configuration is updated per run. No output files are created, but the tests print throughput data.

Dependencies and integration points: Ensures the benchmark tool can be called in-process and that supported factories do not throw under representative parameters.

Risks: These are performance smoke tests, not correctness tests. They can be slow and machine-dependent, especially with larger data sizes and native library availability.

Test signals: Confirms benchmark argument-free API paths, thread fan-out, coder release, and native skip behavior.
