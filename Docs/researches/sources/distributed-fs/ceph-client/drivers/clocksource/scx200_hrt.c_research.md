# sources/distributed-fs/ceph-client/drivers/clocksource/scx200_hrt.c

Purpose: provides a high-resolution timer clocksource for the AMD/NSC SCx200 platform by exposing the chipset HRT counter to the Linux clocksource core.

Important APIs, types, and functions: module parameters `mhz27` and `ppm` select the 27 MHz clock mode and adjust the registered frequency. `read_hrt()` reads the 32-bit counter with `inl(scx200_cb_base + SCx200_TIMER_OFFSET)`. `cs_hrt` is the registered `struct clocksource`. `init_hrt_clocksource()` verifies the SCx200 configuration block, reserves the ISA I/O region, programs the timer configuration byte, computes frequency, and registers the clocksource.

Control flow: module initialization exits unless `scx200_cb_present()` reports the configuration block. It reserves the HRT I/O range with `request_region()`, writes `HR_TMEN` plus optional `HR_TMCLKSEL` to `SCx200_TMCNFG_OFFSET`, computes `HRT_FREQ + ppm` and multiplies by 27 in 27 MHz mode, logs the selected mode, and registers the continuous 32-bit clocksource. Reads return the current I/O counter value directly.

State and persistence: persistent state is limited to reserved I/O/MMIO resources and the registered clocksource object. The timer hardware itself continues counting independently; the driver does not store state to disk.

Dependencies and integration points: integrates with `linux/scx200.h`, the SCx200 configuration block base address, ISA I/O port reservation, Linux clocksource core, module initialization, and low-level `inl()`/`outb()` accessors. It is a platform-specific alternative to the bad TSC on older Geode-class hardware.

Risks: the main risks are hardware availability, exclusive I/O-region ownership, and correct frequency selection. `ppm` is added directly to the 1 MHz base before optional 27x multiplication, so parameter semantics matter. Counter width/frequency assumptions determine wrap handling and time conversion. Test signals include module load on SCx200 hardware, the clocksource appearing with the expected 1 MHz or 27 MHz-derived frequency, monotonic reads across wrap boundaries, and clean failure on non-SCx200 systems or region conflicts.
