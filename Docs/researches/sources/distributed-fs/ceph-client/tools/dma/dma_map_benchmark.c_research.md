# sources/distributed-fs/ceph-client/tools/dma/dma_map_benchmark.c

Purpose: Userspace CLI for the kernel DMA mapping benchmark debugfs ioctl.

Important APIs, types, and functions: `main()` parses options for threads, seconds, NUMA node, DMA mask bits, direction, transmit delay, granule, and mode; validates against UAPI limits; fills `struct map_benchmark`; opens `/sys/kernel/debug/dma_map_benchmark`; invokes `DMA_MAP_BENCHMARK`; and prints average/stddev map and unmap latencies.

Control flow: Defaults to single thread, 20 seconds, NUMA no node, 32-bit bidirectional single mode, granule 1. Invalid mode/thread/seconds/delay/bits/direction/granule exits. Successful ioctl prints mode, parameters, and latency metrics in microseconds.

State and persistence: Read/write interaction with debugfs benchmark endpoint; no local persistence.

Dependencies and integration points: Requires kernel built with `CONFIG_DMA_MAP_BENCHMARK`, debugfs mounted, UAPI `linux/map_benchmark.h`, and permission to open the debugfs file.

Risks: Uses `atoi()` without full parse validation. Direction indexes must remain compatible with `directions[]`. Benchmark can stress DMA mapping paths and should be run on test systems.

Test signals: Run valid defaults, each map mode/direction, invalid bounds, missing debugfs file, and compare kernel-populated latency fields.
