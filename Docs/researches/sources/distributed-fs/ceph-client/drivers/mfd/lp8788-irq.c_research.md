# sources/distributed-fs/ceph-client/drivers/mfd/lp8788-irq.c

Purpose: this companion file implements the LP8788 interrupt controller for the LP8788 MFD core. It maps PMIC interrupt status bits into nested Linux IRQs used by LP8788 child devices.

Important APIs, types, and functions: `struct lp8788_irq_data` holds the parent `struct lp8788`, mutex, IRQ domain, and enabled-bit shadow. `_irq_to_addr()`, `_irq_to_enable_addr()`, `_irq_to_mask()`, and `_irq_to_val()` translate enum IRQ IDs to status/enable registers. `lp8788_irq_chip` provides enable/disable and bus lock/sync operations. `lp8788_irq_handler()` reads three interrupt-status bytes and calls `handle_nested_irq()` for active bits. `lp8788_irq_init()` creates a linear firmware-node IRQ domain and requests a falling-edge threaded parent IRQ. `lp8788_irq_exit()` frees the parent IRQ and removes the domain.

Control flow: child IRQ enable/disable only updates the in-memory `enabled[]` array; hardware enable bits are written in `irq_bus_sync_unlock()` under `irq_lock`. The top-level threaded handler bulk-reads status registers and reports each asserted bit through the domain mapping.

State and persistence: `enabled[]` mirrors desired IRQ mask state; hardware enable registers persist until changed. `lp->irq` and `lp->irqdm` link the core driver to this interrupt layer. No devm cleanup is used for `request_threaded_irq()`, so explicit exit is required.

Dependencies and integration points: depends on the LP8788 exported regmap helpers, Linux IRQ domains, nested threaded IRQ handling, and resources declared in `lp8788.c`.

Risks: the handler comment says it reports only enabled IRQs, but the code checks only status bits and not `enabled[]`; if masked hardware status still appears, nested IRQs may be invoked unexpectedly. `free_irq(lp->irq, lp->irqdm)` passes a different dev_id than the requested `irqd`, which is a cleanup-risk signal. Tests should include IRQ domain mapping, enable/disable register writes, parent IRQ status fan-out, invalid IRQ-number behavior, and remove/error cleanup.
