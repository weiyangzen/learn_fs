# sources/distributed-fs/ceph-client/drivers/irqchip/irq-uniphier-aidet.c

## Purpose
Implements Socionext UniPhier AIDET, an interrupt detector/polarity inverter in front of a GIC. It lets active-low and falling-edge child requests be represented while the parent sees active-high/rising signals.

## Important APIs, Types, And Functions
`struct uniphier_aidet_priv` stores the hierarchy domain, MMIO base, spinlock, and saved DETCONF registers. `uniphier_aidet_irq_set_type()` programs inverter bits and converts low/falling types to parent high/rising. Domain allocation validates one IRQ, sets the child chip, and allocates a GIC SPI parent fwspec.

## Control Flow
Probe finds the parent domain, maps MMIO, initializes the lock, and creates a 256-line hierarchy domain. Allocation translates two-cell child specifiers, validates hwirq and type, installs the AIDET chip, builds a GIC SPI fwspec, and allocates the parent. Suspend saves eight DETCONF words; resume restores them.

## State And Persistence
State is one device-managed private structure and saved DETCONF values for noirq PM. Runtime polarity state is the DETCONF inverter register. Mask/unmask/eoi/affinity operations are delegated to the parent.

## Dependencies And Integration Points
Depends on OF platform probing, parent irqdomain lookup, GIC-style parent semantics, noirq PM, and UniPhier compatible strings from LD4 through NX1.

## Risks
The parent is hard-coded as GIC SPI with hwirq equal to child hwirq. Type conversion must match hardware inverter behavior or low/falling signals will be lost. Multi-IRQ allocation is rejected. PM save/restore only covers DETCONF, not parent state.

## Test Signals
Validate all supported UniPhier compatibles, high/low level and rising/falling edge conversions, parent SPI allocation, suspend/resume retention of DETCONF, and invalid hwirq/type rejection.
