<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/irq.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/irq.c

Purpose: generic PXA internal interrupt-controller support for legacy and device-tree boot paths.

Important APIs/functions: `pxa_mask_irq()` and `pxa_unmask_irq()` manipulate ICMR bank bits. `icip_handle_irq()` handles PXA25x-style pending IRQ scanning; `ichp_handle_irq()` handles CP6 ICHP priority register delivery. `pxa_init_irq()` initializes non-DT controllers, while `pxa_dt_irq_init()` maps an OF interrupt controller. `pxa_irq_syscore` saves/restores interrupt masks and priority registers across suspend.

Control flow: SoC init calls `pxa_init_irq_common()`, which creates a legacy IRQ domain, disables all IRQs, sets all as IRQ not FIQ, enables idle wake only for unmasked interrupts, and attaches an optional wake callback. IRQ entry loops until no pending unmasked interrupt remains.

State and persistence: persistent globals include `pxa_irq_base`, internal IRQ count, priority-support flag, IRQ domain, saved ICMR/IPR arrays under PM, and the mutable irq-chip wake callback.

Dependencies and integration: used by PXA25x/PXA27x/PXA3xx SoC files, Linux IRQ domain/chip APIs, OF address parsing, and ARM exception entry.

Risks and test signals: wrong IRQ count or base mapping breaks all interrupts. PXA25x lacks IPR, while later CPUs use it. Test timer IRQ, GPIO cascade, suspend/resume mask restoration, OF property `marvell,intc-nr-irqs`, and wake-enabled interrupt behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/irq.c -->
