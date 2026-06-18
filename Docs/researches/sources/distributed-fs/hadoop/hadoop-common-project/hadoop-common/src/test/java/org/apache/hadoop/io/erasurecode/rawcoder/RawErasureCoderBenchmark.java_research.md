
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/RawErasureCoderBenchmark.java

Purpose: Command-line and test-callable benchmark driver for raw erasure coder throughput. It measures encode/decode speed only and does not validate output correctness.

Important APIs and types: Exposes `main()` and `performBench()`. Defines `CODER`, `BenchData`, and `BenchmarkCallable`. Uses `DummyRawErasureCoderFactory`, legacy RS, Java RS, native RS, `RawErasureEncoder`, `RawErasureDecoder`, `ErasureCoderOptions`, `ByteBuffer`, `ExecutorService`, and `StopWatch`.

Control flow: Arguments choose encode/decode, coder index, thread count, data size, and chunk size. `performBench()` configures buffer sizes, warms the selected coder, generates a shared test buffer, starts worker callables with duplicate buffers, waits for durations, prints throughput and percentile statistics, and releases the coder.

State and persistence: `BenchData` static fields hold chunk and total sizes for the run. Coders are shared across worker threads, making thread safety part of the benchmark stress. No files are written.

Dependencies and integration points: Connects factory implementations to ad hoc performance tests and `TestRawErasureCoderBenchmark`.

Risks: Shared coder instances may not be safe for all implementations. Native coder availability can affect failures. Because correctness is not checked, corruption can go unnoticed.

Test signals: Useful for throughput, multi-thread stress, argument validation, release paths, and chunk-size bounds.
