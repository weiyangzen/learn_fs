# sources/distributed-fs/ceph-client/drivers/irqchip/irq-digicolor.c

## Purpose
Implements the Conexant Digicolor interrupt controller as a 64-line root controller with two 32-bit banks.

## Important APIs, Types, and Functions
`digicolor_handle_irq()` is the root handler. `digicolor_set_gc()` configures generic chips for each bank. `digicolor_of_init()` maps the interrupt controller, configures a syscon UC register, creates the domain, and installs the handler.

## Control Flow
Init maps the IC, disables both banks, obtains a syscon regmap via `syscon` phandle, selects channel 1 regular IRQ mode, creates a 64-entry generic-chip domain, allocates two 32-line chips, sets ack/mask/unmask registers, and calls `set_handle_irq()`. Dispatch loops reading low bank first, then high bank, handling the first set bit each iteration.

## State and Persistence
Global `digicolor_irq_domain` anchors generic chips. Hardware enable/status/clear registers persist masks and acknowledgements. The UC syscon interrupt-channel selection is persistent platform state.

## Dependencies and Integration Points
Depends on OF, syscon/regmap, generic irqchip, and ARM exception entry. It is the root IRQ path for compatible Digicolor SoCs.

## Risks and Test Signals
Risks include missing syscon phandle, infinite dispatch if a level source is not cleared by its device, low-bank priority starvation, and absent cleanup after partial init failures. Test signals include successful regmap write, active low/high bank IRQ counters, ack register writes clearing latched flags, and no boot errors.
