# sources/distributed-fs/ceph-client/drivers/clocksource/timer-stm32.c

Purpose: STM32 general timer driver registering each compatible timer as a clocksource and clockevent, with sched_clock/delay only from the first 32-bit timer.

Important APIs/types/functions: `struct stm32_timer_private` stores detected width. `stm32_timer_set_width()` probes ARR truncation to detect 16/32 bits. `stm32_timer_set_prescaler()` targets 10 MHz for 16-bit timers and no prescale for 32-bit. Clockevent callbacks use CCR1 compare interrupts.

Control flow: init allocates `timer_of`, initializes base/clock/IRQ, allocates private data, optionally resets hardware, detects width, sets prescaler/rate/period, registers clocksource, then registers clockevent. Clocksource path starts a 32-bit timer immediately for sched_clock/delay if none exists. Next-event writes CNT+delta to CCR1 and returns `-ETIME` if already missed; IRQ clears status, reprograms periodic or shuts down oneshot, then dispatches.

State/persistence: each timer has heap `timer_of` and private width data. Global `stm32_timer_cnt` selects one sched_clock/delay counter.

Dependencies/integration: compatible `st,stm32-timer`, reset controller, `timer-of`, ARM delay timer, clocksource/clockevents.

Risks: `(1 << bits) - 1` overflows for 32-bit `int`; cleanup after private allocation failure calls `timer_of_cleanup()` but frees only outer `to`; periodic mode reprograms using current CNT after IRQ. Test signals include 16- and 32-bit timers, reset behavior, sched_clock only once, compare miss handling, and clockevent max delta correctness.
