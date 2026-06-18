# sources/distributed-fs/ceph-client/drivers/char/hw_random/omap-rng.c

Purpose: TI OMAP and Inside Secure EIP76 RNG platform driver with support for multiple register layouts and health-recovery IRQs.

Important APIs, types, and functions: `struct omap_rng_dev`, `struct omap_rng_pdata`, register maps, `omap_rng_do_read()`, `omap2_rng_init()`, `omap4_rng_init()`, `eip76_rng_init()`, `omap4_rng_irq()`, probe/remove, and PM callbacks.

Control flow: probe maps registers, enables runtime PM and optional clocks, selects pdata from OF or legacy fallback, requests IRQ for OMAP4/EIP76, then registers hwrng. Reads require a full hardware output block, poll `data_present` up to 100 iterations, copy output registers, and acknowledge ready. OMAP4/EIP76 init programs refill cycles, FRO enable/detune, thresholds, interrupts, and TRNG enable.

State and persistence: state is per-device base, clocks, pdata, and hwrng. Suspend/remove disables TRNG and runtime PM; EIP76/OMAP4 IRQ handler can recover stopped FROs by detuning and reenabling them.

Dependencies and integration: platform/OF, clocks, runtime PM, interrupt subsystem, raw MMIO, and hwrng.

Risks and test signals: register-map zero entries are used as feature tests, so incorrect maps can suppress IRQ ack or masks. Tests should cover all compatible strings, timeout/non-waiting reads, IRQ FRO recovery, PM suspend/resume, error unwinding with clocks, and EIP76 16-byte output.
