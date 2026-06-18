# sources/distributed-fs/ceph-client/kernel/irq/pm.c

## Purpose
`pm.c` implements system power-management behavior for interrupts. It suspends device IRQs, preserves wakeup-capable lines, records wakeup events, and resumes early or normal IRQs during syscore and device resume.

## Important APIs, types, and functions
Key functions are `irq_pm_handle_wakeup()`, `irq_pm_install_action()`, `irq_pm_remove_action()`, `suspend_device_irqs()`, `rearm_wake_irq()`, `resume_device_irqs()`, and the syscore resume hook registered by `irq_pm_init_ops()`. Internal helpers are `suspend_device_irq()`, `resume_irq()`, and `resume_irqs()`.

## Control flow
Action installation/removal updates descriptor counters for `IRQF_FORCE_RESUME`, `IRQF_NO_SUSPEND`, and `IRQF_COND_SUSPEND`. Suspend iterates descriptors, skips nested-thread IRQs and no-suspend/chained/unused lines, arms wakeup IRQs, optionally enables disabled wake lines for chips requiring that, disables non-wakeup IRQs, masks chips that request mask-on-suspend, and synchronizes when needed. Resume clears wakeup-armed state, restores IRQs enabled only for suspend wakeup, force-resumes requested lines, and separates early resume (`IRQF_EARLY_RESUME`) from normal resume.

## State and persistence
State lives in `desc->istate`, `desc->depth`, PM action counters, and irqdata flags such as `IRQD_WAKEUP_ARMED` and `IRQD_IRQ_ENABLED_ON_SUSPEND`. It persists only across the active suspend/resume cycle.

## Dependencies and integration points
It depends on irq descriptor locking, wakeup irqchip flags, genirq enable/disable helpers, `pm_system_irq_wakeup()`, syscore registration, suspend infrastructure, and action flags installed by `manage.c`.

## Risks and test signals
Risks include wakeup IRQs left enabled or disabled incorrectly, missing synchronization before suspend completes, nested threaded IRQ mishandling, force-resume depth inconsistencies, shared no-suspend/conditional-suspend accounting errors, and chips requiring mask-on-suspend. Test signals include suspend/resume with wake-capable disabled IRQs, early-resume handlers, force-resume actions, shared IRQs mixing suspend flags, wake event rearming, and irqchips with `IRQCHIP_ENABLE_WAKEUP_ON_SUSPEND` or `IRQCHIP_MASK_ON_SUSPEND`.
