# sources/distributed-fs/ceph-client/arch/riscv/kernel/irq.c

Purpose: Initializes RISC-V interrupt handling, optional IRQ stacks, shadow call stacks for IRQs, and softirq stack switching.

Important APIs/types/functions: Implements `init_IRQ()`, `do_softirq_own_stack()`, `arch_show_interrupts()`, IRQ stack initialization, SCS stack initialization, and per-CPU `irq_stack_ptr`.

Control flow: Boot initializes IRQ domains through irqchip probing and prepares per-CPU IRQ/SCS stacks where configured. Hard interrupt entry can call handlers on an IRQ stack through assembly, and softirq processing can be redirected to the IRQ stack.

State and persistence: Per-CPU IRQ stack arrays, stack pointers, and optional SCS stacks persist for each CPU.

Dependencies and integration points: Depends on irqchip, generic IRQ/softirq core, `entry.S` `call_on_irq_stack`, SCS, VMAP/IRQ stack config, and seq_file interrupt reporting.

Risks and test signals: Stack switching bugs corrupt task stacks or shadow call stacks. Test interrupt storms, softirq-heavy networking/storage, CPU hotplug with IRQ stacks, lockdep, and `/proc/interrupts`.
