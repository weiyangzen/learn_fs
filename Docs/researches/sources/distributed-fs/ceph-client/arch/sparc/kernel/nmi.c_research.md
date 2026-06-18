# sources/distributed-fs/ceph-client/arch/sparc/kernel/nmi.c

Purpose: Implements SPARC64 pseudo-NMI hardlockup watchdog support using performance counter overflow interrupts.

Important APIs/types/functions: Global `nmi_active` tracks watchdog availability and active CPUs; per-CPU `wd_enabled`, `last_irq_sum`, `alert_counter`, and `nmi_touch` track liveness. `arch_touch_nmi_watchdog()` resets touch flags. `perfctr_irq()` is the pseudo-NMI handler. `start_nmi_watchdog()`, `stop_nmi_watchdog()`, `nmi_adjust_hz()`, `nmi_init()`, `watchdog_hardlockup_enable()`, and `watchdog_hardlockup_disable()` manage watchdog lifecycle. `die_nmi()` reports or panics on lockup.

Control flow: Initialization starts counters on all CPUs, spins CPUs briefly in `check_nmi_watchdog()` to verify interrupts arrive, then registers a reboot notifier. Each perf counter interrupt clears the soft interrupt, enters NMI context, switches to hardirq stack, runs die notifiers, checks whether normal IRQ counts advanced or the watchdog was touched, increments alert counters on stalls, and reloads/enables the counter when still active.

State and persistence: Runtime state is per-CPU watchdog counters and PCR/PIC hardware programming through `pcr_ops`. `panic_on_timeout` is set by `nmi_watchdog=panic`. The watchdog is disabled permanently by setting `nmi_active` to `-1` when setup fails.

Dependencies and integration points: It integrates Linux NMI/watchdog APIs, reboot notifiers, kdebug die notifiers, SPARC perf counter operations, `kstack.h` hardirq stack switching, CPU data NMI counters, and SMP cross-CPU calls.

Risks and test signals: Because this is not a real NMI, it depends on high-priority perf interrupts and correct PCR programming. False positives are possible if IRQ accounting stops for legitimate long critical sections. Tests include boot-time watchdog self-test, `nmi_watchdog=panic`, enable/disable per CPU, `nmi_adjust_hz()`, reboot shutdown, perf counter interrupt delivery, and hard lockup injection.
