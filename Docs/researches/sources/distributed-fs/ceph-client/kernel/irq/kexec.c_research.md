# sources/distributed-fs/ceph-client/kernel/irq/kexec.c

## Purpose
`kexec.c` provides the genirq shutdown helper used before jumping into a kexec kernel. It masks and shuts down started interrupts and, where possible, clears active state or sends EOI so the next kernel does not inherit in-flight interrupt state.

## Important APIs, types, and functions
The only function is `machine_kexec_mask_interrupts()`. It iterates every `struct irq_desc` with `for_each_irq_desc()`, inspects the descriptor `irq_chip`, uses `irqd_is_started()`, optionally calls `irq_set_irqchip_state(..., IRQCHIP_STATE_ACTIVE, false)`, conditionally invokes `chip->irq_eoi()`, and finishes each descriptor through `irq_shutdown()`.

## Control flow
For each started interrupt, the function skips missing chips, tries VM-forwarded active-state clearing when `CONFIG_GENERIC_IRQ_KEXEC_CLEAR_VM_FORWARD` is enabled, falls back to EOI for in-progress IRQs with an EOI callback, and then shuts the descriptor down through the normal genirq shutdown path.

## State and persistence
The routine intentionally mutates live interrupt-controller and descriptor state immediately before kexec. It clears active/in-progress hardware state where supported and transitions descriptors to shutdown. No persistent storage is involved.

## Dependencies and integration points
It depends on the generic descriptor iterator, irqchip state callbacks, irqchip EOI operations, and `irq_shutdown()` from the core IRQ internals. It is invoked by architecture kexec flows rather than ordinary driver code.

## Risks and test signals
Risks include chips lacking active-state or EOI support, VM-forwarded interrupts not being cleared, EOI issued to the wrong in-progress state, and shutdown callbacks running late in a crash-like transition. Test signals include kexec with active device interrupts, passthrough/forwarded interrupts, chips with and without EOI callbacks, and verifying the new kernel does not see stuck interrupt lines.
