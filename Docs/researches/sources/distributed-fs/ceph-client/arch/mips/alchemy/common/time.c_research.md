## sources/distributed-fs/ceph-client/arch/mips/alchemy/common/time.c

Purpose: implements Alchemy platform time initialization using the 32.768 kHz Counter1/RTC block as both a clocksource and a one-shot clock event source. If firmware did not enable the 32 kHz counter path or the counter registers do not become accessible, it falls back by disabling `cpu_wait`, forcing the kernel away from the wait-instruction idle path that depends on the low-power counter behavior.

Important APIs and functions: `plat_time_init()` is the exported architecture hook. It indexes `alchemy_m2inttab[]` by `alchemy_get_cputype()` and calls `alchemy_time_init()`. `au1x_counter1_read()` reads `AU1000_SYS_RTCREAD` for the clocksource. `au1x_rtcmatch2_set_next_event()` programs `AU1000_SYS_RTCMATCH2` after waiting for `SYS_CNTRL_M21` to clear. `au1x_rtcmatch2_irq()` dispatches the registered `clock_event_device` handler. The file defines static `clocksource` and `clock_event_device` descriptors with high ratings and 32-bit masks.

Control flow: initialization verifies `SYS_CNTRL_E0 | SYS_CNTRL_32S`, waits for trim/counter synchronization bits, writes `RTCTRIM` and `RTCWRITE`, registers the clocksource at 32768 Hz, computes clockevent mult/shift/min/max deltas, registers the device, and requests the CPU-specific RTC match2 interrupt with `IRQF_TIMER`.

State and persistence: state is hardware-register backed only. There is no filesystem persistence. The clockevent keeps its IRQ number and timing conversion fields in static kernel data. Counter register writes change SoC timing state until reset/suspend logic changes it.

Dependencies and integration: depends on Alchemy system register helpers, MIPS time hooks, Linux clocksource/clockevents, and CPU IDs from `au1000.h`. It integrates before normal timer use through `plat_time_init()` and with the interrupt subsystem through the match2 IRQ.

Risks: busy-wait loops can stall boot if register-ready bits are misreported; the code handles this by timeout except in match programming, which waits without timeout. Incorrect CPU type indexing would use the wrong RTC match interrupt. Firmware may report the 32 kHz-detected bit even if the clock is not actually reliable, which the comments explicitly warn about.

Test signals: boot logs should include `Alchemy clocksource installed` on working boards. Timer interrupt request failures emit an error. Functional tests are stable jiffies/clocksource selection, working one-shot timer events, and idle behavior without hangs.
