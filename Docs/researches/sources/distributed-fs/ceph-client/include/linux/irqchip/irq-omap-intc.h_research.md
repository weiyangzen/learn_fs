# sources/distributed-fs/ceph-client/include/linux/irqchip/irq-omap-intc.h

## Purpose
`irq-omap-intc.h` declares OMAP interrupt controller hooks used by platform idle and suspend code.

## Important APIs, types, and functions
It declares `omap_irq_pending`, `omap_intc_save_context`, `omap_intc_restore_context`, `omap3_intc_suspend`, `omap3_intc_prepare_idle`, and `omap3_intc_resume_idle`.

## Control flow
OMAP PM code can check pending IRQs before idle, save/restore controller context over suspend, and run OMAP3-specific idle preparation/resume sequences.

## State and persistence
State is hardware interrupt controller context saved by the implementation and restored after low-power states.

## Dependencies and integration points
It integrates OMAP irqchip code with SoC idle, suspend, and wakeup paths.

## Risks and test signals
Risks include missed pending interrupts before idle, incomplete context restore, and suspend/resume ordering errors. Tests should cover idle entry/exit, wake sources, system suspend, and pending interrupt races.
