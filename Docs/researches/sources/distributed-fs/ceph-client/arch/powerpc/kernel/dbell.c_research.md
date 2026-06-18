<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/dbell.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/dbell.c

## Purpose
`dbell.c` implements the PowerPC doorbell exception handler. Doorbells are used primarily for inter-processor interrupts and host/KVM notification paths.

## Important APIs, Types, And Functions
The file defines `doorbell_exception` with `DEFINE_INTERRUPT_HANDLER_ASYNC`. In SMP builds it uses `set_irq_regs()`, tracing hooks, `ppc_msgsync()`, `should_hard_irq_enable()`, `do_hard_irq_enable()`, `kvmppc_clear_host_ipi()`, per-CPU `irq_stat.doorbell_irqs`, and `smp_ipi_demux_relaxed()`.

## Control Flow
On SMP, the handler installs the active pt_regs, emits entry tracing, performs message synchronization, conditionally enables hard IRQs according to interrupt state, clears any host KVM IPI for the current CPU, increments statistics, demultiplexes relaxed SMP IPIs, emits exit tracing, and restores prior IRQ regs. On non-SMP builds it only logs a warning.

## State And Persistence
State changes are per-CPU interrupt statistics and clearing pending host IPI state. There is no persistent storage.

## Dependencies And Integration Points
It integrates with the generic interrupt framework, SMP IPI demux, KVM PPC host code, tracepoints, and PowerPC message synchronization semantics.

## Risks
Ordering is important: `ppc_msgsync()` and `smp_ipi_demux_relaxed()` rely on barriers being satisfied. Enabling hard IRQs too early or failing to restore IRQ regs can corrupt nested interrupt handling. Non-SMP receipt indicates platform misconfiguration.

## Test Signals
SMP boot, IPI stress tests, KVM host IPI tests, tracepoint consistency, and increasing `doorbell_irqs` counters are the main signals. Non-SMP builds should compile and warn only if a doorbell arrives.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/dbell.c -->
