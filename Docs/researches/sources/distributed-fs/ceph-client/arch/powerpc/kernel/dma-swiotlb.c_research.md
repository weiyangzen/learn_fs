<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/dma-swiotlb.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/dma-swiotlb.c

## Purpose
`dma-swiotlb.c` contains PowerPC-specific SWIOTLB enablement helpers. It detects systems with RAM above the 32-bit address boundary and finalizes whether the software bounce buffer remains active.

## Important APIs, Types, And Functions
Globals are `ppc_swiotlb_enable` and `ppc_swiotlb_flags`. Functions are `swiotlb_detect_4g()` and initcall `check_swiotlb_enabled()`.

## Control Flow
`swiotlb_detect_4g()` sets `ppc_swiotlb_enable` when the last byte of DRAM is above `0xffffffff`. During `subsys_initcall`, `check_swiotlb_enabled()` either prints SWIOTLB info when enabled or calls `swiotlb_exit()` to tear down unused bounce buffering.

## State And Persistence
The enable and flags globals persist for runtime DMA setup. SWIOTLB memory reservation/lifetime is managed by the generic SWIOTLB layer. There is no durable storage.

## Dependencies And Integration Points
It integrates with memblock DRAM discovery, generic SWIOTLB, platform DMA setup, and device mask decisions for systems with limited DMA addressing.

## Risks
Detection based only on DRAM end is conservative and does not model every device mask. Disabling SWIOTLB too early would break devices unable to DMA high memory; keeping it unnecessarily wastes memory.

## Test Signals
Boot systems with DRAM below and above 4GB, confirm SWIOTLB info or teardown behavior, run DMA on 32-bit-limited devices, and verify no bounce allocation failures under high-memory I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/dma-swiotlb.c -->
