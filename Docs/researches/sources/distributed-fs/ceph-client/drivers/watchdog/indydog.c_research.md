<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/indydog.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/indydog.c`

Purpose: legacy miscdevice watchdog for SGI IP22 Indy hardware using SGI memory-controller watchdog registers exposed through `sgimc`.

Important APIs, types, and functions: `indydog_start()` sets `SGIMC_CCTRL0_WDOG`, `indydog_stop()` clears it, and `indydog_ping()` writes `sgimc->watchdogt = 0`. The file operations implement open, write, ioctl, and release directly rather than using watchdog core.

Control flow: module init registers a reboot notifier and a misc watchdog device on `WATCHDOG_MINOR`. Open enforces single-open via `indydog_alive`, optionally pins the module for nowayout, starts and pings the hardware. Writes ping if non-empty. Ioctl supports support/status/options/keepalive/timeout. Release stops the hardware unless `nowayout` is set. Reboot notifier stops on `SYS_DOWN` or `SYS_HALT`.

State and persistence: state is a single open bit plus hardware enable in `cpuctrl0`; there is no magic-close character tracking. Timeout is fixed at 30 seconds and bootstatus is always reported as zero.

Dependencies and integration points: SGI IP22 architecture headers, miscdevice `/dev/watchdog`, reboot notifier, raw memory-controller access, and legacy watchdog ioctl ABI.

Risks and test signals: risks include lack of watchdog core supervision, no bootstatus, and stop-on-close behavior without magic close. Test single-open enforcement, WDIOC_SETOPTIONS, reboot notifier stop, nowayout module pinning, and repeated write keepalives on IP22 hardware or emulation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/indydog.c -->
