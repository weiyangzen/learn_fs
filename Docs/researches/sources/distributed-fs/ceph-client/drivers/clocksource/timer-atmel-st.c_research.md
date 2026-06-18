# sources/distributed-fs/ceph-client/drivers/clocksource/timer-atmel-st.c

Purpose: supports the AT91RM9200 system timer using its 32 kHz counter as both clocksource and periodic/one-shot clockevent source.

Important APIs, types, and functions: global state includes `last_crtr`, `irqmask`, `clkevt`, `regmap_st`, and `timer_latch`. `read_CRTR()` stabilizes asynchronous counter reads. `at91rm9200_timer_interrupt()`, `clkdev32k_disable_and_flush_irq()`, `clkevt32k_shutdown()`, `clkevt32k_set_oneshot()`, `clkevt32k_set_periodic()`, `clkevt32k_next_event()`, and `atmel_st_timer_init()` are the key routines.

Control flow: init obtains the syscon regmap, disables and clears timer-related interrupts, requests the shared IRQ, enables the slow clock, computes the HZ latch, sets the realtime prescaler, registers the clockevent with a minimum delta of two ticks, and registers the 20-bit `32k_counter` clocksource. One-shot mode uses the alarm register; periodic mode uses PIT interrupts. The ISR masks status by `irqmask`, handles alarms directly, and for periodic mode loops while the counter has advanced by at least one latch to deliver delayed ticks.

State and persistence: `last_crtr` tracks the last periodic tick point and is reset when interrupts are flushed. `irqmask` records the active mode. There is no disk persistence; hardware registers hold interrupt enables, alarm, and period.

Dependencies and integration points: integrates with syscon/regmap, Atmel ST register definitions, slow clock, OF IRQ parsing, clocksource, and clockevents.

Risks: the counter is asynchronous and not strictly monotonic unless read twice until stable. One-shot alarm hardware uses absolute time and requires minimum delta two to avoid wrap-delayed matches. Test signals include 32 kHz clocksource registration, one-shot alarm events, periodic delayed-tick catchup, shared IRQ behavior, and stable reads under stress.
