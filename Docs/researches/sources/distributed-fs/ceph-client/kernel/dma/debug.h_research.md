# sources/distributed-fs/ceph-client/kernel/dma/debug.h

## Purpose
This header declares the DMA API debug hooks and supplies no-op inline versions when DMA API debugging is disabled. It lets DMA mapping code call debug instrumentation unconditionally while compiling away the calls in normal builds.

## Important APIs, Types, And Functions
When `CONFIG_DMA_API_DEBUG` is set, it declares hooks for physical mapping/unmapping, scatterlist mapping/unmapping, coherent allocation/free, single and SG sync for CPU/device, and noncoherent page allocation/free. When disabled, the same names are static inline empty functions.

## Control Flow
There is no runtime control flow beyond compile-time selection. The enabled declarations resolve to `debug.c`; the disabled branch lets callers compile without code generation for debug checks.

## State, Persistence, And Dependencies
The header holds no state. It depends on core DMA types such as `struct device`, `struct scatterlist`, `struct page`, `phys_addr_t`, and `dma_addr_t` being visible through included DMA mapping headers in callers.

## Integration Points
DMA mapping implementation files include this header to instrument operations. It is the narrow interface between production DMA paths and the optional debug tracker.

## Risks
Prototype drift between this header and `debug.c` would break debug builds while non-debug builds still compile. Missing a hook in callers means a class of DMA misuse is invisible to `CONFIG_DMA_API_DEBUG`.

## Test Signals
Build both `CONFIG_DMA_API_DEBUG=y` and `n`, verify no undefined symbols in debug builds, and confirm non-debug builds do not create DMA debugfs files or instrumentation overhead.
