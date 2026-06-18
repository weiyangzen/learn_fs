# sources/distributed-fs/ceph-client/include/linux/irqchip/irq-madera.h

## Purpose
`irq-madera.h` enumerates Cirrus Logic Madera codec interrupt lines and provides wrapper helpers for child MFD drivers to map, request, free, and configure wake for those interrupts.

## Important APIs, types, and functions
It defines `MADERA_IRQ_*` IDs for clocks, jack/mic detection, DSPs, headphone/speaker faults and enable-done events, GPIOs, and bus errors, plus `MADERA_NUM_IRQ`. Helpers are `madera_get_irq_mapping`, `madera_request_irq`, `madera_free_irq`, and `madera_set_irq_wake`.

## Control flow
Child drivers pass a Madera-local IRQ number. The helpers ensure an IRQ device exists, translate through `regmap_irq_get_virq`, and call generic `request_threaded_irq`, `free_irq`, or `irq_set_irq_wake`.

## State and persistence
State lives in the parent `struct madera`: IRQ device presence and regmap IRQ data. The header has no independent state.

## Dependencies and integration points
It depends on the Madera MFD core, regmap IRQ, and threaded IRQ APIs. It integrates codec subdrivers with a shared parent interrupt controller.

## Risks and test signals
Risks include stale or absent `irq_dev`, wrong local IRQ IDs, ONESHOT handler expectations, and wake configuration on unmapped IRQs. Tests should cover each child requesting/freeing IRQs, parent probe failure, wake enable/disable, and IRQ delivery for jack, DSP, GPIO, and fault events.
