# sources/distributed-fs/ceph-client/drivers/irqchip/irq-bcm7038-l1.c

## Purpose
Implements Broadcom BCM7038-style Level 1 interrupt controllers with status, mask-status, mask-set, and mask-clear registers, including SMP affinity and suspend wake support.

## Important APIs, Types, and Functions
`struct bcm7038_l1_chip` stores lock, word count, domain, per-CPU maps, forwarding mask, affinity table, and optional wake state/list linkage. Core functions include `bcm7038_l1_irq_handle()`, `__bcm7038_l1_mask()/unmask()`, `bcm7038_l1_set_affinity()`, `bcm7038_l1_init_one()`, PM syscore callbacks, and platform probe.

## Control Flow
Probe allocates the chip, initializes each possible CPU window, applies `brcm,int-fwd-mask`, creates a linear domain, optionally registers syscore PM hooks, and logs capacity. The chained handler selects the current CPU window, reads status masked by software mask cache, then dispatches each set child.

## State and Persistence
`mask_cache[]` tracks per-CPU hardware masks. `irq_fwd_mask[]` reserves lines forwarded elsewhere and rejected by map. `affinity[]` stores target CPU per hwirq. PM state includes `wake_mask[]` and a global list of controllers for syscore suspend/resume.

## Dependencies and Integration Points
Uses platform irqchip registration, OF resources/parent IRQs, chained handlers, optional MIPS SMP CPU mapping, generic IRQ domains, and syscore PM.

## Risks and Test Signals
Risks include forwarded IRQs being accidentally mapped, non-atomic affinity migration, boot CPU assumptions during suspend, endianness-specific MMIO access, and partial init cleanup gaps. Test signals include correct `brcm,int-fwd-mask` enforcement, wake-capable suspend/resume behavior, affinity changes on MIPS SMP, and stable mask cache after resume.
