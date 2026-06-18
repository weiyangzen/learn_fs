# sources/distributed-fs/ceph-client/drivers/mfd/mt6397-irq.c

Purpose: IRQ controller for older MediaTek PMICs in the MT6323/MT6328/MT6331/MT6391/MT6397 line. It maps one to three 16-bit status/control registers into a nested IRQ domain and adjusts wake masks around system suspend.

Important APIs, types, and functions: `mt6397_irq_chip` implements mask/unmask, bus lock/sync unlock, and optional wake control. `mt6397_irq_handle_reg()` reads one status register, dispatches set bits through `handle_nested_irq()`, and writes status back to ack. `mt6397_irq_thread()` handles configured status banks. `mt6397_irq_pm_notifier()` switches hardware masks to `wake_mask[]` during `PM_SUSPEND_PREPARE` and restores `irq_masks_cur[]` on `PM_POST_SUSPEND`. `mt6397_irq_init()` selects register addresses by chip ID, masks all sources, creates the domain, requests the parent IRQ, and registers the PM notifier.

Control flow: the parent core calls init after reading chip ID. Child mask/unmask changes update in-memory masks until sync unlock writes interrupt-control registers. Parent IRQ fanout reads each available status bank. Suspend notifier narrows enabled hardware sources to those marked wake-capable and enables parent IRQ wake.

State and persistence: `struct mt6397_chip` holds interrupt control/status register addresses, current masks, wake masks, irqdomain, mutex, parent IRQ, and PM notifier. Hardware masks are active state in PMIC registers.

Dependencies and integration points: depends on `mt6397-core.c`, register headers, PM notifier infrastructure, regmap, and IRQ domain mapping. The IRQ domain is passed to child devices by the parent.

Risks: `register_pm_notifier()` is not checked and there is no visible unregister path. `enable_irq_wake()`/`disable_irq_wake()` return values are ignored. Mask semantics use set bits as enabled, which differs from many PMICs and must remain consistent with child expectations. Test signals include all chip ID register layouts, wake mask transitions over suspend/resume, three-bank MT6328 handling, status ack writes, and notifier cleanup during probe/remove failure.
