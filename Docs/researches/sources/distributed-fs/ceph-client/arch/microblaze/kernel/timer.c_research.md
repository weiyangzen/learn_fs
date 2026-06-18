# sources/distributed-fs/ceph-client/arch/microblaze/kernel/timer.c

Purpose: implements the Xilinx timer as MicroBlaze clockevent, clocksource, timecounter, and sched_clock provider.

Important APIs and state: static `timer_baseaddr`, `freq_div_hz`, `timer_clock_freq`, endian-sensitive `read_fn`/`write_fn`, `clockevent_xilinx_timer`, `clocksource_microblaze`, `xilinx_tc`, and OF declaration for `"xlnx,xps-timer-1.00.a"`.

Control flow: init ignores PWM nodes, maps timer registers, probes register endian by writing `TCSR_MDT`, parses IRQ, requires a two-timer device, gets timer clock or falls back to CPU clock, requests IRQ, starts timer1 as continuous clocksource, registers clockevent, and registers sched_clock. Timer0 handles periodic/oneshot events and acks interrupts by rewriting TCSR0.

State and persistence: maps MMIO, stores global timer function pointers, registers IRQ/clock devices, and keeps timer1 running.

Dependencies and integration: called by `timer_probe()` in `time_init()`, depends on OF address/IRQ/clock data and CPU clock fallback.

Risks and test signals: one-timer hardware is rejected; endian detection depends on writable MDT bit; oneshot currently uses ARHT like periodic. Test timer IRQs, clocksource stability, big/little-endian registers, missing clock fallback, and PWM-node exclusion.
