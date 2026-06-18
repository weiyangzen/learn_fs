# sources/distributed-fs/ceph-client/drivers/clocksource/armv7m_systick.c

Purpose: exposes the ARMv7-M SysTick down-counter as a simple MMIO clocksource.

Important APIs/types/functions: `system_timer_of_register()` maps registers, obtains the rate from `clock-frequency` or a clock provider, programs reload/control registers, and calls `clocksource_mmio_init()`.

Control flow: DT `arm,armv7m-systick` probing maps the timer, resolves a nonzero rate, loads the 24-bit reload maximum, enables the counter, and registers a 24-bit down-counting clocksource.

State and persistence: MMIO counter state is configured once; optional clock is enabled and kept on after successful registration.

Dependencies and integration points: depends on OF address mapping, common clock APIs, and `clocksource_mmio_readl_down`.

Risks: no clockevent is provided. Error paths release the clock and unmap registers, but successful path keeps resources permanently. A missing or zero frequency prevents registration.

Test signals: DT probe with explicit frequency and with clk provider, 24-bit wrap handling, and clocksource registration logs.
