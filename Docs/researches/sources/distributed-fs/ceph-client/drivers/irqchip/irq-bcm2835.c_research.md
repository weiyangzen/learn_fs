# sources/distributed-fs/ceph-client/drivers/irqchip/irq-bcm2835.c

## Purpose
Implements the BCM2835/BCM2836 ARMCTRL interrupt controller handling banked GPU/peripheral interrupts, including BCM2835 root operation and BCM2836 chained operation.

## Important APIs, Types, and Functions
`struct armctrl_ic` stores register pointers and the domain. `armctrl_of_init()` performs setup for both variants, `armctrl_xlate()` maps bank/bit cells to packed hwirqs, and `bcm2835_handle_irq()`/`bcm2836_chained_handle_irq()` dispatch pending interrupts. `get_next_armctrl_hwirq()` handles bank and shortcut quirks.

## Control Flow
Init maps registers, creates a linear domain for three banks, creates mappings for valid bank bits, installs level handlers, disables bootloader-left enabled IRQs/FIQ, and either installs a root handler or chains to a parent IRQ. Dispatch repeatedly reads bank0, resolves shortcuts/bank indicators, and calls `generic_handle_domain_irq()`.

## State and Persistence
State is global `intc`, register pointer arrays, and hardware enable/disable/pending registers. The driver has no software mask cache; mask/unmask writes directly to bank enable/disable registers. Shortcut mapping is static.

## Dependencies and Integration Points
Depends on OF address/IRQ parsing, irqdomain, ARM exception handling, and special BCM2835 bank semantics. It may sit under BCM2836 local interrupt controller for Raspberry Pi 2-style systems.

## Risks and Test Signals
Risks include shortcut interrupts that bypass bank indicators, invalid bank0 bits, boot firmware leaving FIQs enabled, and panics on domain/mapping failures. Test signals are correct DT bank translation, no bootloader-left IRQ warnings after clean firmware setup, and visible banked interrupt counts under load.
