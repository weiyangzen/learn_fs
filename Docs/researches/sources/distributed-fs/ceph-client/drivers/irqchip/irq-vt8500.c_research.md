# sources/distributed-fs/ceph-client/drivers/irqchip/irq-vt8500.c

## Purpose
Implements VIA/WonderMedia VT8500 interrupt controller support for primary and cascaded controllers. It exposes 64 hwirqs per instance with destination control, ack, mask/unmask, and trigger type programming.

## Important APIs, Types, And Functions
`struct vt8500_irq_data` stores MMIO base and domain. The irq chip implements ack by writing status, mask/unmask through destination control bytes, and trigger type selection for high level, rising edge, and falling edge. `vt8500_handle_irq_common()` dispatches the current highest-priority interrupt.

## Control Flow
OF init allocates state, maps MMIO, creates a 64-line one-cell domain, initializes hardware by enabling rotating priority and disabling/routing all lines to IRQ, then either chains parent interrupts or installs the global primary handler. Runtime reads the priority/current register, validates special hwirq 63 using status bit 31, and dispatches one domain IRQ.

## State And Persistence
State is per-controller domain/base plus global `primary_intc` for root mode. Hardware destination-control bytes carry enabled, route, and trigger state. There is no PM state cache.

## Dependencies And Integration Points
Depends on ARM exception entry, OF address/IRQ parsing, chained irq helpers, and compatible `via,vt8500-intc`.

## Risks
Low-level trigger is unsupported. The hwirq 63 special case relies on status register interpretation. Multiple controllers are supported only with exactly one primary and optional cascaded children. No explicit cleanup exists after successful early init.

## Test Signals
Boot primary-only and chained configurations, test hwirq 63 handling, mask/unmask, rising/falling/high trigger setup, and multiple parent IRQs on chained controllers.
