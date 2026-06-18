# sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm946.S

## Purpose
This file supplies no-MMU MPU/cache support for ARM946E-S, including configurable D-cache sizing.

## Important APIs, Types, and Functions
It defines `cpu_arm946_*`, `arm946_*` cache/coherency/DMA helpers, and `arm946_processor_functions` with `nommu=1`. Cache geometry comes from `CONFIG_CPU_DCACHE_SIZE` with fixed 32-byte lines and 4 segments. `__arm946_setup()` programs RAM/flash protection regions, cacheability for data and instruction sides, access permissions, and control bits.

## Control Flow
Setup invalidates caches, disables unused memory regions, establishes default/RAM/flash regions, configures cacheable and write-buffer attributes, grants access permissions, and enables I-cache, D-cache, MPU, and optional round-robin cache replacement. Runtime range flushes either clean/invalidate each D-cache line or fall back to whole-cache maintenance.

## State and Persistence Behavior
The file changes CP15 protection-region and cache state and exposes static CPU metadata. No page tables are used.

## Dependencies and Integration Points
It depends on ARM946 CP15 MPU behavior, compile-time memory layout, cacheflush/DMA APIs, `proc-macros.S`, no-MMU boot, and legacy abort handlers.

## Risks
`CONFIG_CPU_DCACHE_SIZE` must match synthesized hardware. Region-size programming depends on valid DRAM/flash sizes. Cache and DMA correctness depends on line alignment and write-through conditionals. Since the processor table is no-MMU, generic MMU paths must stay unreachable.

## Test Signals
Boot ARM946E-S targets for multiple D-cache sizes, run memory and DMA tests, verify flash execution and access permissions, check cache coherency after code writes, and inspect configured protection regions.
