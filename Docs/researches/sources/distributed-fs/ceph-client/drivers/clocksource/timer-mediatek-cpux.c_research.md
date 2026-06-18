# sources/distributed-fs/ceph-client/drivers/clocksource/timer-mediatek-cpux.c

Purpose: MediaTek CPUX General Purpose Timer wrapper setup for SoCs where CPUXGPT feeds the AArch64 system timer. It registers a low-rated clockevent control shim without declaring a timer IRQ.

Important APIs/types/functions: `mtk_cpux_readl()` and `mtk_cpux_writel()` access indexed CPUX registers through wrapper index/data registers. `mtk_cpux_set_irq()` masks/unmasks per-CPU timer IRQ bits for possible CPUs. `mtk_cpux_init()` configures divider and global enable. The static `timer_of to` requests only base and clock.

Control flow: init obtains base/clock via `timer_of_init()`, warns if the supplied clock exceeds the supported range, writes DIV2 to produce a 13 MHz timer from 26 MHz input, enables all CPUXGPT timers, then registers the clockevent with sync-tick minimum. Shutdown masks CPUX IRQ bits but intentionally leaves the timer running because firmware may depend on it; resume unmasks.

State/persistence: global `to` keeps MMIO/clock state. CPUX global control remains enabled for boot lifetime. IRQ mask state is the only clockevent state changed by callbacks.

Dependencies/integration: compatible `mediatek,mt6795-systimer`, `timer-of`, CPU possible mask, AArch64 architectural timer/firmware expectations.

Risks: no actual `set_next_event()` or IRQ handler, so it relies on the architecture timer path; disabling the timer is explicitly unsafe; unsupported clock frequencies may still boot with timing instability; indexed register access must be serialized by hardware/boot context. Test signals include boot without lockups, correct 13 MHz configuration, low clockevent rating, and suspend/resume IRQ masking.
