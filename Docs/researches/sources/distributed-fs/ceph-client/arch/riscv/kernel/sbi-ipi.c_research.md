<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/sbi-ipi.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/sbi-ipi.c

Purpose: Connects SBI IPI delivery to the Linux IRQ/IPI framework and advertises when SBI is used for remote fence operations.

Important APIs/types/functions: Defines static key `riscv_sbi_for_rfence`, `sbi_ipi_handle()`, CPU hotplug callback `sbi_ipi_starting_cpu()`, and init entry `sbi_ipi_init()`.

Control flow: Init creates an IPI irq domain/range, registers the SBI IPI handler, and installs a CPUHP startup callback. Incoming SBI IPI interrupts dispatch through `ipi_mux_process()`, while startup enables the per-CPU virq.

State and persistence: Stores the SBI IPI virq and static key. Per-CPU IRQ enablement follows CPU hotplug state.

Dependencies and integration points: Depends on SBI send-IPI support from `sbi.c`, the generic RISC-V IPI multiplexer in `smp.c`, irqdomain descriptors, and CPU hotplug.

Risks: Incorrect virq range setup loses IPIs or remote fences. CPU hotplug ordering must enable the interrupt before the CPU is targeted.

Test signals: SMP boot with SBI IPIs, CPU hotplug, call-function IPIs, reschedule/tick broadcast, remote fence traffic, and interrupt statistics under `/proc/interrupts`.

Source read size: 86 lines, 1974 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/sbi-ipi.c -->
