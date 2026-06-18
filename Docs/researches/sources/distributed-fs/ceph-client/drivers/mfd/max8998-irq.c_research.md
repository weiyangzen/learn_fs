# sources/distributed-fs/ceph-client/drivers/mfd/max8998-irq.c

Purpose: Nested IRQ controller for MAX8998 and LP3974 devices. It maps four interrupt status registers into logical child IRQs, manages per-register mask caches, and dispatches nested interrupts to MFD children.

Important APIs, types, and functions: `struct max8998_irq_data` gives each logical IRQ a status register index and mask bit. `max8998_irq_lock()`, `max8998_irq_sync_unlock()`, `max8998_irq_mask()`, and `max8998_irq_unmask()` implement the irq chip. `max8998_irq_thread()` bulk reads `MAX8998_REG_IRQ1` through the configured register count, applies masks, and calls `handle_nested_irq()` on irqdomain mappings. `max8998_irq_init()` initializes mask/status registers, creates an irqdomain, and requests primary and optional ONO IRQs. `max8998_irq_exit()` frees non-devm IRQs.

Control flow: the MAX8998 parent calls init after creating the RTC dummy client. Mask updates are staged in memory and pushed to hardware at bus sync unlock. The parent IRQ thread reads, masks, and reports asserted child IRQs. Resume invokes the IRQ thread to clear or relay sleep-latched status.

State and persistence: `irq_masks_cur`, `irq_masks_cache`, `irq_domain`, `irq_base`, `ono`, and `irqlock` live in `struct max8998_dev`. Hardware masks and status masks are initialized to all masked. The irqdomain can be legacy/simple depending on `irq_base`.

Dependencies and integration points: uses `max8998_write_reg()` and `max8998_bulk_read()` from `max8998.c`, IRQ domain helpers, and definitions in `max8998-private.h`. The domain supplies child IRQ resources to PMIC, RTC, and battery children.

Risks: `max8998_irq_domain_map()` declares its chip pointer as `struct max8997_dev *`, likely a typo that compiles only if structure layouts are not dereferenced directly there. Request failures after irqdomain creation do not remove the domain. If `irq_find_mapping()` unexpectedly fails, the parent IRQ is disabled. Test signals include mask synchronization, ONO path, resume replay on LP3974, irqdomain mapping, and negative tests for missing parent IRQ.
