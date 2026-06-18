<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/smp.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/smp.c

## Purpose
Implements OpenRISC SMP CPU discovery/startup, IPI handling, CPU stop, SMP TLB shootdowns, and cross-CPU I-cache invalidation.

## Important APIs, Types, And Functions
State includes `ipi_irq`, `smp_cross_call`, `secondary_release`, `secondary_thread_info`, and `cpu_running`. Functions include `smp_init_cpus()`, `smp_prepare_cpus()`, `__cpu_up()`, `secondary_start_kernel()`, `handle_IPI()`, `arch_smp_send_reschedule()`, `set_smp_cross_call()`, call-function IPI senders, global `flush_tlb_*()`, and `smp_icache_page_inv()`.

## Control Flow
Boot CPU discovers CPU hardware IDs from DT, marks CPUs present, installs IPI callback, releases secondaries with `IPI_WAKEUP`, waits for completion, then synchronizes timers. Secondary CPUs set up `init_mm`, CPU info, clockevents, notify CPU core, sync timer, enable IPIs, mark online, and enter idle.

## State And Persistence
Maintains IPI IRQ/callback, secondary boot handshake variables, CPU online/present/possible masks, `current_pgd`, per-mm CPU masks, and synchronized timer state.

## Dependencies And Integration Points
Depends on OF CPU nodes, interrupt controller IPI driver, generic SMP call-function core, TLB/cacheflush APIs, and `head.S` secondary wait/start labels.

## Risks
If `smp_cross_call` is missing, CPUs cannot start. TLB shootdowns are synchronous and broad because local mm flush flushes all. `ipi_irq` can only be set once.

## Test Signals
SMP boot with multiple DT CPU nodes, IPI reschedule/call-function tests, CPU stop, TLB shootdown under mmap/mprotect, and cross-CPU icache invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/smp.c -->
