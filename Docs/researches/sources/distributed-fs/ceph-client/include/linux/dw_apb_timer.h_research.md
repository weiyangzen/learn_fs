# sources/distributed-fs/ceph-client/include/linux/dw_apb_timer.h

## Purpose
This header declares common support for Synopsys DesignWare APB timers used as clockevent and clocksource devices.

## Important APIs, types, and functions
`APBTMRS_REG_SIZE` is the timer register span. `struct dw_apb_timer` stores MMIO base, frequency, and IRQ. `struct dw_apb_clock_event_device` embeds a clock event device, timer, and optional end-of-interrupt callback. `struct dw_apb_clocksource` embeds a timer and clocksource. APIs initialize/register clockevents and clocksources, start a clocksource, and read its counter.

## Control flow, state, and persistence
Timer state persists in MMIO registers and wrapper structs. Clockevent registration wires interrupts and event callbacks into the generic timekeeping framework. Clocksource start/read controls a free-running counter used for timekeeping.

## Dependencies and integration points
It depends on clockchips, clocksources, and interrupt headers. It is shared by platform timer drivers on ARM and other SoCs with DW APB timers.

## Risks and test signals
Risks include wrong frequency, invalid MMIO base, IRQ/EIO handling mistakes, and clocksource wrap/width assumptions. Tests should cover init failure paths, interrupt event delivery, clocksource monotonicity, suspend/resume if implemented in callers, and per-CPU clockevent registration.
