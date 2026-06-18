# sources/distributed-fs/ceph-client/drivers/clocksource/timer-msc313e.c

Purpose: MStar/SigmaStar MSC313E timer driver using first compatible timer as clocksource/sched_clock/delay and later timers as clockevents.

Important APIs/types/functions: `msc313e_timer_stop/start/setup/current_value()` handle 16-bit split registers. `msc313e_clksrc_init()` registers clocksource; `msc313e_clkevt_init()` allocates a `timer_of` and registers a clockevent. Static `msc313e_clkevt` is copied into each `timer_of`.

Control flow: `msc313e_timer_init()` increments `num_called`; first call initializes source, subsequent calls initialize event. For `sstar,ssd20xd-timer`, event init divides clock by `MSC313E_CLK_DIVIDER` and writes divider. Clockevent next/periodic paths stop, write high/low max, and start in one-shot or periodic. ISR directly dispatches the event handler.

State/persistence: global `msc313e_clksrc` and optional ARM delay state persist. The source path uses a stack `timer_of`; its base remains valid after init. Event path allocates persistent `timer_of` objects.

Dependencies/integration: compatibles `mstar,msc313e-timer` and `sstar,ssd20xd-timer`, `timer-of`, split 16-bit MMIO, optional ARM delay, clocksource/clockevents.

Risks: DT order controls source versus event role; clocksource uses `clocksource_mmio_init()` with custom read and base argument not used by read; event init leak on `timer_of_init()` failure; local IRQ disable is used for split register access. Tests should cover first/subsequent node ordering, SSD20x divider, split-register consistency, and event interrupt delivery.
