# sources/distributed-fs/ceph-client/include/uapi/linux/map_benchmark.h

Purpose: defines the DMA mapping benchmark ioctl ABI used to measure map/unmap latency under configurable thread, duration, NUMA, addressing, direction, transfer-delay, and map-mode settings.

Important APIs and types: `DMA_MAP_BENCHMARK` is the ioctl over magic `'d'`. Limits include `DMA_MAP_MAX_THREADS`, `DMA_MAP_MAX_SECONDS`, and `DMA_MAP_MAX_TRANS_DELAY`. Direction constants include bidirectional, to-device, and from-device. Modes distinguish single-page and scatterlist tests. `struct map_benchmark` carries output averages/stddevs and input parameters such as threads, seconds, NUMA node, DMA bits, DMA direction, transfer delay, granule, map mode, and reserved expansion.

Control flow: userspace fills benchmark parameters, calls the ioctl, the kernel runs map/unmap loops for the requested duration and concurrency, then returns latency statistics in 100ns units and standard deviations.

State and persistence: benchmark state is temporary per ioctl call. Results are returned to userspace and not persisted by the kernel.

Dependencies and integration points: depends on `linux/types.h` and time constants such as `NSEC_PER_MSEC`; integrates DMA API benchmarking, NUMA allocation, scatterlist mapping, and device-specific DMA mask behavior.

Risks and test signals: risks include excessive threads/runtime, invalid DMA direction, NUMA node handling, overflow in timing/statistics, and reserved field misuse. Test parameter bounds, both map modes, all directions, high thread counts, invalid nodes, timing overflow, and reserved-field zeroing.
