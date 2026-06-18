# sources/distributed-fs/ceph-client/arch/parisc/kernel/irq.c

## Purpose

`irq.c` implements PA-RISC external interrupt masking, CPU IRQ chips, transaction interrupt allocation, `/proc/interrupts` formatting, optional IRQ stacks, stack-overflow checks, and the main CPU interrupt dispatch routine.

## Important APIs, Types, And Functions

`cpu_eiem` is the global external interrupt enable mask, and per-CPU `local_ack_eiem` suppresses an interrupt while it is acknowledged and in service. `EIEM_MASK()` converts a virtual IRQ number to the big-endian EIEM bit.

The `cpu_interrupt_type` irq chip provides `cpu_mask_irq()`, `cpu_unmask_irq()`, `cpu_ack_irq()`, and `cpu_eoi_irq()`. SMP affinity validation is handled by `cpu_check_affinity()`.

Transaction helpers include `cpu_claim_irq()`, `txn_claim_irq()`, `txn_alloc_irq()`, `txn_affinity_addr()`, `txn_alloc_addr()`, and `txn_alloc_data()`. They map Linux virtual IRQs to processor transaction addresses and EIRR data bits for I/O devices.

`show_interrupts()` and `arch_show_interrupts()` format normal and architecture-specific interrupt/trap counters. `do_cpu_irq_mask()` is called from entry assembly to dispatch external interrupts. `init_IRQ()` initializes the CPU IRQ range and enables timer/IPI masks.

With `CONFIG_IRQSTACKS`, `union irq_stack_union`, `execute_on_irq_stack()`, and `do_softirq_own_stack()` provide separate IRQ/softirq stacks.

## Control Flow

Masking clears a bit in `cpu_eiem`; unmasking sets it and sends NOP IPIs so other CPUs refresh EIEM. Ack clears the bit from the local per-CPU ack mask, writes the effective EIEM, and clears the pending EIRR bit through control register 23. EOI restores the local mask bit and re-enables the effective EIEM.

`do_cpu_irq_mask()` saves current irq regs, disables local IRQs, enters RCU irq context, reads pending EIRR masked by both global and local masks, converts the highest pending bit to a virtual IRQ, filters spurious IRQs, optionally redirects per-CPU SMP interrupts to their affine CPU, checks stack usage, and calls `generic_handle_irq()` either directly or on the IRQ stack. Before return it restores EIEM when no interrupt was handled or after masked-out paths.

`init_IRQ()` clears all pending external interrupts, claims CPU IRQs, installs timer and optional IPI handlers, initializes `cpu_eiem`, and writes EIEM.

## State And Persistence Behavior

Runtime state includes the global EIEM mask, per-CPU ack masks, per-CPU interrupt statistics, IRQ stack locks and usage counters, the `sysctl_panic_on_stackoverflow` knob, and IRQ descriptor chip/handler assignments. No persistent storage is used.

## Dependencies And Integration Points

The file integrates with generic IRQ descriptors, timer and IPI handlers, SMP CPU data transaction addresses, GSC I/O writes for interrupt redirection, PA-RISC control registers, entry assembly, RCU irq accounting, and stack debugging.

## Risks

EIEM/EIRR bit numbering is big-endian and easy to get wrong. `cpu_eiem` is a volatile global manipulated without an explicit spinlock in some paths, relying on interrupt context and architecture expectations. Affinity redirection must avoid losing per-CPU interrupts. IRQ stack locking uses low-level ldcw semantics; mistakes can recurse or corrupt stacks. Stack-overflow panic logic mutates a sysctl flag to prevent repeated panics.

## Test Signals

Signals include timer ticks, IPI delivery, working device interrupts, sane `/proc/interrupts` output, IRQ affinity changes, transaction IRQ allocation for GSC/PCI/MSI users, stack usage counters under debug configs, and no lost interrupts during mask/unmask storms on SMP.
