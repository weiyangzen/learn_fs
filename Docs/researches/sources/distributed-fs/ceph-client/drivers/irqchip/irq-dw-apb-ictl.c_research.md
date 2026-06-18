# sources/distributed-fs/ceph-client/drivers/irqchip/irq-dw-apb-ictl.c

## Purpose
Implements the Synopsys DesignWare APB interrupt controller as either a root controller or a cascaded child controller.

## Important APIs, Types, and Functions
`dw_apb_ictl_init()` handles both root and cascaded init. `dw_apb_ictl_handle_irq()` and `dw_apb_ictl_handle_irq_cascaded()` dispatch root/chained interrupts. `dw_apb_ictl_irq_domain_alloc()` maps generic chips for hierarchical-style root allocation. `dw_apb_ictl_resume()` restores enable/mask registers.

## Control Flow
Init determines whether a parent exists, maps MMIO, writes enable/mask registers to discover synthesized IRQ width, creates a linear domain, allocates generic chips, configures each 32-line bank's register base and mask/unmask callbacks, then either chains to the parent IRQ or installs root `set_handle_irq()`. Dispatch scans all banks' final status bits.

## State and Persistence
Global `dw_apb_ictl_irq_domain` is used only for root mode. Generic-chip mask caches persist software masks and are restored on PM resume. Hardware mask registers use set-bit-to-mask, clear-bit-to-unmask semantics.

## Dependencies and Integration Points
Depends on OF resources/parent IRQs, generic irqchip, chained IRQ helpers, and root ARM IRQ entry. It supports variable IP synthesis widths from 2 to 64 IRQs.

## Risks and Test Signals
Risks include wrong hwirq offset in root handler for banks beyond zero, destructive enable-register probing on live hardware, parent parse failure, and register-bank base offset assumptions. Test signals include discovered IRQ count, chained/root delivery, PM resume mask restoration, and multi-bank interrupt tests.
