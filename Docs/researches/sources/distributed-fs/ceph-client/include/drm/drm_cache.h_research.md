# sources/distributed-fs/ceph-client/include/drm/drm_cache.h

## Purpose
This header declares DRM cache-management and write-combined memory copy helpers used by graphics drivers for CPU/GPU buffer coherency and efficient reads from WC mappings.

## Important APIs, types, and functions
APIs include `drm_clflush_pages`, `drm_clflush_sg`, `drm_clflush_virt_range`, `drm_need_swiotlb`, `drm_arch_can_wc_memory`, `drm_memcpy_init_early`, and `drm_memcpy_from_wc`. The inline `drm_arch_can_wc_memory` disables WC optimizations on architectures where uncached/no-snoop behavior is unsafe or outside coherent cache mechanisms.

## Control Flow
Drivers flush page arrays, scatter-gather tables, or virtual ranges before or after CPU access as required by buffer placement. Early initialization selects an optimized memcpy-from-WC implementation, then callers copy from WC `iosys_map` sources into destination maps.

## State and Persistence
The header manages no persistent state except implementation selection performed by `drm_memcpy_init_early`. Cache flushes affect CPU cache state and DMA coherency for buffer contents.

## Dependencies and Integration Points
It depends on Linux pages, scatterlists, architecture config symbols, SWIOTLB decisions, and `iosys_map`. It integrates with GEM/TTM buffer access, framebuffer readback, and DMA mapping constraints.

## Risks and Test Signals
Risks include assuming WC memory is safe on ARM/arm64/LoongArch/PPC/MIPS exceptions, missing flushes around noncoherent mappings, incorrect SWIOTLB decisions for DMA masks, and overlapping or unmapped `iosys_map` copies. Tests should cover architecture-specific return values, clflush on multi-page and SG buffers, WC copy length boundaries, and DMA-mask cases requiring SWIOTLB.
