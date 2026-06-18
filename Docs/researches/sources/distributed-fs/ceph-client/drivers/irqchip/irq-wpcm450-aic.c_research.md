# sources/distributed-fs/ceph-client/drivers/irqchip/irq-wpcm450-aic.c

## Purpose
Implements the Nuvoton WPCM450 Advanced Interrupt Controller as a 32-line root irqchip. It initializes source priorities/types, reads the priority encoding register to identify active interrupts, and EOIs through the end-of-service register.

## Important APIs, Types, And Functions
`struct wpcm450_aic` stores MMIO base and domain. `wpcm450_aic_init_hw()` masks all lines, primes IPER/EOSCR, and sets every source to high-level priority 7. The irq chip supports eoi, mask, unmask, and a restricted set_type accepting only level-high.

## Control Flow
OF init requires no parent, allocates singleton state, maps MMIO, initializes hardware, installs `set_handle_irq()`, and creates a 32-line two-cell domain. Runtime reads IPER, divides by four to get the hwirq, dispatches it, and EOIs after handler completion.

## State And Persistence
Global singleton `aic` holds controller state. Hardware mask/source/priority/EOS registers persist. There is no PM state or multi-instance support.

## Dependencies And Integration Points
Depends on ARM exception entry, OF address/init, irqdomain, and compatible `nuvoton,wpcm450-aic`.

## Risks
Only level-high interrupts are accepted despite hardware supporting more modes, so DTs using edge/low types fail. No parent is allowed. Domain creation return is not checked after initialization, so allocation failure would leave a partially installed root handler.

## Test Signals
Boot WPCM450, verify all 32 hwirqs map, level-high interrupt delivery and EOI, mask/unmask command registers, rejection of non-level-high DT trigger types, and no-parent enforcement.
