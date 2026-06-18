<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sbsa_gwdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sbsa_gwdt.c

Purpose: watchdog-core driver for ARM SBSA Generic Watchdog with single-stage reset mode or two-stage WS0 panic mode.

Important APIs, types, and functions: `struct sbsa_gwdt` stores watchdog, system counter frequency, architecture version, MediaTek WS0 race workaround flag, and refresh/control frame bases. Key routines are versioned WOR read/write, `sbsa_gwdt_set_timeout()`, `sbsa_gwdt_get_timeleft()`, `sbsa_gwdt_keepalive()`, `sbsa_gwdt_get_version()`, start/stop, WS0 interrupt handler, probe, suspend, and resume.

Control flow: probe maps control and refresh frames, reads generic timer frequency, initializes watchdog, reads IIDR version/implementer, computes max heartbeat for 32-bit or 48-bit WOR, detects WS1 boot reset and already-enabled state, optionally requests WS0 IRQ for panic action, doubles max timeout in single-stage mode, initializes timeout, writes WOR, stops on reboot, and registers. Start sets WCS enable; ping writes WRR; get-timeleft combines WCV and system counter, adding an extra WOR stage in single-stage mode.

State and persistence behavior: state is hardware WCS flags, WOR offset, WCV compare, bootstatus, action module parameter, timeout, and min heartbeat workaround. Suspend stops active hardware and resume restarts when watchdog core says hardware was running.

Dependencies and integration points: depends on ARM arch timer counter/frequency, MMIO 64-bit lo/hi helpers, platform resources, optional IRQ, watchdog core, and panic path.

Risks and edge cases: `action` is a global module parameter and can be downgraded if IRQ request fails. MediaTek workaround changes min heartbeat to avoid refresh-at-WS0 race. Timeleft math assumes counter monotonicity and valid WCV.

Test signals: v0/v1 WOR width, action 0 and 1, IRQ failure fallback, WS1 bootstatus, already-running detection, MediaTek IIDR workaround, suspend/resume, and timeleft before/after WS0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sbsa_gwdt.c -->
