# sources/distributed-fs/ceph-client/drivers/clocksource/timer-zevio.c

## Purpose

`timer-zevio.c` supports LSI Zevio timer blocks. It optionally creates a one-shot clockevent from timer1 and creates a 16-bit free-running clocksource from timer2.

## APIs And Flow

`struct zevio_timer` stores MMIO windows, clock, embedded clockevent, and generated names. `zevio_timer_add()` allocates state, maps timer and optional interrupt registers, gets clock 0, maps IRQ 0, names the devices, configures timer1 as a clockevent when possible, then starts timer2 as an incrementing forever counter and registers it with `clocksource_mmio_init()`. Timer1 event callbacks load delta, enable/ack interrupts, stop the timer, and call the event handler.

## State, Dependencies, Risks, Tests

Allocated state persists for kernel lifetime. Hardware state includes timer1 current/control/interrupt mask and timer2 current/divider/control. Dependencies include OF address/IRQ/clock lookup, clockevents, clocksource MMIO helpers, IRQs, and slab allocation. Risks include registering a clockevent after `request_irq()` failure, interrupt mapping leaks, 16-bit wrap frequency, no rate-change handling, and no PM hooks. Test nodes with and without IRQ resources, event delivery, unique names, and wraparound monotonicity.
