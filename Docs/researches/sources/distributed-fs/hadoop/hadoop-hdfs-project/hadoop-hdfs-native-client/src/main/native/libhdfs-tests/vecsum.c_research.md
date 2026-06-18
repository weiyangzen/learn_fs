# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/vecsum.c

## Purpose
`vecsum.c` is a native benchmark and correctness utility for comparing local mmap reads, normal libhdfs reads, and libhdfs zero-copy reads while summing deterministic double values. It is built as `test_libhdfs_vecsum` on non-Windows platforms but behaves more like a configurable microbenchmark than a self-contained unit test.

## Important APIs and types
Key types are `options`, `local_data`, `libhdfs_data`, and `stopwatch`. `parse_vecsum_type` accepts `local`, `libhdfs`, or `zcr`. Data setup uses `test_file_chunk_setup`, `local_data_create_file`, `local_data_create`, `libhdfs_data_create_file`, and `libhdfs_data_create`. Read paths are `vecsum_local`, `vecsum_libhdfs` through `hdfsReadFully`, and `vecsum_zcr` through `hadoopReadZero`. The summation implementation uses SSE intrinsics when `HAVE_INTEL_SSE_INTRINSICS` is defined and scalar fallback otherwise.

## Control flow
`main` validates chunk-size alignment, reads environment-driven options, prepares either local or HDFS data, starts a stopwatch, runs the selected read/sum mode for `VECSUM_PASSES`, prints per-pass sums, and reports aggregate throughput. If the target file is absent or has the wrong length, setup rewrites it with deterministic chunks. HDFS setup connects using `VECSUM_RPC_ADDRESS` or `default`, enables short-circuit checksum skipping, validates path info, and opens the file for reading.

## State and persistence
The benchmark may create or rewrite `VECSUM_PATH` either locally or in HDFS to `VECSUM_LENGTH` bytes. It allocates 8 MiB chunks and read buffers. Local mode mmaps the file; HDFS mode keeps an `hdfsFS` and `hdfsFile`; zero-copy mode keeps `hadoopRzOptions` and releases each returned buffer.

## Dependencies
It depends on POSIX file APIs, `mmap`, `clock_gettime` or Mach clock APIs on macOS, optional SSE2 intrinsics, `config.h`, and libhdfs read and zero-copy APIs. CMake links it with threads and `rt` on non-Darwin Unix.

## Risks
The environment contract is strict: `VECSUM_PATH`, `VECSUM_PASSES`, and `VECSUM_TYPE` are required, while `VECSUM_LENGTH` must be an 8 MiB multiple. The HDFS writer expects full 8 MiB writes and treats short writes as errors. Zero-copy mode treats partial reads smaller than the configured chunk as invalid, so it assumes file length and read size alignment. The local cleanup frees the struct but does not itself unlink files; benchmark data persists by design.

## Test signals
Useful signals are successful deterministic file creation, equal-looking per-pass sums across local/libhdfs/zcr modes, no partial reads, no zero-copy errors, and stopwatch throughput output. It is skipped on Windows because it uses `sys/mman.h`.
