# sources/distributed-fs/ceph-client/arch/arm/mm/nommu.c

## Purpose
This file provides the ARM no-MMU memory-management support path. It reserves exception-vector memory, chooses an MPU setup backend, initializes boot memory, supplies no-MMU cache flush helpers, and implements identity-style I/O remapping for systems where physical and kernel virtual addresses are effectively the same.

## Important APIs, Types, and Functions
Important state is `vectors_base`, plus `mpu_rgn_info` when `CONFIG_ARM_MPU` is enabled. `setup_vectors_base()` configures high vectors or VBAR depending on `CONFIG_CPU_HIGH_VECTOR`, `CONFIG_REMAP_VECTORS_TO_RAM`, and security extension availability. `arm_mm_memblock_reserve()` reserves vector pages and address zero. `adjust_lowmem_bounds()` calls the PMSA-specific low-memory adjustment, updates `high_memory`, and caps memblock allocation. `paging_init()` initializes traps, programs the MPU, and calls `bootmem_init()`.

Runtime APIs include `flush_dcache_folio()`, `flush_dcache_page()`, `copy_to_user_page()`, `__arm_ioremap_pfn()`, `__arm_ioremap_caller()`, `ioremap()`, `ioremap_cache()`, `ioremap_wc()`, optional `pci_remap_cfgspace()`, `arch_memremap_wb()`, and `iounmap()`.

## Control Flow
Early boot calls `arm_mm_memblock_reserve()`, which computes vector placement and reserves the vector region before normal allocations. `adjust_lowmem_bounds()` reads `MMFR0.PMSA`, dispatches to `pmsav7_adjust_lowmem_bounds()` or `pmsav8_adjust_lowmem_bounds()`, then aligns the memory allocator's current limit with the usable DRAM end. `paging_init()` installs the trap vectors at `vectors_base`, dispatches MPU programming through `pmsav7_setup()` or `pmsav8_setup()`, and initializes bootmem.

The I/O mapping path does not build page tables. `ioremap*()` delegates to `__arm_ioremap_caller()`, which returns the physical address cast as `__iomem`; `iounmap()` is intentionally empty.

## State and Persistence Behavior
The file mutates boot-time global state only: vector placement, `mpu_rgn_info`, memblock reservations, `high_memory`, and the memblock current limit. There is no persistent storage. Runtime cache functions affect processor cache state, and the remap functions expose stable identity mappings without allocation lifetime tracking.

## Dependencies and Integration Points
It depends on CP15 helpers, memblock, ARM trap setup, ARM MPU helpers from `pmsa-v7.c` and `pmsa-v8.c`, cacheflush hooks from selected `proc-*.S` files, and generic MM/bootmem setup. It integrates with drivers through exported cache flushing and `ioremap*()` APIs, with PCI through `pci_remap_cfgspace()`, and with exception handling through `early_trap_init()`.

## Risks
Vector placement is high risk: missing security extensions while requesting RAM-remapped vectors leaves vectors at zero, and address zero must stay reserved to avoid false successful allocations. Identity ioremap means callers do not get normal MMU permission isolation or unmap semantics. PMSA dispatch depends on correct CPUID feature decoding; unsupported PMSA values silently skip MPU setup. `copy_to_user_page()` only performs I-cache coherency for executable VMAs, so incorrect `VM_EXEC` flags can expose stale instruction fetches.

## Test Signals
Build and boot no-MMU ARM configurations for CP15, non-CP15, high-vector, RAM-remapped-vector, PMSAv7, PMSAv8, and V7-M variants. Check boot logs for vector remap errors and MPU selection messages. Runtime signals include successful exception entry, no allocation of address zero, working driver `ioremap()` access, executable user mapping coherency after writes, and PCI config-space access when `CONFIG_PCI` is enabled.
