# File Research: sources/cow-pools/openzfs/module/zfs/zfs_chksum.c

## Summary
Benchmarks checksum implementations and exposes results through a raw kstat. It also selects the fastest implementation for algorithms with multiple backends.

## Main Responsibilities
- Defines benchmark result rows for checksum implementations.
- Runs startup and full requested benchmarks over fixed block sizes.
- Benchmarks Edon-R, Skein, SHA-256, SHA-512, and BLAKE3 implementations.
- Selects fastest SHA/BLAKE backend using 256 KiB throughput.
- Installs and removes the `zfs/chksum_bench` kstat.
- Initializes/finalizes BLAKE3 per-CPU context in kernel builds.

## Key APIs
- `chksum_init()`
- `chksum_fini()`

## Important Behavior
Startup performs a lighter 256 KiB benchmark. Reading the kstat triggers `chksum_benchmark()` again for full 1 KiB through 16 MiB results, then marks benchmarking done.

Benchmarks run with preemption disabled while timing and report MiB/s. Large 4 MiB and 16 MiB tests use non-linear ABD buffers.

## State and Lifetime
Global state includes `chksum_stat_data`, `chksum_stat_cnt`, `chksum_stat_limit`, and `chksum_kstat`. Init allocates benchmark rows and installs raw kstat callbacks; fini deletes kstat and frees the rows.

## Risks
Benchmarking runs in kernel context and can consume CPU when the kstat is read. Fastest-backend selection depends on the 256 KiB benchmark, which may not match every workload.
