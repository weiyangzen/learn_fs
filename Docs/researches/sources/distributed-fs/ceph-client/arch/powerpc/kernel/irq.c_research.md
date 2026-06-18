# sources/distributed-fs/ceph-client/arch/powerpc/kernel/irq.c

## Purpose
Provides generic PowerPC IRQ handling glue: interrupt accounting, IRQ stack switching, platform IRQ dispatch, softirq stack support, IRQ initialization, hardware IRQ lookup, and SMP IRQ CPU selection.

## Important APIs, Types, And Functions
Defines and exports per-CPU `irq_stat`, plus `ppc_n_lost_interrupts` on PPC32. Key functions are `arch_show_interrupts`, `arch_irq_stat_cpu`, `__do_IRQ`, `do_IRQ`, `init_IRQ`, `do_softirq_own_stack`, `virq_to_hw`, and `irq_choose_cpu`. Internal helpers include `check_stack_overflow`, `call_do_softirq`, `__do_irq`, `call_do_irq`, `alloc_vm_stack`, and `vmap_irqstack_init`. It defines static call `ppc_get_irq`.

## Control Flow
`init_IRQ` allocates vmapped hard/soft IRQ stacks when configured, calls platform IRQ init, and patches the static call to `ppc_md.get_irq`. On an external interrupt, `do_IRQ` calls `__do_IRQ`, which switches to the per-CPU hardirq stack if not already on it, then `__do_irq` traces entry, checks stack depth, asks the platform interrupt controller for a virtual IRQ, optionally hard-enables interrupts for perf, handles spurious IRQ zero, and calls `generic_handle_irq`. Softirqs can similarly run on a per-CPU softirq stack. `/proc/interrupts` and `/proc/stat` aggregate architecture counters.

## State And Persistence
State includes per-CPU IRQ statistics, hardirq/softirq stack pointers, BookE critical/debug/machine-check stack arrays, static call target, and SMP round-robin rover protected by a raw spinlock. All state is runtime memory.

## Dependencies And Integration Points
Depends on generic IRQ core, `ppc_md.get_irq` and `ppc_md.init_IRQ`, tracing, lockdep, vmalloc, softirq stack support, device tree/PCI IRQ infrastructure, SMP CPU maps, and PowerPC stack frame conventions.

## Risks And Edge Cases
Risks include stack overflow during nested interrupts, failing to allocate vmapped stacks, platform `get_irq` returning zero for real interrupts, hard-enabling IRQs too early, static call not installed, and round-robin CPU selection on masks with no online CPUs. Inline assembly stack switching must preserve ABI-clobbered registers correctly.

## Test Signals
Signals include `/proc/interrupts` counters, spurious IRQ counts, timer/perf/doorbell/MCE/HMI accounting, interrupt storm tests, vmapped IRQ stack boot, softirq-on-own-stack tests, platform PIC dispatch, and SMP affinity distribution checks.
