# sources/distributed-fs/ceph-client/tools/dma/config

Purpose: Kconfig fragment enabling the kernel DMA map benchmark support required by the userspace tool.

Important APIs, types, and functions: Contains `CONFIG_DMA_MAP_BENCHMARK=y`.

Control flow: Not executable; consumed as configuration input.

State and persistence: Sets a build-time kernel config option when merged into a kernel configuration.

Dependencies and integration points: Pairs with `dma_map_benchmark.c` and the kernel debugfs benchmark interface.

Risks: Enabling benchmark code may expose debug/test interfaces and should be restricted to test kernels.

Test signals: Merge config, build kernel, confirm `/sys/kernel/debug/dma_map_benchmark` exists with debugfs mounted.
