# sources/distributed-fs/ceph-client/drivers/mfd/wm8350-irq.c

`wm8350-irq.c` implements nested IRQ support for WM8350-family PMICs. It maps primary and secondary PMIC interrupt bits to Linux IRQ descriptors, tracks masks, configures parent IRQ polarity, and dispatches nested child interrupts from a threaded handler.

Important functions and data are `struct wm8350_irq_data`, `wm8350_irqs[]`, `wm8350_irq()`, `wm8350_irq_enable()`, `wm8350_irq_disable()`, `wm8350_irq_sync_unlock()`, `wm8350_irq_init()`, and `wm8350_irq_exit()`. Init masks top-level and individual sources, reads back mask registers, initializes `irq_lock`, allocates IRQ descriptors, configures parent IRQ polarity from platform data, installs nested edge handlers, requests the threaded parent IRQ, and unmasks top-level interrupts. The threaded handler reads `WM8350_SYSTEM_INTERRUPTS` minus its mask, lazily reads secondary status registers, applies cached masks, and dispatches `wm8350->irq_base + i`.

State includes `irq_lock`, `irq_masks[]`, `chip_irq`, `irq_base`, and hardware interrupt mask/status/polarity registers. Dependencies include genirq nested-thread APIs, WM8350 core helpers, platform IRQ base/polarity data, and child drivers using offsets from `irq_base`.

Risks: `primary_only` is present in descriptors but not used by dispatch; descriptor allocation failure returns 0 and leaves the device probed without child IRQs; copied source includes a duplicated codec primary initializer; `wm8350_irq_exit()` frees `chip_irq` unconditionally; mask sync writes all mask registers every unlock. Test signals include no-IRQ, low-trigger, and high-trigger probes; descriptor setup; charger/RTC/AUXADC/GPIO/comparator/codec/UV/OC dispatch; and forced IRQ allocation/request failures.
