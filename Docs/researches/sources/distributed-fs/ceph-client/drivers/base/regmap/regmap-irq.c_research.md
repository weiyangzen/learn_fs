<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-irq.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-irq.c

Purpose: Implements a generic nested IRQ controller for devices whose interrupt status, mask, ack, wake, and type registers are accessed through regmap.

Important APIs/types/functions: `struct regmap_irq_chip_data` stores runtime buffers, domain, lock, regmap, chip config, parent IRQ, wake count, and register mapping callback. Exported APIs include `regmap_add_irq_chip_fwnode()`, `regmap_add_irq_chip()`, `regmap_del_irq_chip()`, devm variants, `regmap_irq_get_irq_reg_linear()`, `regmap_irq_set_type_config_simple()`, `regmap_irq_chip_get_base()`, `regmap_irq_get_virq()`, and `regmap_irq_get_domain()`. Core handlers are `regmap_irq_sync_unlock()`, `regmap_irq_enable()`, `regmap_irq_disable()`, `regmap_irq_set_type()`, `regmap_irq_set_wake()`, `read_irq_data()`, and `regmap_irq_thread()`.

Control flow: Add validates chip geometry, allocates status/mask/wake/type/config buffers, initializes all interrupts masked, syncs hardware mask/unmask registers or calls `handle_mask_sync`, optionally acks masked pending interrupts, initializes wake registers, stores level-trigger baseline state, creates an IRQ domain, and requests a threaded parent IRQ. The IRQ thread optionally runs pre/post callbacks and runtime PM, reads status via no-status, main-status/sub-status, bulk, or per-register paths, handles level-change filtering, masks disabled IRQs, acks pending status early, and dispatches nested IRQs through the domain. Bus lock/unlock batches enable/disable/type/wake changes and writes them to hardware on unlock.

State and persistence behavior: Runtime state persists in heap-allocated buffers until deletion or devres release. `mask_buf`, `wake_buf`, `type_buf`, and `config_buf` stage software state; sync-unlock persists it to device registers. `prev_status_buf` stores previous level status. `wake_count` is a delta propagated to the parent IRQ wake state.

Dependencies and integration points: Depends on IRQ domain APIs, nested threaded IRQ handling, regmap reads/writes/update_bits/bulk reads, runtime PM, devres, firmware nodes, and lockdep keys. It integrates with driver-provided `struct regmap_irq_chip` metadata and callbacks.

Risks: Chip configuration must match register stride, masks, and number of registers or interrupts can be missed or storm. `clear_on_unmask` conflicts with ack modes and is rejected. Bulk status reads are used only for linear stride-1 layouts. Ack polarity and clear-ack behavior are hardware-specific and dangerous if misdeclared. Runtime PM errors are logged but some paths continue. Devm release depends on storing the correct `d->irq`.

Test signals: Strong tests cover add-time validation, initial masking/ack/wake writes, enable/disable batching, type-in-mask and config callbacks, main-status subregister reads, level status edge detection, wake propagation, holes in IRQ lists, and devm release/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-irq.c -->
