# sources/distributed-fs/ceph-client/drivers/irqchip/irq-csky-apb-intc.c

## Purpose
Implements C-SKY APB and GX6605S root interrupt controllers with 64-line or dual 128-line support.

## Important APIs, Types, and Functions
Globals `reg_base`, `root_domain`, and `nr_irq` define the singleton controller. `ck_intc_init_comm()` performs common setup. `ck_set_gc()` configures generic chips and optional pulse-signal unmasking via `irq_ck_mask_set_bit()`. `gx_irq_handler()` and `ck_irq_handler()` dispatch pending bits; `setup_irq_channel()` initializes source-channel mapping.

## Control Flow
Init requires root placement, maps registers, creates a linear generic-chip domain, disables all IRQs, configures enable/mask/control registers by variant, initializes source channels with variant magic ordering, configures generic chips per 32-line bank, and installs the root handler. Handlers repeatedly process high then low pending registers until no bit remains.

## State and Persistence
MMIO enable/mask/source registers hold persistent controller state. Generic-chip mask caches track enabled bits. `nr_irq` is mutated for dual-controller mode before common init, and dual mode configures a second register block at `CK_INTC_DUAL_BASE`.

## Dependencies and Integration Points
Depends on C-SKY architecture IRQ entry, OF irqchip declarations, generic irqchip, and one-cell interrupt translation. It is a root interrupt controller and rejects parent nodes.

## Risks and Test Signals
Risks include singleton `nr_irq` mutation, pulse-signal IFR clearing tied to mask offset minus eight, source-channel magic ordering, and repeated handler loops if pending bits are not cleared by devices. Test signals are correct 64/128 domain size, disabled interrupts at boot, pulse-source delivery, and no parent-controller configuration accepted.
