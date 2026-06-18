# sources/distributed-fs/ceph-client/kernel/irq/generic-chip.c

## Purpose
`generic-chip.c` provides reusable IRQ chip implementations for common MMIO register layouts. It handles mask/unmask/ack/eoi/wake register operations, allocates and maps generic chips into IRQ domains, sets up direct IRQ ranges, supports alternate chip types by trigger mode, and hooks generic chips into syscore suspend/resume/shutdown.

## Important APIs, types, and functions
Register helpers include `irq_gc_mask_disable_reg()`, `irq_gc_mask_set_bit()`, `irq_gc_mask_clr_bit()`, `irq_gc_unmask_enable_reg()`, `irq_gc_ack_set_bit()`, `irq_gc_ack_clr_bit()`, `irq_gc_mask_disable_and_ack_set()`, `irq_gc_eoi()`, and `irq_gc_set_wake()`. Allocation/setup APIs include `irq_init_generic_chip()`, `irq_alloc_generic_chip()`, `irq_domain_alloc_generic_chips()`, `irq_domain_remove_generic_chips()`, `__irq_alloc_domain_generic_chips()`, `irq_get_domain_generic_chip()`, `irq_map_generic_chip()`, `irq_unmap_generic_chip()`, `irq_setup_generic_chip()`, `irq_setup_alt_chip()`, and `irq_remove_generic_chip()`. `irq_generic_chip_ops` is the standard domain ops table.

## Control flow
Generic callbacks lock `gc->lock`, update mask caches, and write the configured register offset relative to `gc->reg_base`. Domain allocation creates one `irq_chip_generic` per `irqs_per_chip`, initializes optional big-endian accessors and caller init hooks, then links chips into `gc_list`. Mapping validates the hwirq index, initializes mask cache on first install, computes the interrupt bit mask, installs chip/handler/domain info, and applies status flags. Removal unregisters handlers/chips and clears status. Syscore callbacks iterate `gc_list` to call chip or chip-generic suspend/resume/shutdown hooks.

## State and persistence
Persistent runtime state is in each `irq_chip_generic`: register base, lock, mask caches, wake masks, installed/unused bitmaps, chip types, domain pointer, and optional PM callbacks. The global `gc_list` tracks chips for system PM. Per-domain generic chip arrays live until domain removal; direct chips live until explicit removal or driver cleanup.

## Dependencies and integration points
The file depends on MMIO accessors, IRQ domains, descriptor configuration helpers, syscore PM, lockdep class assignment, and driver-provided `struct irq_chip_type` register descriptions. It is used heavily by simple irqchip drivers that do not need bespoke callbacks.

## Risks and test signals
Risks include incorrect mask-cache polarity for hardware, missing locking around shared registers, `irqs_per_chip` over 32-bit mask assumptions, installed/unused bitmap mistakes, alternate chip selection mismatch with trigger type, syscore iterating removed chips, and big-endian accessor misconfiguration. Test signals include register write traces for each helper, domain map/unmap, direct setup/remove, suspend/resume/shutdown callbacks, wake enable validation, nested lock class use, and trigger-type switching through `irq_setup_alt_chip()`.
