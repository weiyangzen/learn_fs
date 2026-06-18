# sources/distributed-fs/ceph-client/drivers/irqchip/irq-sun4i.c

## Purpose
Implements the legacy Allwinner A1X/SUNIV root interrupt controller. It is a primary ARM irqchip that installs the global `handle_irq` entry and exposes 96 hwirqs through a one-cell linear domain.

## Important APIs, Types, And Functions
`struct sun4i_irq_chip_data` stores MMIO base, domain, and SoC-specific enable/mask register offsets. The irq chip implements ack for NMI hwirq 0, mask/unmask through enable registers, and fasteoi handling. `sun4i_handle_irq()` reads the vector register and dispatches domain hwirqs.

## Control Flow
OF init allocates singleton state, chooses register offsets for A10 or SUNIV, maps MMIO, disables all interrupts, unmasks mask registers, clears pending bits, enables protection, configures NMI source type, creates the domain, and installs `set_handle_irq()`. Runtime reads the vector, special-cases hwirq 0 by checking pending status, and loops until no vector remains.

## State And Persistence
State is a global singleton pointer plus register state. There is no suspend/resume cache; this controller is expected to remain configured or be restored by platform code.

## Dependencies And Integration Points
Depends on ARM exception entry, OF address/init, irqdomain, and compatible `allwinner,sun4i-a10-ic` or `allwinner,suniv-f1c100s-ic`.

## Risks
Global singleton design excludes multiple instances. Vector value zero is ambiguous and requires the pending-register check; incorrect handling could drop hwirq 0 or spin on spurious interrupts. Register offsets differ between variants and must match compatible selection.

## Test Signals
Boot on supported Allwinner SoCs, verify root handler installation, hwirq 0/NMI delivery, normal peripheral interrupts across all three banks, and no stale pending interrupts after initialization.
