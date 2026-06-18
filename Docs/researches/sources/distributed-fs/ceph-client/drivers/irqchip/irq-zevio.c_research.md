# sources/distributed-fs/ceph-client/drivers/irqchip/irq-zevio.c

## Purpose
Implements the Zevio/TI-Nspire classic root interrupt controller. It initializes IRQ/FIQ priority blocks, exposes 32 IRQ lines through a generic-chip domain, and dispatches the current interrupt from hardware registers.

## Important APIs, Types, And Functions
Global `zevio_irq_domain` and `zevio_irq_io` store singleton state. `zevio_init_irq_base()` disables, sets max priority, and resets each IRQ/FIQ block. `zevio_irq_ack()` acks by reading the reset register. Generic-chip callbacks handle enable/disable mask registers.

## Control Flow
OF init rejects multiple instances, maps MMIO, programs non-inverted non-sticky highest-priority operation, initializes IRQ and FIQ blocks, creates a 32-line generic-chip domain, configures mask/enable/disable/ack offsets, installs the root handler, and logs controller presence. Runtime loops while status is nonzero, reads `IO_CURRENT`, and dispatches that hwirq.

## State And Persistence
State is global singleton domain/MMIO and generic chip mask cache. Hardware priority, invert, sticky, enable, and reset registers persist. There is no PM handling.

## Dependencies And Integration Points
Depends on ARM exception entry, OF address/init, generic irq chips, and compatible `lsi,zevio-intc`.

## Risks
The code uses `BUG_ON` for critical allocation/mapping failures. FIQ is initialized but not exposed as a separate domain. Ack by read from reset register is unusual and hardware-specific. Singleton guard rejects additional controllers.

## Test Signals
Boot supported hardware, confirm root handler installation, dispatch all 32 IRQs, verify priority/status loop exits, mask/unmask via generic chip, and ensure no second controller node is accepted.
