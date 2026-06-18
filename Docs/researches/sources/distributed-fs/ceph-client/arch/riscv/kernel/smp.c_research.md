<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/smp.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/smp.c

Purpose: Implements RISC-V SMP IPI routing, CPU stop/crash coordination, reschedule/call-function/tick broadcast IPIs, backtrace IPIs, and IPI statistics.

Important APIs/types/functions: Defines IPI message types, `__cpuid_to_hartid_map`, `smp_setup_processor_id()`, `riscv_hartid_to_cpuid()`, `send_ipi_mask()`, `handle_IPI()`, `riscv_ipi_enable/disable()`, `riscv_ipi_set_virq_range()`, `show_ipi_stats()`, `arch_send_call_function_ipi_mask()`, `smp_send_stop()`, `crash_smp_send_stop()`, `arch_smp_send_reschedule()`, `arch_trigger_cpumask_backtrace()`, and `kgdb_roundup_cpus()`.

Control flow: IPI senders map logical CPUs to IPI message bits and call the irqchip/SBI-backed send operation. The shared IPI interrupt handler drains pending message bits and dispatches reschedule, call-function, CPU stop, CPU crash-stop, IRQ work, and timer broadcast actions. Stop/crash paths send IPIs, wait for acknowledgements, and report failures.

State and persistence: Keeps CPU-to-hart mapping, per-IPI virq descriptors, per-CPU dummy devices, and crash-stop atomic counters. Pending message bits live in generic IPI mux state.

Dependencies and integration points: Works with `sbi-ipi.c`, irqchip-provided IPI ranges, scheduler reschedule, generic SMP call functions, tick broadcast, crash/kdump, KGDB, and stack backtrace infrastructure.

Risks: Missing IPI virq setup or wrong CPU mask filtering can hang SMP boot, stop_machine, or TLB shootdowns. Crash-stop paths run in fragile contexts and must avoid waiting forever.

Test signals: SMP boot, CPU hotplug, reschedule and call-function stress, tick broadcast, panic/kdump CPU stopping, KGDB roundup, and `/proc/interrupts` IPI counters.

Source read size: 367 lines, 7913 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/smp.c -->
