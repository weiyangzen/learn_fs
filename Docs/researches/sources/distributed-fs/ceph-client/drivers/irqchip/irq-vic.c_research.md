# sources/distributed-fs/ceph-client/drivers/irqchip/irq-vic.c

## Purpose
Implements ARM PL190/PL192 Vectored Interrupt Controller support for legacy ARM platforms. It can operate as a root controller or cascaded controller, supports valid/wakeup source masks, and saves/restores VIC registers for PM.

## Important APIs, Types, And Functions
`struct vic_device` stores MMIO base, base IRQ, valid and resume source masks, saved registers, and domain. Static `vic_devices` holds early controllers. Core functions include `vic_register()`, `vic_handle_irq()`, `vic_handle_irq_cascaded()`, `vic_ack_irq()`, `vic_mask_irq()`, `vic_unmask_irq()`, and vendor-aware `__vic_init()`.

## Control Flow
OF init maps registers, reads `valid-mask` and `valid-wakeup-mask`, gets an optional parent IRQ, then calls `__vic_init()`. Initialization identifies the AMBA vendor, disables and clears interrupts, initializes vector registers, creates a simple domain, pre-creates valid mappings, and installs either root or chained handling. PM late init registers syscore ops when any VIC exists.

## State And Persistence
Static device records persist for the kernel lifetime. PM saves interrupt select, enable, soft interrupt, and protect registers; suspend enables only resume IRQs, and resume restores saved state. Wake configuration is maintained as `resume_irqs` filtered by `resume_sources`.

## Dependencies And Integration Points
Depends on ARM exception entry, AMBA vendor IDs, OF irqchip init, simple irqdomains, syscore PM, and compatible strings `arm,pl190-vic`, `arm,pl192-vic`, and `arm,versatile-vic`.

## Risks
Static array size is controlled by `CONFIG_ARM_VIC_NR`. Vendor-specific ST 64-interrupt behavior uses offset-sensitive initialization. Wake source validation depends on correct base IRQ calculation. Root handler polling can spin if status never clears.

## Test Signals
Boot ARM and ST VIC variants, verify valid-mask mapping, root and cascaded handling, soft interrupt ack clearing, wake-mask suspend/resume, and multiple VIC ordering during resume.
