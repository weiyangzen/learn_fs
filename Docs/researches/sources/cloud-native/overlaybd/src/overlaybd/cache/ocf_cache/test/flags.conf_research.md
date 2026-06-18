<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/test/flags.conf -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/test/flags.conf

## Purpose
Provides sample gflags for running the OCF performance test manually.

## Important APIs, Types, And Functions
Configures single-file OCF cache mode, 8192-byte page/cache line size, libaio IO engine, 32-way concurrency, 2 GiB media file, no prefetch, random reads, source/destination paths, request limit, and multi-file parameters.

## Control Flow
The file is consumed by gflags-compatible invocation rather than C++ code directly. It selects single-file random-read benchmark behavior by default.

## State And Persistence
References `/root/cache-bench/media` and `/root/cache-bench/src`, so runs can create or reuse cache media and source data under that directory.

## Dependencies And Integration Points
Matches flags defined in `ocf_perf_test.cpp`.

## Risks And Test Signals
Paths and large media size are host-specific and unsuitable for ordinary CI. The file is useful as a reproducibility hint for manual benchmarks. Source size reviewed: 15 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/test/flags.conf -->
