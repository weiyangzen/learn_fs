# sources/distributed-fs/ceph-client/drivers/clocksource/timer-npcm7xx.c

Purpose: Nuvoton NPCM/WPCM timer driver using timer0 as clockevent and timer1 as 24-bit down-counting clocksource.

Important APIs/types/functions: static `npcm7xx_to` is a `timer_of` with base/clock/IRQ. Clockevent callbacks manipulate TCSR0/TICR0. `npcm7xx_clocksource_init()` programs timer1 max count and registers MMIO down clocksource. `npcm7xx_clockevents_init()` initializes timer0 and registers clockevent.

Control flow: init calls `timer_of_init()`, divides input clock by prescale+1, optionally enables a second clock for timer1, initializes source then event, and logs base/IRQ. Periodic mode writes `timer_of_period()` to TICR0 and starts period/int/count bits; next-event writes requested value and starts. ISR clears T0 interrupt in TISR and dispatches.

State/persistence: one static `timer_of` keeps base/clock/IRQ. Timer1 clock source runs continuously; timer0 state follows clockevent mode. Optional second clock is enabled and retained.

Dependencies/integration: compatibles `nuvoton,wpcm450-timer` and `nuvoton,npcm750-timer`, `timer-of`, optional second clock, clocksource/clockevents.

Risks: second clock acquisition treats any non-NULL pointer as present before `IS_ERR()`; clocksource init return is ignored; clockevent cpumask fixed to CPU0; 24-bit source has limited range. Test signals include timer0 interrupts, timer1 down-count monotonic conversion, prescaler rate correctness, and boot log with base/IRQ.
