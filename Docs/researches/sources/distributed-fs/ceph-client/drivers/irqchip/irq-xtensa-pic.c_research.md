# sources/distributed-fs/ceph-client/drivers/irqchip/irq-xtensa-pic.c

## Purpose
Implements the built-in Xtensa programmable interrupt controller. It provides the default irqdomain and simple mask/unmask/ack/retrigger operations over Xtensa special registers.

## Important APIs, Types, And Functions
`xtensa_pic_irq_domain_xlate()` handles one- or two-cell specifiers using common Xtensa translation. The irq chip updates `intenable`, clears pending bits through `intclear`, and retriggers software interrupts through `intset`.

## Control Flow
Legacy or DT init creates a domain, installs common Xtensa map ops, and sets it as the default domain. Runtime masking clears a bit in `intenable`, unmasking sets it, ack writes the hwirq bit to `intclear`, and retrigger rejects non-software interrupt types.

## State And Persistence
State is CPU-local special registers and the default domain. The file keeps no private heap or MMIO state and has no suspend/resume hooks.

## Dependencies And Integration Points
Depends on Xtensa architecture macros, common Xtensa irqchip helpers, irqdomain APIs, and compatible `cdns,xtensa-pic`.

## Risks
The controller directly manipulates special registers, so callers must respect CPU-local semantics. Retrigger only works for software interrupts. DT specifier translation must distinguish internal versus external numbering consistently with other Xtensa controllers.

## Test Signals
Boot legacy and DT platforms, verify default domain setup, mask/unmask/ack on internal interrupts, software retrigger behavior, and rejection of non-software retrigger attempts.
