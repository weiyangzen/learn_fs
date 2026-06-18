# sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-time.c

Purpose: calibrates the R4k counter on IP22 using the SGI 8254-compatible timer and handles unexpected 8254 interrupts.

Important APIs and control flow: `dosample()` programs timer counter 2, samples CP0 count until the latched top byte reaches zero, stops the counter, and rounds the result. `plat_time_init()` primes caches, obtains two or three samples, averages if needed, logs the CPU rate, sets `mips_hpt_frequency`, and calls `setup_pit_timer()` on FullHouse. `indy_8254timer_irq()` logs unexpected 8254 interrupts and drops to ARC interactive mode.

State, persistence, and integration: state is `mips_hpt_frequency` and optional PIT timer setup. Dependencies include `sgint` timer registers and ARCS fallback. Risks include busy-wait calibration sensitivity, fatal handling of 8254 interrupts, and clock drift if samples are inconsistent. Test signals are calibration log, stable scheduler clock, and timer IRQ delivery through R4k compare.
