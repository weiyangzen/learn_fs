# sources/distributed-fs/ceph-client/arch/x86/kernel/irq_32.c

## Purpose
Implements 32-bit x86 hardirq and softirq stack allocation/switching and low-stack overflow diagnostics before calling generic IRQ handling.

## Important APIs And State
Defines optional `sysctl_panic_on_stackoverflow`, per-CPU `softirq_stack_ptr`, `irq_init_percpu_irqstack()`, optional `do_softirq_own_stack()`, and `__handle_irq()`. It uses per-CPU `hardirq_stack_ptr` from common IRQ code.

## Control Flow
`irq_init_percpu_irqstack()` allocates per-CPU hardirq and softirq stacks with `THREAD_SIZE_ORDER`. `execute_on_irq_stack()` detects whether already on the hardirq stack, saves previous ESP at the bottom of the IRQ stack, optionally prints overflow diagnostics, switches stacks via inline asm and calls the IRQ descriptor handler. `__handle_irq()` checks low kernel stack, uses IRQ stack for kernel-mode interrupts when possible, otherwise handles directly. Softirq own-stack support similarly switches to per-CPU softirq stack for `__do_softirq()`.

## Dependencies And Integration Points
Depends on 32-bit stack layout, generic IRQ descriptors, `CALL_NOSPEC`, per-CPU stack pointers, softirq core, and debug stack overflow config.

## Risks And Test Signals
Risks include incorrect ESP switching/restoration, nested hardirq stack detection failure, stack overflow false negatives, and allocation failure during CPU bringup. Tests include 32-bit IRQ storms, nested interrupts, softirq-on-own-stack, CPU hotplug stack allocation, debug stack overflow panic mode, and nospec thunk correctness.
