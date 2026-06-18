# sources/distributed-fs/ceph-client/kernel/dma/map_benchmark.c

## Purpose
This file implements a debugfs-driven benchmark driver for DMA map/unmap latency. It can bind to a platform or PCI device, expose `/sys/kernel/debug/dma_map_benchmark`, and run kthreads that repeatedly map and unmap either a single contiguous buffer or a scatterlist.

## Important APIs, Types, And Functions
`struct map_benchmark_data` stores user parameters, target device, debugfs entry, direction, atomic timing sums, squared sums, and loop count. `struct map_benchmark_ops` abstracts benchmark modes. Single-buffer helpers allocate pages with `alloc_pages_exact()` and use `dma_map_single()`/`dma_unmap_single()`. SG helpers allocate one page per SG entry and use `dma_map_sg()`/`dma_unmap_sg()`. `map_benchmark_thread()` measures loop latencies. `do_map_benchmark()` creates/stops workers and computes averages/stddev. `map_benchmark_ioctl()` validates user input and runs `DMA_MAP_BENCHMARK`.

## Control Flow
Probe allocates per-device state and creates the debugfs file. The ioctl copies `struct map_benchmark` from userspace, validates mode, thread count, duration, transmit delay, NUMA node, granule, and direction, temporarily sets the device DMA mask, runs the benchmark, restores the old mask, then copies results back. Each worker prepares its buffers, optionally stains CPU caches for TO_DEVICE/BIDIRECTIONAL, times map and unmap separately in 100 ns units, waits the requested fake transfer delay, accumulates sums atomically, and yields with `cond_resched()`.

## State, Persistence, And Dependencies
State is per-bound-device devm memory and a debugfs dentry, plus per-run kthreads and buffers. The benchmark temporarily mutates `dev->dma_mask` through `dma_set_mask()` and restores it afterward. Dependencies include debugfs, DMA mapping API, kthreads, timekeeping, NUMA CPU masks, PCI and platform driver registration, and the UAPI in `uapi/linux/map_benchmark.h`.

## Integration Points
Userspace selftests can bind the benchmark driver to a device and issue the ioctl through debugfs. The file registers both PCI and platform drivers named `dma_map_benchmark`.

## Risks
Benchmarking changes the device DMA mask during the run; failure to restore would affect the real driver, so restoration is a key invariant. High thread counts and long durations can load the system. SG preparation must unwind partially allocated pages correctly. The file allows only one debugfs file name globally, so a second bound device fails as intended.

## Test Signals
Run the DMA map benchmark selftest in single and SG modes, all supported directions, different granules, NUMA binding, invalid parameter rejection, DMA mask restore after failure and success, map failure handling, module init/exit, and cleanup of debugfs on driver detach.
