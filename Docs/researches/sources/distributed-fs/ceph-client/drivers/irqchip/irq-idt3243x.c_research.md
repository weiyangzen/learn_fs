<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-idt3243x.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-idt3243x.c

## Purpose
Implements the IDT/Renesas 79RC3243x 32-source interrupt controller as a cascaded generic irqchip.

## Important APIs, Types, And Functions
`struct idt_pic_data` holds the MMIO base, irqdomain, and generic chip pointer. `idt_pic_init()` maps the parent and MMIO resources, creates a linear domain, allocates domain generic chips, sets mask/unmask callbacks, masks all sources, and installs `idt_irq_dispatch()`.

## Control Flow
Runtime dispatch enters from the parent chained IRQ, reads pending bits, masks out sources that are disabled in `gc->mask_cache`, and forwards each set bit to the domain. Child interrupts use `handle_level_irq`, `irq_gc_mask_set_bit`, and `irq_gc_mask_clr_bit` against the PIC mask register.

## State And Persistence
State is the private struct, domain, generic chip `mask_cache`, and the hardware mask register. There are no power-management callbacks or late dynamic state beyond IRQ mappings.

## Dependencies And Integration Points
It depends on OF IRQ/address helpers, chained IRQ support, generic irqchip, and compatible `idt,32434-pic`. It exposes a 32-entry linear domain under one parent interrupt line.

## Risks
The dispatcher relies on `mask_cache` matching the hardware mask register; out-of-band writes would cause stale filtering. All IRQs are level handled, so edge-like sources need hardware latching. Init error paths must clean parent mapping and MMIO.

## Test Signals
Test parent cascade registration, pending-bit fan-out, mask cache filtering, all 32 child mappings, and probe failures with missing parent IRQ, MMIO base, or domain allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-idt3243x.c -->
