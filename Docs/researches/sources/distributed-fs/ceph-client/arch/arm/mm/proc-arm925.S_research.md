# sources/distributed-fs/ceph-client/arch/arm/mm/proc-arm925.S

## Purpose
This file implements ARM925T/ARM915 low-level support, including OMAP/TI925-specific reset and cache-workaround behavior.

## Important APIs, Types, and Functions
It defines `cpu_arm925_*`, `arm925_*` cache/coherency/DMA hooks, `arm925_crval`, and `arm925_processor_functions`. Setup enables a TI configuration "transparent mode", invalidates caches/TLBs, optionally disables write-back, and computes control bits. The proc-info macro emits ARM925 and ARM915 entries and uses `v4t_early_abort` plus `legacy_pabort`.

## Control Flow
CPU probe calls `__arm925_setup()`. Runtime cache maintenance handles a 16-byte line, 2-segment, 256-entry D-cache and contains write-through/workaround conditionals. Reset first writes a platform-specific software reset halfword before falling through to generic cache/TLB disable operations. Idle temporarily disables I-cache around WFI.

## State and Persistence Behavior
The file mutates TI config registers, CP15 control, cache/TLB state, TTB, and hardware PTEs. Static proc-info records identify the core variants.

## Dependencies and Integration Points
It depends on OMAP/TI925 assumptions, ARMv4T helper tables, generic DMA/cache APIs, and ARM CPU suspend/idle conventions. It integrates through processor and cache function tables.

## Risks
The file documents known write-back flakiness with DMA, making `CONFIG_CPU_DCACHE_WRITETHROUGH` an important operational setting. Platform reset writes a hard-coded address. Transparent-mode and cache-clean mode assumptions are hardware-specific and risky to alter.

## Test Signals
Boot OMAP/ARM925/ARM915 systems, run DMA-heavy USB/storage tests, validate reset behavior, stress page-table updates, and compare write-through versus write-back builds. Check executable coherency after user-page writes.
