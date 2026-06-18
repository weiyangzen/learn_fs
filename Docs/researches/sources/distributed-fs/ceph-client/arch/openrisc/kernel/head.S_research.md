<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/head.S -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/head.S

## Purpose
Implements OpenRISC reset vectors, early boot, exception vector dispatch, boot-time and runtime TLB miss handlers, cache/MMU enabling, secondary CPU parking/startup, emergency UART output, and initial page-aligned data structures.

## Important APIs, Types, And Functions
Important labels include `_start`, `_dispatch_*` vector entries, `boot_dtlb_miss_handler`, `boot_itlb_miss_handler`, `dtlb_miss_handler`, `itlb_miss_handler`, `_ic_enable`, `_dc_enable`, `_flush_tlb`, `secondary_wait`, `secondary_start`, `_emergency_putc`, `_emergency_print`, `_emergency_print_nr`, `_early_uart_init`, `_secondary_evbar`, `swapper_pg_dir`, and `_unhandled_stack`.

## Control Flow
Reset jumps to `_start`, clears BSS/registers, starts TTCR, enables caches, flushes TLB, enables MMU, validates the FDT pointer, calls `or1k_early_setup()`, and enters `start_kernel()`. Vector slots use `EXCEPTION_HANDLE()` to build frames and jump into `entry.S` handlers. Boot TLB handlers identity-map early addresses; later handlers walk `current_pgd` and refill DTLB/ITLB or fall back to page-fault handlers.

## State And Persistence
Initializes SR, TTMR, cache state, TLB entries, `thread_info->ksp`, `swapper_pg_dir`, and secondary-release handshake state. Emergency output may use shadow GPRs or low memory scratch.

## Dependencies And Integration Points
Depends on linker placement, OpenRISC SPRs, generated offsets, FDT magic, serial configuration, page table layout, `current_pgd`, `current_thread_info_set`, and C setup/SMP entry points.

## Risks
Early code runs with changing address translation and must carefully convert virtual to physical addresses. Runtime TLB refill assumes two-level page tables and page-size/bit-mask contracts. Emergency UART constants are platform-specific.

## Test Signals
Boot on simulator and hardware, FDT fallback, MMU/caches enabled, runtime TLB misses resolved, secondary CPUs released, and early exception/emergency UART diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/head.S -->
