
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-eic-sprd.c

Purpose: supports Spreadtrum digital-chip External Interrupt Controller GPIO-like inputs across debounce, latch, async, and sync EIC submodules.

Important APIs/types/functions: `enum sprd_eic_type`, `struct sprd_eic`, and `struct sprd_eic_variant_data` describe each controller. Important functions are `sprd_eic_update()`, `sprd_eic_get()`, `sprd_eic_set_debounce()`, `sprd_eic_irq_mask()`, `sprd_eic_irq_unmask()`, `sprd_eic_irq_set_type()`, `sprd_eic_toggle_trigger()`, `sprd_eic_handle_one_type()`, `sprd_eic_irq_handler()`, and `sprd_eic_probe()`.

Control flow: probe selects the EIC type by compatible, maps up to three banks, configures GPIO operations appropriate to the type, attaches a gpio_irq_chip to one parent IRQ, registers the gpiochip, and registers an atomic notifier. Because all EIC submodules share one interrupt line, the parent chained handler calls a notifier chain so each instance scans its masked interrupt status. Debounce/latch modules emulate edge triggers by programming the opposite level after observing stable state; async/sync modules program native edge/level registers.

State and persistence behavior: the driver stores bank MMIO bases, type, IRQ, and spinlock. Hardware registers hold debounce, masks, polarity, and pending status. No suspend/resume context is present. Debounce request/free toggles debounce mask only for debounce EIC instances.

Dependencies and integration points: depends on OF compatibles for SC9860 EIC types, gpiolib IRQ helpers, chained IRQs, atomic notifier chains, and MMIO resources per bank.

Risks: notifier-chain dispatch means every EIC instance scans on every shared interrupt. Debounce/latch edge emulation can race with signal changes and loops until state is stable. Latch EIC exposes no `get()` callback. Debounce values are truncated to 12-bit millisecond units.

Test signals: probe for all four compatibles, bank-count-derived `ngpio`, trigger programming for level/edge/both on each type, shared-parent notifier dispatch, debounce config, and edge emulation when input changes during reprogramming.
