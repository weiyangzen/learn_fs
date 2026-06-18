<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_watchdog.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_watchdog.c

## Purpose
Implements `/dev/watchdog` using the IPMI watchdog timer. It watches for IPMI SMI interfaces, creates an IPMI user, exposes watchdog file operations and ioctls, maintains timeout/pretimeout policy, supports panic/reboot handling, and optionally uses x86 NMI pretimeout handling.

## Important APIs, Types, and Functions
- `ipmi_wdog_init()` registers parameter policy, reboot notifier, and an IPMI SMI watcher.
- `ipmi_register_watchdog()` creates the IPMI user, learns IPMI version, registers the misc watchdog device, optionally tests NMI pretimeout, and starts or stops the timer.
- `ipmi_set_timeout()`, `_ipmi_set_timeout()`, and `__ipmi_set_timeout()` send IPMI Set Watchdog Timer.
- `ipmi_heartbeat()`, `_ipmi_heartbeat()`, and `__ipmi_heartbeat()` send Reset Watchdog Timer and restore settings if the BMC reports timer-not-initialized.
- File operations implement open, write heartbeat and magic close, read/poll/fasync pretimeout notification, ioctls, and release.
- `ipmi_wdog_panic_handler()` and `wdog_reboot_handler()` adjust or disable the timer on panic, halt, poweroff, and reboot.

## Control Flow
The module registers an SMI watcher; when a suitable IPMI interface appears, it creates an IPMI user and registers `/dev/watchdog`. Opening the device marks it busy and defers actual start until first heartbeat. Writes reset the timer and optionally set magic close on `V`. Ioctls set timeout/pretimeout, enable/disable card, and keep alive. Close disables the card only after magic close unless `nowayout` or unexpected close behavior keeps it alive.

## State and Persistence
Global state includes timeout parameters, selected IPMI interface, `watchdog_user`, watchdog action/preaction/preop strings and encoded values, IPMI version, misc open bit, read waitqueue state, async queue, pretimeout flags, and shared static IPMI message buffers guarded by `ipmi_watchdog_mutex`, `ipmi_read_mutex`, atomics, and completion.

## Dependencies and Integration Points
Depends on IPMI user and SMI watcher APIs, Linux watchdog ABI, miscdevice `/dev/watchdog`, reboot notifiers, panic IPMI request path, and x86 NMI APIs when available. Module parameters expose `wdog_ifnum`, `timeout`, `pretimeout`, `panic_wdt_timeout`, `action`, `preaction`, `preop`, `start_now`, and `nowayout`.

## Risks
The driver uses static IPMI message buffers and completion accounting, so cleanup waits until lower layers release both send and receive messages. Panic and NMI paths intentionally avoid normal locking or use constrained operations. `preaction_op()` and `preop_op()` return 0 even if the set helper returns an error, which makes invalid strings worth checking against expected module-param behavior. Magic-close and nowayout interactions are safety-critical.

## Test Signals
Exercise watchdog open exclusivity, first heartbeat start, WDIOC timeout/pretimeout/keepalive/setoptions, magic close versus unexpected close, BMC reset response recovery, SMI hotplug/gone, reboot/halt/panic notifier behavior, and x86 NMI pretimeout registration/testing when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_watchdog.c -->
