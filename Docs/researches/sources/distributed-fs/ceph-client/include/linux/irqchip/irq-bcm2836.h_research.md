# sources/distributed-fs/ceph-client/include/linux/irqchip/irq-bcm2836.h

## Purpose
`irq-bcm2836.h` defines register offsets and local interrupt IDs for the BCM2836/Raspberry Pi 2 root local interrupt controller.

## Important APIs, types, and functions
It defines local control/prescaler/GPU routing/PM routing/timer/mailbox status and set/clear offsets, plus IRQ numbers for physical/virtual timers, mailboxes, GPU fast IRQ, PMU fast IRQ, and `LAST_IRQ`.

## Control flow
The BCM2836 irqchip driver writes routing and enable registers, reads per-CPU pending registers, uses mailbox set/clear registers for IPIs, and maps the local IRQ IDs into the generic IRQ domain.

## State and persistence
State is hardware register state for per-CPU local routing, timer/mailbox enables, pending bits, and mailbox latches.

## Dependencies and integration points
It integrates Raspberry Pi local interrupts with ARM timer, PMU, GPU interrupt routing, SMP IPIs, and generic IRQ domains.

## Risks and test signals
Risks include CPU/mailbox bit indexing errors, FIQ overriding IRQ routing, and stale mailbox bits. Tests should cover timer interrupts on each CPU, IPIs via mailbox 0, PMU routing, GPU fast IRQ routing, and SMP boot/hotplug.
