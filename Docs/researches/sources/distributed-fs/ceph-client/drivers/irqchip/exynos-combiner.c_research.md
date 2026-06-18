# sources/distributed-fs/ceph-client/drivers/irqchip/exynos-combiner.c

Purpose: Implements the Samsung Exynos IRQ combiner, a cascaded controller that groups eight interrupt sources per combiner input and forwards them to parent IRQs.

Important APIs/types/functions: `struct combiner_chip_data`, `combiner_mask_irq()`, `combiner_unmask_irq()`, `combiner_handle_cascade_irq()`, `combiner_irq_domain_xlate()`, `combiner_irq_domain_map()`, `combiner_init_one()`, `combiner_of_init()`, and PM syscore suspend/resume hooks.

Control flow: OF init maps registers, reads optional `samsung,combiner-nr`, allocates per-combiner state, creates a linear IRQ domain, parses each parent IRQ, disables all group bits, and installs a chained handler. The chained handler reads status, masks to the current 8-source group, handles the first pending hwirq via the domain, and exits the parent chain.

State and persistence: Global state includes `combiner_data`, `combiner_irq_domain`, `max_nr`, and per-combiner base/mask/parent fields. Under `CONFIG_PM`, enabled bits are saved before suspend and restored after clearing all group bits on resume.

Dependencies/integration: Uses OF address/IRQ parsing, irqdomain, chained IRQ helpers, syscore PM, and generic level handlers.

Risks and test signals: Test multiple pending bits in one cascade, missing parent IRQ mappings, `combiner-nr` sizing, suspend/resume restore, affinity delegation to parent irqchip, and whether only servicing `__ffs(status)` per parent interrupt is sufficient on all hardware.
