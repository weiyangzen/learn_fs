# sources/distributed-fs/ceph-client/drivers/clocksource/timer-pistachio.c

Purpose: Imagination Pistachio GPT clocksource-only driver using a general-purpose timer selected through peripheral syscon clock muxing.

Important APIs/types/functions: `struct pistachio_clocksource` wraps base, raw spinlock, and clocksource. `gpt_readl/writel()` calculate per-GPT offsets. `pistachio_clocksource_read_cycles()` reads overflow then current value in strict order under lock. `pistachio_clocksource_enable/disable()` program GPT0 reload/local enable.

Control flow: init maps GPT registers, gets peripheral regmap from `img,cr-periph`, switches timer control to fast clock, obtains and enables `sys` and `fast` clocks, disables IRQ masks for all GPTs, enables global timer block, initializes lock, registers sched_clock, then registers the clocksource.

State/persistence: static `pcs_gpt` stores all state. GPT0 local enable and reload value control the source. No clockevent state exists.

Dependencies/integration: compatible `img,pistachio-gptimer`, syscon regmap phandle, named clocks, clocksource/sched_clock.

Risks: no clockevent support; clocksource read depends on overflow-read latch semantics; failure paths after clock enable only partially unwind; `CLOCK_SOURCE_SUSPEND_NONSTOP` assumes timer continues through suspend. Test signals include regmap mux programming, fast clock rate, clocksource monotonicity, suspend behavior, and absence of GPT IRQs.
