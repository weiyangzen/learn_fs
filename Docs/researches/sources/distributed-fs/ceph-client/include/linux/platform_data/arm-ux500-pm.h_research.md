# sources/distributed-fs/ceph-client/include/linux/platform_data/arm-ux500-pm.h

Purpose: declares UX500 platform power-management helpers for coordinating PRCMU/GIC state around low-power CPU idle and suspend flows.

Important APIs and types: exported functions include `prcmu_gic_decouple()`, `prcmu_gic_recouple()`, `prcmu_gic_pending_irq()`, `prcmu_pending_irq()`, `prcmu_is_cpu_in_wfi()`, `prcmu_copy_gic_settings()`, and `ux500_pm_init(phy_base, size)`.

Control flow: platform PM code initializes the PM interface, copies GIC settings, decouples interrupt control before deep idle/suspend, checks pending IRQ/PRCMU wake state, observes CPU WFI status, and recouples the GIC on exit.

State and persistence: runtime PM state is held by UX500 PRCMU/GIC platform code and hardware registers. No state is stored in this declaration header.

Dependencies and integration points: integrates ARM UX500 cpuidle/suspend code, PRCMU firmware/register access, GIC interrupt controller state, and wakeup handling.

Risks and test signals: risks include entering deep idle with pending interrupts, failing to restore GIC coupling, stale copied GIC settings, and CPU WFI detection races. Test cpuidle AFTR/deep states, wake interrupts, suspend/resume, multi-CPU WFI checks, and initialization with invalid physical base/size.
