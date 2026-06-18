# sources/distributed-fs/ceph-client/kernel/dma/Makefile

## Purpose
This Makefile maps DMA Kconfig symbols to object files in `kernel/dma`. It is the build integration point that selects direct mapping, ops helpers, dummy ops, CMA, coherent memory, debug instrumentation, SWIOTLB, coherent pools, remapping, and map benchmarking.

## Important APIs, Types, And Functions
Object selections include `mapping.o direct.o` for `CONFIG_HAS_DMA`, `ops_helpers.o` for `CONFIG_DMA_OPS_HELPERS`, `dummy.o` for `CONFIG_ARCH_HAS_DMA_OPS`, `contiguous.o` for `CONFIG_DMA_CMA`, `coherent.o` for `CONFIG_DMA_DECLARE_COHERENT`, `debug.o` for `CONFIG_DMA_API_DEBUG`, `swiotlb.o` for `CONFIG_SWIOTLB`, `pool.o` for `CONFIG_DMA_COHERENT_POOL`, `remap.o` for `CONFIG_MMU`, and `map_benchmark.o` for `CONFIG_DMA_MAP_BENCHMARK`.

## Control Flow
Kbuild evaluates each `obj-$(CONFIG_*)` expression and links the corresponding object into the kernel or module build according to configuration. There is no runtime behavior.

## State, Persistence, And Dependencies
The only state is build configuration. It depends on Kconfig symbols defined in `kernel/dma/Kconfig` and architecture Kconfig files.

## Integration Points
This file connects the generic DMA framework source files to the kernel build. It must stay aligned with declarations in `linux/dma-map-ops.h`, `linux/dma-direct.h`, and feature guards inside the C files.

## Risks
Missing object selection causes unresolved symbols or silent loss of configured functionality. Over-selection can build code whose assumptions are not met by the architecture. Ordering is mostly not semantic, but `mapping.o direct.o` are paired for `HAS_DMA`.

## Test Signals
Build tests for each relevant `CONFIG_*` combination are the main signal, especially `HAS_DMA=n`, `ARCH_HAS_DMA_OPS=y`, `DMA_CMA=y`, `DMA_DECLARE_COHERENT=y`, `DMA_API_DEBUG=y`, `SWIOTLB=y`, and `DMA_MAP_BENCHMARK=y`.
