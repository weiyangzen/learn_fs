# sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm940.S

## Purpose
This file provides no-MMU MPU/cache support for ARM940T.

## Important APIs, Types, and Functions
It defines `cpu_arm940_*` hooks, `arm940_*` cache/coherency/DMA functions, and a `nommu=1` processor-function table using `nommu_early_abort` and `legacy_pabort`. `__arm940_setup()` programs separate data and instruction protection areas, RAM and flash regions, cacheability, write-buffer, access permissions, and control bits.

## Control Flow
After proc-info match, setup invalidates I/D caches, disables unused protection areas, establishes area 0 as a 4 GB default, area 1 as RAM, and area 2 as flash, then enables I-cache, D-cache, and the MPU. Runtime cache APIs perform whole-cache or range operations over ARM940 geometry.

## State and Persistence Behavior
The file mutates CP15 protection region, access permission, cacheability, write-buffer, and control registers. It stores static proc-info and cache function metadata.

## Dependencies and Integration Points
It depends on compile-time DRAM/flash layout, protection region macros, no-MMU CPU probe, cacheflush and DMA APIs, and legacy abort handling.

## Risks
The code contains hardware-specific region programming and must keep data and instruction side registers consistent. Incorrect DRAM/flash sizing can break all memory access. A suspicious flash-size path uses registers that must be reviewed carefully on changes. No page-table hooks exist.

## Test Signals
Boot ARM940T no-MMU builds, verify RAM and flash access, cache flush and DMA behavior, exceptions, and reset. Exercise write-through and write-back variants and inspect MPU/protection register values.
